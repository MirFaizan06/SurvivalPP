// Corvane, the Ashen Groom - the sixth main boss.  1100 HP, four phases, the fastest and hardest Keeper.  His fight is a duel of STANCES:
//   Ember (orange glow): immune to projectiles and fire - strike him with steel.   Soul (blue glow): immune to melee - shoot him, throw things, use magic.
//   Hollow (grey glow): takes everything, but is furious (faster, harder).  Every few seconds he changes stance after a telegraph; hits that
//   his current stance deflects are healed back.  On top: Duel Lunge, Soul Chains, Marrow Rain, Grave Echoes, and the Widow's Toll rings.
import { world, system, EntityComponentTypes, EntityDamageCause } from '@minecraft/server';
import { tickMusic, stopMusic } from './music.js';
import { playIntro, INTRO_TAG } from './cinematic.js';
import { NS, DIM_IDS, safe, dimOf, spawnParticle, playSound, rand, randInt, runLater } from './util.js';
import { nearbyPlayers, titleAll, healthFrac } from './boss.js';
import { vec, nearestPlayer, countNear, openSpot, cast, due, hp, knock, fogController, speak } from './bossutil.js';

export const GROOM = `${NS}:ashen_groom`;
const FOG_ID = 'ecr_corvane';
const FOGS = [`${NS}:soul_mist`, `${NS}:soul_gale`, `${NS}:soul_void`, `${NS}:soul_hollow`];
const fog = fogController(FOG_ID, FOGS);
const state = new Map();
const STANCE_NAME = ['§6EMBER §7- steel only (projectiles and fire are deflected)', '§bSOUL §7- ranged and magic only (melee is deflected)', '§fHOLLOW §7- he takes everything... and he is furious'];
const SOULS = 'minecraft:wither_skeleton';

const LINES = [
    ['"You have her ring... no. Not hers. It only looks like hers."', '"I have held this guard for a very long time. I will not be rude about it."', '"The veil on my arm is not mine. Please do not stare."'],
    ['"Steel, then. Or fire. Or the other thing. Choose, I am happy to wait - I am not good at waiting."', '"She forged and I rang. We never did meet in the middle."', '"The Wayfarer thanked me for the lamp-oil. I never knew why."'],
    ['"Do you know what a widower is? A man who keeps his promises to someone who cannot hold him to them."', '"The bells are not for the dead. They are for the ones still walking."', '"Faster. I must be faster. She is on the other side of this valley."'],
    ['"Tell her the ring still fits."', '"This is the part where I fall. I have rehearsed it. Please, do it well."', '"Break the vow. It was only ever holding us apart."'],
];

function stanceDelay(phase) {
    return [260, 220, 180, 150][phase];
}

function setStance(boss, s, st, announce = true) {
    s.stance = st;
    safe(() => boss.triggerEvent(`ecr:stance_${st}`));
    if (st === 2) {
        safe(() => { boss.addEffect('speed', 120, { amplifier: 2, showParticles: false }); boss.addEffect('strength', 120, { amplifier: 1, showParticles: false }); });
    }
    if (announce) for (const p of nearbyPlayers(boss.dimension, boss.location, 60)) safe(() => p.onScreenDisplay.setTitle(`§l${['§6EMBER', '§bSOUL', '§fHOLLOW'][st]} STANCE`, { subtitle: STANCE_NAME[st], fadeInDuration: 2, stayDuration: 40, fadeOutDuration: 8 }));
    for (let i = 0; i < 20; i++) spawnParticle(boss.dimension, st === 0 ? `${NS}:ember_spark` : `${NS}:soul_flame`, { x: boss.location.x + rand(-1, 1), y: boss.location.y + rand(0.2, 3.4), z: boss.location.z + rand(-1, 1) });
    playSound(boss.dimension, st === 2 ? 'mob.wither.spawn' : 'random.anvil_use', boss.location, { volume: 1.6, pitch: st === 0 ? 0.8 : st === 1 ? 1.4 : 0.5 });
}

