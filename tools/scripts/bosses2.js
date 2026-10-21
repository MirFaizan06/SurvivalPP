// v1.2 overworld bosses: Hollow King, Mosswood Colossus, Silkqueen.
// Summoning is condition-based (relic + ritual block + time/place), each boss has its own signature abilities.
import { world, system, EntityComponentTypes, EntityDamageCause } from '@minecraft/server';
import { NS, DIM_IDS, safe, dimOf, consumeMainhand, say, msg, spawnParticle, playSound, rand, randInt, runLater } from './util.js';
import { nearbyPlayers, titleAll, healthFrac, shockwave } from './boss.js';

const T = (n) => `${NS}:${n}`;

const BOSSES = {
    hollow_king: {
        relic: T('grave_sigil'), block: 'minecraft:bone_block', type: T('hollow_king'), name: 'Hollow King',
        hint: '§7The Grave Sigil only answers on a §fBone Block§7 at §bnight§7 (or deep underground).',
        ok: (dim, block) => dim.id === 'minecraft:overworld' && (isNight() || block.location.y < 48),
        colour: 'minecraft:endrod', sound: 'mob.wither.spawn',
        intro: ['§2The ground exhales...', '§7Something old rises from the grave'], title: ['§2§lHOLLOW KING', '§aKneel before the dead'],
        minion: [T('gravewalker'), T('revenant')],
    },
    mosswood_colossus: {
        relic: T('verdant_heart'), block: 'minecraft:moss_block', type: T('mosswood_colossus'), name: 'Mosswood Colossus',
        hint: '§7The Verdant Heart only answers on a §aMoss Block§7 under the open §esky§7 in §edaylight§7.',
        ok: (dim, block) => dim.id === 'minecraft:overworld' && !isNight() && openSky(dim, block),
        colour: 'minecraft:crop_growth_emitter', sound: 'dig.moss',
        intro: ['§2The forest holds its breath...', '§7Roots stir beneath your feet'], title: ['§2§lMOSSWOOD COLOSSUS', '§aThe forest remembers'],
        minion: [T('sporeling')],
    },
    silkqueen: {
        relic: T('silk_idol'), block: 'minecraft:web', type: T('silkqueen'), name: 'Silkqueen',
        hint: '§7The Silk Idol only answers on a §fCobweb§7 deep underground (below §bY 45§7).',
        ok: (dim, block) => dim.id === 'minecraft:overworld' && block.location.y < 45,
        colour: 'minecraft:endrod', sound: 'mob.spider.say',
        intro: ['§5The web trembles...', '§7Eight eyes open in the dark'], title: ['§5§lSILKQUEEN', '§dYou are in her web now'],
        minion: [T('cave_weaver')],
    },
};
const BY_RELIC = Object.fromEntries(Object.entries(BOSSES).map(([k, v]) => [v.relic, { key: k, ...v }]));
const BY_TYPE = Object.fromEntries(Object.entries(BOSSES).map(([k, v]) => [v.type, { key: k, ...v }]));
const state = new Map();
const lastUse = new Map();

function isNight() {
    const t = world.getTimeOfDay();
    return t >= 12800 && t <= 23200;
}

function openSky(dim, block) {
    const top = safe(() => dim.getTopmostBlock({ x: block.location.x, z: block.location.z }));
    return !!top && top.location.y <= block.location.y + 1;
}

// --------------------------------------------------------------------------------------------- helpers
function countNear(dim, loc, types, r) {
    let n = 0;
    for (const t of types) n += (safe(() => dim.getEntities({ type: t, location: loc, maxDistance: r })) || []).length;
    return n;
}

function openSpot(dim, c, r) {
    for (let i = 0; i < 14; i++) {
        const a = rand(0, Math.PI * 2), d = rand(r * 0.6, r);
        const x = Math.floor(c.x + Math.cos(a) * d), z = Math.floor(c.z + Math.sin(a) * d);
        for (let dy = 3; dy >= -4; dy--) {
            const y = Math.floor(c.y) + dy;
            const feet = safe(() => dim.getBlock({ x, y, z })), head = safe(() => dim.getBlock({ x, y: y + 1, z })), floor = safe(() => dim.getBlock({ x, y: y - 1, z }));
            if (feet && head && floor && feet.isAir && head.isAir && !floor.isAir && !floor.isLiquid) return { x: x + 0.5, y, z: z + 0.5 };
        }
    }
    return undefined;
}

