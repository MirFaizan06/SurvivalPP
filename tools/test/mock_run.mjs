// Runtime smoke test: loads the packaged add-on scripts against a fake @minecraft/server, boots them exactly like the game does
// (startup event -> deferred initAll -> intervals) and fires a battery of fake events through every module.
// Any exception that a script swallows (they log "[ecr] label: message") or lets escape fails the run.
//   node tools/test/mock_run.mjs <path to ECR_BP/scripts> <work dir>
import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const [, , SCRIPTS, WORK] = process.argv;
if (!SCRIPTS || !WORK) { console.error('usage: mock_run.mjs <scripts dir> <work dir>'); process.exit(2); }

// ------------------------------------------------------------------ build the work dir with a mock @minecraft/server
fs.rmSync(WORK, { recursive: true, force: true });
fs.mkdirSync(path.join(WORK, 'scripts'), { recursive: true });
for (const f of fs.readdirSync(SCRIPTS)) fs.copyFileSync(path.join(SCRIPTS, f), path.join(WORK, 'scripts', f));
fs.writeFileSync(path.join(WORK, 'package.json'), '{"type":"module"}');
const imported = { server: new Set(), ui: new Set() };
for (const f of fs.readdirSync(SCRIPTS)) {
    const src = fs.readFileSync(path.join(SCRIPTS, f), 'utf8');
    for (const m of src.matchAll(/import\s*\{([^}]+)\}\s*from\s*'@minecraft\/(server|server-ui)'/g)) {
        for (const n of m[1].split(',').map((s) => s.trim()).filter(Boolean)) imported[m[2] === 'server' ? 'server' : 'ui'].add(n);
    }
}
const CLASSES = new Set(['ItemStack', 'BlockPermutation', 'ModalFormData', 'ActionFormData', 'EntityTypes', 'BlockVolume']);
const mk = (pkg, names, extra) => {
    const dir = path.join(WORK, 'node_modules', '@minecraft', pkg);
    fs.mkdirSync(dir, { recursive: true });
    fs.writeFileSync(path.join(dir, 'package.json'), '{"name":"x","type":"module","exports":"./index.js"}');
    let code = 'const M = globalThis.__mock;\n';
    for (const n of names) code += CLASSES.has(n) ? `export const ${n} = M.classes.${n};\n` : (n === 'world' || n === 'system') ? `export const ${n} = M.${n};\n` : `export const ${n} = M.enumProxy('${n}');\n`;
    fs.writeFileSync(path.join(dir, 'index.js'), code + (extra || ''));
};
mk('server', [...imported.server]);
mk('server-ui', [...imported.ui]);

// ------------------------------------------------------------------ fakes
const logs = [];
const origWarn = console.warn;
console.warn = (...a) => { logs.push(a.join(' ')); };
const failures = [];
const note = (m) => failures.push(m);

const handlers = { before: {}, after: {}, intervals: [], timeouts: [], runs: [] };
const signal = (bucket) => new Proxy({}, { get: (t, k) => ({ subscribe(fn) { (bucket[k] ||= []).push(fn); return fn; }, unsubscribe() {} }) });
const dyn = new Map();
const snake = (k) => 'minecraft:' + k.replace(/([a-z0-9])([A-Z])/g, '$1_$2').toLowerCase();
const enumProxy = (name) => new Proxy({}, { get: (t, k) => (typeof k !== 'string' ? undefined : (name === 'EntityComponentTypes' || name === 'ItemComponentTypes') ? snake(k) : k) });

let tick = 1000;
let timeOfDay = 14000;
const fakeLoc = (x = 0, y = 64, z = 0) => ({ x, y, z });