// ------------------------------------------------------------------------------------------- abilities
function duelLunge(boss, target, phase) {
    const dim = boss.dimension;
    const from = { x: boss.location.x, y: boss.location.y, z: boss.location.z };
    const dir = vec.norm({ x: target.location.x - from.x, y: 0, z: target.location.z - from.z });
    cast(boss, 30);
    for (let t = 0; t < 18; t += 3) {
        runLater(t, () => {
            for (let r = 2; r <= 14; r += 1.4) spawnParticle(dim, `${NS}:soul_flame`, { x: from.x + dir.x * r, y: from.y + 0.2, z: from.z + dir.z * r });
        });
    }
    runLater(20, () => {
        if (!boss.isValid) return;
        const to = { x: from.x + dir.x * 13, y: from.y, z: from.z + dir.z * 13 };
        for (const p of nearbyPlayers(dim, from, 16)) {                                   // everyone on the line
            const dx = p.location.x - from.x, dz = p.location.z - from.z;
            const along = dx * dir.x + dz * dir.z, side = Math.abs(-dx * dir.z + dz * dir.x);
            if (along > 0 && along < 14 && side < 2.2) {
                safe(() => p.applyDamage(11 + phase * 2, { cause: EntityDamageCause.entityAttack, damagingEntity: boss }), 'lungeHit');
                knock(p, from, 1.4, 0.5);
            }
        }
        const dest = openSpot(dim, to, 1.5) || to;
        safe(() => boss.teleport(dest, { facingLocation: { x: dest.x + dir.x, y: dest.y, z: dest.z + dir.z } }));
        spawnParticle(dim, `${NS}:soul_burst`, { x: dest.x, y: dest.y + 1, z: dest.z });
        playSound(dim, 'item.trident.riptide_3', dest, { volume: 2, pitch: 0.7 });
    });
}

function soulChains(boss, players, phase) {
    const dim = boss.dimension;
    const c = { x: boss.location.x, y: boss.location.y, z: boss.location.z };
    cast(boss, 40);
    playSound(dim, 'mob.warden.sonic_charge', c, { volume: 2, pitch: 1.2 });
    for (const p of players) safe(() => p.sendMessage('§b⛓ Soul chains! §fBreak line of sight or be dragged to him.'));
    for (let t = 0; t < 30; t += 5) runLater(t, () => {
        for (const p of players) if (p.isValid) {
            const dx = c.x - p.location.x, dz = c.z - p.location.z, d = Math.hypot(dx, dz) || 1;
            for (let r = 1; r < d; r += 1.3) spawnParticle(dim, `${NS}:soul_flame`, { x: p.location.x + (dx / d) * r, y: p.location.y + 1.2, z: p.location.z + (dz / d) * r });
        }
    });
    runLater(32, () => {
        if (!boss.isValid) return;
        for (const p of players) {
            if (!p.isValid) continue;
            const dx = c.x - p.location.x, dz = c.z - p.location.z, d = Math.hypot(dx, dz) || 1;
            if (d < 4) continue;
            safe(() => { p.applyKnockback({ x: (dx / d) * Math.min(3, d * 0.22), z: (dz / d) * Math.min(3, d * 0.22) }, 0.35); p.applyDamage(4 + phase, { cause: EntityDamageCause.magic, damagingEntity: boss }); p.addEffect('slowness', 40, { amplifier: 1, showParticles: false }); }, 'chainHit');
        }
        runLater(14, () => {
            if (!boss.isValid) return;
            playSound(dim, 'random.anvil_land', c, { volume: 1.6, pitch: 1.0 });
            for (let k = 0; k < 24; k++) spawnParticle(dim, `${NS}:soul_burst`, { x: c.x + Math.cos(k) * 3, y: c.y + 0.6, z: c.z + Math.sin(k) * 3 });
            for (const p of nearbyPlayers(dim, c, 4)) { safe(() => p.applyDamage(8 + phase * 2, { cause: EntityDamageCause.entityAttack, damagingEntity: boss }), 'chainSweep'); knock(p, c, 1.5, 0.5); }
        });
    });
}

