// Stasis Chamber system: Java-style pearl stasis, remote trigger with a fishing rod, cross-dimension,
// with chunk keeping handled through persistent ticking areas.
import { world, system, ItemStack, EntityDamageCause } from '@minecraft/server';
import {
    NS, DIM_NAMES, safe, dimOf, posKey, parseKey, isCreative, mainhand, setMainhand, consumeMainhand, say, msg,
    spawnParticle, playSound, getState, setState, runLater, dbLoad, dbSave,
} from './util.js';

export const CHAMBER = `${NS}:stasis_chamber`;
export const PLATE = `${NS}:stasis_plate`;
const PEARL = 'minecraft:ender_pearl';
const ROD = 'minecraft:fishing_rod';
const LINK_PROP = 'ecr:link';
const RANGE = 6;              // plates fire chambers inside this radius
const PEARL_FALL_DAMAGE = 5;  // vanilla ender pearl landing damage

let DB = null;
const D = () => (DB ??= dbLoad());
const save = () => dbSave(D());

// --------------------------------------------------------------------------------------- chunk keeping
function areaId(dimId, x, z) {
    return `ecr_${dimId.replace('minecraft:', '')}_${Math.floor(x / 16)}_${Math.floor(z / 16)}`;
}

const pendingAreas = new Map();

/** Makes sure the chunk around (x,z) is permanently loaded & ticking. Resolves true on success. */
export function ensureLoaded(dimId, x, y, z) {
    const id = areaId(dimId, x, z);
    const mgr = world.tickingAreaManager;
    if (safe(() => mgr.hasTickingArea(id))) return Promise.resolve(true);
    if (pendingAreas.has(id)) return pendingAreas.get(id);
    const cx = Math.floor(x / 16) * 16, cz = Math.floor(z / 16) * 16;
    const opts = { dimension: dimOf(dimId), from: { x: cx, y: Math.floor(y), z: cz }, to: { x: cx + 15, y: Math.floor(y), z: cz + 15 } };
    if (!safe(() => mgr.hasCapacity(opts))) return Promise.resolve(false);
    const p = (async () => {
        try {
            await mgr.createTickingArea(id, opts);
            D().areas[id] = { d: dimId, x: cx, y: Math.floor(y), z: cz };
            save();
            return true;
        } catch (e) {
            return false;
        } finally {
            pendingAreas.delete(id);
        }
    })();
    pendingAreas.set(id, p);
    return p;
}

async function blockAt(dimId, x, y, z) {
    let b = safe(() => dimOf(dimId).getBlock({ x, y, z }));
    if (b) return b;
    await ensureLoaded(dimId, x, y, z);
    return safe(() => dimOf(dimId).getBlock({ x, y, z }));
}

/** Re-creates every saved ticking area (they do not survive a world restart). */
export async function restoreAreas() {
    const areas = D().areas;
    for (const id of Object.keys(areas)) {
        const a = areas[id];
        const mgr = world.tickingAreaManager;
        if (safe(() => mgr.hasTickingArea(id))) continue;
        const opts = { dimension: dimOf(a.d), from: { x: a.x, y: a.y, z: a.z }, to: { x: a.x + 15, y: a.y, z: a.z + 15 } };
        try {
            if (mgr.hasCapacity(opts)) await mgr.createTickingArea(id, opts);
        } catch (e) { /* ignore */ }
    }
}

// --------------------------------------------------------------------------------------- effects
function fx(dimId, x, y, z, kind) {
    const d = dimOf(dimId);
    const loc = { x: x + 0.5, y: y + 0.6, z: z + 0.5 };
    if (kind === 'load') {
        playSound(d, 'random.orb', loc, { volume: 1, pitch: 0.6 });
        for (let i = 0; i < 10; i++) spawnParticle(d, 'minecraft:endrod', { x: loc.x + (Math.random() - 0.5), y: loc.y + Math.random(), z: loc.z + (Math.random() - 0.5) });
    } else if (kind === 'fire') {
        playSound(d, 'mob.endermen.portal', loc, { volume: 1, pitch: 1 });
        for (let i = 0; i < 24; i++) spawnParticle(d, 'minecraft:endrod', { x: loc.x + (Math.random() - 0.5) * 1.4, y: loc.y + Math.random() * 1.6, z: loc.z + (Math.random() - 0.5) * 1.4 });
    } else if (kind === 'click') {
        playSound(d, 'random.click', loc, { volume: 0.8, pitch: 1.2 });
    }
}

// --------------------------------------------------------------------------------------- chambers
export function chamberKey(block) {
    return posKey(block.dimension.id, block.location.x, block.location.y, block.location.z);
}

function pearlCount(player) {
    const it = mainhand(player);
    return it && it.typeId === PEARL ? it.amount : 0;
}

