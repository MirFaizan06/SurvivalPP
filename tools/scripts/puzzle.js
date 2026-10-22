// Exploration puzzles of Chapters III and IV: Verse Stones, the chimes of the Frozen Cathedral, the Cantor's Lectern, the sconces of the Drowned Chapel,
// the Marsh Altar and the Lore Tablets - plus the Tuning Fork that hums towards what you are looking for.
import { world, system, BlockVolume, EquipmentSlot, EntityComponentTypes } from '@minecraft/server';
import { ActionFormData } from '@minecraft/server-ui';
import { NS, safe, msg, say, mainhand, getState, setState, playSound, spawnParticle, rand } from './util.js';
import { getStory, saveStory, advanceRoad, toastTo } from './story.js';
import { spawnCantor, CANTOR } from './cantor.js';
import { spawnMorwen, MORWEN } from './morwen.js';

const FORK = `${NS}:tuning_fork`;
const LANTERN = `${NS}:keepers_lantern`;
const SUN = ['dawn', 'zenith', 'dusk', 'midnight'];
const SCONCE = ['eye', 'star', 'moon'];

const VERSES = [
    '§bDawn wakes the choir, pale gold on the ice;\nthe first note is laid like a stone on the snow.',
    '§bNoon stands on the peak and the song stands tall;\nnothing is hidden, nothing is held.',
    '§bDusk gathers the voices and folds them in blue;\nwhat was sung aloud is sung low.',
    '§bMidnight is the silence between two breaths -\nand there a Keeper learns what she is guarding.',
];
const VERSE_HINT = ['§7(Dawn - where the sun\'s road begins.)', '§7(Zenith - the sun at its highest.)', '§7(Dusk - the sun going down.)', '§7(Midnight - the sun beneath the world.)'];

/** the 12 lore tablets (block state ecr:text); structures choose which ones they hold */
export const TABLETS = [
    ["Wayfarer's Note I", "I stopped here to rest my feet and my courage. The First Keeper begged me to turn back. I am going on anyway.\n\nIf you are reading this, so are you."],
    ["Wayfarer's Note II", "The Seals are not locks. They are wounds that learned to hold still.\n\nKeep that in mind when a Keeper weeps."],
    ["Wayfarer's Note III", "Eight stood at the Cracking. Seven took Shards. I took only the page.\n\nI never understood why until I heard Ysolde sing it."],
    ["The Choir's Rule", "A cantor sings so the Shard may sleep. The day the song ends, the Seal opens.\n\nSo the cantor may not rest, may not stop, and may not be thanked."],
    ['Fen Note I', "The eye must watch before the star can guide."],
    ['Fen Note II', "The moon leads home, and comes last.\n\nLight them as you would leave a lantern for a lost friend."],
    ["Morwen's Lament", "I hung a light in every window of the fen. Each night one more traveller followed it home.\n\nThen the Shard learned to hang lights of its own."],
    ["The Smith's Warning", "Alloys of rime keep a blade sharp in the cold. Alloys of wisp-light keep a blade honest in the dark.\n\nNeither will keep you alive. Carry both."],
    ['Echo on the Stone', "The Sovereign took his Shard into himself to spare the others. I think that is the bravest and most foolish thing anyone ever did.\n\n- W."],
    ['The Frozen Cathedral', "Raised by the Third Keeper's pilgrims: the pipes breathe whatever the Cantor sings.\n\nWhen the pipes go silent, run."],
    ['The Drowned Chapel', "The sconces were lit by those who came home.\n\nThe ones who did not are the wisps."],
    ['Last line (smudged)', "Four Seals behind me and her lamp still ahead. If the light in the fen was hers, I do not want to put it out."],
];

// ------------------------------------------------------------------------------------------- helpers
function shownForm(p, title, body) {
    new ActionFormData().title(`§d${title}`).body(`§f${body}`).button('Close').show(p).catch(() => { /* busy */ });
}

function isNight() {
    const t = world.getTimeOfDay();
    return t >= 12800 && t <= 23200;
}

function holds(p, id) {
    return safe(() => {
        const eq = p.getComponent(EntityComponentTypes.Equippable);
        for (const slot of [EquipmentSlot.Mainhand, EquipmentSlot.Offhand]) {
            const it = eq.getEquipment(slot);
            if (it && it.typeId === id) return true;
        }
        return false;
    }) === true;
}

function burst(dim, loc, id = `${NS}:rime_burst`, n = 1) {
    for (let i = 0; i < n; i++) spawnParticle(dim, id, { x: loc.x + 0.5 + rand(-0.4, 0.4), y: loc.y + 1.2 + rand(0, 0.8), z: loc.z + 0.5 + rand(-0.4, 0.4) });
}