class FakePerm {
    constructor(id, states = {}) { this.type = { id }; this.states = states; }
    getState(n) { return this.states[n]; }
    withState(n, v) { return new FakePerm(this.type.id, { ...this.states, [n]: v }); }
}
class FakeBlock {
    constructor(typeId, loc, dim) { this.typeId = typeId; this.location = loc; this.dimension = dim; this.permutation = new FakePerm(typeId); this.isLiquid = false; this.isWaterlogged = false; }
    get isAir() { return this.typeId === 'minecraft:air'; }
    center() { return { x: this.location.x + 0.5, y: this.location.y + 0.5, z: this.location.z + 0.5 }; }
    setType(t) { this.typeId = typeof t === 'string' ? t : t.id; this.permutation = new FakePerm(this.typeId); }
    setPermutation(p) { this.permutation = p; this.typeId = p.type.id; }
    getLightLevel() { return 12; }
    below() { return new FakeBlock('minecraft:farmland', fakeLoc(this.location.x, this.location.y - 1, this.location.z), this.dimension); }
    above() { return new FakeBlock('minecraft:air', fakeLoc(this.location.x, this.location.y + 1, this.location.z), this.dimension); }
    north() { return this.above(); } south() { return this.above(); } east() { return this.above(); } west() { return this.above(); }
    getComponent() { return undefined; }
    getItemStack(n = 1) { return new ItemStack(this.typeId, n); }
    canBeDestroyedByLiquidSpread() { return false; }
}
class ItemStack {
    constructor(typeId, amount = 1) { this.typeId = typeId; this.amount = amount; this.props = {}; this.lore = []; this.nameTag = undefined; this.maxAmount = 64; }
    getComponent(n) {
        if (n === 'minecraft:durability') return { damage: 0, maxDurability: 100 };
        if (n === 'minecraft:enchantable') return { getEnchantments: () => [], hasEnchantment: () => 0, getEnchantment: () => undefined, addEnchantment() {} };
        return undefined;
    }
    getDynamicProperty(k) { return this.props[k]; } setDynamicProperty(k, v) { this.props[k] = v; }
    setLore(l) { this.lore = l; } getLore() { return this.lore; }
    clone() { const c = new ItemStack(this.typeId, this.amount); c.props = { ...this.props }; return c; }
    hasTag() { return false; } getTags() { return []; }
}
class ModalFormData {
    title() { return this; } dropdown() { return this; } toggle() { return this; } textField() { return this; } slider() { return this; } submitButton() { return this; }
    show() { return Promise.resolve({ canceled: true }); }
}
class FakeEntity {
    constructor(typeId, dim, loc) {
        this.typeId = typeId; this.dimension = dim; this.location = loc || fakeLoc(); this.id = `${typeId}#${Math.floor(Math.random() * 1e6)}`; this.isValid = true; this.nameTag = '';
        this.tags = new Set(); this.props = { 'ecr:phase': 0, 'ecr:puffing': true }; this.effects = []; this.events = []; this.health = 100;
    }
    getComponent(n) {
        if (n === 'minecraft:health') return { currentValue: this.health, effectiveMax: 100, setCurrentValue: (v) => { this.health = v; } };
        if (n === 'minecraft:inventory') return { container: { size: 36, getItem: () => undefined, setItem() {}, addItem() {} } };
        if (n === 'minecraft:equippable') return { getEquipment: () => undefined, setEquipment() {} };
        if (n === 'minecraft:projectile') return { shoot() {}, owner: undefined };
        if (n === 'minecraft:type_family') return { hasTypeFamily: () => true };
        return undefined;
    }
    hasComponent() { return true; }
    getTags() { return [...this.tags]; }
    addEffect(e, d, o) { this.effects.push([e, d, o]); } removeEffect() {} getEffect() { return undefined; }
    hasTag(t) { return this.tags.has(t); } addTag(t) { this.tags.add(t); } removeTag(t) { this.tags.delete(t); }
    triggerEvent(e) { this.events.push(e); }
    getProperty(k) { return this.props[k]; } setProperty(k, v) { this.props[k] = v; }
    playSound(id) { (this.sounds ||= []).push(id); }
    applyDamage() { return true; } applyKnockback() {} setOnFire() {} teleport(l) { this.location = l; } kill() { this.isValid = false; } remove() {} runCommand(c) { (this.cmds ||= []).push(c); return { successCount: 1 }; }
    setRotation() {} getRotation() { return { x: 0, y: 0 }; } getViewDirection() { return { x: 0, y: 0, z: 1 }; }
    getDynamicProperty(k) { return this.props[`dp:${k}`]; } setDynamicProperty(k, v) { this.props[`dp:${k}`] = v; }
}
class FakePlayer extends FakeEntity {
    constructor(dim, name = 'Steve', id = 'p1') {
        super('minecraft:player', dim, fakeLoc(0, 64, 0));
        this.name = name; this.id = id; this.isSneaking = false; this.commandPermissionLevel = 0; this.mode = 'survival'; this.sent = [];
        this.onScreenDisplay = { setActionBar: (m) => this.sent.push(['bar', m]), setTitle: (t) => this.sent.push(['title', t]) };
        this.inv = new Map(); this.equip = new Map(); this.isOnGround = true;
        this.cam = []; this.perms = [];
        this.camera = { setCamera: (id, o) => this.cam.push(['set', id, o]), fade: (o) => this.cam.push(['fade', o]), clear: () => this.cam.push(['clear']), addShake: (o) => this.cam.push(['shake', o]) };
        this.inputPermissions = { setPermissionCategory: (c, on) => this.perms.push([c, on]) };
    }
    getGameMode() { return this.mode; }
    getBlockFromViewDirection() { return { block: new FakeBlock('ecr:stasis_plate', fakeLoc(70, 64, 70), this.dimension), face: 'Up' }; }
    addExperience() {} addLevels() {} getTotalXp() { return 0; }
    isOp() { return false; }
    sendMessage(m) { this.sent.push(['msg', m]); }
    getSpawnPoint() { return undefined; }
    getComponent(n) {
        if (n === 'minecraft:inventory') return { container: { size: 36, getItem: (i) => this.inv.get(i), setItem: (i, it) => { if (it) this.inv.set(i, it); else this.inv.delete(i); }, addItem: (it) => { for (let i = 0; i < 36; i++) if (!this.inv.has(i)) { this.inv.set(i, it); return undefined; } return it; } } };
        if (n === 'minecraft:equippable') return { getEquipment: (s) => this.equip.get(s), setEquipment: (s, it) => { if (it) this.equip.set(s, it); else this.equip.delete(s); } };
        return super.getComponent(n);
    }
}
class FakeDim {
    constructor(id) { this.id = id; this.blocks = new Map(); this.entities = []; this.players = []; this.spawned = []; }
    getBlock(l) {
        const k = `${Math.floor(l.x)},${Math.floor(l.y)},${Math.floor(l.z)}`;
        if (!this.blocks.has(k)) this.blocks.set(k, new FakeBlock(l.y < 60 ? 'minecraft:stone' : 'minecraft:air', { x: Math.floor(l.x), y: Math.floor(l.y), z: Math.floor(l.z) }, this));
        return this.blocks.get(k);
    }
    setBlock(b) { this.blocks.set(`${b.location.x},${b.location.y},${b.location.z}`, b); }
    getTopmostBlock(l) { return this.getBlock({ x: l.x, y: 63, z: l.z }); }
    getEntities(o = {}) {
        let r = this.entities.filter((e) => e.isValid);
        if (o.type) r = r.filter((e) => e.typeId === o.type);
        return r;
    }
    getPlayers() { return this.players; }
    containsBlock(vol, f) { return [...this.blocks.values()].some((b) => (f.includeTypes || []).includes(b.typeId) && b.location.x >= vol.from.x && b.location.x <= vol.to.x && b.location.z >= vol.from.z && b.location.z <= vol.to.z); }
    getBiome() { return { id: this.biome || 'minecraft:plains' }; }
    spawnEntity(t, l) { const e = new FakeEntity(t, this, l); this.entities.push(e); this.spawned.push(t); return e; }
    spawnItem(i, l) { this.spawned.push(`item:${i.typeId}`); return new FakeEntity('minecraft:item', this, l); }
    spawnParticle() {} playSound() {} runCommand() { return { successCount: 1 }; } createExplosion() { return true; }
}
const dims = {};
const getDim = (id) => (dims[id] ||= new FakeDim(id));
const player = new FakePlayer(getDim('minecraft:overworld'));
getDim('minecraft:overworld').players.push(player);

