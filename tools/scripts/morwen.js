// Morwen, the Mire Lantern - the fourth main boss.  The fen swallows light: every few seconds she snuffs the lights of everyone who is not carrying one.
// Phase 1 "Misdirection": Foxfire bolts, Wisp swarms, Lantern swing.   Phase 2 "Lost": Lantern Mirages (hit the wrong one and you pay), darker fog.
// Phase 3 "Hollow Light": Lantern Rain and a fog you cannot see through - keep your own light burning (the Keeper's Lantern lights the whole party).
import { world, system, EntityComponentTypes, EntityDamageCause } from '@minecraft/server';
import { tickMusic, stopMusic } from './music.js';
import { playIntro, INTRO_TAG } from './cinematic.js';
import { NS, DIM_IDS, safe, dimOf, spawnParticle, playSound, rand, randInt, runLater } from './util.js';
import { nearbyPlayers, titleAll, healthFrac } from './boss.js';
import { vec, nearestPlayer, countNear, openSpot, cast, due, knock, fogController, speak, holdsLight, holdsKeepersLantern } from './bossutil.js';

export const MORWEN = `${NS}:mire_lantern`;
const WISP = `${NS}:mire_wisp`;
const DECOY = `${NS}:mire_decoy`;
const BOLT = `${NS}:wisp_bolt`;
const FOG_ID = 'ecr_morwen';
const FOGS = [`${NS}:fen_mist`, `${NS}:fen_dark`, `${NS}:fen_hollow`];
const fog = fogController(FOG_ID, FOGS);
const state = new Map();

const LINES = [
    ['"Lost, are you? They always are. Follow the light - it never lies."', '"I kept the lamp burning so no one would wander into the dark. That is all I ever did."', '"Careful where you step. The fen remembers everyone it has kept."'],
    ['"Which one is me? ...Which one was ever me?"', '"The Wayfarer carried a light like yours. She left half of it here, with me."', '"The Shard says the light is a lure. I say the light is a promise. It does not listen."'],
    ['"Put out my lantern, wayfarer. Please. Before it learns your name."', '"The Fourth Seal is a lantern that cannot go out. Do you understand what that is like?"', '"I only wanted someone to come home."'],
];

// who is "lit": holds a light, or stands within 10 blocks of a Keeper's Lantern bearer
function litSet(players) {
    const keepers = players.filter(holdsKeepersLantern);
    const lit = new Set();
    for (const p of players) {
        if (holdsLight(p)) { lit.add(p.id); continue; }
        if (keepers.some((k) => vec.len(vec.sub(k.location, p.location)) <= 10)) lit.add(p.id);
    }
    return lit;
}

function fireBolt(boss, dir, speed = 1.3, y = 2.3) {
    const o = boss.location;
    const e = safe(() => boss.dimension.spawnEntity(BOLT, { x: o.x + dir.x * 1.2, y: o.y + y, z: o.z + dir.z * 1.2 }), 'spawnBolt');
    if (!e) return;
    safe(() => {
        const comp = e.getComponent(EntityComponentTypes.Projectile);
        if (comp) { comp.owner = boss; comp.shoot({ x: dir.x * speed, y: dir.y * speed, z: dir.z * speed }); }
    }, 'shootBolt');
}

// ------------------------------------------------------------------------------------------- abilities
function foxfire(boss, target, shots, spread) {
    const aim = vec.norm(vec.sub({ x: target.location.x, y: target.location.y + 1.0, z: target.location.z }, { x: boss.location.x, y: boss.location.y + 2.3, z: boss.location.z }));
    cast(boss, 20);
    playSound(boss.dimension, 'mob.blaze.shoot', boss.location, { volume: 1.2, pitch: 0.7 });
    for (let i = 0; i < shots; i++) {
        const a = shots === 1 ? 0 : -spread / 2 + (spread * i) / (shots - 1);
        runLater(i * 4, () => boss.isValid && fireBolt(boss, vec.rotY(aim, a)));
    }
}

