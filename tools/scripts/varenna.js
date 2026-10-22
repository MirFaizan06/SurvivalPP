// Varenna, the Cinder Bride - the fifth main boss and the first of the Burning Deep.  900 HP, four phases.  Her fight is a forge:
//   * Forged Blades: she hammers out spectral swords that charge you.  While any blade lives she is shielded - and every blade a PLAYER cuts down
//     is a parry: it costs her 2.5% of her life.
//   * Anvil Slam (telegraphed rings + ember geysers), Cinder Brand (a mark that detonates on whoever stands next to the branded - spread out),
//     Forge Heat (hot sectors of the floor, telegraphed, rotating), and in the last phase the Wedding March (she keeps forging and teleports to strike).
import { world, system, EntityComponentTypes, EntityDamageCause } from '@minecraft/server';
import { tickMusic, stopMusic } from './music.js';
import { playIntro, INTRO_TAG } from './cinematic.js';
import { NS, DIM_IDS, safe, dimOf, spawnParticle, playSound, rand, randInt, runLater } from './util.js';
import { nearbyPlayers, titleAll, healthFrac } from './boss.js';
import { vec, nearestPlayer, countNear, openSpot, cast, due, hp, knock, fogController, speak } from './bossutil.js';

export const BRIDE = `${NS}:cinder_bride`;
const BLADE = `${NS}:forged_blade`;
const FOG_ID = 'ecr_varenna';
const FOGS = [`${NS}:forge_haze`, `${NS}:forge_inferno`, `${NS}:forge_cinders`, `${NS}:forge_ashfall`];
const fog = fogController(FOG_ID, FOGS);
const state = new Map();

const LINES = [
    ['"You came to my wedding without an invitation. How rude... and how welcome."', '"I forged this ring from the Seal itself. Do you know what it cost?"', '"He is waiting for me. He has been waiting for a very long time."'],
    ['"Hammer, ring and flame. I gave him all three. He gave me his silence."', '"Every blade I make is a promise I could not keep."', '"The Wayfarer stood where you stand. She knew his name before she knew mine."'],
    ['"Do not step on the hot iron. I am not cruel - I am only very, very warm."', '"The forge remembers every vow spoken over it."', '"I can feel the Shard in my hand. It wants to be married to someone."'],
    ['"Dance with me. The march has only one step."', '"Break the ring, wayfarer. Break it before it breaks us both."', '"Tell Corvane... tell him I kept the veil."'],
];

function spawnBlade(boss, spot) {
    safe(() => {
        boss.dimension.spawnEntity(BLADE, spot);
        spawnParticle(boss.dimension, `${NS}:forge_burst`, spot);
    }, 'spawnBlade');
}

// ------------------------------------------------------------------------------------------- abilities
function forgeBlades(boss, n, cap) {
    const dim = boss.dimension;
    n = Math.min(n, cap - countNear(dim, BLADE, boss.location, 48));
    cast(boss, 40);
    playSound(dim, 'random.anvil_use', boss.location, { volume: 2, pitch: 0.7 });
    for (let i = 0; i < n; i++) {
        const a = rand(0, Math.PI * 2);
        const p = { x: boss.location.x + Math.cos(a) * 3.2, y: boss.location.y + rand(1.5, 3), z: boss.location.z + Math.sin(a) * 3.2 };
        runLater(10 + i * 5, () => boss.isValid && spawnBlade(boss, p));
    }
}

