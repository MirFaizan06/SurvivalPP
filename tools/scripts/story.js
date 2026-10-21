// The story: Wayfarer's Journal, chapter progress, lore pages, the offering step and the Blossom Altar ritual.
// Adding a chapter = append to STEPS (and PAGES); progress is stored per player in the dynamic property ecr:story.
import { world, system, ItemStack, EquipmentSlot, EntityComponentTypes } from '@minecraft/server';
import { ActionFormData } from '@minecraft/server-ui';
import { NS, DIM_IDS, safe, dimOf, mainhand, say, msg, playSound, spawnParticle, rand } from './util.js';
import { startHanaeRitual } from './blossom.js';

const JOURNAL = `${NS}:wayfarers_journal`;
const MIRROR = `${NS}:veiled_mirror`;
const KEY = 'ecr:story';
const GIVEN = 'ecr:journal_given';
const CHERRY = 'minecraft:cherry_grove';

// ------------------------------------------------------------------------------------------- content
/** @type {[string, number, string][]} */
const OFFERINGS = [['minecraft:pink_petals', 16, 'Pink Petals'], [`${NS}:silk_gland`, 1, 'Silk Gland'], [`${NS}:hollow_bone`, 1, 'Hollow Bone'], [`${NS}:spore_cluster`, 1, 'Spore Cluster']];
const KILLS = { gravewalker: 3, cave_weaver: 2 };
/** the Eclipse's taint also spreads into ordinary monsters inside a cherry grove: this many of them also complete step 2 */
const GROVE_KILLS = 8;
const COMMON_MONSTERS = new Set(['minecraft:zombie', 'minecraft:skeleton', 'minecraft:spider', 'minecraft:cave_spider', 'minecraft:husk', 'minecraft:stray', 'minecraft:drowned', 'minecraft:zombie_villager', 'minecraft:witch', 'minecraft:creeper', 'minecraft:enderman', 'minecraft:slime', 'minecraft:bogged', 'minecraft:parched']);

/** one entry per step; `chapter` groups them for the journal header */
const STEPS = [
    { chapter: 'Chapter I - The Veiled Blossom', title: 'The First Whisper',
      clue: "The Wayfarer's first entry:\n§o'Where pink snow never melts and the trees never stop blooming, the First Keeper sleeps. Walk beneath the blossoms. Listen.'§r\n\n§dTravel to a Cherry Grove and linger there." },
    { chapter: 'Chapter I - The Veiled Blossom', title: 'Tainted Roots',
      clue: "§o'Something is wrong with the grove. Hollow things crawl up from the roots wearing the Eclipse's taint. Cut the sickness back.'§r\n\n§dSlay the Hollow Court's servants." },
    { chapter: 'Chapter I - The Veiled Blossom', title: 'Offerings',
      clue: "§o'She will not speak to strangers. Bring her what the sickness stole - a little of each of its children.'§r\n\n§dGather the offerings, hold them, and press 'Present offerings'." },
    { chapter: 'Chapter I - The Veiled Blossom', title: 'The Hidden Shrine',
      clue: "§o'The offerings became a Veiled Mirror - she sees through glass, never through eyes. Her shrine hides among the oldest blossoms: a red gate, a path of stone, an altar of pink marble.'§r\n\n§dFind Hanae's Shrine in a Cherry Grove and touch the Blossom Altar." },
    { chapter: 'Chapter I - The Veiled Blossom', title: 'The Veil',
      clue: "§o'The altar is awake. Come back at night, mirror in hand, and call her. She tests everyone who comes. Do not be afraid of what you see in the glass.'§r\n\n§dAt night, in a Cherry Grove, use the Veiled Mirror on the Blossom Altar." },
    { chapter: 'Chapter II - The Second Seal', title: 'The Edge of the World',
      clue: "§o'The First Seal is ours... but her plea will not leave me. The Second Keeper stands at the edge of the world - the Eclipse Sovereign, in the End. He knew my name when I found him.'§r\n\n§dForge an Eclipse Sigil, find an Eclipse Altar, and defeat the Eclipse Sovereign." },
];
const COMPLETE = 6;

