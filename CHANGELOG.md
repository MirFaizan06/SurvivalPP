# Changelog

All notable changes to **Survival++ | Eclipsed Realms** (Tech Bytes Design). Versions follow `major.minor.patch`; the pack version is set in `tools/version.json`.

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
