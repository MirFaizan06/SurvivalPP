// Eclipse Sovereign: summoning ritual, phase logic, signature attacks; plus mob / weapon combat hooks
import { world, system, EntityComponentTypes, EntityDamageCause } from '@minecraft/server';
import { NS, DIM_IDS, safe, dimOf, mainhand, consumeMainhand, isCreative, say, msg, spawnParticle, playSound, rand, randInt, runLater } from './util.js';

const BOSS = `${NS}:eclipse_sovereign`;
const MINION = `${NS}:voidweaver`;
const SIGIL = `${NS}:eclipse_sigil`;
const state = new Map();   // boss id -> runtime data

export function nearbyPlayers(dim, loc, r) {
    return safe(() => dim.getPlayers({ location: loc, maxDistance: r }), 'nearbyPlayers') || [];
}

export function titleAll(dim, loc, title, sub) {
    for (const p of nearbyPlayers(dim, loc, 96)) {
        safe(() => p.onScreenDisplay.setTitle(title, { subtitle: sub, fadeInDuration: 10, stayDuration: 50, fadeOutDuration: 20 }));
    }
}

// ----------------------------------------------------------------------------------------------- ritual
export function startRitual(altar, player) {
    const dim = altar.dimension;
    const it = mainhand(player);
    if (!it || it.typeId !== SIGIL) return;
    const existing = safe(() => dim.getEntities({ type: BOSS, location: altar.center(), maxDistance: 160 })) || [];
    if (existing.length > 0) {
        say(player, '§cThe Sovereign already stirs nearby.');
        return;
    }
    consumeMainhand(player, 1);
    const c = { x: altar.location.x + 0.5, y: altar.location.y + 1, z: altar.location.z + 0.5 };
    playSound(dim, 'mob.wither.spawn', c, { volume: 6, pitch: 0.6 });
    titleAll(dim, c, '§5The sky grows dark...', '§7The Eclipse awakens');
    let t = 0;
    const id = system.runInterval(() => {
        safe(() => {
            t += 2;
            const radius = 4 - (t / 120) * 2.5;
            for (let i = 0; i < 6; i++) {
                const a = rand(0, Math.PI * 2) + t * 0.08;
                spawnParticle(dim, 'minecraft:endrod', { x: c.x + Math.cos(a) * radius, y: c.y + rand(0, 3.5) + (t / 120) * 2, z: c.z + Math.sin(a) * radius });
            }
            if (t % 20 === 0) playSound(dim, 'beacon.ambient', c, { volume: 2, pitch: 0.5 + t / 160 });
            if (t === 50 || t === 90) {
                const a = rand(0, Math.PI * 2);
                safe(() => dim.spawnEntity('minecraft:lightning_bolt', { x: c.x + Math.cos(a) * 9, y: c.y, z: c.z + Math.sin(a) * 9 }));
            }
            if (t >= 120) {
                system.clearRun(id);
                const boss = dim.spawnEntity(BOSS, { x: c.x, y: c.y + 2, z: c.z });
                playSound(dim, 'mob.enderdragon.growl', c, { volume: 6, pitch: 0.7 });
                for (let i = 0; i < 40; i++) spawnParticle(dim, 'minecraft:huge_explosion_emitter', { x: c.x + rand(-2, 2), y: c.y + rand(0, 4), z: c.z + rand(-2, 2) });
                titleAll(dim, c, '§5§lECLIPSE SOVEREIGN', '§dThe void remembers');
                for (const p of nearbyPlayers(dim, c, 24)) safe(() => p.addEffect('darkness', 100, { amplifier: 0, showParticles: false }));
                state.set(boss.id, { next: { slam: system.currentTick + 120, summon: system.currentTick + 400 } });
            }
        }, 'ritualTick');
    }, 2);
}

// ----------------------------------------------------------------------------------------------- boss brain
export function healthFrac(e) {
    const h = e.getComponent(EntityComponentTypes.Health);
    return h ? h.currentValue / h.effectiveMax : 1;
}

export function shockwave(dim, loc, radius, damage, kb, boss) {
    for (let i = 0; i < 36; i++) {
        const a = (i / 36) * Math.PI * 2;
        spawnParticle(dim, 'minecraft:large_explosion', { x: loc.x + Math.cos(a) * radius * 0.7, y: loc.y + 0.4, z: loc.z + Math.sin(a) * radius * 0.7 });
    }
    playSound(dim, 'random.explode', loc, { volume: 3, pitch: 0.6 });
    for (const p of nearbyPlayers(dim, loc, radius)) {
        safe(() => {
            p.applyDamage(damage, { cause: EntityDamageCause.entityExplosion, damagingEntity: boss });
            const dx = p.location.x - loc.x, dz = p.location.z - loc.z;
            const d = Math.max(0.5, Math.hypot(dx, dz));
            p.applyKnockback({ x: (dx / d) * kb, z: (dz / d) * kb }, 0.7);
        }, 'shock');
    }
}