// ------------------------------------------------------------------------------------------- Verse Stones
function readVerse(p, block) {
    const v = Number(getState(block, 'ecr:verse')) || 0;
    const st = getStory(p);
    const fresh = !st.verses[v];
    st.verses[v] = true;
    const heard = st.verses.filter(Boolean).length;
    saveStory(p, st);
    burst(block.dimension, block.location, `${NS}:frost_note`, 2);
    playSound(block.dimension, 'note.harp', block.location, { volume: 1.2, pitch: [0.84, 1.0, 0.75, 0.56][v] });
    shownForm(p, `Verse ${v + 1}: ${['Dawn', 'Zenith', 'Dusk', 'Midnight'][v]}`, `${VERSES[v]}\n\n${VERSE_HINT[v]}\n\n§7Verses heard: ${heard}/4${fresh ? '' : ' (heard before)'}`);
    if (heard === 4 && st.c3 === 0 && st.step >= 5) {
        system.runTimeout(() => {
            msg(p, '§b❄ §fThe four verses are one lock. §7Four chimes hang where the song was written - strike them in the order of the sun\'s road.');
            advanceRoad(p, getStory(p), 'c3', 1);
        }, 20);
    } else if (heard === 4 && st.step < 5) {
        msg(p, "§7You have heard every verse, but the Wayfarer's road is not yet open to you. Finish Chapter I first - the verses will wait.");
    }
}

// ------------------------------------------------------------------------------------------- Chimes
function strike(p, block, idx) {
    const dim = block.dimension;
    const st = getStory(p);
    if (st.c3 < 1) {
        say(p, '§bThe chime hums, but no song answers. §7Your journal has not led you here yet.');
        playSound(dim, 'note.chime', block.location, { volume: 1, pitch: 0.7 });
        return;
    }
    if (st.c3 >= 2) {
        playSound(dim, 'note.bell', block.location, { volume: 1.6, pitch: [0.84, 1.0, 1.26, 0.67][idx] });
        burst(dim, block.location, `${NS}:frost_note`, 1);
        return;
    }
    const seq = st.chimes || [];
    if (idx === seq.length) {                                            // the next note of the sun's road
        seq.push(idx);
        st.chimes = seq;
        playSound(dim, 'note.bell', block.location, { volume: 2, pitch: [0.84, 1.0, 1.26, 0.67][idx] });
        burst(dim, block.location, `${NS}:frost_note`, 3);
        say(p, `§b♪ ${seq.length}/4`);
        saveStory(p, st);
        if (seq.length === 4) {
            system.runTimeout(() => {
                const cur = getStory(p);
                cur.chimes = [];
                saveStory(p, cur);
                advanceRoad(p, cur, 'c3', 2);
                for (let i = 0; i < 40; i++) spawnParticle(dim, `${NS}:snow_swirl`, { x: block.location.x + rand(-6, 6), y: block.location.y + rand(0, 6), z: block.location.z + rand(-6, 6) });
                playSound(dim, 'beacon.activate', block.location, { volume: 2, pitch: 0.8 });
                msg(p, "§b❄ §fThe pipes of the cathedral draw breath. §7Somewhere beneath the vault, a lectern wakes. Bring the Tuning Fork.");
            }, 20);
        }
    } else {                                                             // discord
        st.chimes = [];
        saveStory(p, st);
        playSound(dim, 'random.glass', block.location, { volume: 2, pitch: 0.5 });
        burst(dim, block.location, `${NS}:rime_burst`, 3);
        safe(() => {
            p.applyDamage(3, {});
            p.addEffect('slowness', 80, { amplifier: 1, showParticles: false });
        }, 'discord');
        say(p, '§c✖ A wrong note. §7The chimes fall silent - begin the sun\'s road again.');
    }
}

// ------------------------------------------------------------------------------------------- Lectern
function lectern(p, block) {
    const dim = block.dimension;
    const st = getStory(p);
    if (st.c3 < 2) { say(p, "§bThe lectern is cold. §7Its song has not been sung yet."); return; }
    if (!holds(p, FORK)) { say(p, "§bThe lectern waits for a fork to give it the note. §7(Hold the Cantor's Tuning Fork.)"); return; }
    const c = { x: block.location.x + 0.5, y: block.location.y + 1, z: block.location.z + 0.5 };
    if ((safe(() => dim.getEntities({ type: CANTOR, location: c, maxDistance: 200 })) || []).length) { say(p, '§bThe Frost Cantor already sings.'); return; }
    msg(p, '§b❄ §fYou strike the fork against the lectern. The note does not fade.');
    for (const q of dim.getPlayers({ location: c, maxDistance: 40 })) safe(() => q.onScreenDisplay.setTitle('§b...', { subtitle: '§7a song resumes', fadeInDuration: 10, stayDuration: 40, fadeOutDuration: 10 }));
    system.runTimeout(() => safe(() => spawnCantor(dim, c), 'spawnCantor'), 50);
}