const world = {
    beforeEvents: signal(handlers.before), afterEvents: signal(handlers.after),
    getDimension: (id) => getDim(id), getAllPlayers: () => [player], getPlayers: () => [player],
    getTimeOfDay: () => timeOfDay, getDefaultSpawnLocation: () => fakeLoc(0, 64, 0),
    getDynamicProperty: (k) => dyn.get(k), setDynamicProperty: (k, v) => { if (v === undefined) dyn.delete(k); else dyn.set(k, v); },
    getDynamicPropertyIds: () => [...dyn.keys()], sendMessage: (m) => logs.push(`[chat] ${m}`),
    gameRules: { showDeathMessages: true }, structureManager: { place() {}, get: () => undefined },
    tickingAreaManager: { hasTickingArea: () => false, createTickingArea: async () => {}, removeTickingArea() {}, getAllTickingAreas: () => [], maxChunkCount: 100, chunkCount: 0 },
    getEntity: () => undefined,
};
const system = {
    beforeEvents: signal(handlers.before), afterEvents: signal(handlers.after),
    get currentTick() { return tick; },
    runInterval(fn, t = 1) { handlers.intervals.push([fn, t]); return handlers.intervals.length; },
    runTimeout(fn, t = 0) { handlers.timeouts.push([fn, t]); return handlers.timeouts.length; },
    run(fn) { handlers.runs.push(fn); return 0; }, clearRun(id) { const e = handlers.intervals[id - 1]; if (e) e[0] = () => {}; }, waitTicks: () => Promise.resolve(),
};
const formQueue = [];
class ActionFormData extends ModalFormData { body() { return this; } button() { return this; } show() { return Promise.resolve(formQueue.length ? { canceled: false, selection: formQueue.shift() } : { canceled: true }); } }
globalThis.__mock = { world, system, enumProxy, classes: { EntityTypes: { get: (id) => ({ id }), getAll: () => [] }, ItemStack, BlockPermutation: { resolve: (id, st) => new FakePerm(id, st) }, ModalFormData, ActionFormData, BlockVolume: class { constructor(a, b) { this.from = a; this.to = b; } } } };

// ------------------------------------------------------------------ helpers to drive the game loop
const flush = () => {
    for (let i = 0; i < 5; i++) {
        const t = handlers.timeouts.splice(0); const r = handlers.runs.splice(0);
        for (const [fn] of t) call(fn, 'timeout'); for (const fn of r) call(fn, 'run');
    }
};
const call = (fn, label, ...args) => {
    try { const r = fn(...args); if (r && r.catch) r.catch((e) => note(`${label}: async ${e && e.stack ? e.stack : e}`)); return r; } catch (e) { note(`${label}: ${e && e.stack ? e.stack.split('\n').slice(0, 3).join(' | ') : e}`); }
};
const fire = (kind, name, ev) => { for (const fn of handlers[kind][name] || []) call(fn, `${kind}.${name}`, ev); flush(); };
const runTicks = (n) => { for (let i = 0; i < n; i++) { tick += 10; for (const [fn, t] of handlers.intervals) if (tick % Math.max(1, t) < 10) call(fn, 'interval'); flush(); } };

// ------------------------------------------------------------------ boot
const registered = {};
await import(pathToFileURL(path.join(WORK, 'scripts', 'main.js')).href);
const startup = handlers.before.startup || [];
if (!startup.length) note('main.js did not subscribe to system.beforeEvents.startup');
for (const fn of startup) call(fn, 'startup', { blockComponentRegistry: { registerCustomComponent: (n, c) => { registered[n] = c; } }, itemComponentRegistry: { registerCustomComponent() {} } });
flush();
const ready = logs.find((l) => l.includes('ready - Tech Bytes Design'));
if (!ready) note('no "ready" line logged: modules did not initialise');
else if (/failed modules/.test(ready)) note(`module init failure: ${ready}`);
console.log(`registered block components: ${Object.keys(registered).length} (${Object.keys(registered).join(', ')})`);
console.log(`intervals: ${handlers.intervals.length}, event handlers: ${Object.values(handlers.before).flat().length} before / ${Object.values(handlers.after).flat().length} after`);

// ------------------------------------------------------------------ scenarios
const ow = getDim('minecraft:overworld');
const blockAt = (id, x, y, z) => { const b = new FakeBlock(id, fakeLoc(x, y, z), ow); ow.setBlock(b); return b; };
const hold = (id, n = 1) => { const it = new ItemStack(id, n); player.equip.set('Mainhand', it); player.inv.set(0, it); return it; };

runTicks(40);                                                                   // let every interval run a few times with an empty world

