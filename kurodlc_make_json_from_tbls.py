# Script to generate .kurodlc.json file from modded t_costume.tbl, t_dlc.tbl and
# t_item.tbl.
# Usage:  Place in a folder with modded t_costume.tbl, t_dlc.tbl and
# t_item.tbl. as well as the original tables (wt_costume.tbl.original,
# t_dlc.tbl.original, t_item.tbl.original) and run.
#
# Requires kurodlc_lib.py, place in the same folder.
#
# GitHub eArmada8/kuro_dlc_tool

try:
    import os, sys
    from kurodlc_lib import kuro_tables
except ModuleNotFoundError as e:
    print("Python module missing! {}".format(e.msg))
    input("Press Enter to abort.")
    raise   

if __name__ == "__main__":
    # Set current directory
    if getattr(sys, 'frozen', False):
        os.chdir(os.path.dirname(sys.executable))
    else:
        os.chdir(os.path.abspath(os.path.dirname(__file__)))

    kt = kuro_tables()

    kurodlc_json = {}
    for table in ['t_costume', 't_dlc', 't_item', 't_recipe', 't_shop', 't_skill']:
        new_tbl, orig_tbl = table + '.tbl', table + '.tbl.original'
        if os.path.exists(new_tbl) and os.path.exists(orig_tbl):
            orig_tbl_data = kt.read_table(orig_tbl)
            new_tbl_data = kt.read_table(new_tbl)
            for subtable in orig_tbl_data:
                diff_entries = [x for x in new_tbl_data[subtable]
                    if not x in orig_tbl_data[subtable]]
                if len(diff_entries) > 0:
                    kurodlc_json[subtable] = diff_entries
    if len(kurodlc_json) > 0:
        json_name = input("Please input name for .kurodlc.json file (e.g. \"my_mod\" for \"my_mod.kurodlc.json\") ")
        valid = '-_.[]() abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        json_name = ''.join([x if x in valid else '_' for x in json_name])
        kt.write_struct_to_json(kurodlc_json, json_name + '.kurodlc.json')
    else:
        print("No entries found, all analyzed tbl files equal or unreadable (or originals not available.")
        input("Press Enter to quit.")