/** lore pages: unlocked by progress ('at' = step) or by defeating a boss ('boss') */
const PAGES = {
    prologue: { title: 'Prologue - The Hollow Sun', at: 0, text: "Before the Eclipse there was one sky, and one dawn that never ended.\n\nThen the Hollow Sun rose and swallowed the First Dawn whole. The world cracked into three Realms - the Overworld, the Burning Deep and the Void Shore - and the Eclipse's power shattered into Seven Shards.\n\nSeven Keepers bound the Shards into Seven Seals and swore to guard them.\n\nThis journal was begun by the Wayfarer, who set out to find every Seal and end the Eclipse. Its pages fill only as you walk her road." },
    seals: { title: 'The Seven Seals', at: 1, text: "A Seal is a prison and a lock in one. Break one carelessly and the Shard bleeds into the one who guards it.\n\nThe Wayfarer numbered them:\n  I   - the Blossom, in the Cherry Grove\n  II  - the Eclipse, at the edge of the End\n  III-VII - ... (the ink is smeared)\n\nHer notes grow shorter after the second." },
    ores: { title: 'Dawn, Blood and Shadow', at: 2, text: "Azurite is the First Dawn, frozen into crystal where it fell.\nPyrelite is the Eclipse's blood, cooled in the Burning Deep.\nEclipsite is its shadow, turned to stone on the Void Shore.\n\nCarry all three and the Eclipse will notice." },
    hollow_court: { title: 'The Hollow Court', at: 1, text: "The Eclipse does not only guard. It collects.\n\nGravewalkers, Revenants, Cave Weavers and Sporelings are its Hollow Court - things that once lived and were taught to serve a sun that gives no light.\n\nAbove them rule the Hollow Lords. They keep no Seals, but they hoard the relics that were once keys to the Keepers' shrines." },
    hollow_king: { title: 'The Hollow King', boss: 'hollow_king', text: "A mortal king who bargained with the Eclipse to cheat death. It kept its word: he cannot die, and he cannot rest.\n\nHis court wanders the graveyards, serving a throne that no longer exists.\n\nA Hollow Lord - a casualty of the Eclipse, not a Keeper." },
    mosswood_colossus: { title: 'The Mosswood Colossus', boss: 'mosswood_colossus', text: "The forest's last Greenwarden. When the Eclipse withered the sun, its roots drank shadow instead and the guardian woke wrong.\n\nThe Sporelings are the seeds it can no longer plant.\n\nA Hollow Lord." },
    silkqueen: { title: 'The Silkqueen', boss: 'silkqueen', text: "The Mother of Threads. She spun webs to hold the cracking world together. The Eclipse taught her that everything caught is hers.\n\nHer Cave Weavers are her unfinished lullabies.\n\nA Hollow Lord." },
    veiled_blossom: { title: 'Hanae, Keeper of the First Seal', boss: 'veiled_blossom', text: "Miko of the Cherry Grove. She bound the First Shard with her own life, and veiled her face so the Shard could not see through her eyes.\n\nHer Echoes are the pilgrims she could not save. She never meant to kill anyone who came - only to make them turn back.\n\n§o\"The ending was never meant to be reached.\"§r\n\nShe gave you the Seal anyway." },
    eclipse_sovereign: { title: 'The Eclipse Sovereign', boss: 'eclipse_sovereign', text: "The Second Keeper, warden of the Void Shore. He stood at the edge of the world and watched the Eclipse rise.\n\nHe took the Shard into himself to spare the others - and became its herald. The Voidweavers are his unspoken doubts.\n\nThe Wayfarer's last legible line: §o'He knew my name.'§r" },
};

// ------------------------------------------------------------------------------------------- state
function fresh() {
    return { step: 0, grove: 0, kills: { gravewalker: 0, cave_weaver: 0 }, groveKills: 0, pages: [], mirror: false };
}