function wispSwarm(boss, n, cap) {
    const dim = boss.dimension;
    n = Math.min(n, cap - countNear(dim, WISP, boss.location, 48));
    for (let i = 0; i < n; i++) {
        const a = rand(0, Math.PI * 2);
        const p = { x: boss.location.x + Math.cos(a) * 4, y: boss.location.y + rand(1.5, 3), z: boss.location.z + Math.sin(a) * 4 };
        safe(() => { dim.spawnEntity(WISP, p); spawnParticle(dim, `${NS}:wisp_burst`, p); }, 'spawnWisp');
    }
    if (n > 0) { playSound(dim, 'mob.vex.ambient', boss.location, { volume: 2, pitch: 0.7 }); cast(boss, 26); }
}

function lanternSwing(boss, target, phase) {
    const dim = boss.dimension;
    cast(boss, 18);
    playSound(dim, 'random.bow', boss.location, { volume: 1.5, pitch: 0.5 });
    runLater(14, () => {
        if (!boss.isValid) return;
        const c = boss.location;
        for (let k = 0; k < 18; k++) {
            const a = (k / 18) * Math.PI * 2;
            spawnParticle(dim, `${NS}:lantern_mote`, { x: c.x + Math.cos(a) * 3.4, y: c.y + 1.2, z: c.z + Math.sin(a) * 3.4 });
        }
        for (const p of nearbyPlayers(dim, c, 4.2)) {
            safe(() => p.applyDamage(5 + phase, { cause: EntityDamageCause.entityAttack, damagingEntity: boss }), 'swingHit');
            knock(p, c, 1.1, 0.4);
        }
    });
}

/** Snuff: the fen drinks every light that is not held - unlit players go dark (Darkness), lit players are told their light holds */
function snuff(boss, players, phase) {
    const dim = boss.dimension;
    const lit = litSet(players);
    cast(boss, 30);
    playSound(dim, 'mob.warden.heartbeat', boss.location, { volume: 2, pitch: 0.7 });
    for (const p of players) {
        if (lit.has(p.id)) {
            safe(() => p.onScreenDisplay.setActionBar('§e✦ Your light holds against the dark.'));
            for (let i = 0; i < 6; i++) spawnParticle(dim, `${NS}:lantern_mote`, { x: p.location.x + rand(-0.6, 0.6), y: p.location.y + rand(0.2, 2), z: p.location.z + rand(-0.6, 0.6) });
        } else {
            safe(() => {
                p.addEffect('darkness', 160 + phase * 40, { amplifier: 0, showParticles: false });
                if (phase >= 2) p.addEffect('slowness', 100, { amplifier: 0, showParticles: false });
                p.onScreenDisplay.setActionBar('§8The fen swallows your light... §7(hold a torch or lantern)');
            }, 'snuffHit');
        }
    }
}

/** decoys + the real one hide among them: she teleports to one of N spots, the others are mirages that punish a strike */
function mirage(boss, s) {
    const dim = boss.dimension;
    const c = s.home || boss.location;
    const spots = [];
    for (let i = 0; i < 4; i++) {
        const sp = openSpot(dim, c, 10, 0.5);
        if (sp) spots.push(sp);
    }
    if (spots.length < 2) return;
    const real = spots.splice(randInt(0, spots.length - 1), 1)[0];
    cast(boss, 40);
    for (const sp of spots) {
        safe(() => { const d = dim.spawnEntity(DECOY, sp); d.setRotation({ x: 0, y: rand(0, 360) }); spawnParticle(dim, `${NS}:wisp_burst`, { x: sp.x, y: sp.y + 1, z: sp.z }); }, 'spawnDecoy');
    }
    runLater(16, () => {
        if (!boss.isValid) return;
        spawnParticle(dim, `${NS}:wisp_burst`, { x: boss.location.x, y: boss.location.y + 1, z: boss.location.z });
        safe(() => boss.teleport(real));
        spawnParticle(dim, `${NS}:wisp_burst`, { x: real.x, y: real.y + 1, z: real.z });
        playSound(dim, 'mob.endermen.portal', real, { volume: 1.6, pitch: 0.6 });
    });
    for (const p of nearbyPlayers(dim, c, 40)) safe(() => p.sendMessage('§a✦ The lantern-lights multiply - §fonly one of them is real. §7The real Morwen flickers with lantern-motes.'));
}

