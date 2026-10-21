// Shared helpers for Eclipsed Realms (Tech Bytes Design)
import { world, system, ItemStack, EquipmentSlot, GameMode, EntityComponentTypes, ItemComponentTypes } from '@minecraft/server';

export const NS = 'ecr';
export const DIM_IDS = ['minecraft:overworld', 'minecraft:nether', 'minecraft:the_end'];
export const DIM_NAMES = { 'minecraft:overworld': 'Overworld', 'minecraft:nether': 'Nether', 'minecraft:the_end': 'The End' };

export const DEBUG = true;
const seenErrors = new Set();

export function safe(fn, label = '') {
    try {
        return fn();
    } catch (e) {
        if (DEBUG && label) {
            const m = `[ecr] ${label}: ${e && e.message ? e.message : e}`;
            if (!seenErrors.has(m)) {         // log each distinct problem once, visible in the content log
                seenErrors.add(m);
                console.warn(m);
            }
        }
        return undefined;
    }
}

export function dimOf(id) {
    return world.getDimension(id);
}

export function posKey(dimId, x, y, z) {
    return `${dimId}|${Math.floor(x)}|${Math.floor(y)}|${Math.floor(z)}`;
}

export function parseKey(key) {
    const [d, x, y, z] = key.split('|');
    return { dimId: d, x: +x, y: +y, z: +z };
}

export function isCreative(player) {
    return safe(() => player.getGameMode() === GameMode.Creative, 'gm') === true;
}

export function mainhand(player) {
    return safe(() => player.getComponent(EntityComponentTypes.Equippable).getEquipment(EquipmentSlot.Mainhand), 'mainhand');
}

export function setMainhand(player, item) {
    safe(() => player.getComponent(EntityComponentTypes.Equippable).setEquipment(EquipmentSlot.Mainhand, item), 'setMainhand');
}

export function consumeMainhand(player, n = 1) {
    if (isCreative(player)) return;
    const it = mainhand(player);
    if (!it) return;
    if (it.amount <= n) setMainhand(player, undefined);
    else {
        it.amount -= n;
        setMainhand(player, it);
    }
}

export function damageMainhand(player, amount = 1) {
    if (isCreative(player)) return;
    const it = mainhand(player);
    if (!it) return;
    safe(() => {
        const dur = it.getComponent(ItemComponentTypes.Durability);
        if (!dur) return;
        // honour Unbreaking
        let lvl = 0;
        const ench = it.getComponent(ItemComponentTypes.Enchantable);
        if (ench) {
            const e = ench.getEnchantment('unbreaking');
            if (e) lvl = e.level;
        }
        if (lvl > 0 && Math.random() > 1 / (lvl + 1)) return;
        const next = dur.damage + amount;
        if (next >= dur.maxDurability) {
            setMainhand(player, undefined);
            player.playSound('random.break');
        } else {
            dur.damage = next;
            setMainhand(player, it);
        }
    }, 'damageMainhand');
}

export function enchantLevel(item, id) {
    if (!item) return 0;
    return safe(() => {
        const ench = item.getComponent(ItemComponentTypes.Enchantable);
        if (!ench) return 0;
        const e = ench.getEnchantment(id);
        return e ? e.level : 0;
    }, 'enchantLevel') || 0;
}

export function center(block) {
    return { x: block.location.x + 0.5, y: block.location.y + 0.5, z: block.location.z + 0.5 };
}

export function say(player, msg) {
    safe(() => player.onScreenDisplay.setActionBar(msg), 'say');
}

export function msg(player, text) {
    safe(() => player.sendMessage(text), 'msg');
}

export function rand(a, b) {
    return a + Math.random() * (b - a);
}

export function randInt(a, b) {
    return Math.floor(rand(a, b + 1));
}

export function spawnParticle(dim, id, loc) {
    safe(() => dim.spawnParticle(id, loc), 'particle');
}

export function playSound(dim, id, loc, opts) {
    safe(() => dim.playSound(id, loc, opts), 'sound');
}

export function getState(block, name) {
    return safe(() => block.permutation.getState(name), 'getState');
}

export function setState(block, name, value) {
    safe(() => block.setPermutation(block.permutation.withState(name, value)), 'setState');
}

export function runLater(ticks, fn) {
    return system.runTimeout(() => safe(fn, 'runLater'), ticks);
}

export const DB_KEY = 'ecr:db_v1';

export function dbLoad() {
    const raw = safe(() => world.getDynamicProperty(DB_KEY));
    if (typeof raw === 'string') {
        try {
            const j = JSON.parse(raw);
            return { chambers: j.chambers || {}, plates: j.plates || {}, areas: j.areas || {} };
        } catch (e) { /* fall through */ }
    }
    return { chambers: {}, plates: {}, areas: {} };
}

export function dbSave(db) {
    safe(() => world.setDynamicProperty(DB_KEY, JSON.stringify(db)), 'dbSave');
}
