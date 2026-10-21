// Custom death messages for the Eclipsed Realms mobs.
// Bedrock's vanilla death message cannot be customised per mob, so while one of our mobs (or projectiles) is near a player the
// 'showDeathMessages' gamerule is switched off and restored afterwards (crash-safe), and we broadcast our own message instead.
import { world, system, EntityDamageCause } from '@minecraft/server';
import { NS, DIM_IDS, safe, dimOf } from './util.js';

const FLAG = 'ecr:deathmsg_suppressed';
let suppressed = false;

const MOBS = {
    [`${NS}:ashen_warg`]: {
        name: 'Ashen Warg',
        melee: [
            '§c☠ §f%v §cwas torn apart by an §6Ashen Warg',
            '§c☠ §f%v §cbecame kindling for an §6Ashen Warg',
            '§c☠ §f%v §cwas hunted down and devoured by an §6Ashen Warg',
            '§c☠ §f%v §cwas dragged into the ashes by an §6Ashen Warg',
            '§c☠ §6An Ashen Warg §cfeasts tonight - §f%v §cwas the meal',
        ],
        ranged: [
            '§c☠ §f%v §cwas incinerated by an §6Ashen Warg§c\'s ember spit',
            '§c☠ §f%v §cwas scorched to cinders by an §6Ashen Warg',
            '§c☠ §f%v §cturned to ash beneath an §6Ashen Warg§c\'s fire',
        ],
    },
    [`${NS}:voidweaver`]: {
        name: 'Voidweaver',
        melee: [
            '§5☠ §f%v §dwas unraveled by a §5Voidweaver',
            '§5☠ §f%v §dbecame a thread in a §5Voidweaver§d\'s loom',
            '§5☠ §f%v §dwas pulled apart by a §5Voidweaver',
        ],
        ranged: [
            '§5☠ §f%v §dwas erased from existence by a §5Voidweaver§d\'s void bolt',
            '§5☠ §f%v §dwas woven into the void by a §5Voidweaver',
            '§5☠ §f%v §dfell to a §5Voidweaver§d\'s sorcery',
            '§5☠ §f%v §dfaded out of reality - a §5Voidweaver §dwas watching',
        ],
    },
    [`${NS}:eclipse_sovereign`]: {
        name: 'Eclipse Sovereign',
        melee: [
            '§4☠ §f%v §cwas judged by the §5§lEclipse Sovereign',
            '§4☠ §f%v §cwas crushed beneath the §5§lEclipse Sovereign§r§c\'s gauntlet',
            '§4☠ §cThe sky went dark for §f%v§c - the §5§lEclipse Sovereign §cpassed sentence',
            '§4☠ §f%v §cwas consumed by the §5§lEclipse',
        ],
        ranged: [
            '§4☠ §f%v §cwas erased by the §5§lEclipse Sovereign§r§c\'s orb',
            '§4☠ §f%v §clearned what lies beyond the light - §5§lEclipse Sovereign',
            '§4☠ §f%v §cwas unmade by the §5§lTotal Eclipse',
        ],
    },
    [`${NS}:gravewalker`]: {
        name: 'Gravewalker',
        melee: [
            '§2☠ §f%v §awas dragged into an early grave by a §2Gravewalker',
            '§2☠ §f%v §awas clawed apart by a §2Gravewalker',
            '§2☠ §f%v §ajoined the congregation of a §2Gravewalker',
            '§2☠ §f%v §awas buried alive by a §2Gravewalker',
        ],
        ranged: [
            '§2☠ §f%v §awas laid to rest by a §2Gravewalker',
        ],
    },
    [`${NS}:revenant`]: {
        name: 'Revenant',
        melee: [
            '§b☠ §f%v §3was cut down by a §bRevenant',
            '§b☠ §f%v §3was hacked apart by a §bRevenant§3’s rusted blade',
            '§b☠ §f%v §3met a §bRevenant §3who refused to stay dead',
        ],
        ranged: [
            '§b☠ §f%v §3was pierced by a §bRevenant§3’s bone shard',
            '§b☠ §f%v §3was shot down by a §bRevenant',
            '§b☠ §f%v §3never saw the §bRevenant §3on the ridge',
            '§b☠ §f%v §3was chilled to the bone by a §bRevenant',
        ],
    },
    [`${NS}:cave_weaver`]: {
        name: 'Cave Weaver',
        melee: [
            '§5☠ §f%v §dwas poisoned by a §5Cave Weaver',
            '§5☠ §f%v §dwas wrapped up and drained by a §5Cave Weaver',
            '§5☠ §f%v §dbecame dinner for a §5Cave Weaver',
        ],
        ranged: [
            '§5☠ §f%v §dwas tangled in a §5Cave Weaver§d’s web and eaten',
            '§5☠ §f%v §dcould not escape a §5Cave Weaver§d’s silk',
        ],
    },
    [`${NS}:sporeling`]: {
        name: 'Sporeling',
        melee: [
            '§a☠ §f%v §2was overgrown by a §aSporeling',
            '§a☠ §f%v §2inhaled the wrong mushrooms near a §aSporeling',
            '§a☠ §f%v §2became fertiliser for a §aSporeling',
        ],
        ranged: [
            '§a☠ §f%v §2choked on a §aSporeling§2’s spores',
        ],
    },
    [`${NS}:hollow_king`]: {
        name: 'Hollow King',
        melee: [
            '§2☠ §f%v §awas judged by the §2§lHollow King',
            '§2☠ §f%v §akneeled too late before the §2§lHollow King',
            '§2☠ §f%v §ajoined the §2§lHollow King§r§a’s court',
        ],
        ranged: [
            '§2☠ §f%v §awas cursed by the §2§lHollow King',
            '§2☠ §f%v §alost their soul to the §2§lHollow King',
        ],
    },
    [`${NS}:mosswood_colossus`]: {
        name: 'Mosswood Colossus',
        melee: [
            '§2☠ §f%v §awas flattened by the §2§lMosswood Colossus',
            '§2☠ §f%v §awas buried under the §2§lMosswood Colossus§r§a’s roots',
            '§2☠ §f%v §awas reclaimed by the forest',
        ],
        ranged: [
            '§2☠ §f%v §awas swallowed by the §2§lWildgrowth',
        ],
    },
    [`${NS}:silkqueen`]: {
        name: 'Silkqueen',
        melee: [
            '§5☠ §f%v §dwas devoured by the §5§lSilkqueen',
            '§5☠ §f%v §dbecame the §5§lSilkqueen§r§d’s latest cocoon',
            '§5☠ §f%v §dwas venomed in the §5§lSilkqueen§r§d’s web',
        ],
        ranged: [
            '§5☠ §f%v §dwas bound and bled by the §5§lSilkqueen',
        ],
    },
};

