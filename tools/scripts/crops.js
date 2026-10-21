// Crops: growth (light + farmland moisture), bone meal, right-click harvest & replant, drops with Fortune; food effects.
import { world, system, ItemStack } from '@minecraft/server';
import { NS, safe, getState, setState, rand, randInt, say, spawnParticle, playSound, consumeMainhand, enchantLevel, isCreative } from './util.js';

const CROP = /^ecr:([a-z]+)_crop$/;
const SPEED = { tomato: 0.22, corn: 0.18, strawberry: 0.2, chili: 0.2, oats: 0.28 };
const SEED = { tomato: 'tomato_seeds', corn: 'corn_kernels', strawberry: 'strawberry_seeds', chili: 'chili_seeds', oats: 'oat_seeds' };
const PRODUCE = { tomato: 'tomato', corn: 'corn_cob', strawberry: 'strawberry', chili: 'chili_pepper', oats: 'oats' };
const MATURE = 3;

function spawn(block, id, n) {
    if (n <= 0) return;
    safe(() => block.dimension.spawnItem(new ItemStack(id, n), { x: block.location.x + 0.5, y: block.location.y + 0.4, z: block.location.z + 0.5 }), 'cropDrop');
}

/** vanilla-like growth: needs light >= 9, much faster on hydrated farmland */
function growthChance(block, crop) {
    const light = safe(() => block.getLightLevel());
    if (light !== undefined && light < 9) return 0;
    const soil = safe(() => block.below());
    let c = SPEED[crop] ?? 0.2;
    if (soil && soil.typeId === 'minecraft:farmland') {
        const m = getState(soil, 'moisturized_amount') ?? 0;
        c *= m > 0 ? 1.0 + m * 0.08 : 0.5;
    } else {
        return -1;                       // unsupported soil
    }
    return c;
}

function advance(block, by) {
    const g = getState(block, 'ecr:growth') ?? 0;
    const n = Math.min(MATURE, g + by);
    if (n !== g) setState(block, 'ecr:growth', n);
    return n;
}

export function harvest(block, player) {
    const m = CROP.exec(block.typeId);
    if (!m) return false;
    const crop = m[1];
    if ((getState(block, 'ecr:growth') ?? 0) < MATURE) return false;
    const fortune = player ? enchantLevel(safe(() => player.getComponent('minecraft:equippable').getEquipment('Mainhand')), 'fortune') : 0;
    spawn(block, `${NS}:${PRODUCE[crop]}`, randInt(1, 2) + (fortune ? randInt(0, fortune) : 0));
    if (Math.random() < 0.45 + 0.1 * fortune) spawn(block, `${NS}:${SEED[crop]}`, 1);
    setState(block, 'ecr:growth', crop === 'strawberry' ? 1 : 0);          // replant (berry bushes regrow)
    playSound(block.dimension, 'dig.grass', { x: block.location.x + 0.5, y: block.location.y + 0.5, z: block.location.z + 0.5 }, { volume: 0.9, pitch: 1.2 });
    return true;
}

export function registerCropComponent(reg) {
    reg.registerCustomComponent(`${NS}:crop`, {
        onRandomTick(e) {
            const b = e.block;
            const m = CROP.exec(b.typeId);
            if (!m) return;
            const g = getState(b, 'ecr:growth') ?? 0;
            if (g >= MATURE) return;
            const chance = growthChance(b, m[1]);
            if (chance < 0) {                                              // farmland was removed: pop the plant
                const { x, y, z } = b.location;
                safe(() => e.dimension.runCommand(`setblock ${x} ${y} ${z} air destroy`));
                return;
            }
            if (Math.random() < chance) setState(b, 'ecr:growth', g + 1);
        },
        onPlayerInteract(e) {
            // right-click a ripe plant to harvest + replant (bone meal is handled before the interaction)
            if (e.player && e.player.isSneaking) return;
            harvest(e.block, e.player);
        },
    });
}

/** bone meal on a crop: +1-2 growth stages, like vanilla */
export function boneMealCrop(player, block) {
    consumeMainhand(player, 1);
    const c = { x: block.location.x + 0.5, y: block.location.y + 0.4, z: block.location.z + 0.5 };
    for (let i = 0; i < 8; i++) spawnParticle(block.dimension, 'minecraft:crop_growth_emitter', { x: c.x + rand(-0.4, 0.4), y: c.y + rand(0, 0.5), z: c.z + rand(-0.4, 0.4) });
    playSound(block.dimension, 'item.bone_meal.use', c, { volume: 1, pitch: 1 });
    advance(block, randInt(1, 2));
}

export function isCropBlock(typeId) {
    return CROP.test(typeId);
}

// ------------------------------------------------------------------------------------------- break drops (Fortune)
export function initCrops() {
    world.afterEvents.playerBreakBlock.subscribe((ev) => {
        const m = CROP.exec(ev.brokenBlockPermutation.type.id);
        if (!m || isCreative(ev.player)) return;
        const g = /** @type {number} */ (ev.brokenBlockPermutation.getState(/** @type {any} */ ('ecr:growth')) ?? 0);
        const fortune = enchantLevel(ev.itemStackBeforeBreak, 'fortune');
        if (g >= MATURE) {
            spawn(ev.block, `${NS}:${PRODUCE[m[1]]}`, randInt(1, 2) + (fortune ? randInt(0, fortune) : 0));
            spawn(ev.block, `${NS}:${SEED[m[1]]}`, randInt(0, 1 + fortune));
        }
    });
}

// ------------------------------------------------------------------------------------------- food effects (data-driven food cannot carry effects any more)
const EFFECTS = {
    chili_pepper: [['fire_resistance', 30, 0]],
    chili_stew: [['fire_resistance', 120, 0], ['strength', 30, 0]],
    tomato_soup: [['regeneration', 5, 0]],
    hunters_stew: [['regeneration', 8, 0], ['resistance', 60, 0]],
    porridge: [['absorption', 90, 0]],
    roasted_corn: [['speed', 25, 0]],
    berry_pie: [['haste', 40, 0]],
    cooked_venison: [],
};

export function initFoodEffects() {
    world.afterEvents.itemCompleteUse.subscribe((ev) => {
        const id = ev.itemStack && ev.itemStack.typeId;
        if (!id || !id.startsWith(`${NS}:`)) return;
        const list = EFFECTS[id.slice(NS.length + 1)];
        if (!list) return;
        for (const [eff, secs, amp] of list) safe(() => ev.source.addEffect(eff, secs * 20, { amplifier: amp, showParticles: true }), 'foodEffect');
    });
}
