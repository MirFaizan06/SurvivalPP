// Self-check: tells you (in chat and in the content log) if the game failed to load any of this add-on's creatures.
// Run it any time with:  /scriptevent ecr:diag
import { world, system, EntityTypes } from '@minecraft/server';
import { NS, safe, msg } from './util.js';

/** every creature the add-on defines (kept in sync with the behaviour pack by lint4) */
export const CREATURES = [
    'ashen_warg', 'voidweaver', 'eclipse_sovereign', 'meadow_deer', 'highland_yak', 'wild_boar', 'pheasant', 'gravewalker', 'revenant', 'cave_weaver', 'sporeling',
    'hollow_king', 'mosswood_colossus', 'silkqueen', 'veiled_blossom', 'blossom_vex', 'blossom_echo',
    'frost_cantor', 'mire_lantern', 'rimewalker', 'hoarbone', 'mirewalker', 'lanternbone', 'mire_wisp', 'mire_decoy',
];

function missing() {
    return CREATURES.filter((n) => !safe(() => EntityTypes.get(`${NS}:${n}`)));
}

export function initDiag() {
    const report = (target) => {
        const miss = missing();
        const text = miss.length
            ? `§c[Eclipsed Realms] ${miss.length} creature(s) failed to load: ${miss.join(', ')}. §7Open Settings > Creator > Content Log (GUI + file) and look for errors mentioning these names, then re-activate the Behavior Pack in your world.`
            : `§a[Eclipsed Realms] all ${CREATURES.length} creatures loaded.`;
        console.warn(text.replace(/§./g, ''));
        if (target) msg(target, text);
        return miss;
    };
    // once per session, for the first player to join: only speak up when something is wrong
    let said = false;
    world.afterEvents.playerSpawn.subscribe((ev) => {
        if (!ev.initialSpawn || said) return;
        said = true;
        system.runTimeout(() => safe(() => { if (missing().length) report(ev.player); else report(undefined); }, 'diag'), 200);
    });
    system.afterEvents.scriptEventReceive.subscribe((ev) => {
        if (ev.id !== `${NS}:diag`) return;
        const p = /** @type {any} */ (ev.sourceEntity);
        report(p && p.typeId === 'minecraft:player' ? p : undefined);
    });
}