function spawnMinions(boss, types, n, cap, particle) {
    const dim = boss.dimension;
    const have = countNear(dim, boss.location, types, 48);
    n = Math.min(n, Math.max(0, cap - have));
    for (let i = 0; i < n; i++) {
        const spot = openSpot(dim, boss.location, 7);
        if (!spot) continue;
        safe(() => {
            dim.spawnEntity(types[i % types.length], spot);
            for (let k = 0; k < 10; k++) spawnParticle(dim, particle, { x: spot.x + rand(-0.5, 0.5), y: spot.y + rand(0, 2), z: spot.z + rand(-0.5, 0.5) });
        }, 'spawnMinion');
    }
    return n;
}

function cast(boss, ticks = 40) {
    safe(() => boss.triggerEvent(`${NS}:cast_on`));
    runLater(ticks, () => boss.isValid && boss.triggerEvent(`${NS}:cast_off`));
}

function due(s, key, now, every, first = every) {
    if (s.next[key] === undefined) s.next[key] = now + first;
    if (now < s.next[key]) return false;
    s.next[key] = now + every;
    return true;
}

function heal(boss, amount) {
    safe(() => {
        const h = boss.getComponent(EntityComponentTypes.Health);
        h.setCurrentValue(Math.min(h.effectiveMax, h.currentValue + amount));
    });
}

function placeTempWeb(dim, loc, ticks) {
    const b = safe(() => dim.getBlock({ x: Math.floor(loc.x), y: Math.floor(loc.y), z: Math.floor(loc.z) }));
    if (!b || !b.isAir) return;
    safe(() => b.setType('minecraft:web'));
    runLater(ticks, () => { const c = dim.getBlock(b.location); if (c && c.typeId === 'minecraft:web') c.setType('minecraft:air'); });
}

// --------------------------------------------------------------------------------------------- ritual
function startRitual(cfg, block, player) {
    const dim = block.dimension;
    const c = { x: block.location.x + 0.5, y: block.location.y + 1, z: block.location.z + 0.5 };
    if ((safe(() => dim.getEntities({ type: cfg.type, location: c, maxDistance: 160 })) || []).length) {
        say(player, `§cThe ${cfg.name} already stirs nearby.`);
        return;
    }
    consumeMainhand(player, 1);
    playSound(dim, cfg.sound, c, { volume: 5, pitch: 0.6 });
    titleAll(dim, c, cfg.intro[0], cfg.intro[1]);
    let t = 0;
    const id = system.runInterval(() => {
        safe(() => {
            t += 2;
            const radius = 5 - (t / 100) * 3.5;
            for (let i = 0; i < 6; i++) {
                const a = rand(0, Math.PI * 2) + t * 0.1;
                spawnParticle(dim, cfg.colour, { x: c.x + Math.cos(a) * radius, y: c.y + rand(0, 3) + (t / 100) * 2, z: c.z + Math.sin(a) * radius });
            }
            if (t % 20 === 0) playSound(dim, 'beacon.ambient', c, { volume: 2, pitch: 0.5 + t / 140 });
            if (t === 60) safe(() => dim.spawnEntity('minecraft:lightning_bolt', { x: c.x + rand(-8, 8), y: c.y, z: c.z + rand(-8, 8) }));
            if (t >= 100) {
                system.clearRun(id);
                const boss = dim.spawnEntity(cfg.type, { x: c.x, y: c.y + 1, z: c.z });
                playSound(dim, 'mob.enderdragon.growl', c, { volume: 6, pitch: 0.8 });
                for (let i = 0; i < 24; i++) spawnParticle(dim, 'minecraft:huge_explosion_emitter', { x: c.x + rand(-2, 2), y: c.y + rand(0, 4), z: c.z + rand(-2, 2) });
                titleAll(dim, c, cfg.title[0], cfg.title[1]);
                state.set(boss.id, { next: {} });
            }
        }, 'ritual2Tick');
    }, 2);
}