// ------------------------------------------------------------------------------------------- Sconces + Marsh Altar
function resetSconces(dim, centre) {
    for (let dx = -14; dx <= 14; dx++) for (let dy = -6; dy <= 8; dy++) for (let dz = -14; dz <= 14; dz++) {
        const b = safe(() => dim.getBlock({ x: Math.floor(centre.x) + dx, y: Math.floor(centre.y) + dy, z: Math.floor(centre.z) + dz }));
        if (b && b.typeId.startsWith(`${NS}:sconce_`)) setState(b, 'ecr:lit', 0);
    }
}

function sconce(p, block, idx) {
    const dim = block.dimension;
    const st = getStory(p);
    if (st.c4 < 1) { say(p, '§aThe sconce is cold and wet. §7Your journal has not led you here yet.'); return; }
    if (!holds(p, LANTERN)) { say(p, "§aOnly the Keeper's Lantern can kindle this."); return; }
    if (st.c4 >= 2) { say(p, '§aThe sconce already burns.'); return; }
    const seq = st.sconces || [];
    if (getState(block, 'ecr:lit') === 1) { say(p, '§7Already lit.'); return; }
    if (idx === seq.length) {
        seq.push(idx);
        st.sconces = seq;
        saveStory(p, st);
        setState(block, 'ecr:lit', 1);
        playSound(dim, 'item.firecharge.use', block.location, { volume: 1.2, pitch: 0.8 });
        burst(dim, block.location, `${NS}:wisp_glow`, 3);
        say(p, `§e✦ ${seq.length}/3`);
        if (seq.length === 3) {
            system.runTimeout(() => {
                const cur = getStory(p);
                cur.sconces = [];
                saveStory(p, cur);
                advanceRoad(p, cur, 'c4', 2);
                playSound(dim, 'beacon.activate', block.location, { volume: 2, pitch: 0.6 });
                msg(p, "§a✦ §fAll three sconces burn. §7Somewhere in the chapel an altar opens its hands. Return at night with the Keeper's Lantern.");
            }, 20);
        }
    } else {
        st.sconces = [];
        saveStory(p, st);
        resetSconces(dim, block.location);
        playSound(dim, 'mob.warden.heartbeat', block.location, { volume: 2, pitch: 0.6 });
        safe(() => {
            p.addEffect('darkness', 100, { amplifier: 0, showParticles: false });
            for (let i = 0; i < 3; i++) dim.spawnEntity(`${NS}:mire_wisp`, { x: p.location.x + rand(-3, 3), y: p.location.y + 1.5, z: p.location.z + rand(-3, 3) });
        }, 'sconceWrong');
        say(p, '§8The flames gutter out. §7Wrong order - the fen stirs.');
    }
}

function marshAltar(p, block) {
    const dim = block.dimension;
    const st = getStory(p);
    if (st.c4 < 2) { say(p, '§aThe altar is silent. §7Light the three sconces first.'); return; }
    if (!holds(p, LANTERN)) { say(p, "§aThe altar waits for the Keeper's Lantern."); return; }
    if (!isNight()) { say(p, "§aThe lantern stays dim. §7She only answers under the night sky."); return; }
    const biome = safe(() => dim.getBiome(block.location).id) || '';
    if (!/swamp/.test(biome)) { say(p, '§aThe altar has lost its fen.'); return; }
    const c = { x: block.location.x + 0.5, y: block.location.y + 1, z: block.location.z + 0.5 };
    if ((safe(() => dim.getEntities({ type: MORWEN, location: c, maxDistance: 200 })) || []).length) { say(p, '§aThe Mire Lantern already walks.'); return; }
    msg(p, "§a✦ §fYou raise the lantern over the altar. §7Every light in the fen leans towards you.");
    for (const q of dim.getPlayers({ location: c, maxDistance: 40 })) safe(() => q.onScreenDisplay.setTitle('§a...', { subtitle: '§7the lights lean closer', fadeInDuration: 10, stayDuration: 40, fadeOutDuration: 10 }));
    system.runTimeout(() => safe(() => spawnMorwen(dim, c), 'spawnMorwen'), 50);
}

