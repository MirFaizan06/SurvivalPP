// Sanctum Warden - a claim / "chunk ban" block for Bedrock.
// Owner-managed protection zone: grace period, trusted players, passes, escalating responses,
// optional block/container protection. Operators are always exempt.
import { world, system, ItemStack, EquipmentSlot, EntityComponentTypes, CommandPermissionLevel } from '@minecraft/server';
import { ModalFormData } from '@minecraft/server-ui';
import { NS, DIM_NAMES, safe, dimOf, posKey, parseKey, mainhand, say, msg, spawnParticle, playSound, getState } from './util.js';

export const WARDEN = `${NS}:sanctum_warden`;
const PASS = `${NS}:sanctum_pass`;
const PASS_PROP = 'ecr:pass_zone';
const DB_KEY = 'ecr:sanctum_v1';           // legacy single-blob storage (migrated on first load)
const IDX_KEY = 'ecr:sanctum_idx';         // v2: index of zone keys + one dynamic property per zone (no size-limit trouble)
const zkey = (k) => `ecr:sz|${k}`;
const MAX_PER_PLAYER = 3;                  // wardens one (non-operator) player may keep; stops claim-spam on servers
const ABANDON_MS = 21 * 24 * 60 * 60 * 1000;   // owner unseen for 21 real days -> the zone lapses and can be claimed
const GRACE_TICKS = 60;       // 3 s to leave before the response fires
const RADII = [0, 8, 12, 16, 24, 32, 48];
const RADIUS_LABELS = ['Whole chunk (16x16, all heights)', '8 blocks', '12 blocks', '16 blocks', '24 blocks', '32 blocks', '48 blocks'];
const MODES = ['Warn only', 'Repel', 'Expel (teleport to spawn)', 'Seize items + Expel', 'Seize items + Expel + Kick'];

let Z = null;
let stored = new Set();
const zones = () => {
    if (Z) return Z;
    Z = {};
    const idxRaw = safe(() => world.getDynamicProperty(IDX_KEY));
    try {
        if (typeof idxRaw === 'string') {
            for (const k of JSON.parse(idxRaw)) {
                const raw = safe(() => world.getDynamicProperty(zkey(k)));
                if (typeof raw === 'string') Z[k] = JSON.parse(raw);
            }
        } else {
            const legacy = safe(() => world.getDynamicProperty(DB_KEY));
            if (typeof legacy === 'string') Z = JSON.parse(legacy);
        }
    } catch (e) { /* corrupt entry: start with what parsed */ }
    stored = new Set(Object.keys(Z));
    if (typeof idxRaw !== 'string' && stored.size) system.run(() => { saveZones(); safe(() => world.setDynamicProperty(DB_KEY, undefined)); });
    return Z;
};
const saveZones = () => safe(() => {
    const all = zones();
    const keys = Object.keys(all);
    for (const k of keys) world.setDynamicProperty(zkey(k), JSON.stringify(all[k]));
    for (const k of stored) if (!(k in all)) world.setDynamicProperty(zkey(k), undefined);
    stored = new Set(keys);
    world.setDynamicProperty(IDX_KEY, JSON.stringify(keys));
}, 'saveZones');

/** a zone nobody can manage any more (placed without an owner, or the owner has not been online for weeks) */
const isLapsed = (z) => !z.o || (!!z.s && Date.now() - z.s > ABANDON_MS);

const offenders = new Map();    // `${zoneKey}|${playerId}` -> { t0, warned }
const bounds = new Map();       // zoneKey -> ticks left of boundary display

/** Operators / admins bypass zones - but nothing in the Sanctum REQUIRES an operator, so it works on servers where everyone is a plain member. */
function isOp(p) {
    return safe(() => p.commandPermissionLevel >= CommandPermissionLevel.Admin) === true || safe(() => p.isOp()) === true || p.hasTag('ecr_sanctum_bypass');
}

function insideZone(key, z, p) {
    const k = parseKey(key);
    if (p.dimension.id !== k.dimId) return false;
    const l = p.location;
    if (z.r === 0) return Math.floor(l.x / 16) === Math.floor(k.x / 16) && Math.floor(l.z / 16) === Math.floor(k.z / 16);
    const dx = l.x - (k.x + 0.5), dz = l.z - (k.z + 0.5);
    return dx * dx + dz * dz <= z.r * z.r && Math.abs(l.y - k.y) <= 96;
}