// --------------------------------------------------------------------------------------------- boss brains
function phaseUpdate(boss, cfg, s, now) {
    const frac = healthFrac(boss);
    const want = frac <= 0.33 ? 2 : frac <= 0.66 ? 1 : 0;
    const cur = safe(() => boss.getProperty('ecr:phase')) ?? 0;
    if (want > cur) {
        if (cur === 0 && want === 2) safe(() => boss.triggerEvent('ecr:enter_phase_2'));
        safe(() => boss.triggerEvent(want === 2 ? 'ecr:enter_phase_3' : 'ecr:enter_phase_2'));
        s.transition = want;
    }
    return Math.max(cur, want);
}

function kingBrain(boss, s, now, phase) {
    const dim = boss.dimension, L = boss.location;
    const near = nearbyPlayers(dim, L, 6);
    if (s.transition !== undefined) {
        titleAll(dim, L, s.transition === 2 ? '§4§lTHE DEAD ANSWER' : '§2The grave deepens', s.transition === 2 ? '§7The Hollow King will not fall again' : '§7He calls his court');
        shockwave(dim, L, 12, 8, 1.6, boss);
        for (const p of nearbyPlayers(dim, L, 12)) safe(() => p.addEffect('blindness', 60, { amplifier: 0, showParticles: false }));
        spawnMinions(boss, BOSSES.hollow_king.minion, 4, 8, 'minecraft:endrod');
        playSound(dim, 'mob.wither.spawn', L, { volume: 3, pitch: 0.8 });
        s.transition = undefined;
    }
    if (near.length && due(s, 'slam', now, [170, 130, 100][phase], 80)) {
        cast(boss, 20);
        shockwave(dim, L, 7, 10 + phase * 4, 1.4 + phase * 0.2, boss);
    }
    if (due(s, 'court', now, [620, 460, 320][phase], 240)) {
        cast(boss, 50);
        const n = spawnMinions(boss, phase >= 1 ? BOSSES.hollow_king.minion : [T('gravewalker')], [2, 3, 4][phase], 8, 'minecraft:endrod');
        if (n) playSound(dim, 'mob.zombie.unfect', L, { volume: 3, pitch: 0.6 });
    }
    if (due(s, 'drain', now, [260, 200, 150][phase], 160)) {
        const victims = nearbyPlayers(dim, L, 16);
        if (victims.length) {
            cast(boss, 40);
            playSound(dim, 'mob.wither.ambient', L, { volume: 2, pitch: 0.7 });
            for (const p of victims) {
                safe(() => {
                    p.addEffect('weakness', 120, { amplifier: 0, showParticles: true });
                    p.addEffect('slowness', 60, { amplifier: 0, showParticles: false });
                    p.applyDamage(3, { cause: EntityDamageCause.magic });
                    for (let k = 0; k <= 10; k++) {
                        const f = k / 10;
                        spawnParticle(dim, 'minecraft:endrod', { x: p.location.x + (L.x - p.location.x) * f, y: p.location.y + 1.2 + (L.y + 3 - p.location.y - 1.2) * f, z: p.location.z + (L.z - p.location.z) * f });
                    }
                }, 'drain');
                heal(boss, 6);
            }
        }
    }
    if (phase === 2 && due(s, 'wail', now, 300, 120)) {
        for (const p of nearbyPlayers(dim, L, 30)) safe(() => p.addEffect('darkness', 80, { amplifier: 0, showParticles: false }));
        playSound(dim, 'mob.ghast.scream', L, { volume: 4, pitch: 0.5 });
    }
    if (now % 20 === 0) for (let i = 0; i < 6; i++) spawnParticle(dim, 'minecraft:endrod', { x: L.x + rand(-1.5, 1.5), y: L.y + rand(0.5, 4), z: L.z + rand(-1.5, 1.5) });
}

