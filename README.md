# Trails through Daybreak DLC table maker for custom costumes

This is a small collection of scripts to write t_costume.tbl, t_dlc.tbl and t_item.tbl (and optionally t_shop.tbl) for making costume mods in Trails through Daybreak NIS America release (PC) and Ys X NIS America release (PC).  The making of tables in Kuro no Kiseki II CLE (PC) release has been tested, although not extensively.  Other platforms / CLE releases are not tested, so YMMV.

## Credits

This tool was written using the schemas provided in KuroTools, and has thus benefited from the extensive research that went into KuroTools that was given away for free.  I am eternally grateful, thank you.

## Requirements:
1. Python 3.9 or newer is required for use of this script.  It is free from the Microsoft Store, for Windows users.  For Linux users, please consult your distro.

## How to use

*All scripts require kurodlc_lib.py to be in the same folder to run.*

### kurodlc_make_json_from_mdls.py

*This script expects t_name.tbl to be available.*

Before you start, you will want to determine some information:
1. DLC ID number:  I recommend keeping the number <350, but be sure to use a number that isn't already in use.
2. Item ID numbers:  You need to choose item numbers that are valid, but are not already in the game.
3. Recipe ID numbers - *Ys-only*:  You need to choose item numbers that are valid, but are not already in the game.

You can use `kurodlc_find_dlc_id.py`, `kurodlc_find_item_id.py` and `kurodlc_find_recipe_id.py` to check for unused ID numbers.  Place the original t_costume.tbl, t_dlc.tbl and t_item.tbl (and optionally t_shop.tbl, and t_recipe.tbl {*Ys only*}) in the folder (if they are already renamed to t_costume.tbl.original, t_dlc.tbl.original, t_item.tbl.original, t_recipe.tbl.original, and t_shop.tbl.original, that is fine).  Run the scripts and they will tell you roughly what numbers are in use.  The easiest is to pick something slightly above the upper number, but do not go too high or the game will not accept the numbers.

Place all your .mdl files in a folder, and put `kurodlc_make_json_from_mdls.py` and t_name.tbl files in the same folder.  Run `kurodlc_make_json_from_mdls.py`.  If there are .json files with settings, the script will just make the .kurodlc.json file, but the first time you run it (assuming you did not make the .json files by hand) it will ask you questions.

Questions it will ask you:
* Game platform:
    1. Pick Kuro (Daybreak) or Ys X
* DLC options:
	1. DLC ID:  This number you determined above.
	2. DLC Name:  The name of the DLC that the user will see in the DLC menu
	3. DLC Description:  The description of the DLC that the user will see in the DLC menu
