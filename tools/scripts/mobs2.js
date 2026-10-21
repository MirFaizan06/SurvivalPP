// v1.2 mob / item behaviours: sporeling spores, Cave Weaver webs, Silkqueen's Fang venom, Hollow Crown, Heartwood Core.
import { world, system, EntityComponentTypes, EquipmentSlot } from '@minecraft/server';
import { NS, DIM_IDS, safe, dimOf, mainhand, consumeMainhand, say, spawnParticle, playSound, rand, runLater } from './util.js';

const SPORELING = `${NS}:sporeling`;
const WEB_BOLT = `${NS}:web_bolt`;

function sporeBurst(dim, loc, radius, nauseaTicks, poisonTicks) {
    for (let i = 0; i < 18; i++) {
        spawnParticle(dim, 'minecraft:mycelium_dust_particle', { x: loc.x + rand(-radius, radius) * 0.6, y: loc.y + rand(0.2, 1.8), z: loc.z + rand(-radius, radius) * 0.6 });
        if (i % 3 === 0) spawnParticle(dim, 'minecraft:crop_growth_emitter', { x: loc.x + rand(-radius, radius) * 0.5, y: loc.y + rand(0.2, 1.5), z: loc.z + rand(-radius, radius) * 0.5 });
    }
    playSound(dim, 'block.sculk_catalyst.bloom', loc, { volume: 1.0, pitch: 1.5 });
    const victims = safe(() => dim.getEntities({ location: loc, maxDistance: radius, excludeFamilies: ['fungus', 'boss', 'inanimate'] })) || [];
    for (const v of victims) {
        if (!safe(() => v.isValid)) continue;
        if (v.typeId === 'minecraft:player' || v.hasComponent(EntityComponentTypes.Health)) {
            safe(() => v.addEffect('nausea', nauseaTicks, { amplifier: 0, showParticles: true }));
            if (poisonTicks > 0) safe(() => v.addEffect('poison', poisonTicks, { amplifier: 0, showParticles: true }));
        }
    }
}

function placeTempWeb(dim, loc, ticks) {
    const pos = { x: Math.floor(loc.x), y: Math.floor(loc.y), z: Math.floor(loc.z) };
    const b = safe(() => dim.getBlock(pos));
    if (!b || !b.isAir) return false;
    safe(() => b.setType('minecraft:web'));
    runLater(ticks, () => {
        const c = dim.getBlock(pos);
        if (c && c.typeId === 'minecraft:web') c.setType('minecraft:air');
    });
    return true;
}

export function initMobs2() {
    // ---- sporelings: a poof when hurt, a bigger one on death, and a constant haze while they are puffing at you
    world.afterEvents.entityHurt.subscribe((ev) => {
        const e = ev.hurtEntity;
        if (e.typeId !== SPORELING) return;
        if (Math.random() < 0.4) sporeBurst(e.dimension, e.location, 2.5, 100, 0);
    });
    world.afterEvents.entityDie.subscribe((ev) => {
        const e = ev.deadEntity;
        if (e.typeId !== SPORELING) return;
        sporeBurst(e.dimension, e.location, 3.5, 160, 60);
    });
    system.runInterval(() => {
        for (const id of DIM_IDS) {
            const list = safe(() => dimOf(id).getEntities({ type: SPORELING })) || [];
            for (const e of list) {
                safe(() => {
                    if (e.getProperty('ecr:puffing') === true) sporeBurst(e.dimension, e.location, 3, 80, 0);
                }, 'sporeHaze');
            }
        }
    }, 30);

    // ---- Cave Weaver / Silkqueen web bolts leave a short-lived web where they land
    const onWeb = (dim, loc, entity) => {
        const at = entity ? entity.location : loc;
        if (!placeTempWeb(dim, at, 300)) placeTempWeb(dim, { x: at.x, y: at.y + 1, z: at.z }, 300);
    };
    world.afterEvents.projectileHitEntity.subscribe((ev) => {
        if (ev.projectile.typeId !== WEB_BOLT) return;
        const hit = safe(() => ev.getEntityHit());
        onWeb(ev.projectile.dimension, ev.location, hit && hit.entity);
    });
    world.afterEvents.projectileHitBlock.subscribe((ev) => {
        if (ev.projectile.typeId !== WEB_BOLT) return;
        onWeb(ev.projectile.dimension, ev.location, undefined);
    });

    // ---- Silkqueen's Fang: venom on hit
    world.afterEvents.entityHitEntity.subscribe((ev) => {
        const a = ev.damagingEntity;
        if (!a || a.typeId !== 'minecraft:player') return;
        const it = mainhand(/** @type {any} */ (a));
        if (it && it.typeId === `${NS}:queens_fang`) {
            safe(() => ev.hitEntity.addEffect('poison', 100, { amplifier: 1, showParticles: true }));
            safe(() => ev.hitEntity.addEffect('slowness', 40, { amplifier: 0, showParticles: false }));
        }
    });

    // ---- Hollow Crown: night vision while worn
    system.runInterval(() => {
        for (const p of world.getAllPlayers()) {
            safe(() => {
                const head = p.getComponent(EntityComponentTypes.Equippable).getEquipment(EquipmentSlot.Head);
                if (head && head.typeId === `${NS}:hollow_crown`) p.addEffect('night_vision', 260, { amplifier: 0, showParticles: false });
            }, 'crown');
        }
    }, 100);

    // ---- Heartwood Core: right-click to consume for a burst of vitality
    world.afterEvents.itemUse.subscribe((ev) => {
        if (!ev.itemStack || ev.itemStack.typeId !== `${NS}:colossus_core`) return;
        const p = /** @type {any} */ (ev.source);
        consumeMainhand(p, 1);
        safe(() => {
            p.addEffect('absorption', 2400, { amplifier: 4, showParticles: true });
            p.addEffect('regeneration', 400, { amplifier: 1, showParticles: true });
            p.addEffect('resistance', 1200, { amplifier: 0, showParticles: true });
        }, 'coreEffects');
        for (let i = 0; i < 24; i++) spawnParticle(p.dimension, 'minecraft:crop_growth_emitter', { x: p.location.x + rand(-0.8, 0.8), y: p.location.y + rand(0, 2), z: p.location.z + rand(-0.8, 0.8) });
        playSound(p.dimension, 'random.levelup', p.location, { volume: 1, pitch: 0.7 });
        say(p, '§2The heartwood floods you with vitality');
    });
}
