# CLAUDE.md - developer guide for Survival++ | Eclipsed Realms

Minecraft Bedrock add-on (BP + RP + JS scripts) by **Tech Bytes Design**. Target: Bedrock **1.26.50+**, `@minecraft/server 2.6.0`, `@minecraft/server-ui 2.0.0`. Repo: `MirFaizan06/SurvivalPP`. The user ships updates incrementally ("v1.2", "v1.3"...) and expects each one to be: built, validated, documented, pushed, with GitHub Pages updated.

## The one rule
**Nothing in the packs is hand-edited.** Textures, models, animations, JSON and the packaged scripts are all *generated* from `tools/`. Edit the generator, rebuild, lint, typecheck, package.

## Layout
```
tools/dev.py          CLI: setup | build | lint | typecheck | package | all
tools/version.json    pack version [major, minor, patch], title, file stem  (bump here)
tools/gen/            Python generators (PIL + numpy): build.py is the orchestrator
tools/scripts/        the add-on's JavaScript (copied into BP/scripts)
tools/docs/           GitHub Pages source (python tools/docs/build_docs.py -> docs/)
docs/                 generated site (served by GitHub Pages, main /docs)
releases/             packaged .mcaddon per version (commit the new one)
README.md CHANGELOG.md CLAUDE.md
```
Key generators (`tools/gen/`): `common.py` (paths, palettes, helpers), `registry.py` (lang + texture registries), `geo.py`/`paint.py` (Blockbench-style model builder + procedural painter + software renderer), `anims.py`/`anims2.py` (Molang animation sets), `mob_*.py` (models), `gen_*.py` (entities/items/blocks/world), `structures*.py` (.mcstructure NBT writer + designs), `tex_*.py` (textures), `lint.py`/`lint2.py`/`lint3.py`/`lint4.py` (checks: refs+schemas / components / structure palettes vs vanilla block data / entity+spawn schemas, Molang, animations, biome tags, lang), `sbuild.py` (structure builder DSL), `structures3.py`/`structures4.py` (the ten adventure structures), `gen_world3.py` (their world-gen rules + tiered loot), `preview_structures.py` (isometric plan renders).
Build order lives in `build.py: generate()` - add new modules there.

## Commands
```
python tools/dev.py setup       # once: clones Mojang/bedrock-samples + npm typings/ajv into .ref/
python tools/dev.py build       # regenerate everything into <build>/out/ECR_BP and ECR_RP
python tools/dev.py lint        # cross-reference lint + official JSON-schema validation (must be 0 problems)
python tools/dev.py typecheck   # tsc over tools/scripts against real @minecraft/server typings (must be clean)
python tools/dev.py test        # runtime smoke test: tools/test/mock_run.mjs boots the packaged scripts against a fake @minecraft/server (must print 0 problems)
python tools/dev.py package     # zip -> releases/SurvivalPlusPlus_EclipsedRealms_v<ver>.mcaddon
python tools/dev.py all            # build + lint + typecheck + test + package
```
Env overrides: `BEDROCK_SAMPLES` (bedrock-samples path), `SPP_NPM` (dir with node_modules), `SPP_BUILD` (build output dir).
**On Windows put `SPP_BUILD` outside OneDrive** (e.g. `C:/ter/build_out`) - OneDrive locks files and `rmtree` fails with WinError 5. Known-good setup used so far:
`SPP_BUILD=C:/ter/build_out BEDROCK_SAMPLES=C:/ter/ref/bedrock-samples SPP_NPM=C:/ter/ref/npm`.
Known/expected lint output: `items checked N bad 12` (tool `destroy_speeds` false positives) with **LINT 0 / LINT2 0 problems**.

## Release checklist (every update)
1. Bump `tools/version.json`. 2. Implement in generators/scripts. 3. `build` -> `lint` -> `typecheck` -> `test` all clean. 4. `package`. 5. Update `CHANGELOG.md` (Added/Changed/Fixed), `README.md`, docs fragments in `tools/docs/pages/`, run `python tools/docs/build_docs.py`. 6. Commit, tag `vX.Y.Z`, push `main`. GitHub Pages (Settings -> Pages -> `main` / `/docs`) updates itself. 7. Tell the user honestly what was *not* tested in-game.