function marrowRain(boss, phase) {
    const dim = boss.dimension;
    const players = nearbyPlayers(dim, boss.location, 36);
    if (!players.length) return;
    cast(boss, 40);
    const spots = [];
    for (const p of players) spots.push({ x: p.location.x, y: p.location.y, z: p.location.z });
    for (let i = 0; i < 3 + phase * 2; i++) { const p = players[i % players.length]; spots.push({ x: p.location.x + rand(-6, 6), y: p.location.y, z: p.location.z + rand(-6, 6) }); }
    spots.forEach((sp, i) => {
        for (let t = 0; t < 24; t += 6) runLater(i * 2 + t, () => { for (let k = 0; k < 8; k++) spawnParticle(dim, `${NS}:soul_flame`, { x: sp.x + Math.cos(k) * 1.8, y: sp.y + 0.1, z: sp.z + Math.sin(k) * 1.8 }); });
        runLater(i * 2 + 26, () => {
            spawnParticle(dim, `${NS}:soul_burst`, { x: sp.x, y: sp.y + 0.6, z: sp.z });
            playSound(dim, 'dig.bone_block', sp, { volume: 1.6, pitch: 0.7 });
            for (const v of nearbyPlayers(dim, sp, 2.2)) safe(() => { v.applyDamage(7 + phase, { cause: EntityDamageCause.magic, damagingEntity: boss }); v.addEffect('wither', 80, { amplifier: 0, showParticles: false }); }, 'marrowHit');
        });
    });
}

/** the Widow's Toll: bell-rings that roll out from him (jump them) - at the end of each phase boundary and every ~12 s in the last phase */
function widowsToll(boss, phase, count) {
    const dim = boss.dimension;
    const c = { x: boss.location.x, y: boss.location.y, z: boss.location.z };
    cast(boss, 30 + count * 14);
    for (let n = 0; n < count; n++) {
        runLater(20 + n * 14, () => {
            if (!boss.isValid) return;
            playSound(dim, 'block.bell.hit', c, { volume: 3, pitch: 0.5 + n * 0.12 });
            let r = 1.5;
            const id = system.runInterval(() => {
                safe(() => {
                    if (!boss.isValid || r > 16) { system.clearRun(id); return; }
                    const pts = Math.max(12, Math.floor(r * 4));
                    for (let k = 0; k < pts; k++) { const a = (k / pts) * Math.PI * 2; spawnParticle(dim, `${NS}:soul_flame`, { x: c.x + Math.cos(a) * r, y: c.y + 0.15, z: c.z + Math.sin(a) * r }); }
                    for (const p of nearbyPlayers(dim, c, r + 1.6)) {
                        if (Math.abs(Math.hypot(p.location.x - c.x, p.location.z - c.z) - r) > 1.5) continue;
                        if (p.location.y - c.y > 0.9 || !safe(() => p.isOnGround)) continue;
                        if (p.getTags().includes('ecr_tolled')) continue;
                        safe(() => { p.addTag('ecr_tolled'); runLater(10, () => safe(() => p.removeTag('ecr_tolled'))); p.applyDamage(6 + phase * 2, { cause: EntityDamageCause.entityAttack, damagingEntity: boss }); }, 'tollHit');
                        knock(p, c, 0.9, 0.35);
                    }
                    r += 1.25;
                }, 'tollTick');
            }, 2);
        });
    }
}

