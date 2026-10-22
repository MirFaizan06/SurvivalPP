// Boss introductions: a short "movie scene" per main boss, played with the scripted camera (Player.camera) for every player near the boss.
// While it plays: the HUD is hidden, movement/camera input is locked, players are protected, the boss is held in place (tag ecr_intro).
// Everything is restored by a failsafe timer, so a failed camera call can never leave a player stuck.
import { world, system, InputPermissionCategory, EasingType, CameraShakeType } from '@minecraft/server';
import { NS, safe } from './util.js';

const OFF_KEY = 'ecr:cinematic_off';
export const INTRO_TAG = 'ecr_intro';
const RANGE = 40;

/** per-boss scene: shots are [forward, side, up] offsets from the boss (forward = towards the player), `look` is the height on the boss that
 *  the lens follows (fraction of its height), `secs` is how long the move to this shot takes. */
export const INTROS = {
    [`${NS}:veiled_blossom`]: {
        title: '§d✿ §fThe Veiled Blossom §d✿', sub: '§7Hanae, Keeper of the First Seal', h: 2.4, sound: 'block.bell.resonate', color: [0.55, 0.2, 0.35],
        shots: [{ pos: [16, 3, 6], look: 0.6, secs: 0 }, { pos: [10, 6, 3.5], look: 0.6, secs: 3.2, ease: 'InOutSine' },
            { pos: [5, -2.5, 1.2], look: 0.8, secs: 2.4, ease: 'OutCubic' }, { pos: [2.6, 0.4, 2.2], look: 0.85, secs: 2.0, ease: 'InOutSine' },
            { pos: [12, 0, 6], look: 0.6, secs: 2.0, ease: 'InOutSine' }],
        shakeAt: 5.4,
    },
    [`${NS}:eclipse_sovereign`]: {
        title: '§5§lThe Eclipse Sovereign', sub: '§7Second Keeper - Herald of the Hollow Sun', h: 4.0, sound: 'mob.enderdragon.growl', color: [0.2, 0.0, 0.3],
        shots: [{ pos: [22, 4, 14], look: 0.7, secs: 0 }, { pos: [14, -7, 5], look: 0.7, secs: 3.4, ease: 'InOutSine' },
            { pos: [7, 3, 0.5], look: 0.9, secs: 2.4, ease: 'OutCubic' }, { pos: [3.5, 0, 3.5], look: 0.92, secs: 1.8, ease: 'InOutSine' },
            { pos: [18, 0, 9], look: 0.7, secs: 2.0, ease: 'InOutSine' }],
        shakeAt: 5.0,
    },
    [`${NS}:frost_cantor`]: {
        title: '§b§lYsolde, the Frost Cantor', sub: '§7Keeper of the Third Seal - the choir that never ends', h: 3.4, sound: 'beacon.power', color: [0.6, 0.8, 1.0],
        shots: [{ pos: [20, 2, 10], look: 0.7, secs: 0 }, { pos: [12, 8, 4.5], look: 0.7, secs: 3.6, ease: 'InOutSine' },
            { pos: [6, -3, 0.8], look: 0.85, secs: 2.4, ease: 'OutCubic' }, { pos: [3, 0.5, 3.1], look: 0.9, secs: 2.0, ease: 'InOutSine' },
            { pos: [15, 0, 8], look: 0.7, secs: 2.2, ease: 'InOutSine' }],
        shakeAt: 6.2,
    },
    [`${NS}:mire_lantern`]: {
        title: '§a§lMorwen, the Mire Lantern', sub: '§7Keeper of the Fourth Seal - the light that leads you astray', h: 3.0, sound: 'mob.evocation_illager.prepare_summon', color: [0.15, 0.3, 0.1],
        shots: [{ pos: [18, 5, 3], look: 0.6, secs: 0 }, { pos: [11, -6, 2.5], look: 0.6, secs: 3.4, ease: 'InOutSine' },
            { pos: [6, 2, 0.4], look: 0.85, secs: 2.4, ease: 'OutCubic' }, { pos: [2.8, -0.4, 2.7], look: 0.88, secs: 2.0, ease: 'InOutSine' },
            { pos: [13, 0, 7], look: 0.6, secs: 2.2, ease: 'InOutSine' }],
        shakeAt: 5.8,
    },
};

/** player id -> token of the cinematic that currently owns them */
const owned = new Map();

function disabled() {
    return safe(() => world.getDynamicProperty(OFF_KEY)) === true;
}

function lock(p, on) {
    safe(() => p.inputPermissions.setPermissionCategory(InputPermissionCategory.Camera, !on), 'camLock');
    safe(() => p.inputPermissions.setPermissionCategory(InputPermissionCategory.Movement, !on), 'moveLock');
}

/** put the player back to normal; safe to call any number of times */
export function release(p) {
    safe(() => p.camera.clear(), 'camClear');
    lock(p, false);
    safe(() => p.runCommand('hud @s reset'), 'hudReset');
    owned.delete(p.id);
}

function dirTo(boss, p) {
    let dx = p.location.x - boss.location.x;
    let dz = p.location.z - boss.location.z;
    const l = Math.hypot(dx, dz);
    if (l < 0.5) { dx = 0; dz = 1; } else { dx /= l; dz /= l; }
    return { fx: dx, fz: dz, sx: -dz, sz: dx };
}

function shotPos(c, d, shot, scale) {
    const [f, s, u] = shot.pos;
    return { x: c.x + (d.fx * f + d.sx * s) * scale, y: c.y + u * scale, z: c.z + (d.fz * f + d.sz * s) * scale };
}

