// v1.6 gear: Rimesteel / Glacite / Wispsteel melee effects and the two boss weapons.
//   Frostsong (Frost Cantor): hits chill; right-click = Resonance, a cone of frozen sound that shoves and slows.
//   Mirelight Scythe (Mire Lantern): hits sweep neighbouring monsters and sip life; right-click = Beacon of the Lost, which reveals every monster nearby.
import { world, system, EntityComponentTypes, EntityDamageCause } from '@minecraft/server';
import { NS, safe, mainhand, say, spawnParticle, playSound, rand } from './util.js';

const FROSTSONG = `${NS}:frostsong`;
const SCYTHE = `${NS}:mirelight_scythe`;
const cool = new Map();
const hits = new Map();

function ready(p, key, ticks) {
    const k = `${p.id}|${key}`;
    const now = system.currentTick;
    if ((cool.get(k) || 0) > now) return false;
    cool.set(k, now + ticks);
    return true;
}

function isMonster(e) {
    return safe(() => e.getComponent(EntityComponentTypes.TypeFamily).hasTypeFamily('monster')) === true;
}

function resonance(p) {
    const dim = p.dimension;
    const v = safe(() => p.getViewDirection()) || { x: 0, y: 0, z: 1 };
    const flat = Math.hypot(v.x, v.z) || 1;
    const dir = { x: v.x / flat, z: v.z / flat };
    playSound(dim, 'beacon.power', p.location, { volume: 1.4, pitch: 1.8 });
    for (let r = 1.5; r <= 8; r += 1.5) {
        for (let k = -3; k <= 3; k++) {
            const a = Math.atan2(dir.z, dir.x) + k * 0.2;
            spawnParticle(dim, `${NS}:frost_note`, { x: p.location.x + Math.cos(a) * r, y: p.location.y + 1.2, z: p.location.z + Math.sin(a) * r });
        }
    }
    for (const e of safe(() => dim.getEntities({ location: p.location, maxDistance: 8 })) || []) {
        if (e.id === p.id) continue;
        const dx = e.location.x - p.location.x, dz = e.location.z - p.location.z;
        const d = Math.hypot(dx, dz) || 1;
        if ((dx / d) * dir.x + (dz / d) * dir.z < 0.35) continue;                      // outside the ~70 degree cone
        safe(() => {
            e.applyDamage(6, { cause: EntityDamageCause.entityAttack, damagingEntity: p });
            e.applyKnockback({ x: (dx / d) * 1.4, z: (dz / d) * 1.4 }, 0.5);
            e.addEffect('slowness', 80, { amplifier: 2, showParticles: false });
        }, 'resonanceHit');
    }
}

function beacon(p) {
    const dim = p.dimension;
    playSound(dim, 'mob.evocation_illager.prepare_summon', p.location, { volume: 1.2, pitch: 1.2 });
    for (let k = 0; k < 24; k++) {
        const a = (k / 24) * Math.PI * 2;
        spawnParticle(dim, `${NS}:wisp_glow`, { x: p.location.x + Math.cos(a) * 6, y: p.location.y + 0.4, z: p.location.z + Math.sin(a) * 6 });
    }
    let n = 0;
    for (const e of safe(() => dim.getEntities({ location: p.location, maxDistance: 14 })) || []) {
        if (e.id === p.id || !isMonster(e)) continue;
        safe(() => e.addEffect('glowing', 160, { amplifier: 0, showParticles: false }));
        n++;
    }
    safe(() => p.addEffect('night_vision', 200, { amplifier: 0, showParticles: false }));
    say(p, n ? `§a✦ The lantern-light finds ${n} hidden thing${n > 1 ? 's' : ''}.` : '§a✦ The lantern-light finds nothing near.');
}

export function initGear() {
    world.afterEvents.itemUse.subscribe((ev) => {
        const it = ev.itemStack;
        if (!it) return;
        const p = /** @type {any} */ (ev.source);
        if (it.typeId === FROSTSONG && ready(p, 'resonance', 140)) safe(() => resonance(p), 'resonance');
        else if (it.typeId === SCYTHE && ready(p, 'beacon', 400)) safe(() => beacon(p), 'beacon');
        else if ((it.typeId === FROSTSONG || it.typeId === SCYTHE)) say(p, '§7The weapon is still humming.');
    });
    world.afterEvents.entityHitEntity.subscribe((ev) => {
        const a = ev.damagingEntity, t = ev.hitEntity;
        if (!a || !t || a.typeId !== 'minecraft:player') return;
        const it = mainhand(/** @type {any} */ (a));
        if (!it) return;
        const id = it.typeId;
        if (/^ecr:rimesteel_(sword|axe)$/.test(id)) safe(() => t.addEffect('slowness', 40, { amplifier: 0, showParticles: false }));
        else if (/^ecr:glacite_(sword|axe)$/.test(id)) {
            safe(() => t.addEffect('slowness', 60, { amplifier: 1, showParticles: false }));
            if (Math.random() < 0.25) spawnParticle(t.dimension, `${NS}:rime_burst`, { x: t.location.x, y: t.location.y + 1, z: t.location.z });
        } else if (/^ecr:wispsteel_(sword|axe)$/.test(id)) {
            safe(() => { t.addEffect('weakness', 60, { amplifier: 0, showParticles: false }); t.addEffect('glowing', 80, { amplifier: 0, showParticles: false }); });
        } else if (id === FROSTSONG) {
            safe(() => t.addEffect('slowness', 80, { amplifier: 1, showParticles: false }));
            spawnParticle(t.dimension, `${NS}:frost_note`, { x: t.location.x, y: t.location.y + 1.4, z: t.location.z });
        } else if (id === SCYTHE) {
            const dim = t.dimension;
            for (const e of safe(() => dim.getEntities({ location: t.location, maxDistance: 2.6 })) || []) {
                if (e.id === t.id || e.id === a.id || !isMonster(e)) continue;
                safe(() => e.applyDamage(4, { cause: EntityDamageCause.entityAttack, damagingEntity: a }), 'scytheSweep');
            }
            spawnParticle(dim, `${NS}:wisp_burst`, { x: t.location.x, y: t.location.y + 1, z: t.location.z });
            const n = (hits.get(a.id) || 0) + 1;
            hits.set(a.id, n);
            if (n % 3 === 0) safe(() => {
                const h = a.getComponent(EntityComponentTypes.Health);
                h.setCurrentValue(Math.min(h.effectiveMax, h.currentValue + 1));
                spawnParticle(a.dimension, `${NS}:lantern_mote`, { x: a.location.x, y: a.location.y + 1.2, z: a.location.z });
            }, 'scytheSip');
        }
    });
}