function graveEchoes(boss, n) {
    const dim = boss.dimension;
    n = Math.min(n, 5 - countNear(dim, SOULS, boss.location, 40));
    for (let i = 0; i < n; i++) {
        const sp = openSpot(dim, boss.location, 9, 0.5);
        if (sp) safe(() => { dim.spawnEntity(SOULS, sp); spawnParticle(dim, `${NS}:soul_burst`, sp); }, 'spawnEcho');
    }
    if (n > 0) { cast(boss, 30); playSound(dim, 'mob.wither.ambient', boss.location, { volume: 2, pitch: 0.8 }); }
}

// ------------------------------------------------------------------------------------------- spawning
export function spawnGroom(dim, c) {
    if ((safe(() => dim.getEntities({ type: GROOM, location: c, maxDistance: 200 })) || []).length) return undefined;
    const boss = dim.spawnEntity(GROOM, { x: c.x, y: c.y + 1, z: c.z });
    boss.addTag('ecr_introduced');
    state.set(boss.id, { next: {}, fog: new Map(), stance: 1, phase: 0 });
    safe(() => boss.triggerEvent('ecr:stance_1'));
    const intro = playIntro(boss);
    if (!intro) titleAll(dim, c, '§b§lCorvane, the Ashen Groom', '§7Keeper of the Sixth Seal');
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
    if (!s) { s = { next: {}, fog: new Map(), stance: 1, phase: 0 }; state.set(boss.id, s); safe(() => boss.triggerEvent('ecr:stance_1')); }
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
        const T = [['', ''], ['§b§lTHE TOLL BEGINS', '§7every bell is a name'], ['§3§lGRAVE ECHOES', '§7he is not alone'], ['§f§lWIDOWER', '§7he is only fast now']][s.transition];
        titleAll(dim, L, T[0], T[1]);
        widowsToll(boss, s.transition, 2);
        graveEchoes(boss, 2);
        playSound(dim, 'mob.wither.death', L, { volume: 3, pitch: 1.1 });
        s.transition = undefined;
    }
    // stance rotation: telegraph at -40 ticks (armor flickers), then change.  Phase 3+ often goes Hollow.
    if (now >= (s.nextStance || 0)) {
        const nxt = phase >= 2 && Math.random() < 0.34 ? 2 : (s.stance === 0 ? 1 : 0);
        if (s.pending === undefined) {
            s.pending = nxt; s.nextStance = now + 40;
            for (const p of players) safe(() => p.onScreenDisplay.setActionBar('§7He shifts his stance...'));
            for (let i = 0; i < 14; i++) spawnParticle(dim, `${NS}:soul_flame`, { x: L.x + rand(-1.2, 1.2), y: L.y + rand(0.2, 3.6), z: L.z + rand(-1.2, 1.2) });
            playSound(dim, 'block.bell.use', L, { volume: 1.6, pitch: 1.8 });
        } else {
            setStance(boss, s, s.pending);
            s.nextStance = now + stanceDelay(phase) + (s.pending === 2 ? -60 : 0);
            s.pending = undefined;
        }
    }
    const target = nearestPlayer(boss);
    if (s.stance === 2 && now % 20 === 0) safe(() => boss.addEffect('speed', 40, { amplifier: 2, showParticles: false }));
    if (target && due(s, 'lunge', now, [260, 210, 170, 130][phase], 140)) duelLunge(boss, target, phase);
    if (phase >= 0 && due(s, 'chains', now, [520, 440, 360, 300][phase], 360)) soulChains(boss, players, phase);
    if (phase >= 1 && due(s, 'marrow', now, [0, 400, 320, 260][phase], 240)) marrowRain(boss, phase);
    if (phase >= 2 && due(s, 'echoes', now, 760, 480)) graveEchoes(boss, 2);
    if (phase >= 1 && due(s, 'toll', now, [0, 700, 560, 360][phase], 420)) widowsToll(boss, phase, phase === 3 ? 3 : 2);
    if (due(s, 'speech', now, 520, 150)) speak('Corvane', '§b', dim, L, LINES[phase][randInt(0, LINES[phase].length - 1)]);
    if (now % 10 < 5) {
        spawnParticle(dim, s.stance === 0 ? `${NS}:ember_spark` : `${NS}:soul_flame`, { x: L.x + rand(-1.2, 1.2), y: L.y + rand(0.2, 3.8), z: L.z + rand(-1.2, 1.2) });
        for (const p of players) spawnParticle(dim, `${NS}:soul_flame`, { x: p.location.x + rand(-6, 6), y: p.location.y + rand(0.4, 3), z: p.location.z + rand(-6, 6) });
    }
}

