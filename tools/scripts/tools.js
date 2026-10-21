// Tool behaviours for the custom tools (till / strip / path) and slab merging for the Jacaranda set.
import { world, system, BlockPermutation } from '@minecraft/server';
import { NS, safe, getState, damageMainhand, consumeMainhand, playSound } from './util.js';

const TILLABLE = new Set(['minecraft:dirt', 'minecraft:grass_block', 'minecraft:grass_path']);
const PATHABLE = new Set(['minecraft:grass_block', 'minecraft:dirt', 'minecraft:podzol', 'minecraft:mycelium', 'minecraft:coarse_dirt']);

function strippedId(id) {
    const mine = /^ecr:(?!stripped_)([a-z]+)_(log|wood)$/.exec(id);
    if (mine) return `${NS}:stripped_${mine[1]}_${mine[2]}`;
    const m = /^minecraft:(?!stripped_)([a-z_]+?)_(log|wood|stem|hyphae)$/.exec(id);
    if (m) return `minecraft:stripped_${m[1]}_${m[2]}`;
    return undefined;
}

export function initTools() {
    world.afterEvents.playerInteractWithBlock.subscribe((ev) => {
        const it = ev.itemStack;
        if (!it || !it.typeId.startsWith(`${NS}:`)) return;
        const b = ev.block;
        const player = ev.player;
        const id = b.typeId;
        const c = { x: b.location.x + 0.5, y: b.location.y + 0.5, z: b.location.z + 0.5 };
        if (/_hoe$/.test(it.typeId)) {
            if (TILLABLE.has(id) || id === 'minecraft:coarse_dirt') {
                const above = safe(() => b.above());
                if (above && !above.isAir) return;
                b.setType(id === 'minecraft:coarse_dirt' ? 'minecraft:dirt' : 'minecraft:farmland');
                playSound(b.dimension, 'use.gravel', c, { volume: 1, pitch: 0.8 });
                damageMainhand(player, 1);
            }
        } else if (/_axe$/.test(it.typeId)) {
            const to = strippedId(id);
            if (to) {
                const perm = b.permutation;
                safe(() => {
                    const states = perm.getAllStates();
                    b.setPermutation(BlockPermutation.resolve(to, states));
                    playSound(b.dimension, 'use.wood', c, { volume: 1, pitch: 0.9 });
                    damageMainhand(player, 1);
                }, 'strip');
            }
        } else if (/_shovel$/.test(it.typeId)) {
            if (PATHABLE.has(id)) {
                const above = safe(() => b.above());
                if (above && !above.isAir) return;
                b.setType('minecraft:grass_path');
                playSound(b.dimension, 'use.grass', c, { volume: 1, pitch: 0.9 });
                damageMainhand(player, 1);
            }
        }
    });

    // merge two Jacaranda slabs into a double slab (top face of a bottom slab / bottom face of a top slab)
    world.beforeEvents.playerInteractWithBlock.subscribe((ev) => {
        const it = ev.itemStack;
        if (!it || !/^ecr:[a-z_]+_slab$/.test(it.typeId)) return;
        const b = ev.block;
        if (b.typeId !== it.typeId) return;
        const half = getState(b, 'minecraft:vertical_half');
        const face = ev.blockFace;
        if ((half === 'bottom' && face === 'Up') || (half === 'top' && face === 'Down')) {
            ev.cancel = true;
            const player = ev.player;
            system.run(() => safe(() => {
                b.setType(it.typeId.replace(/_slab$/, '_double_slab'));
                consumeMainhand(player, 1);
                playSound(b.dimension, 'dig.wood', { x: b.location.x + 0.5, y: b.location.y + 0.5, z: b.location.z + 0.5 }, { volume: 1, pitch: 0.9 });
            }, 'slabMerge'));
        }
    });
}
