// Ysolde, the Frost Cantor - the third main boss.  She conducts the fight in 3/4 time: every attack is announced by the beat.
// Phase 1 "Overture": Aria (frozen notes), Resonance Rings (jump them), the Choir answers.   Phase 2 "Crescendo": whiteout blizzard (kneel against it),
// Icicle Chorus.   Phase 3 "Requiem": a double note spiral and the Final Verse - interrupt her with damage or run.
import { world, system, EntityComponentTypes, EntityDamageCause } from '@minecraft/server';
import { tickMusic, stopMusic } from './music.js';
import { playIntro, INTRO_TAG } from './cinematic.js';
import { NS, DIM_IDS, safe, dimOf, msg, spawnParticle, playSound, rand, randInt, runLater } from './util.js';
import { nearbyPlayers, titleAll, healthFrac } from './boss.js';
import { vec, nearestPlayer, countNear, openSpot, cast, due, hp, knock, fogController, speak } from './bossutil.js';

export const CANTOR = `${NS}:frost_cantor`;
const NOTE = `${NS}:frost_note`;
const HOAR = `${NS}:hoarbone`;
const RIME = `${NS}:rimewalker`;
const FOG_ID = 'ecr_cantor';
const FOGS = [`${NS}:cantor_whiteout`, `${NS}:cantor_blizzard`, `${NS}:cantor_requiem`];
const fog = fogController(FOG_ID, FOGS);
const state = new Map();                         // boss id -> runtime data
const SCALE = [0.5, 0.56, 0.67, 0.75, 0.84, 1.0, 1.12, 1.26];

const LINES = [
    ['"Hush, wayfarer... you walk in the middle of a song."', '"Every verse you found was a verse I wrote. Listen to what they say."', '"I kept the Third Shard asleep with a lullaby. Do you hear how it hums?"'],
    ['"Louder. It wakes when I falter. Help me keep time."', '"The snow remembers every voice that ever sang to it."', '"She sang the last verse with me, once. The Wayfarer. She had a beautiful voice."'],
    ['"The song is finishing... and the Shard is singing the rest."', '"Break my verse, wayfarer. Break it before it ends."', '"If the music stops, the Seal opens. If it never stops, I never rest."'],
];

function fireNote(boss, dir, speed = 1.5, y = 2.2) {
    const o = boss.location;
    const e = safe(() => boss.dimension.spawnEntity(NOTE, { x: o.x + dir.x * 1.2, y: o.y + y, z: o.z + dir.z * 1.2 }), 'spawnNote');
    if (!e) return;
    safe(() => {
        const comp = e.getComponent(EntityComponentTypes.Projectile);
        if (comp) { comp.owner = boss; comp.shoot({ x: dir.x * speed, y: dir.y * speed, z: dir.z * speed }); }
    }, 'shootNote');
}

function beatSound(dim, loc, strong, vol = 1.4) {
    playSound(dim, 'note.harp', loc, { volume: vol, pitch: strong ? 1.26 : 0.84 });
}

// ------------------------------------------------------------------------------------------- abilities
function aria(boss, target, shots, spread) {
    const aim = vec.norm(vec.sub({ x: target.location.x, y: target.location.y + 1.0, z: target.location.z }, { x: boss.location.x, y: boss.location.y + 2.2, z: boss.location.z }));
    cast(boss, 20);
    playSound(boss.dimension, 'beacon.power', boss.location, { volume: 1.6, pitch: 1.7 });
    for (let i = 0; i < shots; i++) {
        const a = shots === 1 ? 0 : -spread / 2 + (spread * i) / (shots - 1);
        runLater(i * 3, () => boss.isValid && fireNote(boss, vec.rotY(aim, a)));
    }
}