export function getStory(p) {
    const raw = safe(() => p.getDynamicProperty(KEY));
    if (typeof raw === 'string') {
        try { return { ...fresh(), ...JSON.parse(raw) }; } catch (e) { /* fall through */ }
    }
    return fresh();
}

function save(p, st) {
    safe(() => p.setDynamicProperty(KEY, JSON.stringify(st)), 'storySave');
}

function toast(p, text) {
    msg(p, `§d✿ §f${text}`);
    playSound(p.dimension, 'random.levelup', p.location, { volume: 0.6, pitch: 1.5 });
}

function give(p, id, n) {
    safe(() => {
        const inv = p.getComponent(EntityComponentTypes.Inventory).container;
        const left = inv.addItem(new ItemStack(id, n));
        if (left) p.dimension.spawnItem(left, p.location);
    }, 'storyGive');
}

function unlock(p, st, key) {
    if (st.pages.includes(key)) return false;
    st.pages.push(key);
    toast(p, `A new page appears in your journal: §d${PAGES[key].title}`);
    return true;
}

function advance(p, st, to) {
    if (st.step >= to) return;
    st.step = to;
    const done = STEPS[to - 1];
    save(p, st);
    if (done) toast(p, `§aJournal updated§f - ${done.title} complete.`);
    for (const k of Object.keys(PAGES)) if (PAGES[k].at === to) toast(p, `A new page appears in your journal: §d${PAGES[k].title}`);
    if (to < STEPS.length) msg(p, `§7Open your Wayfarer's Journal for the next clue.`);
    else if (to >= COMPLETE) msg(p, '§d§lChapter complete!§r §7More of the story is yet to be written...');
}

// ------------------------------------------------------------------------------------------- journal UI
function pageUnlocked(st, key) {
    const pg = PAGES[key];
    if (pg.at !== undefined) return st.step >= pg.at;
    return st.pages.includes(key);
}

function progressText(st) {
    if (st.step === 1) return `\n\n§7Gravewalkers: ${Math.min(st.kills.gravewalker, KILLS.gravewalker)}/${KILLS.gravewalker}\nCave Weavers: ${Math.min(st.kills.cave_weaver, KILLS.cave_weaver)}/${KILLS.cave_weaver}\n§8...or any monsters slain inside a Cherry Grove: ${Math.min(st.groveKills || 0, GROVE_KILLS)}/${GROVE_KILLS}`;
    if (st.step === 2) return '\n\n§7' + OFFERINGS.map(([, n, name]) => `${name} x${n}`).join(', ');
    return '';
}

function countItem(p, id) {
    let n = 0;
    safe(() => {
        const inv = p.getComponent(EntityComponentTypes.Inventory).container;
        for (let i = 0; i < inv.size; i++) { const it = inv.getItem(i); if (it && it.typeId === id) n += it.amount; }
    });
    return n;
}

function takeItem(p, id, n) {
    safe(() => {
        const inv = p.getComponent(EntityComponentTypes.Inventory).container;
        for (let i = 0; i < inv.size && n > 0; i++) {
            const it = inv.getItem(i);
            if (!it || it.typeId !== id) continue;
            const t = Math.min(n, it.amount);
            if (it.amount <= t) inv.setItem(i, undefined); else { it.amount -= t; inv.setItem(i, it); }
            n -= t;
        }
    });
}

function presentOfferings(p) {
    const st = getStory(p);
    if (st.step !== 2) return;
    const missing = OFFERINGS.filter(([id, n]) => countItem(p, id) < n);
    if (missing.length) {
        msg(p, `§cThe journal's pages stay blank. §7Still missing: ${missing.map(([, n, name]) => `${name} x${n}`).join(', ')}`);
        return;
    }
    for (const [id, n] of OFFERINGS) takeItem(p, id, n);
    give(p, MIRROR, 1);
    st.mirror = true;
    advance(p, st, 3);
    msg(p, '§d✿ The offerings melt into silver glass. §fA Veiled Mirror lies in your hands.');
}