// 1) sanctum: place, configure menu, intruder logic, limit, lapse + claim
const warden = blockAt('ecr:sanctum_warden', 10, 64, 10);
registered['ecr:sanctum'].onPlace({ block: warden, dimension: ow });
fire('after', 'playerPlaceBlock', { player, block: warden });
registered['ecr:sanctum'].onPlayerInteract({ player, block: warden, dimension: ow });
const intruder = new FakePlayer(ow, 'Alex', 'p2'); intruder.location = fakeLoc(11, 64, 10); ow.players.push(intruder);
const oldAll = world.getAllPlayers; world.getAllPlayers = () => [player, intruder];
runTicks(60);
if (!intruder.sent.some((m) => m[0] === 'title')) note('sanctum: an intruder in a fresh zone got no warning title');
registered['ecr:sanctum'].onPlayerInteract({ player: intruder, block: warden, dimension: ow });
fire('before', 'playerBreakBlock', { player: intruder, block: warden, cancel: false });
fire('before', 'playerInteractWithBlock', { player: intruder, block: blockAt('minecraft:chest', 12, 64, 10), itemStack: undefined, isFirstEvent: true, cancel: false });
for (let i = 0; i < 4; i++) { const w = blockAt('ecr:sanctum_warden', 30 + i * 3, 64, 30); fire('after', 'playerPlaceBlock', { player, block: w }); }
const zkeys = JSON.parse(dyn.get('ecr:sanctum_idx') || '[]');
if (zkeys.length !== 3) note(`sanctum: expected exactly 3 zones after 5 placements, got ${zkeys.length}`);
const realNow = Date.now;
Date.now = () => realNow() + 22 * 86400000;                                  // the owner has been gone for 22 days
const lapsedKey = 'minecraft:overworld|10|64|10';
registered['ecr:sanctum'].onPlayerInteract({ player: intruder, block: warden, dimension: ow });
const claimed = JSON.parse(dyn.get(`ecr:sz|${lapsedKey}`) || 'null');
if (!claimed || claimed.o !== 'p2') note('sanctum: a lapsed (owner gone 22 days) zone could not be claimed by another player');
Date.now = realNow;
world.getAllPlayers = oldAll;

// 2) bosses: ritual conditions
for (const [relic, blk] of [['ecr:grave_sigil', 'minecraft:bone_block'], ['ecr:verdant_heart', 'minecraft:moss_block'], ['ecr:silk_idol', 'minecraft:web']]) {
    const b = blockAt(blk, 50, relic === 'ecr:silk_idol' ? 30 : 64, 50);
    timeOfDay = relic === 'ecr:verdant_heart' ? 6000 : 14000;
    hold(relic);
    const evb = { player, block: b, itemStack: player.equip.get('Mainhand'), isFirstEvent: true, cancel: false };
    fire('before', 'playerInteractWithBlock', evb);
    if (!evb.cancel) note(`ritual: ${relic} on ${blk} was not intercepted`);
    if (player.equip.get('Mainhand')) note(`ritual: ${relic} was not consumed under valid conditions`);
    tick += 40;
}
runTicks(80);
timeOfDay = 6000;                                                               // wrong time for the Hollow King: must keep the relic
{
    const b = blockAt('minecraft:bone_block', 55, 70, 55);
    hold('ecr:grave_sigil');
    fire('before', 'playerInteractWithBlock', { player, block: b, itemStack: player.equip.get('Mainhand'), isFirstEvent: true, cancel: false });
    if (!player.equip.get('Mainhand')) note('ritual: Grave Sigil consumed in daylight above ground (should be refused)');
    if (!player.sent.some((m) => m[0] === 'msg' && String(m[1]).includes('Bone Block'))) note('ritual: no hint shown for failed conditions');
    timeOfDay = 14000;
}
for (const t of ['ecr:hollow_king', 'ecr:mosswood_colossus', 'ecr:silkqueen', 'ecr:eclipse_sovereign']) {
    const boss = ow.spawnEntity(t, fakeLoc(0, 64, 0));
    boss.health = 40;                                                           // phase 3
    runTicks(80);
    if (t === 'ecr:eclipse_sovereign' && !(player.sounds || []).includes('ecr.music.eclipse_sovereign')) note('music: the Eclipse Sovereign theme never played');
    boss.health = 0;
    fire('after', 'entityDie', { deadEntity: boss, damageSource: { cause: 'entityAttack', damagingEntity: player } });
}
for (const t of ['ecr:gravewalker', 'ecr:revenant', 'ecr:cave_weaver', 'ecr:sporeling']) ow.spawnEntity(t, fakeLoc(2, 64, 2));

// 3) mobs2 behaviours
const spore = ow.entities.find((e) => e.typeId === 'ecr:sporeling');
fire('after', 'entityHurt', { hurtEntity: spore, damage: 2, damageSource: {} });
fire('after', 'entityDie', { deadEntity: spore, damageSource: {} });
const bolt = new FakeEntity('ecr:web_bolt', ow, fakeLoc(0, 64, 0));
fire('after', 'projectileHitEntity', { projectile: bolt, location: fakeLoc(1, 64, 1), getEntityHit: () => ({ entity: player }) });
fire('after', 'projectileHitBlock', { projectile: bolt, location: fakeLoc(1, 64, 1), getBlockHit: () => ({ block: blockAt('minecraft:stone', 1, 63, 1) }) });
hold('ecr:queens_fang');
fire('after', 'entityHitEntity', { damagingEntity: player, hitEntity: new FakeEntity('minecraft:zombie', ow) });
hold('ecr:colossus_core', 2);
fire('after', 'itemUse', { source: player, itemStack: player.equip.get('Mainhand') });
player.equip.set('Head', new ItemStack('ecr:hollow_crown'));
runTicks(30);

