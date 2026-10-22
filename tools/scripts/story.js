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
const FORK = `${NS}:tuning_fork`;
const LANTERN = `${NS}:keepers_lantern`;

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

/** The Overworld roads open after the First Seal and are walked in parallel with Chapter II (the End).  Road IV opens when Road III is done.
 *  Progress per road is the number of finished steps (3 = done), stored in the player's story as `c3` / `c4`. */
const ROADS = {
    c3: {
        name: 'Road III - The Silent Choir', short: 'The Silent Choir', opens: (st) => st.step >= 5, hint: 'recommended: diamond or Rimesteel gear, a cold-weather appetite',
        steps: [
            { title: 'Echoes in the Snow',
              clue: "§o'Hanae's plea was not the only voice in the grove. Under it, something hummed a lullaby I knew as a child. Where the snow never leaves, standing stones sing it back - four verses, and I must hear every one.'§r\n\n§bFind the §fVerse Stones§b that stand in snowy lands and read all four verses (Dawn, Zenith, Dusk, Midnight). The §fCantor's Tuning Fork§b hums towards them." },
            { title: "The Sun's Road",
              clue: "§o'The verses were never a song. They are a lock. Four chimes hang in a cathedral of ice, and the song says in what order the sun walks.'§r\n\n§bFind the §fFrozen Cathedral§b in the high snowy peaks and strike its four chimes in the order of the sun's road. A wrong note will be answered." },
            { title: 'The Conductor',
              clue: "§o'The lectern is awake. The Third Keeper has been conducting this song for longer than I have been alive. Do not strike a note you cannot finish.'§r\n\n§bUse the §fTuning Fork§b on the §fCantor's Lectern§b and face Ysolde, the Frost Cantor." },
        ],
    },
    c5: {
        name: 'Road V - The Cinder Bride', short: 'The Cinder Bride', opens: (st) => st.c4 >= 3, hint: 'the Nether, netherite-grade kit, fire resistance, a stack of arrows and a good shield',
        steps: [
            { title: 'The Vows Left Unsaid',
              clue: "§o'Morwen's lamp showed me a road down into the Burning Deep. There is a forge there where a wedding was interrupted at the vows. Three pedestals wait for an offering each, and a tablet carved by someone who was not in a hurry.'§r\n\n§6Find the §fForge of Vows§6 in the Nether, read the Vow Tablets and make the three offerings (a Gold Ingot, a Blaze Rod, a Ghast Tear) in the order the vow was spoken." },
            { title: 'The Bridal Anvil',
              clue: "§o'The forge gave me a ring and a compass that burns. The ring has a twin, and the twin is on the anvil of a ruined chapel. A guest, they say, must bring the ring.'§r\n\n§6Use the §fEmber Compass§6 to find the §fAshen Chapel§6 and touch the §fBridal Anvil§6." },
            { title: 'The Wedding',
              clue: "§o'The anvil has a hollow in the shape of a ring. She is not a monster. She is a bride who has been waiting longer than the Shard has been bound.'§r\n\n§6Set the §fCinder Ring§6 on the Bridal Anvil and face Varenna, the Cinder Bride. Cut down her blades, keep apart when she brands you." },
        ],
    },
    c6: {
        name: 'Road VI - The Ashen Groom', short: 'The Ashen Groom', opens: (st) => st.c5 >= 3, hint: 'bring a bow or trident AND a good sword - he demands both',
        steps: [
            { title: "The Widower's Toll",
              clue: "§o'Varenna asked me to tell him she kept the veil. The bells of Soul Sand Valley have been tolling since before I arrived - and they ring the same pattern every time I get close. I think they are asking a question.'§r\n\n§bUse the §fEmber Compass§b to find the §fToll Tower§b in a Soul Sand Valley, touch its core and ring back the pattern three times." },
            { title: "The Groom's Grave",
              clue: "§o'The tower dropped a key. The compass now points at a hall of broken pews and a single altar. The veil on his arm is hers. The ring on his finger is hers. I did not have the heart to take either.'§r\n\n§bFind the §fHollow Hall§b and touch the §fGrave Altar§b." },
            { title: 'The Last Vow',
              clue: "§o'I will fight the groom the way he asks: with steel when he burns, with arrows when he is blue. Whatever he is when he falls, tell him the ring still fits.'§r\n\n§bSet the §fGrave Key§b into the Grave Altar and face Corvane, the Ashen Groom. Match your weapons to his stance." },
        ],
    },
    c4: {
        name: 'Road IV - The Lantern in the Mire', short: 'The Lantern in the Mire', opens: (st) => st.c3 >= 3, hint: 'bring torches or lanterns - light is a weapon here',
        steps: [
            { title: 'Lights in the Fen',
              clue: "§o'Ysolde's last verse was a map, and it ended in a swamp. At night the water breathes little lights. I think they are the travellers a Keeper once tried to guide home. Gather what is left of them.'§r\n\n§aSlay Mire Wisps and the dead of the fen at night, then present §f6 Wisp Essence§a and a §fLantern§a in the journal." },
            { title: 'The Drowned Chapel',
              clue: "§o'The lantern wants to be lit in a certain order. I found half the riddle on a tablet in a fen hut and half in the chapel itself - a drowned place with three sconces and a hidden room.'§r\n\n§aFind the §fDrowned Chapel§a in a swamp, read the §fFen Notes§a, and light the three sconces with the §fKeeper's Lantern§a in the right order." },
            { title: 'The Lantern Calls',
              clue: "§o'All three burn. The altar waits with open hands. She only answers under a night sky, and only to a lantern that is lit.'§r\n\n§aAt night, in a swamp, use the §fKeeper's Lantern§a on the §fMarsh Altar§a and face Morwen, the Mire Lantern." },
        ],
    },
};

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
    eighth_voice: { title: 'The Eighth Voice', road: 'c3', at: 1, text: "A tablet in the snow, in the Wayfarer's hand:\n\n§o\"Eight stood at the Cracking. Seven took Shards. I took only the page. I never understood why until I heard Ysolde sing it.\"§r\n\nThe journal's ink is Azurite dust - the First Dawn, ground fine. Whoever the Wayfarer was, she wrote with the world's own morning." },
    suns_road: { title: "The Sun's Road", road: 'c3', at: 2, text: "Dawn, Zenith, Dusk, Midnight.\n\nThe four verses were four keys, and the chimes of the Frozen Cathedral their locks. The Choir's rule is simple and terrible: a cantor sings so the Shard may sleep. The day the song ends, the Seal opens. So the cantor may not rest, may not stop, and may not be thanked." },
    frozen_choir: { title: 'The Frozen Choir', road: 'c3', at: 0, text: "Where the Eclipse could not reach the sky, it reached the snow. The dead of the high country - Rimewalkers, Hoarbones - are the Choir's missing voices, taught to sing without breath.\n\nTheir shards of rime make a good alloy: iron that remembers winter." },
    fen_lights: { title: 'The Lights of the Fen', road: 'c4', at: 0, text: "Morwen hung a lantern in every window of the fen so that no traveller would wander into the dark. The Shard learned the trick. Now the lights lead the other way.\n\nMire Wisps are the travellers who followed the wrong light. Their essence is warm, and it remembers the way home." },
    lantern_riddle: { title: 'The Sconces', road: 'c4', at: 2, text: "The eye must watch before the star can guide;\nthe moon leads home, and comes last.\n\nLight them as you would leave a lantern for a lost friend." },
    forge_vows: { title: 'The Forge of Vows', road: 'c5', at: 0, text: "In the Burning Deep a smith-queen forged the Fifth Seal into her own wedding ring, so that it could not be taken from her hand without taking the hand.\n\nShe was to be married that night. The Cracking interrupted the vows - all three of them: gold, flame and tears. Nobody told the bride." },
    bridal_anvil: { title: 'The Bridal Anvil', road: 'c5', at: 2, text: "A ruined chapel, an aisle of black carpet with a single white thread, and an anvil where an altar should be. The ring she wears has a twin. A guest, the tablets say, must bring the other." },
    toll_tower: { title: 'The Toll Tower', road: 'c6', at: 0, text: "The groom could not leave the valley, so he hung bells in a tower and tolled for every one who did not return. After a while the bells began tolling without hands.\n\nThe tower asks a question in bell-notes and expects the same answer back." },
    two_rings: { title: 'Two Rings', road: 'c6', at: 2, text: "Her ring is on his finger. His veil is on her arm. To free one of them, the other must fall - the cruelest arithmetic of the Seals. The Wayfarer found no way around it. Neither will you." },
    cinder_bride: { title: 'Varenna, Keeper of the Fifth Seal', boss: 'cinder_bride', text: "The Cinder Bride, smith-queen of the Burning Deep. She fought with a forge because it was the only language she had left. Every blade she made was a promise she could not keep.\n\n§o\"Tell Corvane... tell him I kept the veil.\"§r" },
    ashen_groom: { title: 'Corvane, Keeper of the Sixth Seal', boss: 'ashen_groom', text: "The Ashen Groom, bell-ringer of Soul Sand Valley. He swore to stand at the altar until she came, and did not think he might never be able to leave.\n\nHe fought in the stances of fire and soul because both of them were all he had left of her.\n\n§o\"I can hear the valley. It is only wind.\"§r" },
    frost_cantor: { title: 'Ysolde, Keeper of the Third Seal', boss: 'frost_cantor', text: "The Third Keeper, cantor of the high snow. She sang the Shard to sleep and has not stopped for longer than anyone remembers; the cold followed her song and froze the world to listen.\n\nShe asked you to finish the verse. The Wayfarer once did.\n\n§o\"Do you hear that? It is silent. I had forgotten silence.\"§r" },
    mire_lantern: { title: 'Morwen, Keeper of the Fourth Seal', boss: 'mire_lantern', text: "The Fourth Keeper, lamplighter of the fen. A Seal that is a lantern which can never go out is a hard thing to carry, and the Shard learned to use the light as bait.\n\nShe could see the Wayfarer's lamp, far ahead. Whoever she was, she is still walking.\n\n§o\"I only wanted someone to come home.\"§r" },
    eclipse_sovereign: { title: 'The Eclipse Sovereign', boss: 'eclipse_sovereign', text: "The Second Keeper, warden of the Void Shore. He stood at the edge of the world and watched the Eclipse rise.\n\nHe took the Shard into himself to spare the others - and became its herald. The Voidweavers are his unspoken doubts.\n\nThe Wayfarer's last legible line: §o'He knew my name.'§r" },
};

