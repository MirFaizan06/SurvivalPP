// The Veiled Blossom (Hanae) - the first main boss.  Ritual, three phases, Petal Fan, Mirror Step, Veiled Echoes, Blossom Vexes,
// Falling Blossoms, the Eclipse Bloom petal spiral, and a fog that changes with the fight.
import { world, system, EntityComponentTypes, EntityDamageCause } from '@minecraft/server';
import { tickMusic, stopMusic } from './music.js';
import { playIntro, INTRO_TAG } from './cinematic.js';
import { NS, DIM_IDS, safe, dimOf, consumeMainhand, say, msg, spawnParticle, playSound, rand, randInt, runLater } from './util.js';
import { nearbyPlayers, titleAll, healthFrac, shockwave } from './boss.js';

export const HANAE = `${NS}:veiled_blossom`;
const VEX = `${NS}:blossom_vex`;
const ECHO = `${NS}:blossom_echo`;
const BLADE = `${NS}:petal_blade`;
const FOG_ID = 'ecr_hanae';
const FOGS = [`${NS}:blossom_veil`, `${NS}:blossom_storm`, `${NS}:eclipse_bloom`];
const NOTES = [0.5, 0.56, 0.67, 0.75, 0.84, 1.0, 1.12, 1.26];       // a pentatonic-ish scale for the shrine bells
const state = new Map();                                              // boss id -> runtime data

const LEAF = 'minecraft:cherry_leaves_particle';

const vec = {
    sub: (a, b) => ({ x: a.x - b.x, y: a.y - b.y, z: a.z - b.z }),
    len: (a) => Math.hypot(a.x, a.y, a.z),
    norm: (a) => { const l = Math.hypot(a.x, a.y, a.z) || 1; return { x: a.x / l, y: a.y / l, z: a.z / l }; },
    rotY: (a, deg) => { const r = (deg * Math.PI) / 180, c = Math.cos(r), s = Math.sin(r); return { x: a.x * c - a.z * s, y: a.y, z: a.x * s + a.z * c }; },
};

function nearestPlayer(boss, r = 48) {
    let best, bd = 1e9;
    for (const p of nearbyPlayers(boss.dimension, boss.location, r)) {
        const d = vec.len(vec.sub(p.location, boss.location));
        if (d < bd) { bd = d; best = p; }
    }
    return best;
}

function countNear(dim, type, loc, r) {
    return (safe(() => dim.getEntities({ type, location: loc, maxDistance: r })) || []).length;
}

function openSpot(dim, c, r) {
    for (let i = 0; i < 14; i++) {
        const a = rand(0, Math.PI * 2), d = rand(r * 0.5, r);
        const x = Math.floor(c.x + Math.cos(a) * d), z = Math.floor(c.z + Math.sin(a) * d);
        for (let dy = 3; dy >= -3; dy--) {
            const y = Math.floor(c.y) + dy;
            const feet = safe(() => dim.getBlock({ x, y, z })), head = safe(() => dim.getBlock({ x, y: y + 1, z })), floor = safe(() => dim.getBlock({ x, y: y - 1, z }));
            if (feet && head && floor && feet.isAir && head.isAir && !floor.isAir && !floor.isLiquid) return { x: x + 0.5, y, z: z + 0.5 };
        }
    }
    return undefined;
}

function cast(boss, ticks = 30) {
    safe(() => boss.triggerEvent(`${NS}:cast_on`));
    runLater(ticks, () => boss.isValid && boss.triggerEvent(`${NS}:cast_off`));
}

function due(s, key, now, every, first = every) {
    if (s.next[key] === undefined) s.next[key] = now + first;
    if (now < s.next[key]) return false;
    s.next[key] = now + every;
    return true;
}

const LINES = [
    ['§f"Turn back, wayfarer. I do not wish to hurt you."', '§f"Seven Seals... and the Eclipse waits behind the last."', '§f"No one who walked this road has ever returned."'],
    ['§f"You keep walking. Why? The ending was never meant to be reached."', '§f"I was like you once. I read the same journal."', '§f"Stop. Please. It is impossible."'],
    ['§f"The Seal is tearing me open... I cannot hold the veil..."', '§f"Run, wayfarer! Run while I can still stay my hand!"', '§f"If you will not stop, then at least... remember me."'],
];

function speak(dim, loc, text) {
    for (const p of nearbyPlayers(dim, loc, 60)) msg(p, `§d[Hanae] ${text}`);
}

function bell(dim, loc, vol = 1.6) {
    playSound(dim, 'note.bell', loc, { volume: vol, pitch: NOTES[randInt(0, NOTES.length - 1)] });
}

