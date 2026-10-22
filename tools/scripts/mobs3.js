// v1.6 undead of the high snow and the fen: Rimewalker, Hoarbone, Mirewalker, Lanternbone and the Mire Wisp.
// Atmosphere (snow drifting off the frozen dead, lights hanging over the fen's dead), death bursts, and a few small rules.
import { world, system } from '@minecraft/server';
import { NS, DIM_IDS, safe, dimOf, spawnParticle, playSound, rand } from './util.js';

const COLD = [`${NS}:rimewalker`, `${NS}:hoarbone`];
const FEN = [`${NS}:mirewalker`, `${NS}:lanternbone`];
const WISP = `${NS}:mire_wisp`;

export function initMobs3() {
    // ambience around the living ones (only near players, kept cheap)
    system.runInterval(() => {
        for (const p of world.getAllPlayers()) {
            safe(() => {
                const dim = p.dimension;
                for (const type of [...COLD, ...FEN, WISP]) {
                    for (const e of dim.getEntities({ type, location: p.location, maxDistance: 32 })) {
                        const L = e.location;
                        if (COLD.includes(type)) spawnParticle(dim, `${NS}:snow_swirl`, { x: L.x + rand(-0.5, 0.5), y: L.y + rand(0.5, 2), z: L.z + rand(-0.5, 0.5) });
                        else if (type === `${NS}:lanternbone`) spawnParticle(dim, `${NS}:lantern_mote`, { x: L.x + rand(-0.4, 0.4), y: L.y + rand(1, 2), z: L.z + rand(-0.4, 0.4) });
                        else if (type === WISP) spawnParticle(dim, `${NS}:wisp_glow`, { x: L.x, y: L.y + 0.5, z: L.z });
                        else spawnParticle(dim, `${NS}:wisp_glow`, { x: L.x + rand(-0.6, 0.6), y: L.y + rand(0.2, 1.8), z: L.z + rand(-0.6, 0.6) });
                    }
                }
            }, 'mobs3Ambient');
        }
    }, 30);

    world.afterEvents.entityDie.subscribe((ev) => {
        const e = ev.deadEntity;
        const id = e.typeId;
        const dim = e.dimension, L = e.location;
        if (COLD.includes(id)) {
            for (let i = 0; i < 2; i++) spawnParticle(dim, `${NS}:rime_burst`, { x: L.x, y: L.y + 1, z: L.z });
            playSound(dim, 'random.glass', L, { volume: 0.8, pitch: 1.4 });
        } else if (FEN.includes(id)) {
            spawnParticle(dim, `${NS}:wisp_burst`, { x: L.x, y: L.y + 1, z: L.z });
            // the light of the fen's dead rises as a wisp, now and then
            if (Math.random() < (id === `${NS}:lanternbone` ? 0.3 : 0.15)) safe(() => dim.spawnEntity(WISP, { x: L.x, y: L.y + 1.2, z: L.z }), 'riseWisp');
        } else if (id === WISP) {
            for (let i = 0; i < 2; i++) spawnParticle(dim, `${NS}:wisp_burst`, { x: L.x, y: L.y + 0.5, z: L.z });
            playSound(dim, 'random.glass', L, { volume: 0.7, pitch: 1.8 });
        }
    });
}