function summonMinions(boss, n) {
    const dim = boss.dimension;
    const nearby = safe(() => dim.getEntities({ type: MINION, location: boss.location, maxDistance: 48 })) || [];
    n = Math.min(n, Math.max(0, 7 - nearby.length));
    safe(() => boss.triggerEvent(`${NS}:cast_on`));
    runLater(50, () => boss.isValid && boss.triggerEvent(`${NS}:cast_off`));
    for (let i = 0; i < n; i++) {
        const a = (i / Math.max(1, n)) * Math.PI * 2 + rand(0, 1);
        const p = { x: boss.location.x + Math.cos(a) * 6, y: boss.location.y, z: boss.location.z + Math.sin(a) * 6 };
        safe(() => {
            const m = dim.spawnEntity(MINION, p);
            for (let k = 0; k < 10; k++) spawnParticle(dim, 'minecraft:endrod', { x: p.x + rand(-0.5, 0.5), y: p.y + rand(0, 2), z: p.z + rand(-0.5, 0.5) });
            return m;
        });
    }
    if (n > 0) playSound(dim, 'mob.endermen.portal', boss.location, { volume: 3, pitch: 0.5 });
}

function bossTick(boss) {
    const now = system.currentTick;
    let s = state.get(boss.id);
    if (!s) {
        s = { next: { slam: now + 100, summon: now + 300 } };
        state.set(boss.id, s);
    }
    const frac = healthFrac(boss);
    const want = frac <= 0.33 ? 2 : frac <= 0.66 ? 1 : 0;
    const cur = safe(() => boss.getProperty('ecr:phase')) ?? 0;
    const dim = boss.dimension;
    if (want > cur) {
        const target = want === 2 ? 'ecr:enter_phase_3' : 'ecr:enter_phase_2';
        if (cur === 0 && want === 2) safe(() => boss.triggerEvent('ecr:enter_phase_2'));
        safe(() => boss.triggerEvent(target));
        shockwave(dim, boss.location, 14, 10, 1.6, boss);
        summonMinions(boss, want === 2 ? 5 : 3);
        titleAll(dim, boss.location, want === 2 ? '§4§lTOTAL ECLIPSE' : '§5The eclipse deepens', want === 2 ? '§7There is no light left' : '§7Void weavers answer the call');
        playSound(dim, 'mob.enderdragon.growl', boss.location, { volume: 5, pitch: 0.55 });
        s.next.slam = now + 60;
        s.next.summon = now + 240;
    }
    const phase = Math.max(cur, want);
    // ground slam when someone stands close
    if (now >= s.next.slam) {
        const close = nearbyPlayers(dim, boss.location, 8);
        if (close.length) {
            safe(() => boss.triggerEvent(`${NS}:cast_off`));
            shockwave(dim, boss.location, 8, 12 + phase * 4, 1.5 + phase * 0.25, boss);
            s.next.slam = now + [170, 130, 95][phase];
        }
    }
    // reinforcements
    if (phase >= 1 && now >= s.next.summon) {
        summonMinions(boss, phase === 2 ? 3 : 2);
        s.next.summon = now + [0, 460, 320][phase];
    }
    // phase 3: void storm drains light around the fight
    if (phase === 2 && now % 100 === 0) {
        for (const p of nearbyPlayers(dim, boss.location, 40)) safe(() => p.addEffect('darkness', 80, { amplifier: 0, showParticles: false }));
    }
    // aura
    if (now % 20 === 0) {
        const L = boss.location;
        for (let i = 0; i < 8; i++) spawnParticle(dim, 'minecraft:endrod', { x: L.x + rand(-2.5, 2.5), y: L.y + rand(0.5, 6), z: L.z + rand(-2.5, 2.5) });
    }
}

export function initBoss() {
    system.runInterval(() => {
        for (const id of DIM_IDS) {
            const bosses = safe(() => dimOf(id).getEntities({ type: BOSS })) || [];
            for (const b of bosses) safe(() => bossTick(b), 'bossTick');
        }
    }, 10);

    world.afterEvents.entityDie.subscribe((ev) => {
        const e = ev.deadEntity;
        if (e.typeId !== BOSS) return;
        state.delete(e.id);
        const dim = e.dimension;
        const loc = e.location;
        for (let i = 0; i < 60; i++) spawnParticle(dim, 'minecraft:huge_explosion_emitter', { x: loc.x + rand(-3, 3), y: loc.y + rand(0, 6), z: loc.z + rand(-3, 3) });
        playSound(dim, 'mob.enderdragon.death', loc, { volume: 6, pitch: 0.8 });
        titleAll(dim, loc, '§d§lThe Eclipse Sovereign has fallen', '§7Its core remains...');
    });
}

// ----------------------------------------------------------------------------------------------- combat hooks
export function initCombat() {
    world.afterEvents.entityHitEntity.subscribe((ev) => {
        const a = ev.damagingEntity;
        const t = ev.hitEntity;
        if (!a || !t) return;
        if (a.typeId === `${NS}:ashen_warg`) {
            safe(() => t.setOnFire(6, true));
            return;
        }
        if (a.typeId !== 'minecraft:player') return;
        const it = mainhand(a);
        if (!it) return;
        const id = it.typeId;
        if (/^ecr:pyrelite_(sword|axe)$/.test(id)) safe(() => t.setOnFire(4, true));
        else if (/^ecr:eclipsite_(sword|axe)$/.test(id)) safe(() => t.addEffect('wither', 80, { amplifier: 0 }));
        else if (/^ecr:azurite_(sword|axe)$/.test(id)) safe(() => t.addEffect('slowness', 50, { amplifier: 0 }));
    });
}