/** total length of a scene in ticks (so callers can wait for it) */
export function introTicks(typeId) {
    const sc = INTROS[typeId];
    if (!sc) return 0;
    return Math.ceil(sc.shots.reduce((a, s) => a + s.secs, 0.8) * 20) + 30;
}

/**
 * Play the scene of `boss` for everyone near it.  Returns the scene length in ticks (0 if there is none or cinematics are off).
 * `onDone` runs when the players are released.
 */
export function playIntro(boss, onDone) {
    const sc = INTROS[boss.typeId];
    if (!sc || disabled()) return 0;
    const players = safe(() => boss.dimension.getPlayers({ location: boss.location, maxDistance: RANGE })) || [];
    if (!players.length) return 0;
    const total = introTicks(boss.typeId);
    const scale = Math.max(0.8, sc.h / 3);
    const centre = { x: boss.location.x, y: boss.location.y, z: boss.location.z };
    const token = Symbol('intro');
    safe(() => boss.addTag(INTRO_TAG));
    safe(() => boss.addEffect('slowness', total + 10, { amplifier: 250, showParticles: false }));
    safe(() => boss.addEffect('resistance', total + 10, { amplifier: 4, showParticles: false }));

    const mine = [];
    for (const p of players) {
        owned.set(p.id, token);
        mine.push(p);
        safe(() => p.addEffect('resistance', total + 40, { amplifier: 4, showParticles: false }));
        safe(() => p.runCommand('hud @s hide'), 'hudHide');
        lock(p, true);
        safe(() => p.camera.fade({ fadeColor: { red: 0, green: 0, blue: 0 }, fadeTime: { fadeInTime: 0.25, holdTime: 0.25, fadeOutTime: 0.5 } }));
        safe(() => p.runCommand('music stop 0.3'));
    }

    // timeline
    let t = 6;                                                   // ticks (the fade hides the first cut)
    sc.shots.forEach((shot, i) => {
        const at = t;
        system.runTimeout(() => {
            for (const p of mine) {
                if (owned.get(p.id) !== token) continue;
                const d = dirTo({ location: centre }, p);
                const loc = shotPos(centre, d, shot, scale);
                const face = { x: centre.x, y: centre.y + sc.h * shot.look, z: centre.z };
                const opts = { location: loc, facingLocation: face };
                if (shot.secs > 0 && i > 0) opts.easeOptions = { easeTime: shot.secs, easeType: EasingType[shot.ease] || EasingType.InOutSine };
                safe(() => p.camera.setCamera('minecraft:free', opts), 'setCamera');
            }
        }, at);
        t += Math.max(1, Math.round(shot.secs * 20));
        if (i === 0) t += 20;                                    // hold the establishing shot for a second
    });
    // dramatic beat: shake + sound + title card
    system.runTimeout(() => {
        for (const p of mine) {
            safe(() => p.camera.addShake({ intensity: 0.5, duration: 1.4, type: CameraShakeType.Positional }));
            if (sc.sound) safe(() => p.playSound(sc.sound, { volume: 1.2 }));
            safe(() => p.onScreenDisplay.setTitle(sc.title, { subtitle: sc.sub, fadeInDuration: 12, stayDuration: 60, fadeOutDuration: 20 }));
        }
        safe(() => boss.dimension.spawnParticle(`${NS}:intro_burst`, { x: centre.x, y: centre.y + sc.h * 0.5, z: centre.z }));
    }, Math.round(sc.shakeAt * 20) + 20);
    // fade to normal, then release
    const end = total - 14;
    system.runTimeout(() => {
        for (const p of mine) safe(() => p.camera.fade({ fadeColor: { red: sc.color[0], green: sc.color[1], blue: sc.color[2] }, fadeTime: { fadeInTime: 0.3, holdTime: 0.2, fadeOutTime: 0.5 } }));
    }, end - 8);
    system.runTimeout(() => {
        for (const p of mine) if (owned.get(p.id) === token) release(p);
        safe(() => boss.removeTag(INTRO_TAG));
        if (onDone) safe(onDone, 'introDone');
    }, end);
    // failsafe: whatever happened above, nobody stays locked
    system.runTimeout(() => {
        for (const p of mine) if (owned.get(p.id) === token) release(p);
        safe(() => boss.removeTag(INTRO_TAG));
    }, total + 60);
    return total;
}

export function initCinematic() {
    // anyone who respawns or joins is certainly not in a scene
    world.afterEvents.playerSpawn.subscribe((ev) => { if (!owned.has(ev.player.id)) safe(() => ev.player.inputPermissions.setPermissionCategory(InputPermissionCategory.Movement, true)); });
    // /scriptevent ecr:cinematic on | off | test <boss>
    system.afterEvents.scriptEventReceive.subscribe((ev) => {
        if (ev.id !== `${NS}:cinematic`) return;
        const p = /** @type {any} */ (ev.sourceEntity);
        const [cmd, arg] = ev.message.trim().toLowerCase().split(/\s+/);
        if (cmd === 'on' || cmd === 'off') {
            safe(() => world.setDynamicProperty(OFF_KEY, cmd === 'off'));
            if (p) safe(() => p.sendMessage(`§d✿ §fBoss introductions are now ${cmd}.`));
        } else if (cmd === 'release' && p && p.typeId === 'minecraft:player') {
            release(p);
        } else if (cmd === 'test' && p && p.typeId === 'minecraft:player') {
            const boss = p.dimension.getEntities({ type: `${NS}:${arg}`, location: p.location, maxDistance: 60 })[0];
            if (boss) playIntro(boss);
            else p.sendMessage(`§cNo ${arg} within 60 blocks. /summon ecr:${arg} first.`);
        }
    });
}