// 4) deaths: player killed by each custom mob / projectile
for (const t of ['ecr:gravewalker', 'ecr:revenant', 'ecr:cave_weaver', 'ecr:sporeling', 'ecr:hollow_king', 'ecr:mosswood_colossus', 'ecr:silkqueen', 'ecr:ashen_warg', 'ecr:voidweaver', 'ecr:eclipse_sovereign']) {
    const killer = new FakeEntity(t, ow);
    for (const projType of [undefined, 'ecr:bone_shard']) {
        fire('after', 'entityDie', { deadEntity: player, damageSource: { cause: 'entityAttack', damagingEntity: killer, damagingProjectile: projType ? new FakeEntity(projType, ow) : undefined } });
    }
}
const chat = logs.filter((l) => l.startsWith('[chat]'));
if (chat.length < 20) note(`deaths: expected a custom message per mob, only ${chat.length} chat lines`);
if (chat.some((l) => l.includes('%v') || l.includes('undefined'))) note('deaths: a message still has a placeholder or undefined');

// 5) crops, blocks, mining, tools, stasis, trees events with a spread of fake interactions
const crop = blockAt('ecr:tomato_crop', 60, 64, 60);
registered['ecr:crop'].onRandomTick({ block: crop, dimension: ow });
registered['ecr:crop'].onPlayerInteract({ block: crop, player, dimension: ow });
hold('minecraft:bone_meal', 5);
fire('before', 'playerInteractWithBlock', { player, block: crop, itemStack: player.equip.get('Mainhand'), isFirstEvent: true, cancel: false });
hold('ecr:tomato_seeds', 3);
fire('before', 'playerInteractWithBlock', { player, block: blockAt('minecraft:farmland', 61, 63, 60), itemStack: player.equip.get('Mainhand'), isFirstEvent: true, cancel: false });
hold('minecraft:ender_pearl');
fire('before', 'playerInteractWithBlock', { player, block: blockAt('ecr:stasis_chamber', 70, 64, 70), itemStack: player.equip.get('Mainhand'), isFirstEvent: true, cancel: false });
hold('minecraft:fishing_rod');
fire('after', 'itemUse', { source: player, itemStack: player.equip.get('Mainhand') });
hold('ecr:pyrelite_sword');
fire('after', 'entityHitEntity', { damagingEntity: player, hitEntity: new FakeEntity('minecraft:zombie', ow) });
fire('after', 'playerBreakBlock', { player, block: blockAt('ecr:azurite_ore', 80, 20, 80), brokenBlockPermutation: new FakePerm('ecr:azurite_ore'), itemStackBeforeBreak: player.equip.get('Mainhand'), dimension: ow });
fire('before', 'playerBreakBlock', { player, block: blockAt('ecr:azurite_ore', 81, 20, 80), itemStack: new ItemStack('minecraft:iron_pickaxe'), cancel: false });
fire('after', 'itemCompleteUse', { source: player, itemStack: new ItemStack('ecr:tomato_soup') });
fire('after', 'playerPlaceBlock', { player, block: blockAt('ecr:jacaranda_sapling', 90, 64, 90) });
for (const n of ['ecr:altar', 'ecr:stasis_chamber', 'ecr:stasis_plate', 'ecr:openable', 'ecr:plate', 'ecr:button', 'ecr:leaves', 'ecr:sapling']) {
    if (registered[n]) for (const evn of ['onPlayerInteract', 'onStepOn', 'onStepOff', 'onRandomTick', 'onTick', 'onPlace', 'onPlayerBreak', 'onEntityFallOn', 'beforeOnPlayerPlace']) {
        if (registered[n][evn]) call(registered[n][evn], `${n}.${evn}`, { block: blockAt('ecr:jacaranda_door', 95, 64, 95), player, dimension: ow, entity: player, face: 'Up' });
    }
}
flush();
runTicks(120);