function colossusBrain(boss, s, now, phase) {
    const dim = boss.dimension, L = boss.location;
    if (s.transition !== undefined) {
        titleAll(dim, L, s.transition === 2 ? '§4§lWILDGROWTH' : '§2The Colossus awakens fully', s.transition === 2 ? '§7Everything green turns on you' : '§7Its sporelings swarm');
        shockwave(dim, L, 13, 9, 1.8, boss);
        spawnMinions(boss, BOSSES.mosswood_colossus.minion, 4, 8, 'minecraft:crop_growth_emitter');
        playSound(dim, 'mob.ravager.roar', L, { volume: 4, pitch: 0.6 });
        s.transition = undefined;
    }
    if (nearbyPlayers(dim, L, 9).length && due(s, 'slam', now, [190, 150, 115][phase], 90)) {
        cast(boss, 24);
        shockwave(dim, L, 9, 16 + phase * 5, 1.8 + phase * 0.25, boss);
    }
    if (due(s, 'roots', now, [280, 220, 160][phase], 140)) {
        const victims = nearbyPlayers(dim, L, 16);
        if (victims.length) {
            cast(boss, 30);
            playSound(dim, 'dig.grass', L, { volume: 3, pitch: 0.5 });
            for (const p of victims) {
                safe(() => {
                    p.addEffect('slowness', 70, { amplifier: 2, showParticles: true });
                    p.addEffect('poison', 60, { amplifier: 0, showParticles: true });
                    p.applyDamage(4, { cause: EntityDamageCause.contact });
                    for (let k = 0; k < 14; k++) spawnParticle(dim, 'minecraft:crop_growth_emitter', { x: p.location.x + rand(-0.8, 0.8), y: p.location.y + rand(0, 1.8), z: p.location.z + rand(-0.8, 0.8) });
                }, 'roots');
            }
        }
    }
    if (due(s, 'seeds', now, [560, 440, 330][phase], 260)) {
        cast(boss, 50);
        spawnMinions(boss, BOSSES.mosswood_colossus.minion, [2, 3, 4][phase], 8, 'minecraft:crop_growth_emitter');
        playSound(dim, 'block.sculk_shrieker.shriek', L, { volume: 1.5, pitch: 1.6 });
    }
    // bark shield: while its sporelings live, the Colossus is nearly untouchable
    if (now % 20 === 0) {
        const kids = countNear(dim, L, BOSSES.mosswood_colossus.minion, 26);
        if (kids > 0) {
            safe(() => boss.addEffect('resistance', 60, { amplifier: 2, showParticles: false }));
            for (let i = 0; i < 6; i++) spawnParticle(dim, 'minecraft:crop_growth_emitter', { x: L.x + rand(-2, 2), y: L.y + rand(0.5, 5), z: L.z + rand(-2, 2) });
            if (due(s, 'shieldmsg', now, 600, 0)) for (const p of nearbyPlayers(dim, L, 40)) say(p, '§2The Colossus is shielded by its sporelings - destroy them!');
        }
    }
    if (now % 40 === 0) for (let i = 0; i < 6; i++) spawnParticle(dim, 'minecraft:villager_happy', { x: L.x + rand(-3, 3), y: L.y + rand(0.5, 5.5), z: L.z + rand(-3, 3) });
}

