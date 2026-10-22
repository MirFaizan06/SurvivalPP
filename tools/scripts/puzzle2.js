// Exploration puzzles of Roads V and VI (the Burning Deep): the three offering pedestals of the Forge of Vows, the Bridal Anvil, the Toll Tower's
// memory game (the tower tolls a pattern of bells - ring it back), the Grave Altar, the Ember Tablets, and the Ember Compass.
import { world, system, EquipmentSlot, EntityComponentTypes, ItemStack } from '@minecraft/server';
import { ActionFormData } from '@minecraft/server-ui';
import { NS, safe, msg, say, getState, setState, playSound, spawnParticle, rand, randInt } from './util.js';
import { getStory, saveStory, advanceRoad, giveTo, roadOpen } from './story.js';
import { scan, compass } from './puzzle.js';
import { spawnBride, BRIDE } from './varenna.js';
import { spawnGroom, GROOM } from './corvane.js';

const RING = `${NS}:cinder_ring`;
const KEY = `${NS}:grave_key`;
const COMPASS = `${NS}:ember_compass`;
/** the vow, in the order it was spoken: gold, flame, tears */
const VOWS = [['gold', 'minecraft:gold_ingot', 'a Gold Ingot'], ['flame', 'minecraft:blaze_rod', 'a Blaze Rod'], ['tears', 'minecraft:ghast_tear', 'a Ghast Tear']];

export const EMBER_TABLETS = [
    ['The First Vow', "\"I give you gold, that you may never want.\"\n\nThe words are cut deep into the stone, and the stone has been scorched around them."],
    ['The Second Vow', "\"I give you flame, that you may never be cold.\"\n\nA blackened blaze rod has been laid across the tablet."],
    ['The Third Vow', "\"I give you tears, that you may never grieve alone.\"\n\nSpeak the vows in the order they were spoken, and the pedestals will answer. Speak them out of turn, and the forge will remember."],
    ["Varenna's Forge", "I made the Seal into a ring so that it could not be taken from my hand without taking the hand.\n\nIt was the only wedding ring in the Burning Deep. It was the only thing I could think of that I would never put down."],
    ['The Wedding That Never Ended', "The ceremony was interrupted at the vows. Nobody told the bride.\n\nShe has been standing at the anvil ever since, waiting for the word that finishes the sentence."],
    ['The Ashen Aisle', "Do not strike the anvil with an empty hand.\n\nThe ring she wears has a twin. If you carry the one she lost, she will know you are a guest."],
    ['The Tolling', "The bells ring for every one who did not return. Listen, then answer in kind.\n\nThe tower will test your memory three times. It is kinder than the valley."],
    ["Corvane's Letter I", "My love - the bells are rung wrong tonight; they ring without hands. I think the valley is learning to grieve on its own.\n\nI will wait by the door. You will not be long. You never were."],
    ["Corvane's Letter II", "My love - I have been standing at the altar for what the bells call a year. They are not counting right. They never did.\n\nThe veil you left me is the only warm thing here."],
    ["The Groom's Oath", "I swore I would stand here until she came. It did not occur to me that I might not be able to leave.\n\nThe Shard is patient. It said it would wait with me."],
    ["Wayfarer's Note IV", "Her ring is on his finger. His veil is on her arm. They have been each other's Seals for longer than the valley has had a name.\n\nTo free one, you have to break the other. I have not found a way around that. I am still looking."],
    ["Wayfarer's Note V", "Both of them knew my name. Neither of them could say how.\n\nI wrote it down once, in my own hand, and the ink ran. I think the Eclipse has been reading over my shoulder since the beginning."],
];

function holds(p, id) {
    return safe(() => {
        const eq = p.getComponent(EntityComponentTypes.Equippable);
        const it = eq.getEquipment(EquipmentSlot.Mainhand);
        return !!it && it.typeId === id;
    }) === true;
}

function heldId(p) {
    return safe(() => p.getComponent(EntityComponentTypes.Equippable).getEquipment(EquipmentSlot.Mainhand)?.typeId);
}