// 6) story: journal gift, grove -> kills -> offerings -> altar -> Hanae (all three phases, fog, mercy) -> Sovereign chapter
const hero = new FakePlayer(ow, 'Wayfarer', 'p9');
ow.players.push(hero);
world.getAllPlayers = () => [hero];
fire('after', 'playerSpawn', { player: hero, initialSpawn: true });
if (![...hero.inv.values()].some((i) => i.typeId === 'ecr:wayfarers_journal')) note('story: a new player did not receive the Wayfarer\'s Journal');
const story = () => JSON.parse(hero.props['dp:ecr:story'] || '{"step":0}');
const tickAll = async (n) => { runTicks(n); await new Promise((r) => setTimeout(r, 0)); };
hero.equip.set('Mainhand', [...hero.inv.values()].find((i) => i.typeId === 'ecr:wayfarers_journal'));
fire('after', 'itemUse', { source: hero, itemStack: hero.equip.get('Mainhand') });
await tickAll(1);
ow.biome = 'minecraft:cherry_grove';
await tickAll(200);
if (story().step !== 1) note(`story: lingering in a cherry grove should reach step 1, got ${JSON.stringify(story())}`);
for (let i = 0; i < 3; i++) fire('after', 'entityDie', { deadEntity: new FakeEntity('ecr:gravewalker', ow), damageSource: { cause: 'entityAttack', damagingEntity: hero } });
for (let i = 0; i < 2; i++) fire('after', 'entityDie', { deadEntity: new FakeEntity('ecr:cave_weaver', ow), damageSource: { cause: 'entityAttack', damagingEntity: hero } });
if (story().step !== 2) note(`story: 3 Gravewalkers + 2 Cave Weavers should reach step 2, got ${JSON.stringify(story())}`);
// offerings: first refuse (nothing in the pack), then accept
formQueue.push(0); hero.equip.set('Mainhand', [...hero.inv.values()].find((i) => i.typeId === 'ecr:wayfarers_journal'));
fire('after', 'itemUse', { source: hero, itemStack: hero.equip.get('Mainhand') }); await tickAll(1);
if (story().step !== 2) note('story: offerings were accepted with an empty pack');
let slot = 20;
for (const [id, n] of [['minecraft:pink_petals', 16], ['ecr:silk_gland', 1], ['ecr:hollow_bone', 1], ['ecr:spore_cluster', 1]]) hero.inv.set(slot++, new ItemStack(id, n));
formQueue.push(0);
fire('after', 'itemUse', { source: hero, itemStack: hero.equip.get('Mainhand') }); await tickAll(1);
if (story().step !== 3) note(`story: presenting the offerings should reach step 3, got ${JSON.stringify(story())}`);
if (![...hero.inv.values()].some((i) => i.typeId === 'ecr:veiled_mirror')) note('story: no Veiled Mirror was granted');
// altar: day refuses, step 3 -> 4, night + cherry grove + mirror starts the fight
const altar = blockAt('ecr:blossom_altar', 100, 64, 100);
hero.location = fakeLoc(100, 64, 103);                                           // standing at the shrine
const mirror = [...hero.inv.values()].find((i) => i.typeId === 'ecr:veiled_mirror');
hero.equip.set('Mainhand', mirror);
timeOfDay = 6000;
registered['ecr:blossom_altar'].onPlayerInteract({ player: hero, block: altar, dimension: ow });
if (story().step !== 4) note('story: touching the altar at step 3 should reach step 4');
if (!hero.equip.get('Mainhand')) note('story: the mirror was spent in daylight');
timeOfDay = 14000;
registered['ecr:blossom_altar'].onPlayerInteract({ player: hero, block: altar, dimension: ow });
if (hero.equip.get('Mainhand')) note('story: the mirror was not consumed by the ritual');
await tickAll(120);
const hanae = ow.entities.find((e) => e.typeId === 'ecr:veiled_blossom');
if (!hanae) note('boss: the Veiled Blossom did not spawn after the ritual');
else {
    hero.health = 100;
    const bladesBefore = ow.spawned.filter((t) => t === 'ecr:petal_blade').length;
    hanae.health = 90; await tickAll(160);                                       // phase 2 (Falling Blossoms, vexes)
    hanae.health = 20; await tickAll(160);                                       // phase 3 (Eclipse Bloom, spiral)
    const bladesMid = ow.spawned.filter((t) => t === 'ecr:petal_blade').length;
    if (bladesMid <= bladesBefore) note('boss: Hanae never fired a petal');
    for (const t of ['ecr:blossom_vex', 'ecr:blossom_echo']) if (!ow.spawned.includes(t)) note(`boss: Hanae never summoned ${t}`);
    if (!(hero.cmds || []).some((c) => c.startsWith('fog @s push ecr:blossom_veil'))) note('boss: the fog was never pushed to the player');
    if (!hero.cam.some((c) => c[0] === 'set') || !hero.cam.some((c) => c[0] === 'clear')) note('cinematic: the intro never moved or released the camera');
    if (!(hero.cmds || []).includes('hud @s hide') || !(hero.cmds || []).includes('hud @s reset')) note('cinematic: the HUD was not hidden and restored');
    if (!hero.perms.some((x) => x[1] === false) || hero.perms.at(-1)[1] !== true) note('cinematic: input permissions were not locked and restored');
    if (!hero.sent.some((m) => m[0] === 'bar' && String(m[1]).includes('\uE420'))) note('bossbar: the themed bar never reached the action bar');
    if (!(hero.sounds || []).includes('ecr.music.veiled_blossom')) note('music: the Veiled Blossom theme never played for the player');
    if (!(hero.cmds || []).some((c) => c.startsWith('fog @s push ecr:eclipse_bloom'))) note('boss: the Eclipse Bloom fog was never pushed');
    // mercy: a nearly dead player stops all attacks
    hero.health = 4; await tickAll(20);
    const bladesBeforeMercy = ow.spawned.filter((t) => t === 'ecr:petal_blade').length;
    await tickAll(60);
    if (ow.spawned.filter((t) => t === 'ecr:petal_blade').length !== bladesBeforeMercy) note('boss: Hanae attacked a player who was almost dead (mercy rule failed)');
    hero.health = 100;
    hanae.health = 0; hanae.isValid = false;
    fire('after', 'entityDie', { deadEntity: hanae, damageSource: { cause: 'entityAttack', damagingEntity: hero } });
    await tickAll(2);
    if (!(hero.cmds || []).some((c) => c.startsWith('fog @s remove ecr_hanae'))) note('boss: the fog was not removed when Hanae fell');
    if (!(hero.cmds || []).some((c) => c.startsWith('stopsound @s ecr.music.veiled_blossom'))) note('music: the theme was not stopped when Hanae fell');
    if (story().step !== 5) note(`story: defeating Hanae should reach step 5, got ${JSON.stringify(story())}`);
}
fire('after', 'entityDie', { deadEntity: new FakeEntity('ecr:eclipse_sovereign', ow), damageSource: { cause: 'entityAttack', damagingEntity: hero } });
await tickAll(2);
if (story().step !== 6) note(`story: defeating the Eclipse Sovereign should complete chapter II, got ${JSON.stringify(story())}`);
if (!(story().pages || []).includes('eclipse_sovereign') || !(story().pages || []).includes('veiled_blossom')) note('story: boss lore pages were not unlocked');