function queenBrain(boss, s, now, phase) {
    const dim = boss.dimension, L = boss.location;
    if (s.transition !== undefined) {
        titleAll(dim, L, s.transition === 2 ? '§4§lBROOD MOTHER' : '§5The Silkqueen rears', s.transition === 2 ? '§7Her children pour from the walls' : '§7The web tightens');
        shockwave(dim, L, 10, 6, 1.4, boss);
        spawnMinions(boss, BOSSES.silkqueen.minion, 4, 8, 'minecraft:endrod');
        s.transition = undefined;
    }
    if (due(s, 'web', now, [210, 160, 115][phase], 100)) {
        const victims = nearbyPlayers(dim, L, 20);
        if (victims.length) {
            cast(boss, 24);
            playSound(dim, 'mob.spider.say', L, { volume: 2, pitch: 0.6 });
            for (const p of victims) {
                safe(() => {
                    placeTempWeb(dim, p.location, 400);
                    placeTempWeb(dim, { x: p.location.x, y: p.location.y + 1, z: p.location.z }, 400);
                    for (let k = 0; k < 10; k++) spawnParticle(dim, 'minecraft:endrod', { x: p.location.x + rand(-1, 1), y: p.location.y + rand(0, 2), z: p.location.z + rand(-1, 1) });
                }, 'webBurst');
            }
        }
    }
    if (due(s, 'brood', now, [500, 390, 300][phase], 220)) {
        cast(boss, 40);
        spawnMinions(boss, BOSSES.silkqueen.minion, [2, 3, 4][phase], 8, 'minecraft:endrod');
    }
    if (due(s, 'tether', now, [230, 190, 150][phase], 150)) {
        for (const p of nearbyPlayers(dim, L, 26)) {
            const dx = L.x - p.location.x, dz = L.z - p.location.z, d = Math.hypot(dx, dz);
            if (d < 10) continue;
            safe(() => {
                p.applyKnockback({ x: (dx / d) * 1.6, z: (dz / d) * 1.6 }, 0.35);
                for (let k = 0; k <= 8; k++) {
                    const f = k / 8;
                    spawnParticle(dim, 'minecraft:endrod', { x: p.location.x + dx * f, y: p.location.y + 1.2 + (L.y + 1 - p.location.y - 1.2) * f, z: p.location.z + dz * f });
                }
            }, 'tether');
        }
        playSound(dim, 'mob.spider.step', L, { volume: 2, pitch: 0.5 });
    }
    if (phase === 2 && due(s, 'venom', now, 260, 140)) {
        for (const p of nearbyPlayers(dim, L, 12)) safe(() => p.addEffect('poison', 100, { amplifier: 0, showParticles: true }));
    }
    if (nearbyPlayers(dim, L, 7).length && due(s, 'slam', now, [150, 120, 90][phase], 70)) shockwave(dim, L, 6, 7 + phase * 3, 1.3, boss);
}

const BRAINS = { hollow_king: kingBrain, mosswood_colossus: colossusBrain, silkqueen: queenBrain };

function bossTick(boss, cfg) {
    const now = system.currentTick;
    let s = state.get(boss.id);
    if (!s) {
        s = { next: {} };
        state.set(boss.id, s);
    }
    const phase = phaseUpdate(boss, cfg, s, now);
    BRAINS[cfg.key](boss, s, now, phase);
}

// --------------------------------------------------------------------------------------------- init
export function initBosses2() {
    world.beforeEvents.playerInteractWithBlock.subscribe((ev) => {
        const cfg = ev.itemStack && BY_RELIC[ev.itemStack.typeId];
        if (!cfg || ev.block.typeId !== cfg.block) return;
        ev.cancel = true;
        const player = ev.player;
        const block = ev.block;
        system.run(() => safe(() => {
            const k = player.id;
            if (system.currentTick - (lastUse.get(k) ?? -100) < 20) return;
            lastUse.set(k, system.currentTick);
            if (!cfg.ok(block.dimension, block)) {
                msg(player, cfg.hint);
                return;
            }
            startRitual(cfg, block, player);
        }, 'bossRitual2'));
    });

    system.runInterval(() => {
        for (const id of DIM_IDS) {
            for (const cfg of Object.values(BY_TYPE)) {
                const bosses = safe(() => dimOf(id).getEntities({ type: cfg.type })) || [];
                for (const b of bosses) safe(() => bossTick(b, cfg), `bossTick:${cfg.key}`);
            }
        }
    }, 10);

    world.afterEvents.entityDie.subscribe((ev) => {
        const e = ev.deadEntity;
        const cfg = BY_TYPE[e.typeId];
        if (!cfg) return;
        state.delete(e.id);
        const dim = e.dimension, loc = e.location;
        for (let i = 0; i < 40; i++) spawnParticle(dim, 'minecraft:huge_explosion_emitter', { x: loc.x + rand(-3, 3), y: loc.y + rand(0, 4), z: loc.z + rand(-3, 3) });
        playSound(dim, 'mob.enderdragon.death', loc, { volume: 5, pitch: 1.0 });
        titleAll(dim, loc, `§6§l${cfg.name} has fallen`, '§7Its spoils lie scattered');
    });
}