// ------------------------------------------------------------------------------------------- projectiles
function fireBlade(boss, dir, speed = 1.5, y = 1.8) {
    const o = boss.location;
    const p = { x: o.x + dir.x * 1.2, y: o.y + y, z: o.z + dir.z * 1.2 };
    const e = safe(() => boss.dimension.spawnEntity(BLADE, p), 'spawnBlade');
    if (!e) return;
    safe(() => {
        const comp = e.getComponent(EntityComponentTypes.Projectile);
        if (comp) {
            comp.owner = boss;
            comp.shoot({ x: dir.x * speed, y: dir.y * speed, z: dir.z * speed });
        }
    }, 'shootBlade');
}

function petalFan(boss, target, shots, spread) {
    const aim = vec.norm(vec.sub({ x: target.location.x, y: target.location.y + 1.0, z: target.location.z }, { x: boss.location.x, y: boss.location.y + 1.8, z: boss.location.z }));
    cast(boss, 18);
    playSound(boss.dimension, 'mob.evocation_illager.cast_spell', boss.location, { volume: 2, pitch: 1.5 });
    for (let i = 0; i < shots; i++) {
        const a = shots === 1 ? 0 : -spread / 2 + (spread * i) / (shots - 1);
        fireBlade(boss, vec.rotY(aim, a));
    }
}

// ------------------------------------------------------------------------------------------- abilities
function mirrorStep(boss, target, phase, s) {
    const dim = boss.dimension;
    const view = safe(() => target.getViewDirection()) || { x: 0, y: 0, z: 1 };
    const flat = vec.norm({ x: view.x, y: 0, z: view.z });
    const dest = openSpot(dim, { x: target.location.x - flat.x * 3, y: target.location.y, z: target.location.z - flat.z * 3 }, 1.4);
    if (!dest) return;
    for (let i = 0; i < 18; i++) spawnParticle(dim, LEAF, { x: dest.x + rand(-1, 1), y: dest.y + rand(0, 2.4), z: dest.z + rand(-1, 1) });
    playSound(dim, 'beacon.power', dest, { volume: 1.5, pitch: 1.8 });
    say(target, '§d✿ The air shimmers behind you...');
    runLater(18, () => {
        if (!boss.isValid) return;
        for (let i = 0; i < 24; i++) spawnParticle(dim, LEAF, { x: boss.location.x + rand(-1, 1), y: boss.location.y + rand(0, 2.6), z: boss.location.z + rand(-1, 1) });
        safe(() => boss.teleport(dest, { facingLocation: target.location }));
        playSound(dim, 'mob.endermen.portal', dest, { volume: 1.5, pitch: 1.4 });
        const strikes = 1;
        for (let k = 0; k < strikes; k++) {
            runLater(8 + k * 10, () => {
                if (!boss.isValid || !target.isValid) return;
                if (vec.len(vec.sub(target.location, boss.location)) <= 4.8) {
                    safe(() => {
                        target.applyDamage(3 + phase, { cause: EntityDamageCause.entityAttack, damagingEntity: boss });
                        const d = vec.norm(vec.sub(target.location, boss.location));
                        target.applyKnockback({ x: d.x * 1.1, z: d.z * 1.1 }, 0.4);
                        target.addEffect('slowness', 30, { amplifier: 0, showParticles: false });
                    }, 'mirrorHit');
                    for (let i = 0; i < 14; i++) spawnParticle(dim, 'minecraft:large_explosion', { x: target.location.x + rand(-0.6, 0.6), y: target.location.y + rand(0.2, 1.8), z: target.location.z + rand(-0.6, 0.6) });
                    playSound(dim, 'random.anvil_land', target.location, { volume: 1.2, pitch: 1.6 });
                }
            });
        }
    });
}

function summonEchoes(boss, n, cap) {
    const dim = boss.dimension;
    n = Math.min(n, cap - countNear(dim, ECHO, boss.location, 48));
    for (let i = 0; i < n; i++) {
        const spot = openSpot(dim, boss.location, 7);
        if (!spot) continue;
        safe(() => {
            dim.spawnEntity(ECHO, spot);
            for (let k = 0; k < 16; k++) spawnParticle(dim, LEAF, { x: spot.x + rand(-0.7, 0.7), y: spot.y + rand(0, 2.6), z: spot.z + rand(-0.7, 0.7) });
        }, 'spawnEcho');
    }
    if (n > 0) { playSound(dim, 'note.chime', boss.location, { volume: 2, pitch: 0.7 }); cast(boss, 30); }
    return n;
}