// 7) Chapter III - the Silent Choir: verses -> fork -> chimes (wrong, then right) -> lectern -> Frost Cantor (phases, fog, bar, music) -> Seal III
const setB = (id, x, y, z, st) => { const b = blockAt(id, x, y, z); b.permutation = new FakePerm(id, st); return b; };
hero.location = fakeLoc(300, 64, 300);
ow.biome = 'minecraft:ice_plains';
fire('after', 'scriptEventReceive', { id: 'ecr:story', message: 'road c3 0', sourceEntity: hero });
if (!hero.inv.size || ![...hero.inv.values()].some((i) => i.typeId === 'ecr:tuning_fork')) fire('after', 'scriptEventReceive', { id: 'ecr:story', message: 'journal', sourceEntity: hero });
for (let v = 0; v < 4; v++) registered['ecr:verse_stone'].onPlayerInteract({ player: hero, block: setB('ecr:verse_stone', 320 + v, 64, 300, { 'ecr:verse': v }), dimension: ow });
await tickAll(40);
if (story().c3 !== 1) note(`story: reading all four verses should open step 2 of Road III, got ${JSON.stringify(story())}`);
const fork = new ItemStack('ecr:tuning_fork'); hero.equip.set('Mainhand', fork);
setB('ecr:chime_dawn', 340, 64, 300, {});
fire('after', 'itemUse', { source: hero, itemStack: fork }); await tickAll(30);
if (!hero.sent.some((m) => m[0] === 'bar' && String(m[1]).includes('blocks to the'))) note('puzzle: the Tuning Fork never reported the direction of the cathedral');
const strikeChime = (n) => registered['ecr:chime'].onPlayerInteract({ player: hero, block: setB(`ecr:chime_${n}`, 330, 64, 300, {}), dimension: ow });
strikeChime('zenith');                                                                  // wrong first note
if (story().chimes && story().chimes.length) note('puzzle: a wrong chime did not reset the sequence');
for (const n of ['dawn', 'zenith', 'dusk', 'midnight']) strikeChime(n);
await tickAll(40);
if (story().c3 !== 2) note(`puzzle: striking the chimes in the sun's road should reach Road III step 3, got ${JSON.stringify(story())}`);
const lec = setB('ecr:choir_lectern', 340, 60, 340, {});
hero.location = fakeLoc(340, 60, 343);
registered['ecr:choir_lectern'].onPlayerInteract({ player: hero, block: lec, dimension: ow });
await tickAll(60);
const cantor = ow.entities.find((e) => e.typeId === 'ecr:frost_cantor');
if (!cantor) note('boss: the Frost Cantor did not spawn at the lectern');
else {
    hero.health = 100;
    await tickAll(200);                                                                 // phase 1 (aria, rings, choir)
    cantor.health = 60; await tickAll(260);                                             // phase 2 (icicles, whiteout)
    cantor.health = 20; await tickAll(400);                                             // phase 3 (spiral, final verse)
    if (!ow.spawned.includes('ecr:frost_note')) note('boss: the Cantor never fired a frozen note');
    if (!ow.spawned.includes('ecr:hoarbone') && !ow.spawned.includes('ecr:rimewalker')) note('boss: the Cantor never called her choir');
    if (!(hero.cmds || []).some((c) => c.startsWith('fog @s push ecr:cantor_whiteout'))) note('boss: the whiteout fog was never pushed');
    if (!(hero.cmds || []).some((c) => c.startsWith('fog @s push ecr:cantor_requiem'))) note('boss: the requiem fog was never pushed');
    if (!(hero.sounds || []).includes('ecr.music.frost_cantor')) note('music: the Frost Cantor theme never played');
    if (!hero.sent.some((m) => m[0] === 'bar' && String(m[1]).includes('\uE428'))) note('bossbar: the Cantor bar never appeared');
    cantor.health = 0; cantor.isValid = false;
    fire('after', 'entityDie', { deadEntity: cantor, damageSource: { cause: 'entityAttack', damagingEntity: hero } });
    await tickAll(2);
    if (!(hero.cmds || []).some((c) => c.startsWith('fog @s remove ecr_cantor'))) note('boss: the Cantor fog was not removed');
    if (story().c3 !== 3) note(`story: defeating the Frost Cantor should finish Road III, got ${JSON.stringify(story())}`);
    if (!(story().pages || []).includes('frost_cantor')) note('story: the Ysolde lore page was not unlocked');
}

