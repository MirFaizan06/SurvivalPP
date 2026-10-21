// Eclipsed Realms: Chronicles of the Seven Seals  -  by Tech Bytes Design
import { world, system } from '@minecraft/server';
import { registerBlockComponents, initBlockEvents } from './blocks.js';
import { initStasis, onRodUse } from './stasis.js';
import { initMining } from './mining.js';
import { initTools } from './tools.js';
import { initBoss, initCombat } from './boss.js';
import { initArmor } from './armor.js';
import { initSanctum } from './sanctum.js';
import { initDeaths } from './deaths.js';
import { initCrops, initFoodEffects } from './crops.js';
import { initBosses2 } from './bosses2.js';
import { initMobs2 } from './mobs2.js';
import { initStory } from './story.js';
import { initBlossom } from './blossom.js';
import { initDiag } from './diag.js';

// Custom block components must be registered during the startup event.
system.beforeEvents.startup.subscribe((ev) => {
    try {
        registerBlockComponents(ev.blockComponentRegistry);
    } catch (e) {
        console.warn(`[Eclipsed Realms] component registration failed: ${e}`);
    }
});

// Everything else needs world.beforeEvents / system.runInterval, which are NOT available during early execution,
// so initialisation is deferred by one tick.  Each module is isolated: one failure never stops the others.
function initAll() {
    /** @type {[string, () => void][]} */
    const modules = [
        ['blocks', initBlockEvents], ['mining', initMining], ['tools', initTools], ['stasis', initStasis],
        ['boss', initBoss], ['combat', initCombat], ['armor', initArmor], ['sanctum', initSanctum], ['deaths', initDeaths], ['crops', initCrops], ['foods', initFoodEffects], ['bosses2', initBosses2], ['mobs2', initMobs2], ['story', initStory], ['blossom', initBlossom], ['diag', initDiag],
        ['rod', () => world.afterEvents.itemUse.subscribe((ev) => {
            if (ev.itemStack && ev.itemStack.typeId === 'minecraft:fishing_rod') onRodUse(ev.source, ev.itemStack);
        })],
    ];
    const failed = [];
    for (const [name, fn] of modules) {
        try {
            fn();
        } catch (e) {
            failed.push(name);
            console.warn(`[Eclipsed Realms] module '${name}' failed to start: ${e && e.stack ? e.stack : e}`);
        }
    }
    console.warn(`[Eclipsed Realms] ready - Tech Bytes Design${failed.length ? ` (failed modules: ${failed.join(', ')})` : ''}`);
}

system.runTimeout(initAll, 1);