function holdsPassFor(p, key) {
    return safe(() => {
        const inv = p.getComponent(EntityComponentTypes.Inventory).container;
        for (let i = 0; i < inv.size; i++) {
            const it = inv.getItem(i);
            if (it && it.typeId === PASS && it.getDynamicProperty(PASS_PROP) === key) return true;
        }
        const off = p.getComponent(EntityComponentTypes.Equippable).getEquipment(EquipmentSlot.Offhand);
        return !!(off && off.typeId === PASS && off.getDynamicProperty(PASS_PROP) === key);
    }) === true;
}

function trusted(p, key, z) {
    if (z.testUntil && z.testUntil > system.currentTick && z.o === p.id) return false;   // owner test mode
    if (z.o && z.o === p.id) return true;
    if (isOp(p)) return true;
    if (z.t.includes(p.name.toLowerCase())) return true;
    return holdsPassFor(p, key);
}

// ------------------------------------------------------------------------------------ responses
function seizeItems(p, dim, at) {
    safe(() => {
        const inv = p.getComponent(EntityComponentTypes.Inventory).container;
        for (let i = 0; i < inv.size; i++) {
            const it = inv.getItem(i);
            if (it) { dim.spawnItem(it, at); inv.setItem(i, undefined); }
        }
        const eq = p.getComponent(EntityComponentTypes.Equippable);
        for (const slot of [EquipmentSlot.Head, EquipmentSlot.Chest, EquipmentSlot.Legs, EquipmentSlot.Feet, EquipmentSlot.Offhand]) {
            const it = eq.getEquipment(slot);
            if (it) { dim.spawnItem(it, at); eq.setEquipment(slot, undefined); }
        }
    }, 'seize');
}

function expel(p, key, z) {
    const k = parseKey(key);
    let spawn = safe(() => p.getSpawnPoint());
    let dest, dimId;
    if (spawn && !(spawn.dimension.id === k.dimId && Math.hypot(spawn.x - k.x, spawn.z - k.z) <= (z.r || 16) + 4)) {
        dest = { x: spawn.x + 0.5, y: spawn.y + 0.2, z: spawn.z + 0.5 };
        dimId = spawn.dimension.id;
    } else {
        const w = world.getDefaultSpawnLocation();
        dest = { x: w.x + 0.5, y: w.y + 1, z: w.z + 0.5 };
        dimId = 'minecraft:overworld';
    }
    safe(() => p.teleport(dest, { dimension: dimOf(dimId) }), 'expelTeleport');
}

function punish(p, key, z0) {
    const z = (z0.testUntil && z0.testUntil > system.currentTick && z0.o === p.id) ? { ...z0, m: Math.min(z0.m, 2) } : z0;
    const k = parseKey(key);
    const dim = dimOf(k.dimId);
    const at = { x: k.x + 0.5, y: k.y + 1.2, z: k.z + 0.5 };
    playSound(dim, 'mob.wither.shoot', at, { volume: 2, pitch: 0.7 });
    if (z.m === 1) {
        const dx = p.location.x - at.x, dz = p.location.z - at.z;
        const d = Math.max(0.5, Math.hypot(dx, dz));
        safe(() => p.applyKnockback({ x: (dx / d) * 2.2, z: (dz / d) * 2.2 }, 0.7));
        say(p, '§c§lThe Warden repels you.');
        return;
    }
    if (z.m >= 3) seizeItems(p, dim, at);
    expel(p, key, z);
    const name = p.name;
    safe(() => p.onScreenDisplay.setTitle('§4Expelled', { subtitle: `§7You entered ${z.n}'s sanctum`, fadeInDuration: 5, stayDuration: 40, fadeOutDuration: 10 }));
    // tell the owner
    const owner = world.getAllPlayers().find((o) => o.id === z.o);
    if (owner) msg(owner, `§5[Sanctum] §d${name} §7was ${z.m >= 3 ? 'stripped and ' : ''}expelled${z.m === 4 ? ' and kicked' : ''} from your Sanctum at ${k.x} ${k.y} ${k.z}.`);
    if (z.m === 4) {
        system.runTimeout(() => safe(() => dimOf('minecraft:overworld').runCommand(`kick "${name}" Entered a restricted Sanctum.`), 'kick'), 30);
    }
}