function anvilSlam(boss, phase) {
    const dim = boss.dimension;
    const c = { x: boss.location.x, y: boss.location.y, z: boss.location.z };
    cast(boss, 44);
    for (let t = 0; t < 24; t += 4) {
        runLater(t, () => {
            for (let k = 0; k < 24; k++) {
                const a = (k / 24) * Math.PI * 2;
                spawnParticle(dim, `${NS}:ember_spark`, { x: c.x + Math.cos(a) * 7, y: c.y + 0.2, z: c.z + Math.sin(a) * 7 });
            }
        });
    }
    // ember geysers under the players, marked in advance
    const spots = nearbyPlayers(dim, c, 30).slice(0, 4).map((p) => ({ x: p.location.x, y: p.location.y, z: p.location.z }));
    for (let i = 0; i < 2 + phase; i++) spots.push({ x: c.x + rand(-10, 10), y: c.y, z: c.z + rand(-10, 10) });
    for (const sp of spots) for (let t = 0; t < 24; t += 6) runLater(t, () => { for (let k = 0; k < 8; k++) spawnParticle(dim, `${NS}:ember_spark`, { x: sp.x + Math.cos(k) * 1.6, y: sp.y + 0.1, z: sp.z + Math.sin(k) * 1.6 }); });
    runLater(26, () => {
        if (!boss.isValid) return;
        playSound(dim, 'random.explode', c, { volume: 3, pitch: 0.55 });
        for (let k = 0; k < 6; k++) spawnParticle(dim, `${NS}:forge_burst`, { x: c.x, y: c.y + 0.5, z: c.z });
        for (const p of nearbyPlayers(dim, c, 7)) {
            safe(() => p.applyDamage(9 + phase * 2, { cause: EntityDamageCause.entityExplosion, damagingEntity: boss }), 'slamHit');
            knock(p, c, 1.6, 0.7);
        }
        for (const sp of spots) {
            spawnParticle(dim, `${NS}:forge_burst`, { x: sp.x, y: sp.y + 0.4, z: sp.z });
            for (const p of nearbyPlayers(dim, sp, 2.6)) safe(() => { p.applyDamage(6 + phase, { cause: EntityDamageCause.fire, damagingEntity: boss }); p.setOnFire(4, true); }, 'geyserHit');
        }
    });
}

/** Cinder Brand: the mark detonates after 5 seconds on whoever is within 5.5 blocks of the branded player - stand alone and it is a scratch */
function cinderBrand(boss, players, phase) {
    if (!players.length) return;
    const dim = boss.dimension;
    cast(boss, 30);
    const n = Math.max(1, Math.floor(players.length / 2));
    const pool = [...players].sort(() => Math.random() - 0.5).slice(0, n);
    for (const target of pool) {
        safe(() => target.onScreenDisplay.setTitle('§6§lBRANDED', { subtitle: '§fget away from the others!', fadeInDuration: 4, stayDuration: 70, fadeOutDuration: 10 }));
        playSound(dim, 'mob.blaze.shoot', target.location, { volume: 1.5, pitch: 0.6 });
        for (let t = 0; t < 100; t += 5) {
            runLater(t, () => {
                if (!target.isValid) return;
                for (let k = 0; k < 14; k++) {
                    const a = (k / 14) * Math.PI * 2;
                    spawnParticle(dim, `${NS}:ember_spark`, { x: target.location.x + Math.cos(a) * 5.5, y: target.location.y + 0.15, z: target.location.z + Math.sin(a) * 5.5 });
                }
                spawnParticle(dim, `${NS}:ember_spark`, { x: target.location.x, y: target.location.y + 2.2, z: target.location.z });
            });
        }
        runLater(100, () => {
            if (!target.isValid || !boss.isValid) return;
            const c = { x: target.location.x, y: target.location.y, z: target.location.z };
            spawnParticle(dim, `${NS}:forge_burst`, { x: c.x, y: c.y + 1, z: c.z });
            playSound(dim, 'random.explode', c, { volume: 2, pitch: 0.8 });
            const near = nearbyPlayers(dim, c, 5.5);
            const dmg = Math.min(8 + phase * 2 + (near.length - 1) * 5, hp(target) - 2);          // never lethal on its own
            for (const p of near) safe(() => { p.applyDamage(Math.max(2, p.id === target.id ? 6 + phase : dmg), { cause: EntityDamageCause.entityExplosion, damagingEntity: boss }); p.setOnFire(3, true); }, 'brandHit');
        });
    }
}