const PROJECTILES = {
    [`${NS}:void_bolt`]: `${NS}:voidweaver`,
    [`${NS}:eclipse_orb`]: `${NS}:eclipse_sovereign`,
    [`${NS}:ember_spit`]: `${NS}:ashen_warg`,
    [`${NS}:bone_shard`]: `${NS}:revenant`,
    [`${NS}:web_bolt`]: `${NS}:cave_weaver`,
};

const FALLBACK = {
    [EntityDamageCause.fall]: 'fell from a high place',
    [EntityDamageCause.fire]: 'went up in flames',
    [EntityDamageCause.fireTick]: 'burned to death',
    [EntityDamageCause.lava]: 'tried to swim in lava',
    [EntityDamageCause.drowning]: 'drowned',
    [EntityDamageCause.suffocation]: 'suffocated in a wall',
    [EntityDamageCause.starve]: 'starved to death',
    [EntityDamageCause.lightning]: 'was struck by lightning',
    [EntityDamageCause.void]: 'fell out of the world',
    [EntityDamageCause.blockExplosion]: 'blew up',
    [EntityDamageCause.entityExplosion]: 'blew up',
    [EntityDamageCause.magic]: 'was killed by magic',
    [EntityDamageCause.freezing]: 'froze to death',
    [EntityDamageCause.contact]: 'was pricked to death',
    [EntityDamageCause.magma]: 'discovered the floor was lava',
    [EntityDamageCause.fallingBlock]: 'was squashed by a falling block',
    [EntityDamageCause.anvil]: 'was squashed by a falling anvil',
};

