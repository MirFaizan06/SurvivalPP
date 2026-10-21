// Ore rules: netherite-tier pickaxe required, Silk Touch / Fortune / XP like core ores.
import { world, system, ItemStack } from '@minecraft/server';
import { NS, safe, say, isCreative, enchantLevel, damageMainhand, randInt } from './util.js';

const GATED = {
    [`${NS}:azurite_ore`]: { raw: `${NS}:raw_azurite`, xp: [3, 7] },
    [`${NS}:pyrelite_ore`]: { raw: `${NS}:raw_pyrelite`, xp: [4, 9] },
    [`${NS}:eclipsite_ore`]: { raw: `${NS}:raw_eclipsite`, xp: [6, 12] },
};
const OK_PICKS = new Set(['minecraft:netherite_pickaxe', `${NS}:pyrelite_pickaxe`, `${NS}:eclipsite_pickaxe`]);

export function initMining() {
    world.beforeEvents.playerBreakBlock.subscribe((ev) => {
        if (/^ecr:[a-z]+_leaves$/.test(ev.block.typeId)) {
            const tool = ev.itemStack;
            if (tool && enchantLevel(tool, 'silk_touch') > 0 && !isCreative(ev.player)) {
                ev.cancel = true;
                const b = ev.block, id = b.typeId, p = ev.player;
                system.run(() => safe(() => {
                    b.setType('minecraft:air');
                    b.dimension.spawnItem(new ItemStack(id, 1), { x: b.location.x + 0.5, y: b.location.y + 0.5, z: b.location.z + 0.5 });
                    damageMainhand(p, 1);
                }, 'silkLeaves'));
            }
            return;
        }
        const def = GATED[ev.block.typeId];
        if (!def) return;
        const player = ev.player;
        if (isCreative(player)) return;
        const item = ev.itemStack;
        if (!item || !OK_PICKS.has(item.typeId)) {
            ev.cancel = true;
            system.run(() => say(player, '§cThis ore can only be mined with a §5Netherite Pickaxe§c (or better).'));
            return;
        }
        if (enchantLevel(item, 'silk_touch') > 0) {
            ev.cancel = true;
            const b = ev.block;
            const id = b.typeId;
            system.run(() => safe(() => {
                const loc = { x: b.location.x + 0.5, y: b.location.y + 0.5, z: b.location.z + 0.5 };
                b.setType('minecraft:air');
                b.dimension.spawnItem(new ItemStack(id, 1), loc);
                damageMainhand(player, 1);
            }, 'silk'));
        }
    });

    world.afterEvents.playerBreakBlock.subscribe((ev) => {
        const def = GATED[ev.brokenBlockPermutation.type.id];
        if (!def) return;
        const player = ev.player;
        if (isCreative(player)) return;
        const tool = ev.itemStackBeforeBreak;
        const loc = { x: ev.block.location.x + 0.5, y: ev.block.location.y + 0.5, z: ev.block.location.z + 0.5 };
        safe(() => {
            const fortune = enchantLevel(tool, 'fortune');
            if (fortune > 0) {
                const bonus = Math.max(0, randInt(0, fortune + 1) - 1);
                if (bonus > 0) ev.block.dimension.spawnItem(new ItemStack(def.raw, bonus), loc);
            }
            player.addExperience(randInt(def.xp[0], def.xp[1]));
        }, 'oreDrops');
    });
}
