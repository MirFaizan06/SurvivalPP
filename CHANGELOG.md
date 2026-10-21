# Changelog

All notable changes to **Eclipsed Realms: Chronicles of the Seven Seals** (formerly "Survival++ | Eclipsed Realms") (Tech Bytes Design). Versions follow `major.minor.patch`; the pack version is set in `tools/version.json`.

## [1.4.1]

### Fixed
- **Gravewalkers and Cave Weavers never appeared in Cherry Groves**, so Chapter I step 2 ("Tainted Roots") could not be completed by exploring. Gravewalkers now spawn in cherry groves (on the surface, in the dark) and Cave Weavers creep up there at night as well as underground.

## [1.4.0] - "Chronicles Update"

### Renamed
- **Survival++ | Eclipsed Realms is now *Eclipsed Realms: Chronicles of the Seven Seals*** - it is a story-driven add-on. The release file is `EclipsedRealms_v1.4.0.mcaddon`. (The GitHub repository keeps its old URL.)

### Added
- **The story:** the **Wayfarer's Journal** (given once to every player; progress saved per player; re-craftable) with one clue at a time, a progress tracker, an offerings step and unlockable **lore pages**. Chapter I leads to the Veiled Blossom, Chapter II to the Eclipse Sovereign. Chapters are data, so more can be added easily. Full history in `LORE.md` and on the docs site.
- **The Veiled Blossom (Hanae)** - the first main boss: a gentle early-game fight (260 HP) with a floating shrine-maiden model, three phases, petal fans, Mirror Step, Veiled Echoes, custom **Blossom Vexes**, falling-blossom rings, a petal spiral, **fog that changes per phase**, pentatonic shrine bells, spoken warnings, and a mercy rule (she stops when a player is badly hurt). A corrupted texture appears in her last phase.
- **Hanae's Shrine** (torii gate, path, pavilion, pond, blossom trees, loot) generating in Cherry Groves, and the **Blossom Altar** block.
- **Veilbloom Regalia** (Crown, Haori, Hakama, Geta): pink armour with netherite-level protection, set bonus, repaired with **Veilbloom Shards**; **Veiled Mirror**, **Seal of the Blossom** and the journal as items.
- **Custom 3D armour for every tier** (Azurite crystal, Pyrelite horned, Eclipsite void, Veilbloom) - real geometry and painted textures instead of recoloured vanilla layers; inventory icons are renders of the pieces.
- **Custom sword designs** for Azurite, Pyrelite and Eclipsite (32x32 sprites).
- **Themed boss health bars** for the Eclipse Sovereign, Hollow King, Mosswood Colossus, Silkqueen and the Veiled Blossom (vanilla bar stays underneath as a fallback).
- **New thumbnail** featuring the Veiled Blossom.
- Lore pages for the Hollow Lords, Hanae and the Eclipse Sovereign. The side bosses are now canon "Hollow Lords"; the Eclipse Sovereign is the second main boss.

### Tooling
- Story + boss runtime tests in the mock run (journal gift, grove, kills, offerings, altar, all three boss phases, fog push/remove, mercy rule, Chapter II).
- Lint: UI textures, fog definitions pushed by scripts, `entity_alphablend`.

## [1.3.0] - "Adventure Update" (Version 1 final)

### Added
- **Ten adventure structures** that generate naturally in new chunks, with tiered loot, traps and monster spawners:
  Bandit Lookout, Sunken Well (easy) - Ruined Watch Keep, Dune Vault, Thorn Shrine, Frost Cairn (medium) - Highland Bastion, Sunken Crypt, Pyre Bastion (Nether), Eclipse Vault (End) (hard).
- Traps: TNT-under-pressure-plate floors, fall-in shafts, spike pits, powder-snow pits, lava vaults/moats, silverfish (infested) walls, cobwebs and spawners that use the pack's own monsters (Revenant, Gravewalker, Cave Weaver, Ashen Warg, Voidweaver).
- 20 new chest loot tables in five tiers (food and iron up to netherite, Elytra, Totems, enchanted gear, Azurite/Pyrelite/Eclipsite, boss relics at rising odds).
- **Bug-sweep tooling:** structure block/state validator against Mojang's vanilla block data (`lint3`), entity + spawn-rule schemas, Molang/animation/geometry/texture/biome-tag/loot/lang cross-checks (`lint4`), a runtime smoke test that boots every script against a fake game and fires events through each module (`python tools/dev.py test`), isometric structure previews.
- New docs page: Adventure Structures.

### Fixed
- **Chests in structures used a block state that does not exist** (`facing_direction`, so the chest orientation was probably ignored); they now use `minecraft:cardinal_direction` (also fixed in the v1 End shrine and the v1.2 structures).
- **Sporeling spawn rule used a biome tag that no biome has** (`mushroom_island`), now `mooshroom_island`; Highland Yak can spawn on snow layers.
- Removed animations that were generated but never used.