// ------------------------------------------------------------------------------------------- registration
export function registerPuzzleBlocks(reg) {
    reg.registerCustomComponent(`${NS}:verse_stone`, { onPlayerInteract: (e) => safe(() => readVerse(e.player, e.block), 'verse') });
    reg.registerCustomComponent(`${NS}:chime`, {
        onPlayerInteract: (e) => safe(() => {
            const idx = SUN.findIndex((n) => e.block.typeId === `${NS}:chime_${n}`);
            if (idx >= 0) strike(e.player, e.block, idx);
        }, 'chime'),
    });
    reg.registerCustomComponent(`${NS}:choir_lectern`, { onPlayerInteract: (e) => safe(() => lectern(e.player, e.block), 'lectern') });
    reg.registerCustomComponent(`${NS}:sconce`, {
        onPlayerInteract: (e) => safe(() => {
            const idx = SCONCE.findIndex((n) => e.block.typeId === `${NS}:sconce_${n}`);
            if (idx >= 0) sconce(e.player, e.block, idx);
        }, 'sconce'),
    });
    reg.registerCustomComponent(`${NS}:marsh_altar`, { onPlayerInteract: (e) => safe(() => marshAltar(e.player, e.block), 'marshAltar') });
    reg.registerCustomComponent(`${NS}:lore_tablet`, {
        onPlayerInteract: (e) => safe(() => {
            const i = (Number(getState(e.block, 'ecr:text')) || 0) % TABLETS.length;
            const [title, text] = TABLETS[i];
            shownForm(e.player, title, text);
            playSound(e.block.dimension, 'random.pop', e.block.location, { volume: 0.6, pitch: 0.8 });
        }, 'tablet'),
    });
}

// ------------------------------------------------------------------------------------------- the Tuning Fork
const cooldown = new Map();
const KINDS = {
    verse: { ids: [`${NS}:verse_stone`], text: 'a verse still unsung' },
    cathedral: { ids: SUN.map((n) => `${NS}:chime_${n}`), text: 'the Frozen Cathedral' },
};

/** looks for `ids` in loaded chunks around the player, ring by ring, spread over several ticks */
export function scan(p, ids, done) {
    const dim = p.dimension;
    const cx = Math.floor(p.location.x / 16), cz = Math.floor(p.location.z / 16);
    const cells = [];
    const R = 9;
    for (let dx = -R; dx <= R; dx++) for (let dz = -R; dz <= R; dz++) cells.push([dx, dz, dx * dx + dz * dz]);
    cells.sort((a, b) => a[2] - b[2]);
    let i = 0;
    const id = system.runInterval(() => {
        for (let n = 0; n < 12 && i < cells.length; n++, i++) {
            const [dx, dz] = cells[i];
            const x0 = (cx + dx) * 16, z0 = (cz + dz) * 16;
            const hit = safe(() => dim.containsBlock(new BlockVolume({ x: x0, y: -60, z: z0 }, { x: x0 + 15, y: 320, z: z0 + 15 }), { includeTypes: ids }, false));
            if (hit) { system.clearRun(id); done({ x: x0 + 8, z: z0 + 8 }); return; }
        }
        if (i >= cells.length) { system.clearRun(id); done(undefined); }
    }, 1);
}

export function compass(dx, dz) {
    const a = (Math.atan2(dx, -dz) * 180) / Math.PI;
    return ['north', 'north-east', 'east', 'south-east', 'south', 'south-west', 'west', 'north-west'][Math.round(((a + 360) % 360) / 45) % 8];
}

function useFork(p) {
    const now = system.currentTick;
    if ((cooldown.get(p.id) || 0) > now) { say(p, '§7The fork is still ringing.'); return; }
    cooldown.set(p.id, now + 60);
    const st = getStory(p);
    let kind = null;
    if (st.c3 === 0 || (st.c3 === undefined)) kind = st.verses.every(Boolean) ? 'cathedral' : 'verse';
    else if (st.c3 === 1) kind = 'cathedral';
    else if (st.c3 === 2) { say(p, '§bThe fork hums towards the lectern in the cathedral\'s heart. §7Strike it against the lectern.'); return; }
    if (!kind) { say(p, "§bThe fork hums softly. §7Nothing in the snow still needs singing."); return; }
    if (st.step < 5) { say(p, '§bThe fork stays dull. §7Its road has not opened yet.'); return; }
    playSound(p.dimension, 'note.harp', p.location, { volume: 1, pitch: 1.5 });
    say(p, '§b♪ The fork rings, listening...');
    scan(p, KINDS[kind].ids, (hit) => {
        if (!p.isValid) return;
        if (!hit) { say(p, `§bThe fork falls silent. §7Nothing sings within ${9 * 16} blocks - try walking through more snow.`); return; }
        const dx = hit.x - p.location.x, dz = hit.z - p.location.z;
        const d = Math.round(Math.hypot(dx, dz) / 10) * 10;
        say(p, `§b♪ ${KINDS[kind].text}: about ${d} blocks to the ${compass(dx, dz)}.`);
        playSound(p.dimension, 'note.bell', p.location, { volume: 1.2, pitch: d < 60 ? 1.6 : 1.0 });
    });
}

export function initPuzzle() {
    world.afterEvents.itemUse.subscribe((ev) => {
        if (ev.itemStack && ev.itemStack.typeId === FORK) safe(() => useFork(/** @type {any} */ (ev.source)), 'fork');
    });
}