// ------------------------------------------------------------------------------------------- state
function fresh() {
    return { step: 0, grove: 0, kills: { gravewalker: 0, cave_weaver: 0 }, groveKills: 0, pages: [], mirror: false, c3: 0, c4: 0, c5: 0, c6: 0, verses: [false, false, false, false], fork: false, chimes: [], sconces: [], vows: [], compass: false };
}

export function saveStory(p, st) {
    save(p, st);
}

export function giveTo(p, id, n = 1) {
    give(p, id, n);
}

export function toastTo(p, text) {
    toast(p, text);
}

export function roadOpen(st, road) {
    return ROADS[road].opens(st);
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
    for (const k of Object.keys(PAGES)) if (PAGES[k].at === to && !PAGES[k].road) toast(p, `A new page appears in your journal: §d${PAGES[k].title}`);
    if (to >= 5 && !st.fork) { st.fork = true; give(p, FORK, 1); save(p, st); msg(p, "§b❄ §fThe Wayfarer's pages stir: a new road opens. §7A §bCantor's Tuning Fork§7 has appeared in your pack."); }
    if (to < STEPS.length) msg(p, `§7Open your Wayfarer's Journal for the next clue.`);
    else if (to >= COMPLETE) msg(p, '§d§lChapter complete!§r §7More of the story is yet to be written...');
}