function take(p, id) {
    safe(() => {
        const eq = p.getComponent(EntityComponentTypes.Equippable);
        const it = eq.getEquipment(EquipmentSlot.Mainhand);
        if (!it || it.typeId !== id) return;
        if (it.amount <= 1) eq.setEquipment(EquipmentSlot.Mainhand, undefined);
        else { it.amount -= 1; eq.setEquipment(EquipmentSlot.Mainhand, it); }
    });
}

function burst(dim, loc, id, n = 1) {
    for (let i = 0; i < n; i++) spawnParticle(dim, id, { x: loc.x + 0.5 + rand(-0.4, 0.4), y: loc.y + 1.2 + rand(0, 0.8), z: loc.z + 0.5 + rand(-0.4, 0.4) });
}

function form(p, title, body) {
    new ActionFormData().title(`§6${title}`).body(`§f${body}`).button('Close').show(p).catch(() => { /* busy */ });
}

// ------------------------------------------------------------------------------------------- Road V: the vows
function resetPedestals(dim, centre) {
    for (let dx = -16; dx <= 16; dx++) for (let dy = -3; dy <= 4; dy++) for (let dz = -16; dz <= 16; dz++) {
        const b = safe(() => dim.getBlock({ x: Math.floor(centre.x) + dx, y: Math.floor(centre.y) + dy, z: Math.floor(centre.z) + dz }));
        if (b && b.typeId.startsWith(`${NS}:pedestal_`)) setState(b, 'ecr:offered', 0);
    }
}

function pedestal(p, block, idx) {
    const dim = block.dimension;
    const st = getStory(p);
    if (!roadOpen(st, 'c5')) { say(p, '§6The pedestal is cold. §7Its road has not opened for you yet.'); return; }
    if (st.c5 >= 1) { say(p, '§6The pedestal hums quietly. §7The vows are already spoken.'); return; }
    const held = heldId(p);
    const want = VOWS[idx];
    if (!held || !VOWS.some((v) => v[1] === held)) { say(p, `§6The pedestal waits for an offering. §7(This one asks for ${want[2]}.)`); return; }
    const seq = st.vows || [];
    if (held === want[1] && idx === seq.length) {                           // the right offering, in the right place, at the right time
        take(p, held);
        seq.push(idx);
        st.vows = seq;
        saveStory(p, st);
        setState(block, 'ecr:offered', 1);
        playSound(dim, 'random.anvil_use', block.location, { volume: 1.2, pitch: 1.0 + idx * 0.2 });
        burst(dim, block.location, `${NS}:ember_spark`, 6);
        say(p, `§6🔥 ${seq.length}/3 vows spoken`);
        if (seq.length === 3) {
            system.runTimeout(() => {
                const cur = getStory(p);
                cur.vows = [];
                saveStory(p, cur);
                advanceRoad(p, cur, 'c5', 1);
                giveTo(p, RING, 1);
                if (!countCompass(p)) giveTo(p, COMPASS, 1);
                playSound(dim, 'beacon.activate', block.location, { volume: 2, pitch: 0.6 });
                msg(p, '§6🔥 §fThe three flames join into one. A ring of black gold rises from the anvil-shaped flue: §6the Cinder Ring§f. §7The Ember Compass will lead you to the chapel.');
            }, 20);
        }
        return;
    }
    // out of turn or the wrong offering: the forge remembers - everything already offered is returned, the player is burned
    for (const i of seq) giveTo(p, VOWS[i][1], 1);
    st.vows = [];
    saveStory(p, st);
    resetPedestals(dim, block.location);
    safe(() => { p.applyDamage(5, {}); p.setOnFire(4, true); }, 'vowBurn');
    playSound(dim, 'mob.blaze.shoot', block.location, { volume: 2, pitch: 0.5 });
    burst(dim, block.location, `${NS}:forge_burst`, 1);
    say(p, '§c✖ Out of turn. §7The forge remembers - your offerings are returned. Gold, then flame, then tears.');
}