function lanternRain(boss, phase, players) {
    const dim = boss.dimension;
    if (!players.length) return;
    cast(boss, 40);
    const lit = litSet(players);
    const n = Math.min(players.length + phase, 4);
    for (let i = 0; i < n; i++) {
        const p = players[i % players.length];
        const spot = i < players.length ? { x: p.location.x, y: p.location.y, z: p.location.z } : { x: p.location.x + rand(-5, 5), y: p.location.y, z: p.location.z + rand(-5, 5) };
        for (let t = 0; t < 28; t += 4) {
            runLater(t, () => {
                for (let k = 0; k < 12; k++) {
                    const a = (k / 12) * Math.PI * 2;
                    spawnParticle(dim, `${NS}:lantern_mote`, { x: spot.x + Math.cos(a) * 2.8, y: spot.y + 0.2, z: spot.z + Math.sin(a) * 2.8 });
                }
                spawnParticle(dim, `${NS}:wisp_glow`, { x: spot.x + rand(-1, 1), y: spot.y + 5 - t / 6, z: spot.z + rand(-1, 1) });
            });
        }
        runLater(30, () => {
            playSound(dim, 'random.glass', spot, { volume: 1.6, pitch: 0.6 });
            spawnParticle(dim, `${NS}:wisp_burst`, { x: spot.x, y: spot.y + 0.6, z: spot.z });
            for (const v of nearbyPlayers(dim, spot, 3.0)) {
                const protectedFromIt = lit.has(v.id);
                safe(() => {
                    v.applyDamage(Math.max(2, (5 + phase) * (protectedFromIt ? 0.5 : 1)), { cause: EntityDamageCause.entityExplosion, damagingEntity: boss });
                    if (!protectedFromIt) v.addEffect('blindness', 60, { amplifier: 0, showParticles: false });
                }, 'rainHit');
            }
        });
    }
}

// ------------------------------------------------------------------------------------------- spawning
/** called by the Marsh Altar (puzzle.js) once the three sconces are lit and the Keeper's Lantern is offered */
export function spawnMorwen(dim, c) {
    if ((safe(() => dim.getEntities({ type: MORWEN, location: c, maxDistance: 200 })) || []).length) return undefined;
    const boss = dim.spawnEntity(MORWEN, { x: c.x, y: c.y + 1, z: c.z });
    boss.addTag('ecr_introduced');
    state.set(boss.id, { next: {}, fog: new Map(), phase: 0, home: { x: c.x, y: c.y, z: c.z } });
    const intro = playIntro(boss);
    if (!intro) titleAll(dim, c, '§a§lMorwen, the Mire Lantern', '§7Keeper of the Fourth Seal');
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
    if (!s) { s = { next: {}, fog: new Map(), phase: 0, home: { x: boss.location.x, y: boss.location.y, z: boss.location.z } }; state.set(boss.id, s); }
    if (!boss.hasTag('ecr_introduced')) {
        boss.addTag('ecr_introduced');
        playIntro(boss);
    }
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
    fog.follow(players, phase, s);
    if (s.transition !== undefined) {
        if (s.transition === 1) { titleAll(dim, L, '§a§lLOST', '§7the lights are not what they seem'); wispSwarm(boss, 3, 6); }
        else { titleAll(dim, L, '§2§lHOLLOW LIGHT', '§7keep your own flame burning'); wispSwarm(boss, 3, 7); playSound(dim, 'mob.wither.death', L, { volume: 3, pitch: 1.4 }); }
        s.transition = undefined;
    }
    const target = nearestPlayer(boss);
    // the fen swallows unlit players every few seconds
    if (due(s, 'snuff', now, [440, 340, 260][phase], 200)) snuff(boss, players, phase);
    if (target && due(s, 'bolts', now, [150, 125, 100][phase], 90)) foxfire(boss, target, [2, 3, 4][phase], [24, 40, 56][phase]);
    if (due(s, 'wisps', now, [520, 440, 380][phase], 260)) wispSwarm(boss, phase === 0 ? 2 : 3, [4, 5, 6][phase]);
    if (target && vec.len(vec.sub(target.location, L)) < 4.5 && due(s, 'swing', now, 70, 20)) lanternSwing(boss, target, phase);
    if (phase >= 1 && due(s, 'mirage', now, [0, 760, 620][phase], 400)) mirage(boss, s);
    if (phase >= 2 && due(s, 'rain', now, 250, 180)) lanternRain(boss, phase, players);
    if (due(s, 'speech', now, 520, 150)) speak('Morwen', '§a', dim, L, LINES[phase][randInt(0, LINES[phase].length - 1)]);
    // the real one flickers with lantern motes; wisps drift around the fight
    if (now % 10 < 5) {
        spawnParticle(dim, `${NS}:lantern_mote`, { x: L.x + rand(-0.8, 0.8), y: L.y + rand(1.5, 3.2), z: L.z + rand(-0.8, 0.8) });
        for (const p of players) spawnParticle(dim, `${NS}:wisp_glow`, { x: p.location.x + rand(-6, 6), y: p.location.y + rand(0.3, 3), z: p.location.z + rand(-6, 6) });
    }
}

