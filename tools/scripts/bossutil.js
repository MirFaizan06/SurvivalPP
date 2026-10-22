// Helpers shared by the Chapter III / IV boss brains (Frost Cantor, Mire Lantern).
import { world, EntityComponentTypes, EquipmentSlot } from '@minecraft/server';
import { NS, safe, rand, runLater } from './util.js';
import { nearbyPlayers } from './boss.js';

export const vec = {
    sub: (a, b) => ({ x: a.x - b.x, y: a.y - b.y, z: a.z - b.z }),
    len: (a) => Math.hypot(a.x, a.y, a.z),
    norm: (a) => { const l = Math.hypot(a.x, a.y, a.z) || 1; return { x: a.x / l, y: a.y / l, z: a.z / l }; },
    rotY: (a, deg) => { const r = (deg * Math.PI) / 180, c = Math.cos(r), s = Math.sin(r); return { x: a.x * c - a.z * s, y: a.y, z: a.x * s + a.z * c }; },
};

export function nearestPlayer(boss, r = 48) {
    let best, bd = 1e9;
    for (const p of nearbyPlayers(boss.dimension, boss.location, r)) {
        const d = vec.len(vec.sub(p.location, boss.location));
        if (d < bd) { bd = d; best = p; }
    }
    return best;
}

export function countNear(dim, type, loc, r) {
    return (safe(() => dim.getEntities({ type, location: loc, maxDistance: r })) || []).length;
}

/** a standable spot near `c` (air above a solid, non-liquid block) or undefined */
export function openSpot(dim, c, r, minR = 0.5) {
    for (let i = 0; i < 14; i++) {
        const a = rand(0, Math.PI * 2), d = rand(r * minR, r);
        const x = Math.floor(c.x + Math.cos(a) * d), z = Math.floor(c.z + Math.sin(a) * d);
        for (let dy = 3; dy >= -3; dy--) {
            const y = Math.floor(c.y) + dy;
            const feet = safe(() => dim.getBlock({ x, y, z })), head = safe(() => dim.getBlock({ x, y: y + 1, z })), floor = safe(() => dim.getBlock({ x, y: y - 1, z }));
            if (feet && head && floor && feet.isAir && head.isAir && !floor.isAir && !floor.isLiquid) return { x: x + 0.5, y, z: z + 0.5 };
        }
    }
    return undefined;
}

/** the casting pose (client animation `cast`) for `ticks` */
export function cast(boss, ticks = 30) {
    safe(() => boss.triggerEvent(`${NS}:cast_on`));
    runLater(ticks, () => boss.isValid && boss.triggerEvent(`${NS}:cast_off`));
}

/** cooldown helper: true when `key` is due, then re-arms it */
export function due(s, key, now, every, first = every) {
    if (s.next[key] === undefined) s.next[key] = now + first;
    if (now < s.next[key]) return false;
    s.next[key] = now + every;
    return true;
}

export function hp(p) {
    return safe(() => p.getComponent(EntityComponentTypes.Health).currentValue) ?? 20;
}

export function knock(p, from, kb, up = 0.4) {
    safe(() => {
        const dx = p.location.x - from.x, dz = p.location.z - from.z;
        const d = Math.max(0.5, Math.hypot(dx, dz));
        p.applyKnockback({ x: (dx / d) * kb, z: (dz / d) * kb }, up);
    }, 'knock');
}

/** per-fight fog: players in range get the fog of the current phase, players who leave get their sky back */
export function fogController(fogId, fogs) {
    const set = (player, idx, s) => {
        const cur = s.fog.get(player.id);
        if (cur === idx) return;
        safe(() => {
            if (cur !== undefined) player.runCommand(`fog @s remove ${fogId}`);
            if (idx >= 0) player.runCommand(`fog @s push ${fogs[idx]} ${fogId}`);
        }, 'fog');
        if (idx >= 0) s.fog.set(player.id, idx); else s.fog.delete(player.id);
    };
    const follow = (players, idx, s) => {
        for (const p of players) set(p, idx, s);
        for (const p of world.getAllPlayers()) if (s.fog.has(p.id) && !players.some((q) => q.id === p.id)) set(p, -1, s);
    };
    const clear = (s) => {
        for (const p of world.getAllPlayers()) if (s.fog.has(p.id)) safe(() => p.runCommand(`fog @s remove ${fogId}`), 'fogClear');
        s.fog.clear();
    };
    return { set, follow, clear };
}

export function speak(who, color, dim, loc, text) {
    for (const p of nearbyPlayers(dim, loc, 60)) safe(() => p.sendMessage(`${color}[${who}] ${text}`));
}

/** what counts as "carrying a light" for Morwen's darkness; the Keeper's Lantern also lights everyone within 10 blocks */
const LIGHTS = new Set(['minecraft:torch', 'minecraft:soul_torch', 'minecraft:lantern', 'minecraft:soul_lantern', 'minecraft:glowstone', 'minecraft:sea_lantern', 'minecraft:shroomlight', `${NS}:keepers_lantern`]);

export function holdsLight(p) {
    return safe(() => {
        const eq = p.getComponent(EntityComponentTypes.Equippable);
        for (const slot of [EquipmentSlot.Mainhand, EquipmentSlot.Offhand]) {
            const it = eq.getEquipment(slot);
            if (it && LIGHTS.has(it.typeId)) return true;
        }
        return false;
    }) === true;
}

export function holdsKeepersLantern(p) {
    return safe(() => {
        const eq = p.getComponent(EntityComponentTypes.Equippable);
        for (const slot of [EquipmentSlot.Mainhand, EquipmentSlot.Offhand]) {
            const it = eq.getEquipment(slot);
            if (it && it.typeId === `${NS}:keepers_lantern`) return true;
        }
        return false;
    }) === true;
}