/** a ring that expands from her; only players who are standing on the ground when it passes take the hit - jump it */
function resonanceRing(boss, phase, count) {
    const dim = boss.dimension;
    const c = { x: boss.location.x, y: boss.location.y, z: boss.location.z };
    cast(boss, 30 + count * 14);
    for (let n = 0; n < count; n++) {
        runLater(20 + n * 14, () => {
            if (!boss.isValid) return;
            beatSound(dim, c, n === 0, 2.0);
            let r = 1.5;
            const id = system.runInterval(() => {
                safe(() => {
                    if (!boss.isValid || r > 15) { system.clearRun(id); return; }
                    const pts = Math.max(12, Math.floor(r * 4));
                    for (let k = 0; k < pts; k++) {
                        const a = (k / pts) * Math.PI * 2;
                        spawnParticle(dim, `${NS}:rime_burst`, { x: c.x + Math.cos(a) * r, y: c.y + 0.15, z: c.z + Math.sin(a) * r });
                    }
                    for (const p of nearbyPlayers(dim, c, r + 1.6)) {
                        const d = Math.hypot(p.location.x - c.x, p.location.z - c.z);
                        if (Math.abs(d - r) > 1.5) continue;
                        if (p.location.y - c.y > 0.9 || !safe(() => p.isOnGround)) continue;        // airborne: you cleared the wave
                        const hit = p.getTags().includes('ecr_ringed') ? false : true;
                        if (!hit) continue;
                        safe(() => {
                            p.addTag('ecr_ringed');
                            runLater(10, () => safe(() => p.removeTag('ecr_ringed')));
                            p.applyDamage(3 + phase, { cause: EntityDamageCause.entityAttack, damagingEntity: boss });
                            p.addEffect('slowness', 40, { amplifier: 1, showParticles: false });
                        }, 'ringHit');
                        knock(p, c, 0.9, 0.35);
                    }
                    r += 1.25;
                }, 'ringTick');
            }, 2);
        });
    }
}

function icicleChorus(boss, phase) {
    const dim = boss.dimension;
    const players = nearbyPlayers(dim, boss.location, 36);
    if (!players.length) return;
    cast(boss, 40);
    const n = Math.min(players.length + phase, 4);
    for (let i = 0; i < n; i++) {
        const p = players[i % players.length];
        const spot = i < players.length ? { x: p.location.x, y: p.location.y, z: p.location.z } : { x: p.location.x + rand(-5, 5), y: p.location.y, z: p.location.z + rand(-5, 5) };
        for (let t = 0; t < 30; t += 5) {
            runLater(t, () => {
                for (let k = 0; k < 12; k++) {
                    const a = (k / 12) * Math.PI * 2;
                    spawnParticle(dim, `${NS}:snow_swirl`, { x: spot.x + Math.cos(a) * 2.6, y: spot.y + 0.2, z: spot.z + Math.sin(a) * 2.6 });
                }
            });
        }
        runLater(32, () => {
            beatSound(dim, spot, true, 2);
            spawnParticle(dim, `${NS}:rime_burst`, { x: spot.x, y: spot.y + 0.5, z: spot.z });
            spawnParticle(dim, `${NS}:rime_burst`, { x: spot.x, y: spot.y + 1.5, z: spot.z });
            for (const v of nearbyPlayers(dim, spot, 2.8)) {
                safe(() => {
                    v.applyDamage(4 + phase, { cause: EntityDamageCause.entityAttack, damagingEntity: boss });
                    v.addEffect('slowness', 60, { amplifier: 1, showParticles: false });
                    v.applyKnockback({ x: 0, z: 0 }, 0.9);
                }, 'icicleHit');
            }
        });
    }
}

function choirCall(boss, n, cap) {
    const dim = boss.dimension;
    n = Math.min(n, cap - countNear(dim, HOAR, boss.location, 48) - countNear(dim, RIME, boss.location, 48));
    for (let i = 0; i < n; i++) {
        const spot = openSpot(dim, boss.location, 9, 0.6);
        if (!spot) continue;
        safe(() => {
            dim.spawnEntity(i % 2 === 0 ? HOAR : RIME, spot);
            spawnParticle(dim, `${NS}:rime_burst`, { x: spot.x, y: spot.y + 1, z: spot.z });
        }, 'spawnChoir');
    }
    if (n > 0) { playSound(dim, 'note.flute', boss.location, { volume: 2, pitch: 0.7 }); cast(boss, 30); }
}

