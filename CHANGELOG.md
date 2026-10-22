# Changelog

All notable changes to **Eclipsed Realms: Chronicles of the Seven Seals** (formerly "Survival++ | Eclipsed Realms") (Tech Bytes Design). Versions follow `major.minor.patch`; the pack version is set in `tools/version.json`.

## [1.7.1]

### Changed
- **The Frost Cantor and Mire Lantern have real boss music now.** Their v1.6 themes were calm ambient loops. They are replaced by MintoDog's "Hard Boss Battle 2" (Cantor) and "Hard Boss Battle 1" (Mire Lantern), both CC0. Music lengths and credits updated; the fight logic is unchanged.

## [1.7.0] - "Burning Deep Update"

### Added
- **Road V - The Cinder Bride (Nether):** the **Forge of Vows** (three offering pedestals - Gold Ingot, Blaze Rod, Ghast Tear, in the order the vow was spoken; out of turn burns you and returns the items), the **Ashen Chapel** with the **Bridal Anvil** and a hidden crypt, the **Cinder Ring** and the **Ember Compass**, and **Varenna, the Cinder Bride** (900 HP, four phases): Forged Blades that shield her until a player parries them (each parried blade costs her 2.5% of her life), Anvil Slam with ember geysers, Cinder Brand (spread out), Forge Heat (rotating hot floor sectors), the Last Dance and the Wedding March.
- **Road VI - The Ashen Groom (Nether):** the **Toll Tower** (a Simon-says memory game: ring back 3, 4 and 5 bells) for the **Grave Key**, the **Hollow Hall** with the **Grave Altar**, and **Corvane, the Ashen Groom** (1100 HP, four phases): a duel of **stances** (Ember = immune to projectiles and fire, Soul = immune to melee, Hollow = vulnerable but furious), Duel Lunge, Soul Chains, Marrow Rain, Grave Echoes and the Widow's Toll rings.
- **Boss weapons and trophies:** Vowbreaker (ignite; right-click Anvil Slam), Grievance (wither; right-click Duel Lunge), Cinder Heart and Soul Ember (consumable buffs), Seal of the Forge and Seal of the Vow.
- **Presentation:** intro scenes, themed boss bars (now nine skins), fogs (four per boss), music, particles (embers, soul flames, ash, bursts) and 12 Ember Tablets of lore for both bosses.
- **4 new places** in the Nether with loot tables: Forge of Vows, Ashen Chapel, Toll Tower, Hollow Hall.

### Changed
- **The Veiled Blossom's music** is now a real boss theme ("Battle RPG Theme" by CleytonKauffman, CC0) instead of the calm piano piece. The calm piece was beautiful but not boss-type.
- Chapter count: six main bosses. Roads V and VI are gated behind Roads IV and V.