* Item options:
	1. Item ID: This number you determined above.  For accessories, if you want to group two or more accessories together (for example halo and angel wings), give them the same ID number.  The script will copy over the remaining information, except the attach point.  *untested*
	2. Item Type: Enter 17 for costume, 19 for accessory, 18 for hair color or 24 for ARCUS cover.  Other types are not currently supported.
	3. Attach point: This field only appears for accessories.  The attach point should be in the .inf file for the costumes it supports.  Some example attach points include Head_Point, Megane_Point, DLC_Point01, etc.
	4. Character ID: Please look in t_name.tbl, or choose from the list the script gives you.  The script will look for any costume files in the folder and give those characters as options, but you can choose any ID under 200.  For example, Van is 0, Agnès is 1, and so on.  Please note that this number is NOT the same as the C_CHRxxx number.  (For example, Agnès's character ID is 1, even though her model is chr5001.  Please look in the t_name.tbl, which can be decoded with KuroTools.  *Warning t_name.tbl has spoilers!*)
	5. Item Name:  The name of the item that the user will see in the item / costume menus
	6. Item Description:  The description of the item that the user will see in the item / costume menus
	7. Item Quantity:  How many of this item should be given to the player by the DLC.
	8. Shop IDs:  (optional) Shop IDs of any shops you would like this item to be purchaseable from.
	9. Recipe ID:  (optional, *Ys only*) Shops in Ys X require a recipe to sell items.  You only need one recipe ID per item.

Once you have answered all the questions, it will generate the .kurodoc.json file to be used with `kurodlc_make_tbls.py`.  It will also generate a dlc.json file saving all the DLC options, and a .json file for each .mdl.  Running the script again, the tables will be generated without any questions.  If you want to change any of the data, edit the .json with a text editor, or simply delete the .json file.  If you just delete the file you want to change, the script will still use the other .json files it finds.

If you would like to use only shop ID and not include a DLC for the player to activate, remove the `DLCTableData` section from the .kurodoc.json file.

### kurodlc_extract_original_tbls.py

Put this in file in a folder along with `p3a_lib.py` and a copy of script_en.p3a from Trails Through Daybreak (or script.p3a if you want Japanese language tables).  Run the script and it will extract t_costume.tbl, t_dlc.tbl, t_item.tbl, t_name.tbl, and t_shop.tbl for use with `kurodlc_make_tbls.py`.  t_costume.tbl, t_dlc.tbl, t_item.tbl, and t_shop.tbl will automatically be renamed to t_costume.tbl.original, t_dlc.tbl.original, t_item.tbl.original, and t_shop.tbl.original.

### kurodlc_make_tbls.py

Run this in a folder with the original t_costume.tbl, t_dlc.tbl, t_item.tbl and optionally t_shop.tbl as well as one or more .kurodlc.json files (generated by `kurodlc_make_json_from_mdls.py`), and it will make new t_costume.tbl, t_dlc.tbl, t_item.tbl and t_shop.tbl tables.  The originals will be renamed t_costume.tbl.original, t_dlc.tbl.original, t_item.tbl.original and t_shop.tbl.original if those files do not already exist.

Because Trails Through Daybreak only has a single copy each of t_costume.tbl, t_dlc.tbl, t_item.tbl and t_shop.tbl; the multiple .kurodlc.json aggregation feature allows for combining multiple mods into a single set of tables.  When combining two or more mods, place all the .kurodlc.json files in a folder with t_costume.tbl.original, t_dlc.tbl.original, t_item.tbl.original and t_shop.tbl.original and run the script.  Place the new t_costume.tbl, t_dlc.tbl, t_item.tbl and t_shop.tbl files in /table_en and pack with `p3a_tool.exe` (included with Trails Through Daybreak) into a new P3A file.  Name this file `zzz_combined_tables.p3a` or something similar - P3A archives are loaded in lexicographic order, so the combined tables will load last and overwrite the tables in each individual mod.  (`kurodlc_make_zzz_tbls.py` does this automatically, and should be much more convenient to use for combining tables.)

This script can also be used for updating / replacing entries.  Many table section types have *primary keys*, which are fields that must be unique, e.g. each item should have a unique value in `id`.  If a .kurodlc.json file has a value in `id` that already exists the original table (or other .kurodlc.json files that were loaded earlier in alphabetical order), then the prior entries will be removed automatically to prevent conflicts.

### kurodlc_make_zzz_tbls.py

This is the script for end users to combine mods into a single set of tables.  *Daybreak NISA only, all other games please use kurodlc_make_tbls.py*

Put this script in a folder with scripts_en.p3a (or scripts.p3a if you want the Japanese tables) and all the .kurodlc.json files you want to combine, as well as kurodlc_lib.py and p3a_lib.py.  Run the script and it will create zzz_combined_tables.p3a, which should be put along with all the mods into the /mods folder of your Trails Through Daybreak installation folder.

### kurodlc_make_json_from_tbls.py

Place in a folder with the original tables renamed as t_costume.tbl.original, t_dlc.tbl.original, t_item.tbl.original and optionally t_shop.tbl.original (run `kurodlc_make_tbls.py` once and it will rename them), as well as the modded t_costume.tbl, t_dlc.tbl, t_item.tbl and t_shop.tbl (all four should have been previously generated by this toolset; there is no guarantee it will work if the tables were generated with a different tool).  Run the script, and it will extract all the dlc / items *that does not exist in the original tables* into a new .kurodlc.json file that can be used with kurodlc_make_tbls.py.

### p3a_archive.py and p3a_extract.py

Can be used in place of p3a_tool.exe to archive folders into p3a format or to extract p3a archives.  Drag a folder onto p3a_archive.py to create a .p3a archive.  Drag a .p3a archive to extract all files into a folder with the same name as the .p3a archive (minus the extension).

*Command line options for `p3a_archive.py`:*
`-a, --output_name OUTPUT_NAME`: Name of output p3a file (optional)
`-o, --overwrite`: Overwrite existing files
`-c, --compression {none,lz4,zstd,zstd-dict}`: Compression format
`-v, --version {1100,1200}`: P3A version to use

*Command line options for `p3a_extract.py`:*
`-f, --output_folder OUTPUT_FOLDER`: Name of output folder (optional)
`-o, --overwrite`: Overwrite existing files