function pick(list) {
    return list[Math.floor(Math.random() * list.length)];
}

function pretty(id) {
    return id.replace(/^[a-z_]+:/, '').split('_').map((w) => w[0].toUpperCase() + w.slice(1)).join(' ');
}

function threatNearby() {
    for (const id of DIM_IDS) {
        const dim = safe(() => dimOf(id));
        if (!dim) continue;
        const ents = safe(() => dim.getEntities({ families: ['ecr_mob', 'ecr_projectile'] })) || [];
        if (!ents.length) continue;
        const players = safe(() => dim.getPlayers()) || [];
        for (const e of ents) {
            for (const p of players) {
                const dx = e.location.x - p.location.x, dy = e.location.y - p.location.y, dz = e.location.z - p.location.z;
                if (dx * dx + dy * dy + dz * dz < 40 * 40) return true;
            }
        }
    }
    return false;
}

function setSuppressed(on) {
    if (on === suppressed) return;
    if (on) {
        if (!world.gameRules.showDeathMessages) return;           // the user already turned them off: leave it alone
        world.gameRules.showDeathMessages = false;
        safe(() => world.setDynamicProperty(FLAG, true));
        suppressed = true;
    } else {
        world.gameRules.showDeathMessages = true;
        safe(() => world.setDynamicProperty(FLAG, false));
        suppressed = false;
    }
}

function killerOf(src) {
    const proj = src.damagingProjectile && src.damagingProjectile.typeId;
    const e = src.damagingEntity && src.damagingEntity.typeId;
    if (e && MOBS[e]) return { mob: e, kind: (proj || src.cause === EntityDamageCause.entityExplosion || src.cause === EntityDamageCause.magic) ? 'ranged' : 'melee' };
    if (proj && PROJECTILES[proj]) return { mob: PROJECTILES[proj], kind: 'ranged' };
    if (e && PROJECTILES[e]) return { mob: PROJECTILES[e], kind: 'ranged' };
    return undefined;
}

export function initDeaths() {
    // crash safety: if the world was closed while suppressed, restore the rule
    if (safe(() => world.getDynamicProperty(FLAG)) === true) {
        safe(() => { world.gameRules.showDeathMessages = true; world.setDynamicProperty(FLAG, false); });
    }
    system.runInterval(() => safe(() => setSuppressed(threatNearby()), 'deathWindow'), 5);

    world.afterEvents.entityDie.subscribe((ev) => {
        const victim = /** @type {any} */ (ev.deadEntity);
        if (victim.typeId !== 'minecraft:player') return;
        const src = ev.damageSource;
        const k = killerOf(src);
        if (k) {
            const line = pick(MOBS[k.mob][k.kind]).replace('%v', victim.name);
            world.sendMessage(line);
            return;
        }
        if (!suppressed) return;                                   // vanilla message is shown normally
        // vanilla messages are muted during the fight window: send a close equivalent
        if (src.damagingEntity) {
            const e = /** @type {any} */ (src.damagingEntity);
            const who = e.typeId === 'minecraft:player' ? e.name : (e.nameTag || pretty(e.typeId));
            world.sendMessage(`§f${victim.name} was slain by ${who}`);
        } else {
            world.sendMessage(`§f${victim.name} ${FALLBACK[src.cause] || 'died'}`);
        }
    });
}