export function loadChamber(player, block) {
    const key = chamberKey(block);
    if (getState(block, 'ecr:loaded') === 1) {
        const rec = D().chambers[key];
        if (rec && rec.o !== player.id) {
            say(player, `§cThis chamber holds §d${rec.n}§c's pearl.`);
        } else {
            say(player, '§dA pearl is already held in stasis here. §7(sneak + empty hand to take it back)');
        }
        return;
    }
    if (pearlCount(player) < 1) {
        say(player, '§7Hold an §dEnder Pearl§7 and use the chamber to bind it.');
        return;
    }
    consumeMainhand(player, 1);
    setState(block, 'ecr:loaded', 1);
    D().chambers[key] = { o: player.id, n: player.name };
    save();
    ensureLoaded(block.dimension.id, block.location.x, block.location.y, block.location.z);
    fx(block.dimension.id, block.location.x, block.location.y, block.location.z, 'load');
    say(player, '§dPearl bound to this chamber. §7Link a fishing rod to a Stasis Plate to trigger it from anywhere.');
}

export function retrievePearl(player, block) {
    const key = chamberKey(block);
    const rec = D().chambers[key];
    if (getState(block, 'ecr:loaded') !== 1) return;
    if (rec && rec.o !== player.id && !isCreative(player)) {
        say(player, `§cOnly §d${rec.n}§c can take this pearl.`);
        return;
    }
    setState(block, 'ecr:loaded', 0);
    delete D().chambers[key];
    save();
    safe(() => block.dimension.spawnItem(new ItemStack(PEARL, 1), { x: block.location.x + 0.5, y: block.location.y + 1.1, z: block.location.z + 0.5 }));
    fx(block.dimension.id, block.location.x, block.location.y, block.location.z, 'click');
}

export function chamberBroken(dimId, x, y, z, wasLoaded) {
    const key = posKey(dimId, x, y, z);
    if (D().chambers[key]) {
        delete D().chambers[key];
        save();
    }
    if (wasLoaded) {
        safe(() => dimOf(dimId).spawnItem(new ItemStack(PEARL, 1), { x: x + 0.5, y: y + 0.5, z: z + 0.5 }));
    }
}

/** Fires a chamber: teleports its owner to it (any dimension) and consumes the pearl. */
export async function fireChamber(key) {
    const rec = D().chambers[key];
    if (!rec) return false;
    const { dimId, x, y, z } = parseKey(key);
    const owner = world.getAllPlayers().find((p) => p.id === rec.o);
    if (!owner) return false;                 // owner offline: the pearl waits (like Java)
    const block = await blockAt(dimId, x, y, z);
    if (!block || block.typeId !== CHAMBER || getState(block, 'ecr:loaded') !== 1) {
        delete D().chambers[key];
        save();
        return false;
    }
    setState(block, 'ecr:loaded', 0);
    delete D().chambers[key];
    save();
    const from = { d: owner.dimension.id, l: owner.location };
    fx(from.d, from.l.x - 0.5, from.l.y - 0.6, from.l.z - 0.5, 'fire');
    const dest = { x: x + 0.5, y: y + 1.0, z: z + 0.5 };
    safe(() => owner.teleport(dest, { dimension: dimOf(dimId), keepVelocity: false }), 'teleport');
    if (!isCreative(owner)) safe(() => owner.applyDamage(PEARL_FALL_DAMAGE, { cause: EntityDamageCause.fall }));
    fx(dimId, x, y + 0.4, z, 'fire');
    say(owner, `§dStasis pearl released §7- ${DIM_NAMES[dimId] || dimId} ${x} ${y} ${z}`);
    return true;
}

function nearbyChamberKeys(dimId, x, y, z) {
    const out = [];
    for (const key of Object.keys(D().chambers)) {
        const p = parseKey(key);
        if (p.dimId !== dimId) continue;
        if (Math.abs(p.x - x) <= RANGE && Math.abs(p.y - y) <= RANGE && Math.abs(p.z - z) <= RANGE) out.push(key);
    }
    return out;
}

// --------------------------------------------------------------------------------------- plates
export function registerPlate(block) {
    D().plates[chamberKey(block)] = 1;
    save();
    ensureLoaded(block.dimension.id, block.location.x, block.location.y, block.location.z);
}

export function plateBroken(dimId, x, y, z) {
    const key = posKey(dimId, x, y, z);
    if (D().plates[key]) {
        delete D().plates[key];
        save();
    }
}

const releaseTimers = new Map();