/** Forge Heat: sectors of the floor glow, then burn.  The safe sectors are marked by the absence of embers */
function forgeHeat(boss, phase) {
    const dim = boss.dimension;
    const c = { x: boss.location.x, y: boss.location.y, z: boss.location.z };
    cast(boss, 60);
    const SECT = 8;
    const hot = new Set();
    while (hot.size < 3 + (phase >= 2 ? 1 : 0) + (phase >= 3 ? 1 : 0)) hot.add(randInt(0, SECT - 1));
    for (const p of nearbyPlayers(dim, c, 40)) safe(() => p.sendMessage('§6🔥 The forge floor is heating - §fstay out of the glowing sectors!'));
    const draw = (heavy) => {
        for (const sec of hot) for (let r = 3; r <= 13; r += 2) for (let k = 0; k < (heavy ? 5 : 2); k++) {
            const a = ((sec + rand(0.05, 0.95)) / SECT) * Math.PI * 2;
            spawnParticle(dim, `${NS}:ember_spark`, { x: c.x + Math.cos(a) * r, y: c.y + 0.15, z: c.z + Math.sin(a) * r });
        }
    };
    for (let t = 0; t < 40; t += 5) runLater(t, () => boss.isValid && draw(false));
    for (let t = 40; t < 120; t += 10) {
        runLater(t, () => {
            if (!boss.isValid) return;
            draw(true);
            for (const p of nearbyPlayers(dim, c, 14)) {
                const dx = p.location.x - c.x, dz = p.location.z - c.z;
                if (Math.hypot(dx, dz) < 2.5) continue;
                const sec = Math.floor((((Math.atan2(dz, dx) + Math.PI * 2) % (Math.PI * 2)) / (Math.PI * 2)) * SECT);
                if (hot.has(sec)) safe(() => { p.applyDamage(4 + phase, { cause: EntityDamageCause.fire, damagingEntity: boss }); p.setOnFire(2, true); }, 'heatHit');
            }
        });
    }
}

/** phase 4: she crosses the floor to someone and brings the hammer down */
function lastDance(boss, target, phase) {
    const dim = boss.dimension;
    const view = safe(() => target.getViewDirection()) || { x: 0, y: 0, z: 1 };
    const flat = vec.norm({ x: view.x, y: 0, z: view.z });
    const dest = openSpot(dim, { x: target.location.x - flat.x * 3.5, y: target.location.y, z: target.location.z - flat.z * 3.5 }, 1.2);
    if (!dest) return;
    cast(boss, 40);
    for (let k = 0; k < 20; k++) spawnParticle(dim, `${NS}:ember_spark`, { x: dest.x + rand(-1, 1), y: dest.y + rand(0, 2.6), z: dest.z + rand(-1, 1) });
    safe(() => target.sendMessage('§6🔥 The air burns behind you...'));
    runLater(22, () => {
        if (!boss.isValid) return;
        safe(() => boss.teleport(dest, { facingLocation: target.location }));
        playSound(dim, 'mob.endermen.portal', dest, { volume: 1.5, pitch: 0.6 });
        runLater(14, () => {
            if (!boss.isValid) return;
            playSound(dim, 'random.anvil_land', dest, { volume: 2, pitch: 0.6 });
            spawnParticle(dim, `${NS}:forge_burst`, { x: dest.x, y: dest.y + 0.5, z: dest.z });
            for (const p of nearbyPlayers(dim, dest, 4.4)) { safe(() => p.applyDamage(10 + phase, { cause: EntityDamageCause.entityAttack, damagingEntity: boss }), 'danceHit'); knock(p, dest, 1.5, 0.6); }
        });
    });
}

function summonGuards(boss, n) {
    const dim = boss.dimension;
    for (let i = 0; i < n; i++) {
        const sp = openSpot(dim, boss.location, 8, 0.5);
        if (sp) safe(() => { dim.spawnEntity(i % 2 === 0 ? 'minecraft:blaze' : 'minecraft:wither_skeleton', sp); spawnParticle(dim, `${NS}:forge_burst`, sp); }, 'spawnGuard');
    }
    cast(boss, 30);
}

