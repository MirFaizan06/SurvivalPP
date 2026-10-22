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
    [`${NS}:veiled_blossom`]: {
        name: 'The Veiled Blossom',
        melee: [
            '§d☠ §f%v §fwas gently, sadly put down by §d§lHanae',
            '§d☠ §f%v §fignored every warning from §d§lThe Veiled Blossom',
            '§d☠ §f%v §fwalked a road that §d§lHanae §fbegged them to leave',
        ],
        ranged: [
            '§d☠ §f%v §fdrowned in §d§lHanae§r§f\u2019s falling petals',
            '§d☠ §f%v §fwas not turned back by the §d§lVeiled Blossom',
        ],
    },
    [`${NS}:frost_cantor`]: {
        name: 'The Frost Cantor',
        melee: [
            '§b☠ §f%v §fwas silenced by §b§lYsolde, the Frost Cantor',
            '§b☠ §f%v §ffell out of tune with §b§lThe Frost Cantor',
            '§b☠ §f%v §fbecame the final rest in §b§lYsolde§r§f\u2019s song',
        ],
        ranged: [
            '§b☠ §f%v §fwas struck by a frozen note from §b§lThe Frost Cantor',
            '§b☠ §f%v §fcould not keep time with §b§lYsolde',
            '§b☠ §f%v §fstood on the ground when the §b§lResonance §fpassed',
        ],
    },
    [`${NS}:mire_lantern`]: {
        name: 'The Mire Lantern',
        melee: [
            '§a☠ §f%v §ffollowed the wrong light to §a§lMorwen',
            '§a☠ §f%v §fwas struck by §a§lthe Mire Lantern§r§f\u2019s own lamp',
            '§a☠ §f%v §fwas kept by the fen',
        ],
        ranged: [
            '§a☠ §f%v §fwas burned by foxfire from §a§lThe Mire Lantern',
            '§a☠ §f%v §fput out their own light in §a§lMorwen§r§f\u2019s fen',
            '§a☠ §f%v §fwas lost in the dark of §a§lthe Mire Lantern',
        ],
    },
    [`${NS}:cinder_bride`]: {
        name: 'The Cinder Bride',
        melee: [
            '§6☠ §f%v §fwas given away by §6§lVarenna, the Cinder Bride',
            '§6☠ §f%v §fwas married to the anvil by §6§lthe Cinder Bride',
            '§6☠ §f%v §ffell silent at §6§lVarenna§r§f\u2019s wedding',
        ],
        ranged: [
            '§6☠ §f%v §fwas burned at the altar by §6§lThe Cinder Bride',
            '§6☠ §f%v §fstood too close to the branded and paid for it',
            '§6☠ §f%v §fwas forged into the vow by §6§lVarenna',
        ],
    },
    [`${NS}:ashen_groom`]: {
        name: 'The Ashen Groom',
        melee: [
            '§b☠ §f%v §fwas struck down by §b§lCorvane, the Ashen Groom',
            '§b☠ §f%v §fdid not match their steel to §b§lthe Groom§r§f\u2019s stance',
            '§b☠ §f%v §fanswered the toll for §b§lCorvane',
        ],
        ranged: [
            '§b☠ §f%v §fwas pierced by a soul lance from §b§lThe Ashen Groom',
            '§b☠ §f%v §fwas dragged to the altar by §b§lCorvane§r§f\u2019s chains',
            '§b☠ §f%v §fwas tolled for by §b§lthe Ashen Groom',
        ],
    },
    [`${NS}:forged_blade`]: {
        name: 'Forged Blade',
        melee: ['§6☠ §f%v §fwas cut down by one of §6Varenna§f\u2019s forged blades', '§6☠ §f%v §ffailed to parry a §6Forged Blade', '§6☠ §f%v §fwas skewered by a §6Forged Blade'],
        ranged: ['§6☠ §f%v §fwas cut down by a §6Forged Blade'],
    },
    [`${NS}:mire_wisp`]: {
        name: 'Mire Wisp',
        melee: ['§a☠ §f%v §fchased a §aMire Wisp §finto the water', '§a☠ §f%v §fwas led astray by a §aMire Wisp', '§a☠ §f%v §fwas dazzled by a §aMire Wisp §fand never found the shore'],
        ranged: ['§a☠ §f%v §fwas led astray by a §aMire Wisp'],
    },
    [`${NS}:rimewalker`]: {
        name: 'Rimewalker',
        melee: ['§b☠ §f%v §fwas frozen where they stood by a §bRimewalker', '§b☠ §f%v §fwas dragged into the drift by a §bRimewalker', '§b☠ §f%v §fjoined the silent choir of a §bRimewalker'],
        ranged: ['§b☠ §f%v §fwas buried by a §bRimewalker'],
    },
    [`${NS}:hoarbone`]: {
        name: 'Hoarbone',
        melee: ['§b☠ §f%v §fwas cut down by a §bHoarbone', '§b☠ §f%v §fwas chilled to the marrow by a §bHoarbone'],
        ranged: ['§b☠ §f%v §fwas pierced by a §bHoarbone§f\u2019s frozen arrow', '§b☠ §f%v §fnever saw the §bHoarbone §fon the ridge', '§b☠ §f%v §fwas shot down in the snow by a §bHoarbone'],
    },
    [`${NS}:mirewalker`]: {
        name: 'Mirewalker',
        melee: ['§2☠ §f%v §fwas pulled under by a §2Mirewalker', '§2☠ §f%v §fwas swallowed by the mud and a §2Mirewalker', '§2☠ §f%v §fbecame fen-compost thanks to a §2Mirewalker'],
        ranged: ['§2☠ §f%v §fwas claimed by the fen'],
    },
    [`${NS}:lanternbone`]: {
        name: 'Lanternbone',
        melee: ['§e☠ §f%v §fwas struck with a §eLanternbone§f\u2019s hooked pole', '§e☠ §f%v §fwas guided to a bad end by a §eLanternbone'],
        ranged: ['§e☠ §f%v §fwas burned by a §eLanternbone§f\u2019s foxfire', '§e☠ §f%v §ffollowed a §eLanternbone§f\u2019s light too far', '§e☠ §f%v §fwas lost in the fen by the light of a §eLanternbone'],
    },
    [`${NS}:blossom_vex`]: {
        name: 'Blossom Vex',
        melee: ['§d☠ §f%v §fwas swarmed by Blossom Vexes', '§d☠ §f%v §fwas carried off by a Blossom Vex'],
        ranged: ['§d☠ §f%v §fwas pecked to pieces by petal spirits'],
    },
    [`${NS}:blossom_echo`]: {
        name: 'Veiled Echo',
        melee: ['§d☠ §f%v §fshattered a Veiled Echo too close to their face'],
        ranged: ['§d☠ §f%v §fwas caught in a burst of reflected petals'],
    },
};

const PROJECTILES = {
    [`${NS}:void_bolt`]: `${NS}:voidweaver`,
    [`${NS}:eclipse_orb`]: `${NS}:eclipse_sovereign`,
    [`${NS}:ember_spit`]: `${NS}:ashen_warg`,
    [`${NS}:bone_shard`]: `${NS}:revenant`,
    [`${NS}:web_bolt`]: `${NS}:cave_weaver`,
    [`${NS}:petal_blade`]: `${NS}:veiled_blossom`,
    [`${NS}:frost_note`]: `${NS}:frost_cantor`,
    [`${NS}:cinder_bolt`]: `${NS}:cinder_bride`,
    [`${NS}:soul_lance`]: `${NS}:ashen_groom`,
    [`${NS}:wisp_bolt`]: `${NS}:mire_lantern`,
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