function showPage(p, key) {
    const pg = PAGES[key];
    new ActionFormData().title(`§5${pg.title}`).body(pg.text).button('§0Back').show(p).then(() => openJournal(p)).catch(() => { /* busy */ });
}

function showPages(p) {
    const st = getStory(p);
    const keys = Object.keys(PAGES).filter((k) => pageUnlocked(st, k));
    const form = new ActionFormData().title("§5Lore pages").body(`§7${keys.length} of ${Object.keys(PAGES).length} pages found. Defeat the great foes to find the rest.`);
    for (const k of keys) form.button(`§0${PAGES[k].title}`);
    form.button('§8Back');
    form.show(p).then((res) => {
        if (res.canceled || res.selection === undefined) return;
        if (res.selection >= keys.length) { openJournal(p); return; }
        showPage(p, keys[res.selection]);
    }).catch(() => { /* busy */ });
}

export function openJournal(p) {
    const st = getStory(p);
    const step = STEPS[Math.min(st.step, STEPS.length - 1)];
    const finished = st.step >= COMPLETE;
    const body = finished
        ? "§d§lThe story so far is complete.§r\n\n§7Chapters I and II are written. The Wayfarer's pages beyond the Second Seal are still blank - the road continues.\n\n§7Read your lore pages for everything you have learned."
        : `§5${step.chapter}\n§dStep ${Math.min(st.step + 1, STEPS.length)}: ${step.title}\n\n§0${step.clue}${progressText(st)}`;
    const form = new ActionFormData().title("§5Wayfarer's Journal").body(body);
    const actions = [];
    if (st.step === 2) { form.button('§dPresent offerings'); actions.push('offer'); }
    form.button('§0Lore pages'); actions.push('pages');
    form.button('§8Close'); actions.push('close');
    form.show(p).then((res) => {
        if (res.canceled || res.selection === undefined) return;
        const a = actions[res.selection];
        if (a === 'offer') presentOfferings(p);
        else if (a === 'pages') showPages(p);
    }).catch(() => { /* busy */ });
}

// ------------------------------------------------------------------------------------------- the altar
export function registerBlossomAltar(reg) {
    reg.registerCustomComponent(`${NS}:blossom_altar`, {
        onPlayerInteract(e) {
            const p = e.player;
            const st = getStory(p);
            const it = mainhand(p);
            if (st.step < 3) {
                say(p, '§dThe altar is cold and silent. §7Perhaps your journal knows how to wake it.');
                return;
            }
            if (st.step === 3) {
                advance(p, st, 4);
                spawnParticle(e.dimension, 'minecraft:cherry_leaves_particle', { x: e.block.location.x + 0.5, y: e.block.location.y + 1.2, z: e.block.location.z + 0.5 });
                msg(p, "§dThe altar warms beneath your hand. §7'Come back at night with the mirror,' a voice like petals seems to say.");
                if (!(it && it.typeId === MIRROR)) return;
            }
            if (!(it && it.typeId === MIRROR)) {
                say(p, '§dThe altar waits for the Veiled Mirror.');
                return;
            }
            const t = world.getTimeOfDay();
            const biome = safe(() => e.dimension.getBiome(e.block.location).id);
            if (!(t >= 12800 && t <= 23200)) { say(p, '§dThe mirror stays dull. §7She only answers under the night sky.'); return; }
            if (biome !== CHERRY) { say(p, '§dThe mirror shows only your own face. §7This shrine has lost its grove.'); return; }
            startHanaeRitual(e.block, p);
        },
    });
}