/** finish a step of an Overworld road (to = number of finished steps after this call) */
export function advanceRoad(p, st, road, to) {
    if ((st[road] || 0) >= to) return false;
    const r = ROADS[road];
    st[road] = to;
    save(p, st);
    const done = r.steps[to - 1];
    if (done) toast(p, `§a${r.short} §f- ${done.title} complete.`);
    for (const k of Object.keys(PAGES)) if (PAGES[k].road === road && PAGES[k].at === to) toast(p, `A new page appears in your journal: §d${PAGES[k].title}`);
    if (road === 'c4' && to >= 3 && !st.compass) { st.compass = true; give(p, `${NS}:ember_compass`, 1); save(p, st); msg(p, "§6🔥 §fMorwen's last light shows a road down into the Burning Deep. §7An §6Ember Compass§7 has appeared in your pack."); }
    if (to < r.steps.length) msg(p, '§7Open your Wayfarer\'s Journal for the next clue.');
    else msg(p, `§d§l${r.name} - complete!`);
    return true;
}

// ------------------------------------------------------------------------------------------- journal UI
function pageUnlocked(st, key) {
    const pg = PAGES[key];
    if (pg.road) return (st[pg.road] || 0) >= pg.at && roadOpen(st, pg.road);
    if (pg.at !== undefined) return st.step >= pg.at;
    return st.pages.includes(key);
}

