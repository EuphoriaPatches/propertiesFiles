# Euphoria Patches Properties Files

## What Are These Files?

These `.properties` files help Euphoria Patches recognize blocks, items, entities, and dimensions from different mods. By contributing to these files, you help improve compatibility for everyone!

<picture style="pointer-events: none;">
<img src="https://img.shields.io/github/commits-difference/EuphoriaPatches/propertiesFiles?base=release&head=main&style=for-the-badge&logo=github&logoColor=%23e661e8&label=Commits%20since%20last%20Euphoria%20Patches%20Update&labelColor=0d1117&color=magenta" alt="Commits since last update">
</picture>

## Current Total Modded Blocks: <ins>54.38K</ins> | All Supported Mods: [<ins>List</ins>](https://www.euphoriapatches.com/properties/list)
[54382]: #

## ⚠️ IMPORTANT REMINDERS ⚠️
- **Please use the templates provided below!**
- **Always document your additions in `addedMods.md`!**
- **Only do changes to the latest version from GitHub (the files you're looking at right now in this repository)!**

## How to Contribute

There are two easy ways to contribute:

1. **Submit a Pull Request on GitHub** (preferred method) - [See detailed instructions below](#need-help)
2. **Share your changes on Discord** - Post the modified property file on our [Discord server](https://euphoriapatches.com/discord)

We encourage everyone to try the GitHub method when possible, as it makes tracking and reviewing changes easier!

## Getting Started (Step-by-Step)

1. Find the property file you want to modify (block, item, entity, or dimension) - for blocks we have a custom workflow [See detailed instructions below](#euphoria-patcher-properties-merger)
2. Follow the template provided at the top of each file (see examples below)
3. Add your mod entries
4. Document your changes in `addedMods.md`
5. Submit your contribution (be happy)

## Important Templates

Each properties file has a specific format. Click to see the template you need:

<details><summary>📦 <strong>block.properties</strong> template (click to expand)</summary>
<p>

#### Template for Modded Blocks:
```properties
# Description of the block ID
block.XXXXX = vanillaId1 vanillaId2 vanillaId3 ... \
tagsName1 tagsName2 tagsName3... \
\
modName1:modId1 modName1:modId2 modName1:modId3 ... \
\
modName2:modId1 modName2:modId2 modName2:modId3 ... \
\
...
lastModInThisIDName:modId1 lastModInThisIDName:modId2 lastModInThisIDName:modId3

# Description of the Next block ID
block.YYYYY = ...
```

**Important Notes:**
- Group IDs by mods (each mod on its own line)
- Use a backslash `\` at the end of each line EXCEPT the last line of an entry
- Always add a blank line with just `\` between different mods
</p>
</details>

<details><summary>🧰 <strong>item.properties</strong> template (click to expand)</summary>
<p>

#### Template for Modded Items:
```properties
# Description of the item ID
item.XXXXX = vanillaId1 vanillaId2 vanillaId3 ... \
\
modName1:modId1 modName1:modId2 modName1:modId3 ... \
\
modName2:modId1 modName2:modId2 modName2:modId3 ... \
...
lastModInThisIDName:modId1 lastModInThisIDName:modId2 lastModInThisIDName:modId3

# Description of the Next item ID
item.YYYYY = ...
```

**Important Notes:**
- Group IDs by mods (each mod on its own line)
- Use a backslash `\` at the end of each line EXCEPT the last line of an entry
- Always add a blank line with just `\` between different mods
</p>
</details>

<details><summary>🐑 <strong>entity.properties</strong> template (click to expand)</summary>
<p>

#### Template for Modded Entities:
```properties
# Description of the Entity ID
entity.XXXXX = vanillaId1 vanillaId2 vanillaId3 ... \
\
modName1:modId1 modName1:modId2 modName1:modId3 ... \
\
modName2:modId1 modName2:modId2 modName2:modId3 ... \
...
lastModInThisIDName:modId1 lastModInThisIDName:modId2 lastModInThisIDName:modId3

# Description of the Next Entity ID
entity.YYYYY = ...
```

**Important Notes:**
- Group IDs by mods (each mod on its own line)
- Use a backslash `\` at the end of each line EXCEPT the last line of an entry
- Always add a blank line with just `\` between different mods
</p>
</details>

<details><summary>🌎 <strong>dimension.properties</strong> template (click to expand)</summary>
<p>

#### Template for Modded Dimensions:
```properties
dimension.world-1 = vanillaId1 vanillaId2 \
\
modName1:modId1 modName1:modId2 modName1:modId3 ... \
\
modName2:modId1 modName2:modId2 modName2:modId3 ...

dimension.world1 = ...
```

**Important Notes:**
- Group IDs by mods (each mod on its own line)
- Use a backslash `\` at the end of each line EXCEPT the last line of an entry
- Always add a blank line with just `\` between different mods
</p>
</details>

## Documenting Your Changes

After adding your mod entries, please update the `addedMods.md` file with your additions:

<details><summary>📝 <strong>How to document your changes</strong> (click to expand)</summary>
<p>

Add a new line like this to `addedMods.md`:

```markdown
| [ModName](https://link-to-mod) | Mod's Version | Status Definitions | # Optional comments about what's included
```

Example:
```markdown
| [Applied Energistics 2](https://modrinth.com/mod/ae2) | 15.0.8 | Fully Added | # All blocks and items added
```
</p>
</details>

## Euphoria Patcher Properties Merger
You might have noticed that the block.properties files are split. To test it out in-game, enable the `autoMergeBlockProperties` option in the Euphoria Patcher mod config file.  
Any changes you do in the fragmented small files will then automatically be merged into the big block.properties file.  
More info about this, here: [README](https://github.com/EuphoriaPatches/propertiesFiles/blob/main/blockProperties/README.md)

## Version Information

- Each properties file has its own version number
- Version increases ONLY when vanilla components change
- Adding mod entries doesn't change the version number
- These files are always up-to-date with Euphoria Patches dev versions

## Helpful Tools

These tools make contributing easier:

- **[Euphoria Companion](https://modrinth.com/mod/euphoria-companion)**: Get a complete list of all blocks in your current game and which ones are missing in the properties files and much more!
- **[ItemStackExporter](https://modrinth.com/mod/itemstackexporter)**: Export many blocks at once from JEI/REI or inventory

## Advanced Tips

- **Debug Worlds**: If Euphoria Companion isn't available for your version, hold Alt while selecting world type in world creation menu to create a debug world containing every block the game knows about

- **Color Coded Programs**:
  1. Go to "Other" tab in the Shader Settings and enable "Color Coded Programs"
  2. This reveals how blocks are rendered by coloring them based on their render program:
     - Green: Solid blocks (gbuffers_terrain)
     - Dark Blue: Translucent blocks (gbuffers_water)
     - Yellow: Block entities (gbuffers_block)
     - Red: Entities (gbuffers_entities)
     - Other colors: Various other programs

- **Finding Missing Block Properties**:
  1. Enable Color Coded Programs
  2. Hold a spider eye in one hand
  3. Blocks with missing properties will appear as magenta/black striped pattern
  4. Hold spider eyes in both hands to disable the color coding

- **Block States**: Not all blockstates need to be added separately
  - For many blocks (like facing directions), you only need the base ID
  - Some blocks only need specific states differentiated (like `powered=true` vs `powered=false`)

## Need Help?

- **GitHub Help**:
  - [How to fork a repository](https://www.git-tower.com/learn/git/faq/github-fork-repository)
  - [How to create a pull request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request-from-a-fork)
- **Ask questions** on our [Discord](https://euphoriapatches.com/discord)

## Frequently Asked Questions

**Q: Do I need to know coding to contribute?**
A: No! Just follow the templates and add the mod IDs you want to include.

**Q: How do I find mod and block IDs?**
A: Use the F3 screen when and the Targeted Block info on the right side, or F3+H in-game to show advanced tooltips, additionally use the recommended tools (ItemStackExporter or Euphoria Companion).

**Q: How can I use the GitHub version of these files in game to test my additions?**
A: You can download and test as follows:
1. Download the files from this GitHub repository - big green `<> code` button and then download zip. The zip file contains all files of this repository.
2. Navigate to your Minecraft instance folder
3. Go to the `shaderpacks` folder
4. Find the Euphoria Patches folder
5. Inside, go to the `shaders` folder
6. Replace the existing properties files with your downloaded versions
7. Reload shaders in-game with F3+R or by re-selecting the shader pack

> **Note**: [Supplemental Patches](https://modrinth.com/mod/supplemental-patches) is a third-party mod that extends Euphoria Patches with even more modded functionality.