## How to add things
- **Item**: `gen_items2.py` (DROPS / RELICS dicts) + sprite in `tex_items2.py` + recipes via `shaped()/shapeless()` from `gen_items.py`.
- **Block**: `gen_blocks.write_block` (format 1.26.30; custom components are flattened into `components` as `"ecr:name": {}`).
- **Animal / hostile / boss**: model in `mob_animals.py` / `mob_hostiles.py` / `mob_bosses2.py` (`MODELS` dict) -> preview with `python tools/gen/preview_models.py <module> <key> <scale> <centerY>` -> entity builder in `gen_animals.py` / `gen_hostiles.py` / `gen_bosses.py` (client entity, behaviour entity, loot, spawn rules, lang) -> animations in `anims2.py` -> behaviours in `tools/scripts/mobs2.js` / `bosses2.js` -> death messages in `deaths.js`.
- **Structure**: build it with the `B` DSL in `sbuild.py` (see `structures3.py`/`structures4.py`): ground-relative y, strict bounds, `chest()`, `spawner()`, `tnt_trap()`; set `ground_level` = base index; register feature + rule + loot table in `gen_world3.py`; check the plan with `python tools/gen/preview_structures.py <name>` (CUTX=1 for a side cutaway). Block names AND states are validated by `lint3` against `mojang-blocks.json` - chests use `minecraft:cardinal_direction`, stairs `weirdo_direction`/`upside_down_bit`, slabs `minecraft:vertical_half`, snow block is `minecraft:snow`, cobweb is `minecraft:web`.
- **World gen rule**: `gen_world.feature()/rule()`; surface features use `q.heightmap`, underground use `dist_underground`.

## Conventions & gotchas (learned the hard way)
- **Recipes**: use the `shaped()/shapeless()` helpers. A one-ingredient shapeless recipe is auto-converted to a 1x1 shaped recipe (vanilla style) - plain shapeless 1-ingredient recipes do NOT work in the 2x2 inventory grid. All recipes carry `unlock: AlwaysUnlocked`. Our wood needs **explicit** recipes (see `gen_items.wood_extras`), like Mojang does for mangrove; don't rely on `minecraft:planks` tags in vanilla recipes.
- **Scripts**: `world.beforeEvents.*` / `system.runInterval` are unavailable during early execution -> `main.js` defers `initAll` by one tick, each module try/caught. Block-interaction event is `world.beforeEvents.playerInteractWithBlock`. `onPlace` custom-component event has no player -> use `afterEvents.playerPlaceBlock`. Wrap risky API calls in `safe()`.
- **Persistence**: dynamic properties only; Sanctum stores one property per zone (`ecr:sz|<key>`) + index `ecr:sanctum_idx`.
- **Sanctum must never require OP** (servers like Aternos have none). Operators are only an optional bypass.
- **Entities**: format 1.26.50, modelled on vanilla chicken/cow/zombie; `minecraft:attack` supports `effect_name/effect_duration`. Spawn rules: `population_control` `animal`/`monster`; biome tags from the vanilla biome files (e.g. `mountains`, `extreme_hills`, `lush_caves`, `roofed`, `swamp`, `monster`). Glow mobs: base TGA (`entity_alphatest`) + glow overlay TGA (`entity_emissive_alpha`, low alpha = more glow).
- **Rotation convention** in animations: x/y negated vs right-handed, z standard; positive x tilts the front down / swings limbs back. Animation rotation is additive to bind-pose rotation.
- **Lint allowlist**: non-id `ecr:` strings used in scripts (state/property names) must be added to the allowlist in `lint.py`.
- Never use `hash()` for deterministic output (Python randomises it) - use `sum(map(ord, s))`.
- Bash heredocs with quotes/apostrophes break in the Windows tool: write patch scripts with a file-writing tool and run them.
- Obsolete `_patch_*.py` helper scripts are gitignored; delete any left over.
- Always validate vanilla ids (lint knows the list); item ids differ from block ids (e.g. `minecraft:normal_stone_slab`, `minecraft:noteblock`).
- **Honesty**: the environment cannot launch Minecraft. Say plainly that in-game behaviour (especially new world-gen rules, underground structures, particles and animations) is validated against schemas/typings only.

## Content map (v1.3.0)
Ores Azurite/Pyrelite/Eclipsite (+tools, armour) · stones Marlstone/Slate/Verdite/Umbrastone · 5 trees (Jacaranda, Frostpine, Amberwood, Sunwood, Mireweep) · crops Tomato/Corn/Strawberry/Chili/Oats + foods · animals Meadow Deer/Highland Yak/Wild Boar/Pheasant · hostiles Gravewalker/Revenant/Cave Weaver/Sporeling · mobs Ashen Warg/Voidweaver · bosses Eclipse Sovereign, Hollow King, Mosswood Colossus, Silkqueen · structures Pyre Spire, Eclipse Obelisk/Shrine, Forgotten Graveyard, Verdant Shrine, Silk Nest, Hunter's Camp, Mossy Boulder + ten adventure structures (Bandit Lookout, Sunken Well, Watch Keep, Dune Vault, Thorn Shrine, Frost Cairn, Highland Bastion, Sunken Crypt, Pyre Bastion, Eclipse Vault) · systems: stasis chambers (`stasis.js`), Sanctum Warden (`sanctum.js`), custom death messages (`deaths.js`).