function countCompass(p) {
    return safe(() => {
        const inv = p.getComponent(EntityComponentTypes.Inventory).container;
        for (let i = 0; i < inv.size; i++) { const it = inv.getItem(i); if (it && it.typeId === COMPASS) return 1; }
        return 0;
    }) || 0;
}

function bridalAnvil(p, block) {
    const dim = block.dimension;
    const st = getStory(p);
    if (st.c5 < 1) { say(p, "§6The anvil is cold. §7The vows have not been spoken - find the Forge of Vows."); return; }
    if (st.c5 === 1) {
        advanceRoad(p, st, 'c5', 2);
        playSound(dim, 'random.anvil_land', block.location, { volume: 1.4, pitch: 0.7 });
        burst(dim, block.location, `${NS}:ember_spark`, 6);
        msg(p, "§6🔥 §fThe anvil has a hollow in the shape of a ring. §7Come back with the Cinder Ring in your hand - and be ready.");
        return;
    }
    if (!holds(p, RING)) { say(p, '§6The anvil waits for the Cinder Ring.'); return; }
    const c = { x: block.location.x + 0.5, y: block.location.y + 1, z: block.location.z + 0.5 };
    if ((safe(() => dim.getEntities({ type: BRIDE, location: c, maxDistance: 200 })) || []).length) { say(p, '§6The Cinder Bride is already here.'); return; }
    msg(p, '§6🔥 §fYou set the ring on the anvil. It rings once, like a bell.');
    for (const q of dim.getPlayers({ location: c, maxDistance: 40 })) safe(() => q.onScreenDisplay.setTitle('§6...', { subtitle: '§7the forge is lit', fadeInDuration: 10, stayDuration: 40, fadeOutDuration: 10 }));
    system.runTimeout(() => safe(() => spawnBride(dim, c), 'spawnBride'), 50);
}

// ------------------------------------------------------------------------------------------- Road VI: the toll
const games = new Map();                       // player id -> { seq, idx, round, listening }
const BELL_PITCH = [0.7, 0.9, 1.15, 1.5];

function findBells(dim, core) {
    const out = {};
    for (let dx = -7; dx <= 7; dx++) for (let dy = -3; dy <= 4; dy++) for (let dz = -7; dz <= 7; dz++) {
        const b = safe(() => dim.getBlock({ x: Math.floor(core.x) + dx, y: Math.floor(core.y) + dy, z: Math.floor(core.z) + dz }));
        const m = b && /^ecr:toll_bell_(\d)$/.exec(b.typeId);
        if (m) out[Number(m[1])] = b.location;
    }
    return out;
}

function ringBell(dim, loc, n, vol = 2) {
    playSound(dim, 'block.bell.hit', loc, { volume: vol, pitch: BELL_PITCH[n] });
    for (let i = 0; i < 3; i++) spawnParticle(dim, `${NS}:soul_flame`, { x: loc.x + 0.5 + rand(-0.3, 0.3), y: loc.y + 1.1 + rand(0, 0.6), z: loc.z + 0.5 + rand(-0.3, 0.3) });
}

function startRound(p, core) {
    const g = games.get(p.id);
    if (!g) return;
    g.round += 1;
    const len = 2 + g.round;
    g.seq = Array.from({ length: len }, () => randInt(0, 3));
    g.idx = 0;
    g.listening = false;
    const bells = findBells(p.dimension, core);
    g.bells = bells;
    say(p, `§b🔔 Round ${g.round}/3 - listen...`);
    g.seq.forEach((n, i) => system.runTimeout(() => safe(() => {
        if (!p.isValid || games.get(p.id) !== g) return;
        if (bells[n]) ringBell(p.dimension, bells[n], n);
    }), 24 + i * 16));
    system.runTimeout(() => {
        if (!p.isValid || games.get(p.id) !== g) return;
        g.listening = true;
        g.deadline = system.currentTick + len * 50 + 120;
        say(p, '§b🔔 Now ring them back.');
    }, 24 + len * 16 + 6);
}