export async function setPlate(key, powered, who) {
    const { dimId, x, y, z } = parseKey(key);
    const block = await blockAt(dimId, x, y, z);
    if (!block || block.typeId !== PLATE) return false;
    const was = getState(block, 'ecr:powered') === 1;
    if (was === powered) return true;
    setState(block, 'ecr:powered', powered ? 1 : 0);
    fx(dimId, x, y, z, 'click');
    const t = releaseTimers.get(key);
    if (t !== undefined) { system.clearRun(t); releaseTimers.delete(key); }
    if (powered) {
        // failsafe: a plate left pressed releases itself after 30 s
        releaseTimers.set(key, system.runTimeout(() => { releaseTimers.delete(key); setPlate(key, false); }, 600));
        for (const ck of nearbyChamberKeys(dimId, x, y, z)) fireChamber(ck);
    }
    return true;
}

export async function togglePlate(key) {
    const { dimId, x, y, z } = parseKey(key);
    const block = await blockAt(dimId, x, y, z);
    if (!block || block.typeId !== PLATE) return { ok: false };
    const now = getState(block, 'ecr:powered') !== 1;
    await setPlate(key, now);
    return { ok: true, powered: now };
}

// --------------------------------------------------------------------------------------- fishing rod linking
function readLink(item) {
    const raw = safe(() => item.getDynamicProperty(LINK_PROP));
    if (typeof raw !== 'string') return undefined;
    try { return JSON.parse(raw); } catch (e) { return undefined; }
}

function writeLink(player, link, label) {
    const it = mainhand(player);
    if (!it || it.typeId !== ROD) return;
    if (link) {
        it.setDynamicProperty(LINK_PROP, JSON.stringify(link));
        const p = parseKey(link.k);
        it.setLore([`§5Linked: §d${label}`, `§7${DIM_NAMES[p.dimId] || p.dimId}  ${p.x}, ${p.y}, ${p.z}`, '§8Cast = press · Reel = release']);
    } else {
        it.setDynamicProperty(LINK_PROP, undefined);
        it.setLore([]);
    }
    setMainhand(player, it);
}

const lastUse = new Map();

export function onRodUse(player, item) {
    if (!item || item.typeId !== ROD) return;
    const now = system.currentTick;
    if ((lastUse.get(player.id) ?? -99) + 6 > now) return;
    lastUse.set(player.id, now);
    const link = readLink(item);
    const hit = safe(() => player.getBlockFromViewDirection({ maxDistance: 8 }), 'rodRaycast');
    const b = hit && hit.block;
    const aimed = b && (b.typeId === PLATE || b.typeId === CHAMBER) ? b : undefined;

    // 1) aiming at a plate / chamber that this rod is not linked to yet  ->  LINK
    if (aimed && (!link || link.k !== chamberKey(aimed))) {
        const kind = aimed.typeId === PLATE ? 'p' : 'c';
        writeLink(player, { k: chamberKey(aimed), t: kind }, kind === 'p' ? 'Stasis Plate' : 'Stasis Chamber');
        ensureLoaded(aimed.dimension.id, aimed.location.x, aimed.location.y, aimed.location.z);
        fx(aimed.dimension.id, aimed.location.x, aimed.location.y, aimed.location.z, 'load');
        say(player, `§dFishing rod linked to the ${kind === 'p' ? 'Stasis Plate' : 'Stasis Chamber'}.  §7Cast to trigger from anywhere, sneak + use to unlink.`);
        return;
    }
    if (!link) {
        say(player, '§7Aim at a §dStasis Plate§7 or §dStasis Chamber§7 and use the rod to link it.');
        return;
    }
    // 2) sneaking with a linked rod  ->  UNLINK
    if (player.isSneaking) {
        writeLink(player, undefined);
        say(player, '§7Fishing rod link cleared.');
        return;
    }
    // 3) linked rod  ->  TRIGGER (anywhere, any dimension)
    if (link.t === 'p') {
        togglePlate(link.k).then((r) => {
            if (!r.ok) say(player, '§cThe linked Stasis Plate no longer exists.');
            else say(player, r.powered ? '§a▮ Plate pressed' : '§7▯ Plate released');
        });
    } else {
        fireChamber(link.k).then((ok) => {
            if (!ok) say(player, '§7The chamber is empty (or its owner is elsewhere).');
            else say(player, '§dPearl released.');
        });
    }
}

// --------------------------------------------------------------------------------------- redstone polling
const prevPower = new Map();

function pollRedstone() {
    const chambers = Object.keys(D().chambers);
    for (const key of chambers) {
        const { dimId, x, y, z } = parseKey(key);
        const b = safe(() => dimOf(dimId).getBlock({ x, y, z }));
        if (!b) continue;
        const p = safe(() => b.getRedstonePower()) || 0;
        const prev = prevPower.get(key) || 0;
        prevPower.set(key, p);
        if (p > 0 && prev === 0) fireChamber(key);
    }
}

export function initStasis() {
    system.runInterval(() => safe(pollRedstone, 'poll'), 4);
    system.runTimeout(() => restoreAreas(), 40);
    world.afterEvents.playerSpawn.subscribe((ev) => {
        if (ev.initialSpawn) system.runTimeout(() => restoreAreas(), 60);
    });
}