export function initCorvane() {
    system.runInterval(() => {
        for (const id of DIM_IDS) {
            const bosses = safe(() => dimOf(id).getEntities({ type: GROOM })) || [];
            for (const b of bosses) safe(() => bossTick(b), 'corvaneTick');
        }
    }, 5);
    // stances: whatever the current stance deflects is healed straight back
    world.afterEvents.entityHurt.subscribe((ev) => {
        const e = ev.hurtEntity;
        if (!e || e.typeId !== GROOM) return;
        const by = ev.damageSource && ev.damageSource.damagingEntity;
        const cause = ev.damageSource && ev.damageSource.cause;
        const s = state.get(e.id);
        if (!s) return;
        const st = s.stance;
        const deflect = (st === 0 && (cause === EntityDamageCause.projectile || cause === EntityDamageCause.fire || cause === EntityDamageCause.fireTick || cause === EntityDamageCause.lava))
            || (st === 1 && (cause === EntityDamageCause.entityAttack || (by && by.typeId === 'minecraft:player' && cause !== EntityDamageCause.projectile && cause !== EntityDamageCause.magic && cause !== EntityDamageCause.entityExplosion)));
        if (!deflect) return;
        safe(() => {
            const h = e.getComponent(EntityComponentTypes.Health);
            h.setCurrentValue(Math.min(h.effectiveMax, h.currentValue + ev.damage * 0.97));
            spawnParticle(e.dimension, st === 0 ? `${NS}:ember_spark` : `${NS}:soul_flame`, { x: e.location.x, y: e.location.y + 1.8, z: e.location.z });
            playSound(e.dimension, 'random.anvil_land', e.location, { volume: 0.6, pitch: 2.0 });
        }, 'deflect');
        if (by && by.typeId === 'minecraft:player') {
            const now = system.currentTick;
            if ((s.deflectMsg || 0) < now) { s.deflectMsg = now + 60; safe(() => /** @type {any} */ (by).onScreenDisplay.setActionBar(st === 0 ? '§6Deflected - he is in EMBER stance: use steel, not arrows or fire' : '§bDeflected - he is in SOUL stance: use arrows, tridents or magic, not melee')); }
        }
    });
    world.afterEvents.entityDie.subscribe((ev) => {
        const e = ev.deadEntity;
        if (e.typeId !== GROOM) return;
        stopMusic(e);
        const s = state.get(e.id) || { fog: new Map() };
        state.delete(e.id);
        const dim = e.dimension, L = e.location;
        for (const m of safe(() => dim.getEntities({ location: L, maxDistance: 60, type: SOULS })) || []) safe(() => m.kill(), 'killEcho');
        fog.clear(s);
        for (let i = 0; i < 60; i++) spawnParticle(dim, `${NS}:soul_flame`, { x: L.x + rand(-3, 3), y: L.y + rand(0, 5), z: L.z + rand(-3, 3) });
        for (let k = 0; k < 6; k++) runLater(k * 12, () => playSound(dim, 'block.bell.hit', L, { volume: 2.5, pitch: 0.5 + k * 0.1 }));
        titleAll(dim, L, '§b§lThe Last Bell', '§f"...Thank you. The Sixth Seal is yours."');
        speak('Corvane', '§b', dim, L, '"...I can hear the valley. It is only wind. Take my Seal, wayfarer. Tell her... no. I will tell her myself."');
    });
}