function summonVexes(boss, n, cap) {
    const dim = boss.dimension;
    n = Math.min(n, cap - countNear(dim, VEX, boss.location, 48));
    for (let i = 0; i < n; i++) {
        const a = rand(0, Math.PI * 2);
        const p = { x: boss.location.x + Math.cos(a) * 3, y: boss.location.y + rand(1.5, 3), z: boss.location.z + Math.sin(a) * 3 };
        safe(() => { dim.spawnEntity(VEX, p); for (let k = 0; k < 8; k++) spawnParticle(dim, LEAF, { x: p.x + rand(-0.4, 0.4), y: p.y + rand(-0.4, 0.4), z: p.z + rand(-0.4, 0.4) }); }, 'spawnVex');
    }
    if (n > 0) { playSound(dim, 'mob.vex.ambient', boss.location, { volume: 2, pitch: 1.3 }); cast(boss, 24); }
}

function fallingBlossoms(boss, phase) {
    const dim = boss.dimension;
    const players = nearbyPlayers(dim, boss.location, 36);
    if (!players.length) return;
    cast(boss, 40);
    const n = Math.min(players.length + phase, 3);
    for (let i = 0; i < n; i++) {
        const p = players[i % players.length];
        const spot = i < players.length ? { x: p.location.x, y: p.location.y, z: p.location.z } : { x: p.location.x + rand(-5, 5), y: p.location.y, z: p.location.z + rand(-5, 5) };
        for (let t = 0; t < 40; t += 5) {
            runLater(t, () => {
                for (let k = 0; k < 14; k++) {
                    const a = (k / 14) * Math.PI * 2;
                    spawnParticle(dim, LEAF, { x: spot.x + Math.cos(a) * 3.1, y: spot.y + 0.2, z: spot.z + Math.sin(a) * 3.1 });
                }
                spawnParticle(dim, LEAF, { x: spot.x + rand(-1, 1), y: spot.y + 5 - t / 10, z: spot.z + rand(-1, 1) });
            });
        }
        runLater(40, () => {
            bell(dim, spot, 2);
            for (let k = 0; k < 30; k++) spawnParticle(dim, LEAF, { x: spot.x + rand(-3, 3), y: spot.y + rand(0, 2.5), z: spot.z + rand(-3, 3) });
            for (const v of nearbyPlayers(dim, spot, 3.4)) {
                safe(() => {
                    v.applyDamage(3 + phase, { cause: EntityDamageCause.entityExplosion, damagingEntity: boss });
                    v.addEffect('slowness', 40, { amplifier: 0, showParticles: false });
                }, 'blossomHit');
            }
        });
    }
}

function petalSpiral(boss, s, now) {
    cast(boss, 90);
    playSound(boss.dimension, 'mob.wither.spawn', boss.location, { volume: 1.5, pitch: 1.6 });
    let angle = rand(0, 360), t = 0;
    const id = system.runInterval(() => {
        safe(() => {
            if (!boss.isValid || t > 84) { system.clearRun(id); return; }
            for (let k = 0; k < 3; k++) {
                const d = vec.rotY({ x: 1, y: 0.02 * (k - 1), z: 0 }, angle + k * 120);
                fireBlade(boss, d, 1.1, 1.4);
            }
            angle += 23; t += 6;
            if (t % 16 === 0) bell(boss.dimension, boss.location, 1);
        }, 'spiralTick');
    }, 6);
}

// ------------------------------------------------------------------------------------------- fog
function setFog(player, fogIndex, s) {
    const cur = s.fog.get(player.id);
    if (cur === fogIndex) return;
    safe(() => {
        if (cur !== undefined) player.runCommand(`fog @s remove ${FOG_ID}`);
        if (fogIndex >= 0) player.runCommand(`fog @s push ${FOGS[fogIndex]} ${FOG_ID}`);
    }, 'fog');
    if (fogIndex >= 0) s.fog.set(player.id, fogIndex); else s.fog.delete(player.id);
}

function clearFog(s) {
    for (const p of world.getAllPlayers()) {
        if (s.fog.has(p.id)) safe(() => p.runCommand(`fog @s remove ${FOG_ID}`), 'fogClear');
    }
    s.fog.clear();
}