function progressText(st) {
    if (st.step === 1) return `\n\n§7Gravewalkers: ${Math.min(st.kills.gravewalker, KILLS.gravewalker)}/${KILLS.gravewalker}\nCave Weavers: ${Math.min(st.kills.cave_weaver, KILLS.cave_weaver)}/${KILLS.cave_weaver}\n§7...or any monsters slain inside a Cherry Grove: ${Math.min(st.groveKills || 0, GROVE_KILLS)}/${GROVE_KILLS}`;
    if (st.step === 2) return '\n\n§7' + OFFERINGS.map(([, n, name]) => `${name} x${n}`).join(', ');
    return '';
}

function roadProgress(st, road) {
    const n = st[road] || 0;
    if (road === 'c3' && n === 0) return `\n\n§7Verses heard: ${st.verses.filter(Boolean).length}/4 (${['Dawn', 'Zenith', 'Dusk', 'Midnight'].filter((_, i) => st.verses[i]).join(', ') || 'none yet'})`;
    if (road === 'c3' && n === 1) return `\n\n§7Chimes struck in order: ${(st.chimes || []).length}/4`;
    if (road === 'c4' && n === 0) return `\n\n§7Wisp Essence x6 (you have ${Math.min(6, countItem(null, `${NS}:wisp_essence`))}), Lantern x1`;
    if (road === 'c5' && n === 0) return `\n\n§7Vows spoken in order: ${(st.vows || []).length}/3`;
    if (road === 'c6' && n === 0) return '\n\n§7Touch the Toll Core, listen to the tolling and ring it back (3 rounds).';
    if (road === 'c4' && n === 1) return `\n\n§7Sconces lit in order: ${(st.sconces || []).length}/3`;
    return '';
}

function countItem(p, id) {
    let n = 0;
    if (!p) return 0;
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
    new ActionFormData().title(`§d${pg.title}`).body(`§f${pg.text}`).button('Back').show(p).then(() => openJournal(p)).catch(() => { /* busy */ });
}

function showPages(p) {
    const st = getStory(p);
    const keys = Object.keys(PAGES).filter((k) => pageUnlocked(st, k));
    const form = new ActionFormData().title("§dLore pages").body(`§7${keys.length} of ${Object.keys(PAGES).length} pages found. Defeat the great foes to find the rest.`);
    for (const k of keys) form.button(PAGES[k].title);
    form.button('Back');
    form.show(p).then((res) => {
        if (res.canceled || res.selection === undefined) return;
        if (res.selection >= keys.length) { openJournal(p); return; }
        showPage(p, keys[res.selection]);
    }).catch(() => { /* busy */ });
}

function presentLantern(p) {
    const st = getStory(p);
    if (st.c4 !== 0) return;
    /** @type {[string, number, string][]} */
    const need = [[`${NS}:wisp_essence`, 6, 'Wisp Essence'], ['minecraft:lantern', 1, 'Lantern']];
    const missing = need.filter(([id, n]) => countItem(p, id) < n);
    if (missing.length) { msg(p, `§cThe journal's pages stay blank. §7Still missing: ${missing.map(([, n, name]) => `${name} x${n}`).join(', ')}`); return; }
    for (const [id, n] of need) takeItem(p, id, n);
    give(p, LANTERN, 1);
    advanceRoad(p, st, 'c4', 1);
    msg(p, "§a✦ The essence settles into the glass and the flame turns green-gold. §fYou hold the Keeper's Lantern.");
}