// ------------------------------------------------------------------------------------------- spawning
export function spawnBride(dim, c) {
    if ((safe(() => dim.getEntities({ type: BRIDE, location: c, maxDistance: 200 })) || []).length) return undefined;
    const boss = dim.spawnEntity(BRIDE, { x: c.x, y: c.y + 1, z: c.z });
    boss.addTag('ecr_introduced');
    state.set(boss.id, { next: {}, fog: new Map(), phase: 0 });
    const intro = playIntro(boss);
    if (!intro) titleAll(dim, c, '§6§lVarenna, the Cinder Bride', '§7Keeper of the Fifth Seal');
    return boss;
}

// ------------------------------------------------------------------------------------------- brain
function phaseOf(boss) {
    const f = healthFrac(boss);
    return f <= 0.25 ? 3 : f <= 0.5 ? 2 : f <= 0.75 ? 1 : 0;
}

function bossTick(boss) {
    const now = system.currentTick;
    let s = state.get(boss.id);
    if (!s) { s = { next: {}, fog: new Map(), phase: 0 }; state.set(boss.id, s); }
    if (!boss.hasTag('ecr_introduced')) { boss.addTag('ecr_introduced'); playIntro(boss); }
    if (boss.hasTag(INTRO_TAG)) return;
    tickMusic(boss);
    const dim = boss.dimension, L = boss.location;
    const want = phaseOf(boss);
    const cur = safe(() => boss.getProperty('ecr:phase')) ?? 0;
    if (want > cur) {
        for (let p = cur + 1; p <= want; p++) safe(() => boss.triggerEvent(`ecr:enter_phase_${p + 1}`));
        s.transition = want;
    }
    const phase = Math.max(cur, want);
    const players = nearbyPlayers(dim, L, 60);
    fog.follow(players, phase, s);
    if (s.transition !== undefined) {
        const T = [['', ''], ['§6§lTEMPERING', '§7the blades learn her name'], ['§c§lWHITE HEAT', '§7the floor remembers'], ['§4§lTHE WEDDING MARCH', '§7there is only one step']][s.transition];
        titleAll(dim, L, T[0], T[1]);
        forgeBlades(boss, 3, 6 + s.transition * 2);
        summonGuards(boss, s.transition === 3 ? 3 : 2);
        playSound(dim, 'mob.wither.death', L, { volume: 3, pitch: 1.3 });
        s.transition = undefined;
    }
    const target = nearestPlayer(boss);
    if (target && due(s, 'blades', now, [420, 340, 280, 200][phase], 120)) forgeBlades(boss, [3, 4, 5, 6][phase], [5, 7, 9, 10][phase]);
    if (due(s, 'slam', now, [300, 250, 210, 180][phase], 200)) anvilSlam(boss, phase);
    if (phase >= 1 && due(s, 'brand', now, [0, 520, 440, 360][phase], 300)) cinderBrand(boss, players, phase);
    if (phase >= 1 && due(s, 'heat', now, [0, 640, 520, 440][phase], 420)) forgeHeat(boss, phase);
    if (phase >= 2 && target && due(s, 'dance', now, [0, 0, 560, 380][phase], 360)) lastDance(boss, target, phase);
    if (phase >= 2 && due(s, 'guards', now, 900, 600) && countNear(dim, 'minecraft:blaze', L, 40) < 3) summonGuards(boss, 2);
    if (phase === 3 && due(s, 'march', now, 160, 100)) forgeBlades(boss, 1, 10);
    if (due(s, 'speech', now, 520, 150)) speak('Varenna', '§6', dim, L, LINES[phase][randInt(0, LINES[phase].length - 1)]);
    // the shield: blades on the field soak damage (see the hurt hook below)
    s.shield = countNear(dim, BLADE, L, 40) > 0;
    if (s.shield && now % 20 < 5) for (let i = 0; i < 5; i++) spawnParticle(dim, `${NS}:ember_spark`, { x: L.x + rand(-1.4, 1.4), y: L.y + rand(0.2, 3.2), z: L.z + rand(-1.4, 1.4) });
    if (now % 10 < 5) {
        spawnParticle(dim, `${NS}:ember_spark`, { x: L.x + rand(-1.6, 1.6), y: L.y + rand(0, 3.2), z: L.z + rand(-1.6, 1.6) });
        for (const p of players) spawnParticle(dim, `${NS}:ash_drift`, { x: p.location.x + rand(-5, 5), y: p.location.y + rand(1, 4), z: p.location.z + rand(-5, 5) });
    }
}