function tollCore(p, block) {
    const dim = block.dimension;
    const st = getStory(p);
    if (!roadOpen(st, 'c6')) { say(p, '§bThe core is silent. §7Its road has not opened for you yet.'); return; }
    if (st.c6 >= 1) { ringBell(dim, block.location, 1, 1.5); say(p, '§bThe tower has already told you what it knows.'); return; }
    if (games.get(p.id)) { say(p, '§7The tower is already tolling.'); return; }
    games.set(p.id, { seq: [], idx: 0, round: 0, listening: false });
    msg(p, '§b🔔 §fThe core hums. The tower will toll a pattern - ring it back. Three rounds, each longer.');
    startRound(p, block.location);
}

function tollBell(p, block, n) {
    const dim = block.dimension;
    const g = games.get(p.id);
    ringBell(dim, block.location, n, 1.6);
    if (!g || !g.listening) return;
    if (system.currentTick > g.deadline) { failToll(p, g, "too slow"); return; }
    if (g.seq[g.idx] === n) {
        g.idx += 1;
        if (g.idx >= g.seq.length) {
            g.listening = false;
            if (g.round >= 3) {
                games.delete(p.id);
                const st = getStory(p);
                system.runTimeout(() => {
                    advanceRoad(p, getStory(p), 'c6', 1);
                    giveTo(p, KEY, 1);
                    if (!countCompass(p)) giveTo(p, COMPASS, 1);
                    playSound(dim, 'beacon.activate', block.location, { volume: 2, pitch: 0.7 });
                    msg(p, '§b🔔 §fThe tower falls silent. Something drops from the belfry: §bthe Grave Key§f. §7The Ember Compass will lead you to the hall.');
                }, 20);
            } else {
                say(p, '§a✔ Right.');
                system.runTimeout(() => startRound(p, block.location), 40);
            }
        }
    } else {
        failToll(p, g, 'the wrong bell');
    }
}

function failToll(p, g, why) {
    games.delete(p.id);
    safe(() => { p.applyDamage(4, {}); p.addEffect('wither', 60, { amplifier: 0, showParticles: false }); }, 'tollFail');
    playSound(p.dimension, 'mob.wither.hurt', p.location, { volume: 1.4, pitch: 0.8 });
    say(p, `§c✖ ${why}. §7The tower falls silent - touch the core to begin again.`);
}

function graveAltar(p, block) {
    const dim = block.dimension;
    const st = getStory(p);
    if (st.c6 < 1) { say(p, '§bThe altar is silent. §7The bells have not been answered - find the Toll Tower.'); return; }
    if (st.c6 === 1) {
        advanceRoad(p, st, 'c6', 2);
        playSound(dim, 'block.bell.use', block.location, { volume: 1.6, pitch: 0.6 });
        burst(dim, block.location, `${NS}:soul_flame`, 6);
        msg(p, '§b🔔 §fThe altar has a hollow the shape of a key. §7Come back with the Grave Key in your hand - and be ready.');
        return;
    }
    if (!holds(p, KEY)) { say(p, '§bThe altar waits for the Grave Key.'); return; }
    const c = { x: block.location.x + 0.5, y: block.location.y + 1, z: block.location.z + 0.5 };
    if ((safe(() => dim.getEntities({ type: GROOM, location: c, maxDistance: 200 })) || []).length) { say(p, '§bThe Ashen Groom already stands.'); return; }
    msg(p, '§b🔔 §fYou set the key into the altar and turn it. Every bell in the valley answers once.');
    for (const q of dim.getPlayers({ location: c, maxDistance: 40 })) safe(() => q.onScreenDisplay.setTitle('§b...', { subtitle: '§7the groom has waited long enough', fadeInDuration: 10, stayDuration: 40, fadeOutDuration: 10 }));
    system.runTimeout(() => safe(() => spawnGroom(dim, c), 'spawnGroom'), 50);
}