function showRoad(p, road) {
    const st = getStory(p);
    const r = ROADS[road];
    const n = st[road] || 0;
    const finished = n >= r.steps.length;
    const step = r.steps[Math.min(n, r.steps.length - 1)];
    const body = finished
        ? `§d§l${r.name}§r\n\n§fThis road is finished. §7Its lore pages are in your journal.`
        : `§d${r.name}\n§bStep ${n + 1}: ${step.title}\n\n§f${step.clue}${roadProgress(st, road)}\n\n§8${r.hint}`;
    const form = new ActionFormData().title(`§d${r.short}`).body(body.replace('§8', '§7'));
    const actions = [];
    if (road === 'c4' && n === 0) { form.button('§aPresent offerings'); actions.push('offer'); }
    form.button('Back'); actions.push('back');
    form.show(p).then((res) => {
        if (res.canceled || res.selection === undefined) return;
        if (actions[res.selection] === 'offer') presentLantern(p);
        else openJournal(p);
    }).catch(() => { /* busy */ });
}

export function openJournal(p) {
    const st = getStory(p);
    const step = STEPS[Math.min(st.step, STEPS.length - 1)];
    const finished = st.step >= COMPLETE;
    const body = finished
        ? "§d§lThe story so far is complete.§r\n\n§fChapters I and II are written. The Wayfarer's pages beyond the Second Seal are still blank - the road continues.\n\n§7Read your lore pages for everything you have learned."
        : `§d${step.chapter}\n§bStep ${Math.min(st.step + 1, STEPS.length)}: ${step.title}\n\n§f${step.clue}${progressText(st)}`;
    const form = new ActionFormData().title("§dWayfarer's Journal").body(body);
    const actions = [];
    for (const k of Object.keys(ROADS)) if (roadOpen(st, k)) { form.button(`§b${ROADS[k].short}${(st[k] || 0) >= 3 ? ' ✓' : ''}`); actions.push(k); }
    if (st.step === 2) { form.button('§dPresent offerings'); actions.push('offer'); }
    form.button('Lore pages'); actions.push('pages');
    form.button('Close'); actions.push('close');
    form.show(p).then((res) => {
        if (res.canceled || res.selection === undefined) return;
        const a = actions[res.selection];
        if (a === 'offer') presentOfferings(p);
        else if (a === 'pages') showPages(p);
        else if (a === 'c3' || a === 'c4') showRoad(p, a);
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
        else if (cmd === 'road') {
            const [, road, n] = ev.message.trim().split(/\s+/);
            const st = getStory(p);
            if (road === 'c3' || road === 'c4' || road === 'c5' || road === 'c6') { st[road] = Math.max(0, Math.min(3, parseInt(n, 10) || 0)); if (st.step < 5) st.step = 5; save(p, st); msg(p, `§d✿ ${road} set to ${st[road]}.`); }
        }
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
                else if (id === 'frost_cantor') { unlock(p, st, id); if ((st.c3 || 0) < 3) { st.c3 = 2; advanceRoad(p, st, 'c3', 3); } else save(p, st); }
                else if (id === 'cinder_bride') { unlock(p, st, id); if ((st.c5 || 0) < 3) { st.c5 = 2; advanceRoad(p, st, 'c5', 3); } else save(p, st); }
                else if (id === 'ashen_groom') { unlock(p, st, id); if ((st.c6 || 0) < 3) { st.c6 = 2; advanceRoad(p, st, 'c6', 3); } else save(p, st); }
                else if (id === 'mire_lantern') { unlock(p, st, id); if ((st.c4 || 0) < 3) { st.c4 = 2; advanceRoad(p, st, 'c4', 3); } else save(p, st); }
                else if (fresh_) save(p, st);
            }, 'bossPage');
        }
    });
}