// 8) Chapter IV - the Lantern in the Mire: offerings -> sconces (wrong, then right) -> marsh altar -> Morwen (light, mirages, bar, music) -> Seal IV
ow.biome = 'minecraft:swamp';
hero.location = fakeLoc(500, 62, 500);
slot = 20;
for (const [id, n] of [['ecr:wisp_essence', 6], ['minecraft:lantern', 1]]) hero.inv.set(slot++, new ItemStack(id, n));
formQueue.push(1); formQueue.push(0);                                                    // journal -> Road IV -> present offerings
hero.equip.set('Mainhand', new ItemStack('ecr:wayfarers_journal'));
fire('after', 'itemUse', { source: hero, itemStack: hero.equip.get('Mainhand') }); await tickAll(2);
if (story().c4 !== 1) note(`story: presenting 6 Wisp Essence + a Lantern should give Road IV step 2, got ${JSON.stringify(story())}`);
if (![...hero.inv.values()].some((i) => i.typeId === 'ecr:keepers_lantern')) note("story: no Keeper's Lantern was granted");
const lantern = new ItemStack('ecr:keepers_lantern'); hero.equip.set('Mainhand', lantern);
const sc = (n) => registered['ecr:sconce'].onPlayerInteract({ player: hero, block: setB(`ecr:sconce_${n}`, 510, 63, 500, { 'ecr:lit': 0 }), dimension: ow });
const wispsBefore = ow.spawned.filter((t) => t === 'ecr:mire_wisp').length;
sc('moon');                                                                              // wrong first
if (ow.spawned.filter((t) => t === 'ecr:mire_wisp').length <= wispsBefore) note('puzzle: a wrong sconce did not stir the wisps');
if (!hero.effects.some((e) => e[0] === 'darkness')) note('puzzle: a wrong sconce did not darken the player');
for (const n of ['eye', 'star', 'moon']) sc(n);
await tickAll(40);
if (story().c4 !== 2) note(`puzzle: lighting eye, star, moon should reach Road IV step 3, got ${JSON.stringify(story())}`);
timeOfDay = 14000;
const marsh = setB('ecr:marsh_altar', 520, 62, 520, {});
hero.location = fakeLoc(520, 62, 523);
registered['ecr:marsh_altar'].onPlayerInteract({ player: hero, block: marsh, dimension: ow });
await tickAll(60);
const morwen = ow.entities.find((e) => e.typeId === 'ecr:mire_lantern');
if (!morwen) note('boss: the Mire Lantern did not spawn at the Marsh Altar');
else {
    hero.health = 100;
    await tickAll(240);
    morwen.health = 60; await tickAll(300);
    morwen.health = 20; await tickAll(300);
    if (!ow.spawned.includes('ecr:wisp_bolt')) note('boss: Morwen never fired foxfire');
    if (!ow.spawned.includes('ecr:mire_wisp')) note('boss: Morwen never sent wisps');
    if (!ow.spawned.includes('ecr:mire_decoy')) note('boss: Morwen never made a lantern mirage');
    if (!hero.effects.some((e) => e[0] === 'darkness')) note('boss: Morwen never snuffed an unlit player');
    if (!(hero.cmds || []).some((c) => c.startsWith('fog @s push ecr:fen_hollow'))) note('boss: the hollow fog was never pushed');
    if (!(hero.sounds || []).includes('ecr.music.mire_lantern')) note('music: the Mire Lantern theme never played');
    if (!hero.sent.some((m) => m[0] === 'bar' && String(m[1]).includes('\uE430'))) note('bossbar: the Morwen bar never appeared');
    const decoy = ow.entities.find((e) => e.typeId === 'ecr:mire_decoy');
    if (decoy) { decoy.isValid = false; fire('after', 'entityDie', { deadEntity: decoy, damageSource: { cause: 'entityAttack', damagingEntity: hero } }); }
    morwen.health = 0; morwen.isValid = false;
    fire('after', 'entityDie', { deadEntity: morwen, damageSource: { cause: 'entityAttack', damagingEntity: hero } });
    await tickAll(2);
    if (!(hero.cmds || []).some((c) => c.startsWith('fog @s remove ecr_morwen'))) note('boss: the fen fog was not removed');
    if (story().c4 !== 3) note(`story: defeating Morwen should finish Road IV, got ${JSON.stringify(story())}`);
    if (!(story().pages || []).includes('mire_lantern')) note('story: the Morwen lore page was not unlocked');
}

// 9) new mobs, gear and tablets
for (const t of ['ecr:rimewalker', 'ecr:hoarbone', 'ecr:mirewalker', 'ecr:lanternbone', 'ecr:mire_wisp']) { const m = new FakeEntity(t, ow, fakeLoc(40, 64, 40)); ow.entities.push(m); }
runTicks(60);
fire('after', 'entityDie', { deadEntity: new FakeEntity('ecr:mirewalker', ow), damageSource: { cause: 'entityAttack', damagingEntity: hero } });
for (const w of ['ecr:frostsong', 'ecr:mirelight_scythe', 'ecr:rimesteel_sword', 'ecr:glacite_sword', 'ecr:wispsteel_axe']) {
    const it = new ItemStack(w); hero.equip.set('Mainhand', it);
    fire('after', 'itemUse', { source: hero, itemStack: it });
    for (let k = 0; k < 4; k++) fire('after', 'entityHitEntity', { damagingEntity: hero, hitEntity: new FakeEntity('minecraft:zombie', ow, hero.location) });
}
for (let t = 0; t < 12; t++) registered['ecr:lore_tablet'].onPlayerInteract({ player: hero, block: setB('ecr:lore_tablet', 600 + t, 64, 600, { 'ecr:text': t }), dimension: ow });
fire('after', 'scriptEventReceive', { id: 'ecr:bossbar', message: 'off', sourceEntity: hero });
fire('after', 'scriptEventReceive', { id: 'ecr:cinematic', message: 'off', sourceEntity: hero });
fire('after', 'scriptEventReceive', { id: 'ecr:bossbar', message: 'on', sourceEntity: hero });
fire('after', 'scriptEventReceive', { id: 'ecr:cinematic', message: 'on', sourceEntity: hero });
world.getAllPlayers = oldAll;

// ------------------------------------------------------------------ verdict
const swallowed = logs.filter((l) => l.startsWith('[ecr]'));
for (const l of swallowed) note(`swallowed error ${l}`);
const other = logs.filter((l) => !l.startsWith('[chat]') && !l.startsWith('[ecr]') && !l.includes('ready - Tech Bytes Design'));
console.warn = origWarn;
for (const l of other) console.log('  log:', l);
console.log(`spawned during run: ${ow.spawned.length} entities/items (${[...new Set(ow.spawned)].slice(0, 12).join(', ')}...)`);
if (failures.length) {
    console.log(`\nMOCK RUN: ${failures.length} problem(s)`);
    for (const f of failures) console.log('  X', f);
    process.exit(1);
}
console.log('\nMOCK RUN: 0 problem(s)');