### Fixed
- `lint5` guard continues to run on the new content; the mock run found and fixed a stance-rotation bug (a stance value of 0 was treated as "none") before release.
- *Not tested in-game:* everything above (same caveat as v1.6: the camera scenes, glyph bars, particles, animations, structure placement, the memory game's timing, the stance deflection and the boss balance were validated offline only).

## [1.6.0] - "Seals Update"

### Fixed (from the real game's Content Log)
- **Five mobs never loaded** (Gravewalker, Cave Weaver, Revenant, Sporeling, Wild Boar): `hurt_by_target` had a member (`alert_same_type`) that does not exist in 1.26.50. This is why `/summon` said "not found" and the spawn eggs were missing, which made Chapter I step 2 impossible by the book. Removed; the new lint step `lint5.py` now catches every error class below offline.
- **Wooden doors, buttons and pressure plates (all five woods) and the Stasis Trigger Plate did not load**: `redstone_producer` must be a base component, doors need `minecraft:movable`. Their items, the stasis plate recipe and the `blocks.json` entries failed with them.
- **Highland Yak** failed to load (milking used an invalid `play_sounds` and `bucket:1`); it now transforms the bucket into a Milk Bucket.
- **Silk Nests and Sunken Crypts never generated** (their features lacked `constraints`); **Jacaranda and Mireweep weeping trees never generated** (canopy height below 4); **Slate and Umbrastone rules** had a scatter chance of 1/1.
- **All stonecutter recipes** lacked `unlock` data and were rejected.
- **The Wayfarer's Journal text was black on a dark form**; all journal and lore pages now use light colours.
- **Crop textures looked buggy and bright**: redrawn in a muted, vanilla-like style (straight stems, two-tone leaves, no black outline) and the crop blocks regained face dimming.
- **The custom boss bar fell back to the vanilla bar**: bars are now drawn on the action bar with our own font glyphs (`font/glyph_E4.png`), independent of JSON-UI bindings; the UI overlay is kept (variable renamed) on top of the vanilla bar for clients that honour it.

### Added
- **Chapter III / Road III - The Silent Choir:** Verse Stones, the Frozen Cathedral (four chimes, the Cantor's Lectern, hidden vault), the Cantor's Tuning Fork (scans loaded chunks and tells you the direction) and **Ysolde, the Frost Cantor** (520 HP; Aria, Resonance Rings you jump, Icicle Chorus, Whiteout blizzard you kneel against, Requiem spiral, the interruptible Final Verse).
- **Chapter IV / Road IV - The Lantern in the Mire:** Wisp Essence, the Keeper's Lantern, the Fen Hut, the Drowned Chapel (three sconces, Marsh Altar, flooded passage to the second half of the riddle) and **Morwen, the Mire Lantern** (560 HP; the fen swallows unlit players' light, wisp swarms, Lantern Mirages, Lantern Rain; carry a light).
- **The journal forks into roads** after the First Seal (Road IV opens after Road III), with per-road clues, progress, lore pages and a "present offerings" step; `/scriptevent ecr:story road c3 2`.
- **Boss introductions:** a camera-scripted scene per main boss (HUD hidden, input locked, orbit, close-up, title card, fade) with a failsafe release; `/scriptevent ecr:cinematic on|off|release|test <boss>`.
- **Boss bars for all seven bosses** drawn with font glyphs, `/scriptevent ecr:bossbar on|off`.
- **Alloy gear:** Rimesteel (iron+), Glacite (diamond+), Wispsteel (netherite+): tools, custom 3D armour, set bonuses and on-hit effects.
- **Boss weapons:** Frostsong (right-click Resonance) and the Mirelight Scythe (sweep, life sip, right-click Beacon of the Lost).
- **New undead:** Rimewalker (zombie-like), Hoarbone (skeleton-like), Mirewalker (zombie-like), Lanternbone (skeleton-like) and the Mire Wisp, with spawn rules, loot, eggs and death messages.
- **Particles:** frost notes, snow swirls, wisp glow, lantern motes, burst effects. **Music:** two more CC0 boss themes (isaiah658). **Fogs:** three per new boss.
- **8 new places** (Verse Cairn x4 variants, Frozen Cathedral, Fen Hut, Drowned Chapel, Wayfarer's Cairn) with seven new loot tables, 12 lore tablets, and new lore pages.

### Changed
- Hanae and the Eclipse Sovereign also get introduction scenes; their brains wait while the camera plays.
- `LORE.md` and the docs site cover Chapters III and IV, the Eighth Voice and the new places.

### Tooling
- **`lint5.py`**: official-schema member check for every entity component, plus the specific classes of error the game reported (see above). The mock run now covers both new roads end to end (verses, fork, chimes, lectern, boss phases, fog, music, bars, sconces, altar, mirages, cinematic lock/restore).
- *Not tested in-game:* the camera scenes, the glyph bar (needs `font/glyph_E4.png` to render in your client), structure placement and puzzle blocks, particles and animations. Please report anything that looks off with your Content Log.

## [1.5.0] - "Atmosphere Update"

### Added
- **Boss music for both main bosses:** the Veiled Blossom plays a calm, ethereal piano theme; the Eclipse Sovereign plays an epic boss-battle theme. The music starts when the boss exists (ritual, quest or `/summon`), repeats while the fight lasts, fades out the vanilla soundtrack, and stops when the boss dies or you walk away. Both tracks are CC0 (credits in `tools/assets/music/CREDITS.md` and on the docs site).
- **Armour trims:** every armour item (Azurite, Pyrelite, Eclipsite, Veilbloom) now carries the `minecraft:trimmable_armors` tag so the smithing table accepts trim templates. *Note: trims are drawn over the armour's texture using the vanilla texture layout; our armour uses custom 3D models, so a trim may not line up perfectly.*
- **Self-check:** `/scriptevent ecr:diag` (and an automatic check shortly after you join) reports any creature the game failed to load, with instructions for finding the cause in the Content Log.
- **Story helper:** `/scriptevent ecr:story set <step>`, `reset` or `journal` for testing/recovery (needs permission to run `/scriptevent`).
- **Chapter I step 2 has a second way through:** besides 3 Gravewalkers + 2 Cave Weavers, slaying **8 ordinary monsters inside a Cherry Grove** also completes it.

### Changed
- **The Veiled Blossom's fog is now built like Mojang's own overworld fogs** (render-relative distance, weather fog and a coloured volumetric medium) in three colours: soft pink, deep rose, and dark crimson. Petals also drift around everyone in the fight, so the mood carries even where the sky washes out the fog colour.

## [1.4.2]

### Added
- **Spawn eggs for every mob**: Blossom Vex and Veiled Echo now have eggs too (lint now fails the build if any mob lacks one).

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