/** a roaring blizzard: the wind shoves everyone; kneeling (sneaking) holds your ground */
function whiteout(boss, s, now) {
    const dim = boss.dimension;
    cast(boss, 100);
    s.windUntil = now + 100;
    s.windDir = vec.rotY({ x: 1, y: 0, z: 0 }, rand(0, 360));
    for (const p of nearbyPlayers(dim, boss.location, 40)) safe(() => p.sendMessage('§b❄ A whiteout rolls in - §fkneel (sneak) to hold your ground!'));
    playSound(dim, 'elytra.loop', boss.location, { volume: 2, pitch: 0.5 });
}

function windTick(boss, s) {
    const dim = boss.dimension;
    for (const p of nearbyPlayers(dim, boss.location, 40)) {
        for (let i = 0; i < 4; i++) spawnParticle(dim, `${NS}:snow_swirl`, { x: p.location.x + rand(-6, 6), y: p.location.y + rand(0.5, 3.5), z: p.location.z + rand(-6, 6) });
        if (safe(() => p.isSneaking)) continue;
        safe(() => { p.applyKnockback({ x: s.windDir.x * 0.6, z: s.windDir.z * 0.6 }, 0.05); p.addEffect('slowness', 20, { amplifier: 0, showParticles: false }); }, 'wind');
    }
}

function requiemSpiral(boss) {
    cast(boss, 110);
    playSound(boss.dimension, 'mob.wither.spawn', boss.location, { volume: 1.5, pitch: 1.8 });
    let angle = rand(0, 360), t = 0;
    const id = system.runInterval(() => {
        safe(() => {
            if (!boss.isValid || t > 100) { system.clearRun(id); return; }
            for (let arm = 0; arm < 2; arm++) fireNote(boss, vec.rotY({ x: 1, y: 0, z: 0 }, angle + arm * 180), 1.0, 1.6);
            angle += 20; t += 6;
            if (t % 18 === 0) beatSound(boss.dimension, boss.location, true, 1.2);
        }, 'spiralTick');
    }, 6);
}