// ------------------------------------------------------------------------------------------- registration
export function registerNetherBlocks(reg) {
    reg.registerCustomComponent(`${NS}:pedestal`, {
        onPlayerInteract: (e) => safe(() => {
            const idx = VOWS.findIndex((v) => e.block.typeId === `${NS}:pedestal_${v[0]}`);
            if (idx >= 0) pedestal(e.player, e.block, idx);
        }, 'pedestal'),
    });
    reg.registerCustomComponent(`${NS}:bridal_anvil`, { onPlayerInteract: (e) => safe(() => bridalAnvil(e.player, e.block), 'bridalAnvil') });
    reg.registerCustomComponent(`${NS}:toll_core`, { onPlayerInteract: (e) => safe(() => tollCore(e.player, e.block), 'tollCore') });
    reg.registerCustomComponent(`${NS}:toll_bell`, {
        onPlayerInteract: (e) => safe(() => {
            const m = /^ecr:toll_bell_(\d)$/.exec(e.block.typeId);
            if (m) tollBell(e.player, e.block, Number(m[1]));
        }, 'tollBell'),
    });
    reg.registerCustomComponent(`${NS}:grave_altar`, { onPlayerInteract: (e) => safe(() => graveAltar(e.player, e.block), 'graveAltar') });
    reg.registerCustomComponent(`${NS}:ember_tablet`, {
        onPlayerInteract: (e) => safe(() => {
            const i = (Number(getState(e.block, 'ecr:text')) || 0) % EMBER_TABLETS.length;
            form(e.player, EMBER_TABLETS[i][0], EMBER_TABLETS[i][1]);
            playSound(e.block.dimension, 'random.pop', e.block.location, { volume: 0.6, pitch: 0.7 });
        }, 'emberTablet'),
    });
}

// ------------------------------------------------------------------------------------------- the Ember Compass
const cooldown = new Map();

function compassKind(st) {
    if (roadOpen(st, 'c5') && st.c5 < 2) return st.c5 === 0 ? { ids: [`${NS}:pedestal_gold`], text: 'the Forge of Vows' } : { ids: [`${NS}:bridal_anvil`], text: 'the Ashen Chapel' };
    if (roadOpen(st, 'c6') && st.c6 < 2) return st.c6 === 0 ? { ids: [`${NS}:toll_core`], text: 'the Toll Tower' } : { ids: [`${NS}:grave_altar`], text: 'the Hollow Hall' };
    return null;
}

export function initPuzzle2() {
    world.afterEvents.itemUse.subscribe((ev) => {
        if (!ev.itemStack || ev.itemStack.typeId !== COMPASS) return;
        const p = /** @type {any} */ (ev.source);
        safe(() => {
            const now = system.currentTick;
            if ((cooldown.get(p.id) || 0) > now) { say(p, '§7The compass is still settling.'); return; }
            cooldown.set(p.id, now + 60);
            const st = getStory(p);
            const k = compassKind(st);
            if (!k) { say(p, '§6The compass turns slowly and points at nothing.'); return; }
            if (p.dimension.id !== 'minecraft:nether') { say(p, '§6The compass only wakes in the Burning Deep (the Nether).'); return; }
            playSound(p.dimension, 'block.bell.use', p.location, { volume: 1, pitch: 1.4 });
            say(p, '§6🔥 The compass flickers, listening...');
            scan(p, k.ids, (hit) => {
                if (!p.isValid) return;
                if (!hit) { say(p, `§6The compass stays dark. §7Nothing within ${9 * 16} blocks - try another part of the Nether.`); return; }
                const dx = hit.x - p.location.x, dz = hit.z - p.location.z;
                const d = Math.round(Math.hypot(dx, dz) / 10) * 10;
                say(p, `§6🔥 ${k.text}: about ${d} blocks to the ${compass(dx, dz)}.`);
                playSound(p.dimension, 'note.bell', p.location, { volume: 1.2, pitch: d < 60 ? 1.6 : 1.0 });
            });
        }, 'emberCompass');
    });
    // a game left unfinished when the player leaves
    world.afterEvents.playerLeave.subscribe((ev) => { games.delete(ev.playerId); });
}
