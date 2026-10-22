// Custom block components: stasis blocks, altar, wood-set behaviours (doors, gates, plates, buttons, leaves, saplings)
import { world, system, ItemStack, BlockPermutation } from '@minecraft/server';
import {
    NS, safe, getState, setState, say, msg, playSound, spawnParticle, runLater, mainhand, consumeMainhand, isCreative, rand,
} from './util.js';
import * as stasis from './stasis.js';
import { startRitual } from './boss.js';
import { growTree } from './trees.js';
import { registerSanctumComponent } from './sanctum.js';
import { registerCropComponent, boneMealCrop, isCropBlock } from './crops.js';
import { registerBlossomAltar } from './story.js';
import { registerPuzzleBlocks } from './puzzle.js';

const SIGIL = `${NS}:eclipse_sigil`;

function toggleOpen(block, player) {
    setOpen(block, getState(block, 'ecr:open') === 1 ? 0 : 1);
}

function setOpen(block, next) {
    const parts = safe(() => block.getParts && block.getParts());
    if (parts && parts.length) {
        for (const p of parts) safe(() => p.setPermutation(p.permutation.withState('ecr:open', next)));
    } else {
        setState(block, 'ecr:open', next);
    }
    const c = { x: block.location.x + 0.5, y: block.location.y + 0.5, z: block.location.z + 0.5 };
    playSound(block.dimension, next ? 'random.door_open' : 'random.door_close', c, { volume: 0.9, pitch: 0.95 + Math.random() * 0.1 });
}

function hasLogNear(block, r) {
    const { x, y, z } = block.location;
    const dim = block.dimension;
    for (let dx = -r; dx <= r; dx++) {
        for (let dy = -r; dy <= r; dy++) {
            for (let dz = -r; dz <= r; dz++) {
                if (Math.abs(dx) + Math.abs(dy) + Math.abs(dz) > r + 2) continue;
                const b = safe(() => dim.getBlock({ x: x + dx, y: y + dy, z: z + dz }));
                if (!b) continue;
                const id = b.typeId;
                if (/_(log|wood|stem|hyphae)$/.test(id)) return true;
            }
        }
    }
    return false;
}

// ----------------------------------------------------------------------------- pressure plate registry + polling
const PLATE_KEY = 'ecr:wplates_v1';
let PLATES = null;
function plates() {
    if (PLATES) return PLATES;
    const raw = safe(() => world.getDynamicProperty(PLATE_KEY));
    try { PLATES = new Set(typeof raw === 'string' ? JSON.parse(raw) : []); } catch (e) { PLATES = new Set(); }
    return PLATES;
}
function platesSave() {
    safe(() => world.setDynamicProperty(PLATE_KEY, JSON.stringify([...plates()])), 'platesSave');
}
function plateAdd(dimId, loc) {
    plates().add(`${dimId}|${loc.x}|${loc.y}|${loc.z}`);
    platesSave();
}
function plateRemove(dimId, loc) {
    if (plates().delete(`${dimId}|${loc.x}|${loc.y}|${loc.z}`)) platesSave();
}

function pollPlates() {
    let dirty = false;
    for (const key of [...plates()]) {
        const [dimId, x, y, z] = key.split('|');
        const dim = safe(() => world.getDimension(dimId));
        const b = dim && safe(() => dim.getBlock({ x: +x, y: +y, z: +z }));
        if (!b) continue;                                              // chunk not loaded
        if (!/^ecr:[a-z]+_pressure_plate$/.test(b.typeId)) { plates().delete(key); dirty = true; continue; }
        const near = safe(() => dim.getEntities({ location: { x: +x + 0.5, y: +y + 0.25, z: +z + 0.5 }, maxDistance: 0.72 })) || [];
        const on = near.some((en) => en.typeId !== 'minecraft:xp_orb' || true);
        const pressed = getState(b, 'ecr:pressed') === 1;
        if (on && !pressed) {
            setState(b, 'ecr:pressed', 1);
            playSound(dim, 'random.click', { x: +x + 0.5, y: +y, z: +z + 0.5 }, { volume: 0.6, pitch: 0.8 });
        } else if (!on && pressed) {
            setState(b, 'ecr:pressed', 0);
            playSound(dim, 'random.click', { x: +x + 0.5, y: +y, z: +z + 0.5 }, { volume: 0.6, pitch: 0.7 });
        }
    }
    if (dirty) platesSave();
}

