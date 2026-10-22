// Themed boss health bars drawn with our own font glyphs (RP font/glyph_E4.png) on the action bar.
// This does not depend on JSON-UI bindings, so it shows up on every client even when the UI overlay (ui/hud_screen.json) is ignored.
// Every skin owns 8 characters from U+E400 + 8 * index: +0 left emblem, +1 right emblem, +2..+6 bar cell (empty .. full).
import { world, system, EntityComponentTypes } from '@minecraft/server';
import { NS, DIM_IDS, safe } from './util.js';

/** boss entity id -> skin index (the order of gen_ui.SKINS, kept in sync by lint4) */
export const SKINS = ['eclipse_sovereign', 'hollow_king', 'mosswood_colossus', 'silkqueen', 'veiled_blossom', 'frost_cantor', 'mire_lantern'];
const BOSSES = Object.fromEntries(SKINS.map((s, i) => [`${NS}:${s}`, i]));
const BASE = 0xE400;
const CELLS = 20;
const RANGE = 64;
const OFF_KEY = 'ecr:bossbar_off';

/** which players currently have one of our bars on their action bar */
const shown = new Set();

export function barText(skin, frac) {
    const b = BASE + skin * 8;
    const total = Math.round(Math.max(0, Math.min(1, frac)) * CELLS * 4);
    let s = '§f' + String.fromCodePoint(b);
    for (let i = 0; i < CELLS; i++) s += String.fromCodePoint(b + 2 + Math.max(0, Math.min(4, total - i * 4)));
    return s + String.fromCodePoint(b + 1);
}

function fraction(e) {
    const h = safe(() => e.getComponent(EntityComponentTypes.Health));
    if (!h) return 1;
    const max = h.effectiveMax || h.defaultValue || 1;
    return h.currentValue / max;
}

function tick() {
    const off = safe(() => world.getDynamicProperty(OFF_KEY)) === true;
    const want = new Map();
    if (!off) {
        for (const dimId of DIM_IDS) {
            const dim = safe(() => world.getDimension(dimId));
            if (!dim) continue;
            for (const typeId of Object.keys(BOSSES)) {
                const list = safe(() => dim.getEntities({ type: typeId })) || [];
                for (const boss of list) {
                    const frac = fraction(boss);
                    for (const p of safe(() => dim.getPlayers({ location: boss.location, maxDistance: RANGE })) || []) {
                        const prev = want.get(p.id);
                        const d = Math.hypot(p.location.x - boss.location.x, p.location.z - boss.location.z);
                        if (!prev || d < prev.d) want.set(p.id, { p, d, text: barText(BOSSES[typeId], frac) });
                    }
                }
            }
        }
    }
    for (const { p, text } of want.values()) {
        safe(() => p.onScreenDisplay.setActionBar(text), 'bossBar');
        shown.add(p.id);
    }
    for (const id of [...shown]) {
        if (want.has(id)) continue;
        shown.delete(id);
        const p = world.getAllPlayers().find((q) => q.id === id);
        if (p) safe(() => p.onScreenDisplay.setActionBar(''), 'bossBarClear');
    }
}

export function initBossBar() {
    system.runInterval(tick, 5);
    // /scriptevent ecr:bossbar on | off   - the action-bar boss bar can be switched off for the whole world
    system.afterEvents.scriptEventReceive.subscribe((ev) => {
        if (ev.id !== `${NS}:bossbar`) return;
        const m = ev.message.trim().toLowerCase();
        if (m !== 'on' && m !== 'off') return;
        safe(() => world.setDynamicProperty(OFF_KEY, m === 'off'));
        const p = /** @type {any} */ (ev.sourceEntity);
        if (p && p.typeId === 'minecraft:player') safe(() => p.sendMessage(`§d✿ §fAction-bar boss bars are now ${m}.`));
    });
}