// ------------------------------------------------------------------------------------ main loop
function enforce() {
    const all = zones();
    const players = world.getAllPlayers();
    const now = system.currentTick;
    for (const key of Object.keys(all)) {
        const z = all[key];
        if (isLapsed(z)) continue;                          // abandoned / ownerless: no enforcement
        const k = parseKey(key);
        const dim = safe(() => dimOf(k.dimId));
        if (!dim) continue;
        const dimPlayers = players.filter((p) => p.dimension.id === k.dimId);
        const b = safe(() => dim.getBlock({ x: k.x, y: k.y, z: k.z }));
        if (b === undefined) continue;                      // chunk not loaded: nobody nearby anyway
        if (b.typeId !== WARDEN) {                          // warden destroyed by other means
            delete all[key];
            saveZones();
            continue;
        }
        for (const p of dimPlayers) {
            const oKey = `${key}|${p.id}`;
            const inside = insideZone(key, z, p);
            if (!inside) { offenders.delete(oKey); continue; }
            if (trusted(p, key, z)) { offenders.delete(oKey); continue; }
            let o = offenders.get(oKey);
            if (!o) {
                o = { t0: now, warned: false };
                offenders.set(oKey, o);
                const left = Math.ceil(GRACE_TICKS / 20);
                safe(() => p.onScreenDisplay.setTitle('§c§lRESTRICTED SANCTUM', { subtitle: z.m === 0 ? `§7Owned by ${z.n}` : `§7Owned by ${z.n} - leave within ${left}s`, fadeInDuration: 5, stayDuration: 50, fadeOutDuration: 10 }));
                playSound(dim, 'beacon.deactivate', p.location, { volume: 1.2, pitch: 0.8 });
                o.warned = true;
                continue;
            }
            if (z.m === 0) {
                if (now - o.t0 >= 100) { o.t0 = now; say(p, `§c⚠ You are inside ${z.n}'s Sanctum`); }
                continue;
            }
            if (now - o.t0 >= GRACE_TICKS) {
                punish(p, key, z);
                offenders.delete(oKey);
                if (z.m === 1) offenders.set(oKey, { t0: now - GRACE_TICKS + 20, warned: true });   // repel again shortly if they stay
            }
        }
    }
}

function drawBounds() {
    for (const [key, left] of [...bounds.entries()]) {
        const z = zones()[key];
        if (!z || left <= 0) { bounds.delete(key); continue; }
        bounds.set(key, left - 5);
        const k = parseKey(key);
        const dim = safe(() => dimOf(k.dimId));
        if (!dim) continue;
        const y = k.y + 1.2;
        if (z.r === 0) {
            const x0 = Math.floor(k.x / 16) * 16, z0 = Math.floor(k.z / 16) * 16;
            for (let i = 0; i <= 16; i += 2) {
                for (const [x, zz] of [[x0 + i, z0], [x0 + i, z0 + 16], [x0, z0 + i], [x0 + 16, z0 + i]]) spawnParticle(dim, 'minecraft:endrod', { x, y, z: zz });
            }
        } else {
            const n = Math.max(24, Math.floor(z.r * 3));
            for (let i = 0; i < n; i++) {
                const a = (i / n) * Math.PI * 2;
                spawnParticle(dim, 'minecraft:endrod', { x: k.x + 0.5 + Math.cos(a) * z.r, y, z: k.z + 0.5 + Math.sin(a) * z.r });
            }
        }
    }
}

// ------------------------------------------------------------------------------------ menu
function describe(z) {
    return `§5Owner: §d${z.n || 'unknown'}   §5Range: §d${z.r === 0 ? 'chunk' : z.r + ' blocks'}   §5Response: §d${MODES[z.m]}   §5Trusted: §d${z.t.length ? z.t.join(', ') : 'none'}`;
}