/** the Final Verse: 3 seconds of channelling.  Enough damage in that time breaks it (she is stunned); otherwise a huge wave */
function finalVerse(boss, s, now) {
    const dim = boss.dimension;
    const h0 = safe(() => boss.getComponent(EntityComponentTypes.Health).currentValue) ?? 0;
    const max = safe(() => boss.getComponent(EntityComponentTypes.Health).effectiveMax) ?? 520;
    const c = { x: boss.location.x, y: boss.location.y, z: boss.location.z };
    cast(boss, 74);
    s.channel = true;
    for (const p of nearbyPlayers(dim, c, 50)) safe(() => p.onScreenDisplay.setTitle('§b§lTHE FINAL VERSE', { subtitle: '§fbreak it - or run!', fadeInDuration: 4, stayDuration: 40, fadeOutDuration: 10 }));
    for (let t = 0; t < 60; t += 4) {
        runLater(t, () => {
            if (!boss.isValid) return;
            for (let k = 0; k < 20; k++) {
                const a = (k / 20) * Math.PI * 2;
                const r = 9 * (1 - t / 80);
                spawnParticle(dim, `${NS}:snow_swirl`, { x: c.x + Math.cos(a) * r, y: c.y + 0.3, z: c.z + Math.sin(a) * r });
            }
            playSound(dim, 'note.bell', c, { volume: 1.5, pitch: 0.5 + t / 60 });
        });
    }
    runLater(66, () => {
        s.channel = false;
        if (!boss.isValid) return;
        const h1 = safe(() => boss.getComponent(EntityComponentTypes.Health).currentValue) ?? h0;
        if (h0 - h1 >= max * 0.05) {                                              // interrupted
            for (const p of nearbyPlayers(dim, c, 50)) safe(() => p.onScreenDisplay.setTitle('§a§lVERSE BROKEN', { subtitle: '§7her song falters', fadeInDuration: 2, stayDuration: 30, fadeOutDuration: 10 }));
            safe(() => { boss.addEffect('slowness', 70, { amplifier: 3, showParticles: false }); boss.addEffect('weakness', 70, { amplifier: 2, showParticles: false }); });
            s.stunUntil = system.currentTick + 70;
            playSound(dim, 'random.glass', c, { volume: 2, pitch: 0.7 });
            for (let i = 0; i < 30; i++) spawnParticle(dim, `${NS}:rime_burst`, { x: c.x + rand(-1.5, 1.5), y: c.y + rand(0, 3), z: c.z + rand(-1.5, 1.5) });
            return;
        }
        playSound(dim, 'random.explode', c, { volume: 3, pitch: 0.6 });
        for (let i = 0; i < 40; i++) {
            const a = (i / 40) * Math.PI * 2;
            spawnParticle(dim, `${NS}:intro_burst`, { x: c.x + Math.cos(a) * 6, y: c.y + 0.5, z: c.z + Math.sin(a) * 6 });
        }
        for (const p of nearbyPlayers(dim, c, 10)) {
            // never lethal on a single wave: leave at least 4 hit points
            const dmg = Math.max(0, Math.min(8, hp(p) - 4));
            safe(() => { if (dmg > 0) p.applyDamage(dmg, { cause: EntityDamageCause.entityExplosion, damagingEntity: boss }); p.addEffect('slowness', 80, { amplifier: 2, showParticles: false }); }, 'verseHit');
            knock(p, c, 1.8, 0.8);
        }
    });
}

// ------------------------------------------------------------------------------------------- spawning
/** called by the Choir lectern (puzzle.js) once the song has been sung */
export function spawnCantor(dim, c) {
    if ((safe(() => dim.getEntities({ type: CANTOR, location: c, maxDistance: 200 })) || []).length) return undefined;
    const boss = dim.spawnEntity(CANTOR, { x: c.x, y: c.y + 1, z: c.z });
    boss.addTag('ecr_introduced');
    state.set(boss.id, { next: {}, fog: new Map(), beat: 0, phase: 0 });
    const intro = playIntro(boss);
    if (!intro) titleAll(dim, c, '§b§lYsolde, the Frost Cantor', '§7Keeper of the Third Seal');
    return boss;
}

// ------------------------------------------------------------------------------------------- brain
function phaseOf(boss) {
    const f = healthFrac(boss);
    return f <= 0.33 ? 2 : f <= 0.66 ? 1 : 0;
}