### Verified (offline)
Build, official-schema lint, structure palette lint, entity/spawn schemas, TypeScript check of all scripts and a runtime smoke test all pass. In-game behaviour (placement, trap mechanics, particles) could not be tested in this environment.

## [1.2.0] - 2026-10-21 - "Overworld Update"

### Added
- **Bosses (3, Overworld):** Hollow King, Mosswood Colossus, Silkqueen - custom models, glow textures, animations, 3 phases, boss bars, unique abilities, loot and custom death messages. Condition-based summoning (relic + ritual block + time/place).
- **Hostile mobs (4):** Gravewalker, Revenant (ranged/melee, Bone Shard projectile), Cave Weaver (climbs, Web Bolt projectile that leaves temporary webs), Sporeling (spore clouds).
- **Animals (4):** Meadow Deer (stags have antlers), Highland Yak (milkable), Wild Boar (defends its herd), Pheasant (sheds feathers). Breeding, babies, panic/defence behaviour, loot, biome spawn rules, spawn eggs.
- **Stones (4):** Marlstone, Slate, Verdite, Umbrastone - generate in blobs inside normal stone plus biome boosts; polished / bricks / stairs / slabs / double slabs; crafting + stonecutter recipes.
- **Crops (5) and wild plants:** Tomato, Corn, Strawberry, Chili, Oats - 4 growth stages, light + hydrated-farmland rules, bone meal, right-click harvest & replant, Fortune, wild patches in the world.
- **Foods (13):** Roasted Corn, Oat Bread, Strawberry Pie, Tomato Soup, Oat Porridge, Chili Stew, Hunter's Stew, raw/cooked Venison, Yak Meat and Pheasant - with buff effects.
- **Items:** Boar Tusk, Grave Dust, Hollow Bone, Silk Gland, Spore Cluster; relics Grave Sigil, Verdant Heart, Silk Idol; trophies Hollow Crown (wearable, night vision), Heartwood Core (consumable), Silkqueen's Fang (venom sword).
- **Structures & world generation:** Forgotten Graveyard, Verdant Shrine, Silk Nest (underground), Hunter's Camp, Mossy Boulder, each with chest loot (relics can appear rarely).
- **Docs:** rewritten README, this changelog, CLAUDE.md developer guide and a GitHub Pages site (`docs/`).
- **Dev tooling:** `tools/dev.py` (setup / build / lint / typecheck / package / all), portable build, deterministic generators.

### Changed
- **Sanctum Warden recipe is now endgame-hard:** Netherite Ingots, Eclipsite Ingots, Pyrelite Ingots, Obsidian, a **Totem of Undying** and an **Eclipse Core** (Eclipse Sovereign drop).
- **Sanctum Warden is fully server-safe (no operators needed):** limit of 3 wardens per player, zones lapse after the owner is offline for 21 real days (anyone may then claim them), ownerless wardens can be claimed, zone data is stored per zone (no size limit), operator bypass kept but optional.
- All recipes are now `AlwaysUnlocked` (visible in the recipe book from the start).
- Lint now validates entity components against the 1.26.50 schemas.

### Fixed
- **Logs / stripped logs / wood could not be turned into planks in the 2x2 inventory grid** (and the same for every other single-ingredient recipe: ingot ← block, seeds ← produce, buttons, ...). Single-ingredient recipes are now written as vanilla does (1x1 shaped).
- **Our woods could not be used for most wood recipes:** explicit recipes added for crafting table, chest, barrel, bowl, bookshelf, wooden tools, jukebox, note block, composter, lectern, grindstone, loom, cartography / fletching / smithing tables, tripwire hook, campfire; logs and wood now smelt into charcoal.
- Removed a bogus "two slabs -> planks" recipe.

## [1.0.1] - "It actually starts now"
### Fixed
- **Scripts never started** (used APIs unavailable during early startup): everything now initialises one tick after startup, each module isolated.
- Saplings: bone meal + natural growth rewritten.
- Wood blocks are fuel, carry vanilla tags and have 3D inventory icons; stairs/slabs/fences/trapdoors waterlog; doors/gates/trapdoors react to redstone; Silk Touch on leaves.
- Pressure plates polled (mobs/items); Sanctum owner recorded from the placing player; Sanctum **test mode** added.
- Stasis chambers: fishing-rod linking and cross-dimension triggering repaired.
### Added
- Custom death messages for all mobs and projectiles; new pack thumbnail.

## [1.0.0] - "Base"
- Azurite / Pyrelite / Eclipsite ores with full tool and armour sets (Netherite-pickaxe-gated).
- Ashen Warg, Voidweaver and the Eclipse Sovereign boss.
- 5 tree species with complete wood sets and biome-correct generation.
- Java-style stasis chambers across dimensions; Sanctum Warden claim block.
- World generation for Overworld, Nether and End; Pyre Spires, Eclipse Obelisks and Shrines.