export function initMorwen() {
    system.runInterval(() => {
        for (const id of DIM_IDS) {
            const bosses = safe(() => dimOf(id).getEntities({ type: MORWEN })) || [];
            for (const b of bosses) safe(() => bossTick(b), 'morwenTick');
        }
    }, 5);
    world.afterEvents.entityDie.subscribe((ev) => {
        const e = ev.deadEntity;
        if (e.typeId === DECOY) {                                    // the mirage bursts: whoever struck it goes dark
            const killer = ev.damageSource && ev.damageSource.damagingEntity;
            const dim = e.dimension, L = e.location;
            spawnParticle(dim, `${NS}:wisp_burst`, { x: L.x, y: L.y + 1, z: L.z });
            playSound(dim, 'random.glass', L, { volume: 1.5, pitch: 0.8 });
            if (killer && killer.typeId === 'minecraft:player') {
                const p = /** @type {any} */ (killer);
                safe(() => { p.addEffect('darkness', 80, { amplifier: 0, showParticles: false }); p.applyDamage(3, { cause: EntityDamageCause.entityExplosion }); p.sendMessage('§8It was only a reflection...'); }, 'decoyPunish');
            }
            return;
        }
        if (e.typeId !== MORWEN) return;
        stopMusic(e);
        const s = state.get(e.id) || { fog: new Map() };
        state.delete(e.id);
        const dim = e.dimension, L = e.location;
        for (const m of safe(() => dim.getEntities({ location: L, maxDistance: 60, families: ['ecr_minion'] })) || []) safe(() => m.kill(), 'killMinion');
        fog.clear(s);
        for (let i = 0; i < 60; i++) spawnParticle(dim, `${NS}:wisp_glow`, { x: L.x + rand(-3, 3), y: L.y + rand(0, 5), z: L.z + rand(-3, 3) });
        for (let k = 0; k < 6; k++) runLater(k * 12, () => playSound(dim, 'beacon.deactivate', L, { volume: 2, pitch: 0.6 + k * 0.1 }));
        titleAll(dim, L, '§a§lThe Lantern Goes Out', '§f"...Thank you. Four Seals remain."');
        speak('Morwen', '§a', dim, L, '"...It is quiet. The light is gone, and I am not afraid. Take my Seal, wayfarer. She is still walking ahead of you - I could see her lamp."');
    });
}