function openMenu(player, key) {
    const z = zones()[key];
    if (!z) return;
    const form = new ModalFormData()
        .title('§5Sanctum Warden')
        .dropdown('Protection range', RADIUS_LABELS, { defaultValueIndex: Math.max(0, RADII.indexOf(z.r)) })
        .dropdown('Intruder response', MODES, { defaultValueIndex: z.m })
        .toggle('Protect blocks & containers inside the zone', { defaultValue: !!z.b })
        .textField('Trusted players (comma separated)', 'Steve, Alex', { defaultValue: z.t.join(', ') })
        .toggle('Show boundary for 10 seconds', { defaultValue: false })
        .toggle('TEST: treat me as an intruder for 30 seconds', { defaultValue: false })
        .submitButton('Save');
    form.show(player).then((res) => {
        if (res.canceled || !res.formValues) return;
        const [ri, mi, b, names, show, test] = /** @type {any[]} */ (res.formValues);
        z.r = RADII[ri] ?? 16;
        z.m = mi;
        z.b = b ? 1 : 0;
        z.t = String(names || '').split(',').map((s) => s.trim().toLowerCase()).filter((s) => s.length > 0).slice(0, 40);
        saveZones();
        if (show) bounds.set(key, 200);
        if (test) { z.testUntil = system.currentTick + 600; msg(player, '§5[Sanctum] §7Test mode: you will be treated as an intruder for 30 s (walk into the zone).'); }
        msg(player, '§5[Sanctum] §7Saved.  ' + describe(z));
        playSound(player.dimension, 'random.levelup', player.location, { volume: 0.6, pitch: 1.4 });
    }).catch(() => { /* form busy */ });
}

// ------------------------------------------------------------------------------------ registration / events
export function registerSanctumComponent(reg) {
    reg.registerCustomComponent(`${NS}:sanctum`, {
        onPlace(e) {
            // onPlace has no player; ownership is assigned by the playerPlaceBlock handler below
            const key = posKey(e.dimension.id, e.block.location.x, e.block.location.y, e.block.location.z);
            if (!zones()[key]) {
                zones()[key] = { o: '', n: 'World', r: 16, m: 2, b: 1, t: [], s: Date.now() };
                saveZones();
            }
        },
        onPlayerBreak(e) {
            const key = posKey(e.dimension.id, e.block.location.x, e.block.location.y, e.block.location.z);
            if (zones()[key]) { delete zones()[key]; saveZones(); }
        },
        onPlayerInteract(e) {
            const p = e.player;
            const key = posKey(e.dimension.id, e.block.location.x, e.block.location.y, e.block.location.z);
            const z = zones()[key];
            if (!z) { say(p, '§7This warden is dormant.'); return; }
            if (isLapsed(z) && !(z.o === p.id)) {
                // nobody is looking after this Sanctum: the first player to touch it claims it
                if (ownedBy(p) >= MAX_PER_PLAYER && !isOp(p)) { say(p, `§cYou already keep ${MAX_PER_PLAYER} Sanctums.`); return; }
                z.o = p.id; z.n = p.name; z.t = []; z.s = Date.now();
                saveZones();
                msg(p, '§5[Sanctum] §7You claimed an abandoned Sanctum. Right-click it again to configure.');
                playSound(e.dimension, 'random.levelup', p.location, { volume: 1, pitch: 0.8 });
                return;
            }
            const it = mainhand(p);
            const owner = z.o === p.id || isOp(p);
            if (owner && it && it.typeId === PASS) {
                // bind a pass to this zone
                safe(() => {
                    it.setDynamicProperty(PASS_PROP, key);
                    const k = parseKey(key);
                    it.setLore([`§5Sanctum Pass`, `§7${z.n}'s zone  ${k.x}, ${k.y}, ${k.z}`, `§8${DIM_NAMES[k.dimId] || k.dimId}`]);
                    p.getComponent(EntityComponentTypes.Equippable).setEquipment(EquipmentSlot.Mainhand, it);
                });
                say(p, '§dPass attuned to this Sanctum.');
                playSound(e.dimension, 'random.orb', p.location, { volume: 1, pitch: 1.2 });
                return;
            }
            if (owner) { openMenu(p, key); return; }
            say(p, trusted(p, key, z) ? `§aWelcome, you are trusted here. §7(Owner: ${z.n})` : `§cProtected by ${z.n}`);
        },
    });
}