export function initVarenna() {
    system.runInterval(() => {
        for (const id of DIM_IDS) {
            const bosses = safe(() => dimOf(id).getEntities({ type: BRIDE })) || [];
            for (const b of bosses) safe(() => bossTick(b), 'varennaTick');
        }
    }, 5);
    // the shield: while forged blades live, 80% of what players deal is healed back
    world.afterEvents.entityHurt.subscribe((ev) => {
        const e = ev.hurtEntity;
        if (!e || e.typeId !== BRIDE) return;
        const by = ev.damageSource && ev.damageSource.damagingEntity;
        if (!by || by.typeId !== 'minecraft:player') return;
        const s = state.get(e.id);
        if (!s || !s.shield) return;
        safe(() => {
            const h = e.getComponent(EntityComponentTypes.Health);
            h.setCurrentValue(Math.min(h.effectiveMax, h.currentValue + ev.damage * 0.8));
            spawnParticle(e.dimension, `${NS}:ember_spark`, { x: e.location.x, y: e.location.y + 1.6, z: e.location.z });
        }, 'shieldHeal');
        const now = system.currentTick;
        if ((s.shieldMsg || 0) < now) { s.shieldMsg = now + 100; safe(() => /** @type {any} */ (by).onScreenDisplay.setActionBar('§6Her blades shield her - cut them down (a parry hurts her)!')); }
    });
    world.afterEvents.entityDie.subscribe((ev) => {
        const e = ev.deadEntity;
        if (e.typeId === BLADE) {                                                         // a parry
            const killer = ev.damageSource && ev.damageSource.damagingEntity;
            const dim = e.dimension, L = e.location;
            spawnParticle(dim, `${NS}:forge_burst`, { x: L.x, y: L.y + 0.8, z: L.z });
            playSound(dim, 'random.anvil_land', L, { volume: 1.2, pitch: 1.6 });
            if (killer && killer.typeId === 'minecraft:player') {
                for (const b of safe(() => dim.getEntities({ type: BRIDE, location: L, maxDistance: 48 })) || []) {
                    safe(() => {
                        const h = b.getComponent(EntityComponentTypes.Health);
                        h.setCurrentValue(Math.max(1, h.currentValue - h.effectiveMax * 0.025));
                        spawnParticle(dim, `${NS}:forge_burst`, { x: b.location.x, y: b.location.y + 1.6, z: b.location.z });
                    }, 'parry');
                }
                safe(() => /** @type {any} */ (killer).onScreenDisplay.setActionBar('§e⚔ Parried!'));
            }
            return;
        }
        if (e.typeId !== BRIDE) return;
        stopMusic(e);
        const s = state.get(e.id) || { fog: new Map() };
        state.delete(e.id);
        const dim = e.dimension, L = e.location;
        for (const m of safe(() => dim.getEntities({ location: L, maxDistance: 60, families: ['ecr_minion'] })) || []) safe(() => m.kill(), 'killMinion');
        for (const t of ['minecraft:blaze', 'minecraft:wither_skeleton']) for (const m of safe(() => dim.getEntities({ location: L, maxDistance: 50, type: t })) || []) safe(() => m.kill(), 'killGuard');
        fog.clear(s);
        for (let i = 0; i < 60; i++) spawnParticle(dim, `${NS}:ember_spark`, { x: L.x + rand(-3, 3), y: L.y + rand(0, 5), z: L.z + rand(-3, 3) });
        for (let k = 0; k < 6; k++) runLater(k * 10, () => playSound(dim, 'random.anvil_land', L, { volume: 1.6, pitch: 0.5 + k * 0.1 }));
        titleAll(dim, L, '§6§lThe Forge Goes Cold', '§f"...Thank you. The Fifth Seal is yours."');
        speak('Varenna', '§6', dim, L, '"...I can put the hammer down. Take my Seal, wayfarer - and when you find him, tell Corvane I kept the veil."');
    });
}