// ------------------------------------------------------------------------------------------- ritual
export function startHanaeRitual(block, player) {
    const dim = block.dimension;
    const c = { x: block.location.x + 0.5, y: block.location.y + 1, z: block.location.z + 0.5 };
    if ((safe(() => dim.getEntities({ type: HANAE, location: c, maxDistance: 200 })) || []).length) {
        say(player, '§dThe Veiled Blossom already walks this grove.');
        return false;
    }
    consumeMainhand(player, 1);
    msg(player, '§d✿ The Veiled Mirror clouds over, then shatters into petals...');
    titleAll(dim, c, '§dThe mirror trembles...', '§7A veil is lifting');
    const s0 = { fog: new Map() };
    for (const p of nearbyPlayers(dim, c, 50)) setFog(p, 0, s0);
    let t = 0;
    const id = system.runInterval(() => {
        safe(() => {
            t += 2;
            for (let i = 0; i < 8; i++) {
                const a = rand(0, Math.PI * 2) + t * 0.12;
                const r = 5 - (t / 160) * 3.5;
                spawnParticle(dim, LEAF, { x: c.x + Math.cos(a) * r, y: c.y + rand(0, 3) + (t / 160) * 2.5, z: c.z + Math.sin(a) * r });
            }
            if (t % 16 === 0) playSound(dim, 'note.bell', c, { volume: 2, pitch: NOTES[(t / 16) % NOTES.length] });
            if (t === 100) titleAll(dim, c, '§d§l. . .', '§fwho wakes the Veil?');
            if (t >= 160) {
                system.clearRun(id);
                const boss = dim.spawnEntity(HANAE, { x: c.x, y: c.y + 1, z: c.z });
                const s = { next: {}, fog: s0.fog, phase: 0, transition: undefined, shield: false };
                state.set(boss.id, s);
                playSound(dim, 'mob.enderdragon.growl', c, { volume: 3, pitch: 1.6 });
                for (let i = 0; i < 40; i++) spawnParticle(dim, LEAF, { x: c.x + rand(-2.5, 2.5), y: c.y + rand(0, 4), z: c.z + rand(-2.5, 2.5) });
                boss.addTag('ecr_introduced');
                if (!playIntro(boss)) titleAll(dim, c, '§d§lTHE VEILED BLOSSOM', '§fHanae, Keeper of the First Seal');
            }
        }, 'hanaeRitual');
    }, 2);
    return true;
}

// ------------------------------------------------------------------------------------------- brain
function phaseOf(boss) {
    const f = healthFrac(boss);
    return f <= 0.33 ? 2 : f <= 0.66 ? 1 : 0;
}