// ------------------------------------------------------------------------------------------- init
export function initStory() {
    // everyone receives the journal once
    world.afterEvents.playerSpawn.subscribe((ev) => {
        if (!ev.initialSpawn) return;
        const p = ev.player;
        if (safe(() => p.getDynamicProperty(GIVEN)) === true) return;
        system.runTimeout(() => safe(() => {
            give(p, JOURNAL, 1);
            p.setDynamicProperty(GIVEN, true);
            msg(p, "§d✿ §fA worn book rests in your pack: §dthe Wayfarer's Journal§f. Use it to read your first clue.");
        }, 'journalGift'), 60);
    });

    // /scriptevent ecr:story set <step> | reset | journal   (testing / recovery; needs permission to run /scriptevent)
    system.afterEvents.scriptEventReceive.subscribe((ev) => {
        if (ev.id !== `${NS}:story`) return;
        const p = /** @type {any} */ (ev.sourceEntity);
        if (!p || p.typeId !== 'minecraft:player') return;
        const [cmd, arg] = ev.message.trim().split(/\s+/);
        if (cmd === 'reset') { save(p, fresh()); msg(p, '§d✿ Story progress reset.'); }
        else if (cmd === 'journal') give(p, JOURNAL, 1);
        else if (cmd === 'set') {
            const st = getStory(p);
            st.step = Math.max(0, Math.min(COMPLETE, parseInt(arg, 10) || 0));
            if (st.step >= 3 && !st.mirror) { st.mirror = true; give(p, MIRROR, 1); }
            save(p, st);
            msg(p, `§d✿ Story step set to ${st.step}.`);
        }
    });

    world.afterEvents.itemUse.subscribe((ev) => {
        if (ev.itemStack && ev.itemStack.typeId === JOURNAL) openJournal(/** @type {any} */ (ev.source));
    });

    // step 1: linger in a cherry grove
    system.runInterval(() => {
        for (const p of world.getAllPlayers()) {
            safe(() => {
                const st = getStory(p);
                if (st.step !== 0) return;
                if (p.dimension.getBiome(p.location).id !== CHERRY) return;
                st.grove += 2;
                if (st.grove >= 10) { give(p, 'minecraft:bread', 6); advance(p, st, 1); }
                else save(p, st);
            }, 'groveCheck');
        }
    }, 40);

    // kills and boss pages
    world.afterEvents.entityDie.subscribe((ev) => {
        const e = ev.deadEntity;
        const id = e.typeId.replace(`${NS}:`, '');
        const killer = ev.damageSource && ev.damageSource.damagingEntity;
        if (COMMON_MONSTERS.has(e.typeId) && killer && killer.typeId === 'minecraft:player') {
            const p = /** @type {any} */ (killer);
            const st = getStory(p);
            if (st.step === 1 && safe(() => e.dimension.getBiome(e.location).id) === CHERRY) {
                st.groveKills = (st.groveKills || 0) + 1;
                if (st.groveKills >= GROVE_KILLS) { give(p, 'minecraft:emerald', 5); advance(p, st, 2); } else { save(p, st); say(p, `§d✿ §7Taint cut back in the grove: ${st.groveKills}/${GROVE_KILLS}`); }
            }
            return;
        }
        if (id in KILLS && killer && killer.typeId === 'minecraft:player') {
            const p = /** @type {any} */ (killer);
            const st = getStory(p);
            if (st.step === 1) {
                st.kills[id] = (st.kills[id] || 0) + 1;
                const done = Object.keys(KILLS).every((k) => st.kills[k] >= KILLS[k]);
                if (done) { give(p, 'minecraft:emerald', 5); advance(p, st, 2); } else { save(p, st); say(p, `§d✿ §7${id === 'gravewalker' ? 'Gravewalkers' : 'Cave Weavers'}: ${Math.min(st.kills[id], KILLS[id])}/${KILLS[id]}`); }
            }
            return;
        }
        if (!(e.typeId.startsWith(`${NS}:`) && PAGES[id] && PAGES[id].boss === id)) return;
        for (const p of safe(() => e.dimension.getPlayers({ location: e.location, maxDistance: 90 })) || []) {
            safe(() => {
                const st = getStory(p);
                const fresh_ = unlock(p, st, id);
                if (id === 'veiled_blossom' && st.step >= 3 && st.step < 5) { give(p, 'minecraft:experience_bottle', 8); advance(p, st, 5); }
                else if (id === 'eclipse_sovereign' && st.step === 5) advance(p, st, 6);
                else if (fresh_) save(p, st);
            }, 'bossPage');
        }
    });
}