function bossTick(boss) {
    const now = system.currentTick;
    let s = state.get(boss.id);
    if (!s) { s = { next: {}, fog: new Map(), beat: 0, phase: 0 }; state.set(boss.id, s); }
    if (!boss.hasTag('ecr_introduced')) {                                           // /summon: play the scene once
        boss.addTag('ecr_introduced');
        playIntro(boss);
    }
    if (boss.hasTag(INTRO_TAG)) return;                                             // the camera has the stage
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
    fog.follow(players, phase, s);
    if (s.transition !== undefined) {
        if (s.transition === 1) {
            titleAll(dim, L, '§b§lCRESCENDO', '§fthe choir rises');
            choirCall(boss, 2, 5);
        } else {
            titleAll(dim, L, '§9§lREQUIEM', '§7the Shard sings through her');
            choirCall(boss, 2, 6);
            playSound(dim, 'mob.wither.death', L, { volume: 3, pitch: 1.6 });
        }
        s.transition = undefined;
    }
    if (s.stunUntil > now) return;
    // the beat: 3/4 time, one beat every 16 ticks
    if (due(s, 'beat', now, 16)) { s.beat++; if (players.length) beatSound(dim, L, s.beat % 3 === 0, 0.8); }
    const downbeat = s.beat % 3 === 0;
    const target = nearestPlayer(boss);
    if (s.windUntil > now) { if (now % 10 === 0) windTick(boss, s); }
    if (s.channel) return;
    // phase 1: Overture
    if (target && due(s, 'aria', now, [150, 120, 100][phase], 80)) aria(boss, target, [3, 5, 7][phase], [36, 56, 70][phase]);
    if (due(s, 'ring', now, [260, 220, 190][phase], 160)) resonanceRing(boss, phase, phase === 2 ? 3 : 2);
    if (due(s, 'choir', now, [900, 760, 640][phase], 360)) choirCall(boss, phase === 0 ? 1 : 2, [3, 5, 6][phase]);
    // phase 2: Crescendo
    if (phase >= 1 && due(s, 'icicles', now, [0, 300, 230][phase], 220)) icicleChorus(boss, phase);
    if (phase >= 1 && due(s, 'whiteout', now, [0, 700, 560][phase], 420)) whiteout(boss, s, now);
    // phase 3: Requiem
    if (phase === 2 && due(s, 'spiral', now, 680, 240)) requiemSpiral(boss);
    if (phase === 2 && due(s, 'verse', now, 900, 520)) finalVerse(boss, s, now);
    if (due(s, 'speech', now, 520, 150)) speak('Ysolde', '§b', dim, L, LINES[phase][randInt(0, LINES[phase].length - 1)]);
    // ambience
    if (now % 10 < 5) for (const p of players) for (let i = 0; i < 2 + phase * 2; i++) spawnParticle(dim, `${NS}:snow_swirl`, { x: p.location.x + rand(-5, 5), y: p.location.y + rand(0.5, 4), z: p.location.z + rand(-5, 5) });
    if (now % 20 === 0 && downbeat) spawnParticle(dim, `${NS}:frost_note`, { x: L.x + rand(-1.4, 1.4), y: L.y + rand(1, 3.4), z: L.z + rand(-1.4, 1.4) });
}

export function initCantor() {
    system.runInterval(() => {
        for (const id of DIM_IDS) {
            const bosses = safe(() => dimOf(id).getEntities({ type: CANTOR })) || [];
            for (const b of bosses) safe(() => bossTick(b), 'cantorTick');
        }
    }, 5);
    world.afterEvents.entityDie.subscribe((ev) => {
        const e = ev.deadEntity;
        if (e.typeId !== CANTOR) return;
        stopMusic(e);
        const s = state.get(e.id) || { fog: new Map() };
        state.delete(e.id);
        const dim = e.dimension, L = e.location;
        for (const m of safe(() => dim.getEntities({ location: L, maxDistance: 60, families: ['ecr_minion'] })) || []) safe(() => m.kill(), 'killMinion');
        for (const m of safe(() => dim.getEntities({ location: L, maxDistance: 60, type: HOAR })) || []) safe(() => m.kill(), 'killHoar');
        for (const m of safe(() => dim.getEntities({ location: L, maxDistance: 60, type: RIME })) || []) safe(() => m.kill(), 'killRime');
        fog.clear(s);
        for (let i = 0; i < 80; i++) spawnParticle(dim, `${NS}:snow_swirl`, { x: L.x + rand(-3, 3), y: L.y + rand(0, 5), z: L.z + rand(-3, 3) });
        for (let k = 0; k < 8; k++) runLater(k * 10, () => playSound(dim, 'note.harp', L, { volume: 2, pitch: SCALE[k % SCALE.length] }));
        titleAll(dim, L, '§b§lThe Song Ends', '§f"...Thank you. Five Seals remain."');
        speak('Ysolde', '§b', dim, L, '"...Do you hear that? It is silent. I had forgotten silence. Take my Seal, wayfarer - and sing the last verse for me, when you find her."');
    });
}