export function initSanctum() {
    system.runInterval(() => safe(enforce, 'sanctumEnforce'), 10);
    // remember when each owner was last online (zones lapse after ABANDON_MS without the owner)
    system.runInterval(() => safe(() => {
        const all = zones();
        const online = new Set(world.getAllPlayers().map((q) => q.id));
        let dirty = false;
        for (const key of Object.keys(all)) {
            const z = all[key];
            if (z.o && (online.has(z.o) || !z.s)) { z.s = Date.now(); dirty = true; }
        }
        if (dirty) saveZones();
    }, 'sanctumSeen'), 6000);
    system.runInterval(() => safe(drawBounds, 'sanctumBounds'), 5);

    // whoever places a Warden owns it
    world.afterEvents.playerPlaceBlock.subscribe((ev) => {
        if (ev.block.typeId !== WARDEN) return;
        const key = posKey(ev.block.dimension.id, ev.block.location.x, ev.block.location.y, ev.block.location.z);
        if (ownedBy(ev.player) >= MAX_PER_PLAYER && !isOp(ev.player)) {
            safe(() => {
                const item = ev.block.getItemStack(1);
                ev.block.setType('minecraft:air');
                if (item) ev.block.dimension.spawnItem(item, { x: ev.block.location.x + 0.5, y: ev.block.location.y + 0.5, z: ev.block.location.z + 0.5 });
                delete zones()[key];
                saveZones();
            }, 'wardenLimit');
            msg(ev.player, `§c[Sanctum] You can only keep ${MAX_PER_PLAYER} Sanctum Wardens. Remove one first.`);
            return;
        }
        zones()[key] = { o: ev.player.id, n: ev.player.name, r: 16, m: 2, b: 1, t: [], s: Date.now() };
        saveZones();
        msg(ev.player, '§5[Sanctum] §7Warden armed. Right-click it to configure.  §8Default: 16 blocks, expel, block-protection on.');
        bounds.set(key, 100);
    });

    // the warden itself can only be removed by its owner (or an operator)
    world.beforeEvents.playerBreakBlock.subscribe((ev) => {
        const b = ev.block;
        const p = ev.player;
        const all = zones();
        if (b.typeId === WARDEN) {
            const key = posKey(b.dimension.id, b.location.x, b.location.y, b.location.z);
            const z = all[key];
            if (z && z.o !== p.id && !isOp(p) && !isLapsed(z)) {
                ev.cancel = true;
                system.run(() => say(p, `§cOnly ${z.n} can remove this Sanctum Warden.`));
            }
            return;
        }
        const hit = protectedZoneAt(b.dimension.id, b.location, p);
        if (hit) {
            ev.cancel = true;
            system.run(() => say(p, `§cThis area is protected by ${hit.z.n}.`));
        }
    });

    world.beforeEvents.playerInteractWithBlock.subscribe((ev) => {
        if (ev.block.typeId === WARDEN) return;
        const hit = protectedZoneAt(ev.block.dimension.id, ev.block.location, ev.player);
        if (hit && ev.isFirstEvent) {
            ev.cancel = true;
            system.run(() => say(ev.player, `§cThis area is protected by ${hit.z.n}.`));
        }
    });

    world.afterEvents.playerPlaceBlock.subscribe((ev) => {
        const b = ev.block;
        if (b.typeId === WARDEN) return;
        const hit = protectedZoneAt(b.dimension.id, b.location, ev.player);
        if (!hit) return;
        safe(() => {
            const item = b.getItemStack(1);
            const loc = { x: b.location.x + 0.5, y: b.location.y + 0.5, z: b.location.z + 0.5 };
            b.setType('minecraft:air');
            if (item) b.dimension.spawnItem(item, loc);
            say(ev.player, `§cThis area is protected by ${hit.z.n}.`);
        }, 'placeRevert');
    });
}

function protectedZoneAt(dimId, loc, player) {
    const all = zones();
    for (const key of Object.keys(all)) {
        const z = all[key];
        if (!z.b || isLapsed(z)) continue;
        const k = parseKey(key);
        if (k.dimId !== dimId) continue;
        let inZone;
        if (z.r === 0) inZone = Math.floor(loc.x / 16) === Math.floor(k.x / 16) && Math.floor(loc.z / 16) === Math.floor(k.z / 16);
        else inZone = (loc.x + 0.5 - (k.x + 0.5)) ** 2 + (loc.z + 0.5 - (k.z + 0.5)) ** 2 <= z.r * z.r && Math.abs(loc.y - k.y) <= 96;
        if (!inZone) continue;
        if (trusted(player, key, z)) return undefined;
        return { key, z };
    }
    return undefined;
}

function ownedBy(p) {
    return Object.values(zones()).filter((z) => z.o === p.id).length;
}