export function registerBlockComponents(reg) {
    registerSanctumComponent(reg);
    registerCropComponent(reg);
    registerBlossomAltar(reg);
    registerPuzzleBlocks(reg);
    reg.registerCustomComponent(`${NS}:altar`, {
        onPlayerInteract(e) {
            const it = mainhand(e.player);
            if (it && it.typeId === SIGIL) {
                startRitual(e.block, e.player);
            } else {
                say(e.player, '§5The altar hums...  §7Offer an §dEclipse Sigil§7 to awaken the Sovereign.');
            }
        },
    });

    reg.registerCustomComponent(`${NS}:stasis_chamber`, {
        onPlayerBreak(e) {
            const loaded = safe(() => e.brokenBlockPermutation.getState('ecr:loaded') === 1);
            stasis.chamberBroken(e.dimension.id, e.block.location.x, e.block.location.y, e.block.location.z, loaded);
        },
    });

    reg.registerCustomComponent(`${NS}:stasis_plate`, {
        onPlace(e) {
            stasis.registerPlate(e.block);
        },
        onPlayerBreak(e) {
            stasis.plateBroken(e.dimension.id, e.block.location.x, e.block.location.y, e.block.location.z);
        },
    });

    reg.registerCustomComponent(`${NS}:openable`, {
        onPlayerInteract(e) {
            if (e.player.isSneaking) return;
            toggleOpen(e.block, e.player);
        },
        // doors, gates and trapdoors react to redstone like vanilla
        onRedstoneUpdate(e) {
            const want = e.powerLevel > 0 ? 1 : 0;
            if ((getState(e.block, 'ecr:open') === 1 ? 1 : 0) === want) return;
            setOpen(e.block, want);
        },
    });

    // Pressure plates are non-solid, so step events are unreliable: plates register themselves and are polled.
    reg.registerCustomComponent(`${NS}:plate`, {
        onPlace(e) {
            plateAdd(e.dimension.id, e.block.location);
        },
        onPlayerBreak(e) {
            plateRemove(e.dimension.id, e.block.location);
        },
        onBreak(e) {
            plateRemove(e.dimension.id, e.block.location);
        },
    });

    reg.registerCustomComponent(`${NS}:button`, {
        onPlayerInteract(e) {
            const b = e.block;
            if (getState(b, 'ecr:pressed') === 1) return;
            setState(b, 'ecr:pressed', 1);
            playSound(b.dimension, 'random.click', { x: b.location.x + 0.5, y: b.location.y + 0.5, z: b.location.z + 0.5 }, { volume: 0.7, pitch: 0.9 });
            runLater(30, () => {
                if (b.isValid && getState(b, 'ecr:pressed') === 1) {
                    setState(b, 'ecr:pressed', 0);
                    playSound(b.dimension, 'random.click', { x: b.location.x + 0.5, y: b.location.y + 0.5, z: b.location.z + 0.5 }, { volume: 0.6, pitch: 0.7 });
                }
            });
        },
    });

    reg.registerCustomComponent(`${NS}:leaves`, {
        beforeOnPlayerPlace(e) {
            // leaves placed by players never decay (like vanilla persistent leaves)
            safe(() => { e.permutationToPlace = e.permutationToPlace.withState('ecr:persistent', 1); });
        },
        onRandomTick(e) {
            const b = e.block;
            if (getState(b, 'ecr:persistent') === 1) return;
            if (hasLogNear(b, 4)) return;
            const { x, y, z } = b.location;
            safe(() => e.dimension.runCommand(`setblock ${x} ${y} ${z} air destroy`));
        },
    });

    reg.registerCustomComponent(`${NS}:sapling`, {
        onRandomTick(e) {
            if (Math.random() < 1 / 7) growTree(e.block);
        },
    });
}

function boneMeal(player, b) {
    consumeMainhand(player, 1);
    const c = { x: b.location.x + 0.5, y: b.location.y + 0.5, z: b.location.z + 0.5 };
    for (let i = 0; i < 8; i++) spawnParticle(b.dimension, 'minecraft:crop_growth_emitter', { x: c.x + rand(-0.4, 0.4), y: c.y + rand(0, 0.5), z: c.z + rand(-0.4, 0.4) });
    playSound(b.dimension, 'item.bone_meal.use', c, { volume: 1, pitch: 1 });
    if (Math.random() < 0.45) {
        const r = growTree(b);
        if (r === 'space') say(player, '§7There is not enough room for this tree to grow.');
        else if (r === 'soil') say(player, '§7Saplings need dirt, grass or moss to grow.');
    }
}

// ----------------------------------------------------------------------------- interaction events that need cancelling
export function initBlockEvents() {
    system.runInterval(() => safe(pollPlates, 'pollPlates'), 4);

    // An ender pearl used while aiming at a Stasis Chamber binds instead of being thrown
    world.beforeEvents.itemUse.subscribe((ev) => {
        const it = ev.itemStack;
        if (!it || it.typeId !== 'minecraft:ender_pearl') return;
        const hit = safe(() => ev.source.getBlockFromViewDirection({ maxDistance: 6 }));
        const blk = hit && hit.block;
        if (blk && blk.typeId === stasis.CHAMBER) {
            ev.cancel = true;
            const p = ev.source;
            system.run(() => safe(() => stasis.loadChamber(p, blk), 'loadChamber(itemUse)'));
        }
    });
    world.beforeEvents.playerInteractWithBlock.subscribe((ev) => {
        const b = ev.block;
        const player = ev.player;
        const id = b.typeId;
        const item = ev.itemStack;
        if (id === stasis.CHAMBER) {
            if (item && item.typeId === 'minecraft:ender_pearl') {
                ev.cancel = true;                      // do not throw the pearl, bind it
                system.run(() => safe(() => stasis.loadChamber(player, b), 'loadChamber'));
            } else if (!item && player.isSneaking) {
                ev.cancel = true;
                system.run(() => safe(() => stasis.retrievePearl(player, b), 'retrieve'));
            } else if (!item) {
                system.run(() => safe(() => stasis.loadChamber(player, b), 'chamberHint'));
            }
            return;
        }
        if (isCropBlock(id)) {
            if (item && item.typeId === 'minecraft:bone_meal') {
                ev.cancel = true;
                system.run(() => safe(() => boneMealCrop(player, b), 'boneMealCrop'));
            }
            return;
        }
        if (/^ecr:[a-z]+_sapling$/.test(id)) {
            if (item && item.typeId === 'minecraft:bone_meal') {
                ev.cancel = true;
                system.run(() => safe(() => boneMeal(player, b), 'boneMeal'));
            }
            return;
        }
        if (id === `${NS}:eclipse_altar` && item && item.typeId === SIGIL) {
            ev.cancel = true;
            system.run(() => safe(() => startRitual(b, player), 'ritual'));
        }
    });
}