function bossTick(boss) {
    const now = system.currentTick;
    let s = state.get(boss.id);
    if (!s) { s = { next: {}, fog: new Map(), phase: 0, shield: false }; state.set(boss.id, s); }
    if (!boss.hasTag('ecr_introduced')) { boss.addTag('ecr_introduced'); playIntro(boss); }
    if (boss.hasTag(INTRO_TAG)) return;
    tickMusic(boss);
    const dim = boss.dimension, L = boss.location;
    const want = phaseOf(boss);
    const cur = safe(() => boss.getProperty('ecr:phase')) ?? 0;
    if (want > cur) {
        if (cur === 0 && want === 2) safe(() => boss.triggerEvent('ecr:enter_phase_2'));
        safe(() => boss.triggerEvent(want === 2 ? 'ecr:enter_phase_3' : 'ecr:enter_phase_2'));
        s.transition = want;
    }
    const phase = Math.max(cur, want);
    const players = nearbyPlayers(dim, L, 60);
    // fog follows the phase; players walking out of range get their sky back
    for (const p of players) setFog(p, phase, s);
    for (const p of world.getAllPlayers()) {
        if (s.fog.has(p.id) && !players.some((q) => q.id === p.id)) setFog(p, -1, s);
    }
    if (s.transition !== undefined) {
        if (s.transition === 1) {
            titleAll(dim, L, '§d§lFALLING BLOSSOMS', '§fthe grove weeps petals');
            shockwave(dim, L, 8, 2, 1.2, boss);
            summonVexes(boss, 2, 3);
        } else {
            titleAll(dim, L, '§4§lECLIPSE BLOOM', '§7the Seal is breaking her');
            shockwave(dim, L, 10, 3, 1.4, boss);
            summonVexes(boss, 2, 4);
            summonEchoes(boss, 1, 2);
            playSound(dim, 'mob.wither.death', L, { volume: 3, pitch: 1.4 });
        }
        s.transition = undefined;
    }
    const target = nearestPlayer(boss);
    // phase 1: Petal Fan + Mirror Step + Veiled Echoes
    // She never wants to kill: when anyone nearby is badly hurt she lowers her parasol and holds every attack for a while
    if (players.some((p) => (safe(() => p.getComponent(EntityComponentTypes.Health).currentValue) ?? 20) <= 7)) {
        if (!(s.mercyUntil > now)) speak(dim, L, '§f*lowers her parasol* "...Enough. Catch your breath."');
        s.mercyUntil = now + 160;
    }
    const mercy = s.mercyUntil > now;
    if (!mercy) {
        if (target && due(s, 'fan', now, [160, 130, 105][phase], 100)) petalFan(boss, target, [3, 5, 5][phase], [40, 60, 70][phase]);
        if (target && due(s, 'step', now, [300, 250, 200][phase], 200)) mirrorStep(boss, target, phase, s);
        if (due(s, 'echo', now, [1100, 900, 760][phase], 300)) summonEchoes(boss, phase === 2 ? 2 : 1, 2);
        // phase 2+: Blossom Vexes and Falling Blossoms
        if (phase >= 1 && due(s, 'vex', now, [0, 700, 560][phase], 400)) summonVexes(boss, phase === 2 ? 3 : 2, phase === 2 ? 4 : 3);
        if (phase >= 1 && due(s, 'blossoms', now, [0, 340, 260][phase], 220)) fallingBlossoms(boss, phase);
        // phase 3: Petal Spiral (slow and readable)
        if (phase === 2 && due(s, 'spiral', now, 640, 200)) petalSpiral(boss, s, now);
    }
    // she talks while she fights: every warning is the same plea - stop this journey
    if (due(s, 'speech', now, 500, 140)) speak(dim, L, LINES[phase][randInt(0, LINES[phase].length - 1)]);
    // reflections shield her
    const echoes = countNear(dim, ECHO, L, 50);
    if (echoes > 0 && now % 20 < 5) {
        safe(() => boss.addEffect('resistance', 50, { amplifier: 4, showParticles: false }));
        for (let i = 0; i < 6; i++) spawnParticle(dim, LEAF, { x: L.x + rand(-1.4, 1.4), y: L.y + rand(0.2, 3), z: L.z + rand(-1.4, 1.4) });
        if (!s.shield) { s.shield = true; for (const p of players) say(p, '§d✿ Her reflections shield her - shatter the Veiled Echoes!'); }
    } else if (echoes === 0) s.shield = false;
    // ambience: petals drift around everyone in the fight (stronger each phase)
    if (now % 10 < 5) for (const p of players) for (let i = 0; i < 3 + phase * 3; i++) spawnParticle(dim, LEAF, { x: p.location.x + rand(-5, 5), y: p.location.y + rand(0.5, 4), z: p.location.z + rand(-5, 5) });
    if (now % 10 < 5) spawnParticle(dim, LEAF, { x: L.x + rand(-1.6, 1.6), y: L.y + rand(0, 3.2), z: L.z + rand(-1.6, 1.6) });
    if (due(s, 'bell', now, 80, 40)) bell(dim, L, 1.2);
}

export function initBlossom() {
    system.runInterval(() => {
        for (const id of DIM_IDS) {
            const bosses = safe(() => dimOf(id).getEntities({ type: HANAE })) || [];
            for (const b of bosses) safe(() => bossTick(b), 'hanaeTick');
        }
    }, 5);

    world.afterEvents.entityDie.subscribe((ev) => {
        const e = ev.deadEntity;
        if (e.typeId === ECHO) {                                 // a shattered reflection bursts into petals
            const dim = e.dimension, L = e.location;
            for (let i = 0; i < 24; i++) spawnParticle(dim, LEAF, { x: L.x + rand(-1, 1), y: L.y + rand(0, 2.4), z: L.z + rand(-1, 1) });
            playSound(dim, 'random.glass', L, { volume: 1.5, pitch: 1.6 });
            for (const p of nearbyPlayers(dim, L, 2.6)) safe(() => p.applyDamage(3, { cause: EntityDamageCause.entityExplosion }), 'echoBurst');
            return;
        }
        if (e.typeId !== HANAE) return;
        stopMusic(e);
        const s = state.get(e.id) || { fog: new Map() };
        state.delete(e.id);
        const dim = e.dimension, L = e.location;
        for (const m of safe(() => dim.getEntities({ location: L, maxDistance: 60, families: ['ecr_minion'] })) || []) safe(() => m.kill(), 'killMinion');
        clearFog(s);
        for (let i = 0; i < 80; i++) spawnParticle(dim, LEAF, { x: L.x + rand(-3, 3), y: L.y + rand(0, 5), z: L.z + rand(-3, 3) });
        for (let k = 0; k < 8; k++) runLater(k * 10, () => playSound(dim, 'note.bell', L, { volume: 2, pitch: NOTES[k % NOTES.length] }));
        titleAll(dim, L, '§d§lThe Veil Lifts', '§f"...thank you. Six Seals remain."');
        speak(dim, L, '§f"...You will not stop, will you? Then take my Seal, wayfarer. And please... do not let the Eclipse take you too."');
    });
}
