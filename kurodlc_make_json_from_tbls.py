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
    
    if all([os.path.exists(x) for x in ['t_costume.tbl', 't_costume.tbl.original',\
            't_dlc.tbl', 't_dlc.tbl.original', 't_item.tbl', 't_item.tbl.original']]):
        t_costume_original = kt.read_table('t_costume.tbl.original')
        t_dlc_original = kt.read_table('t_dlc.tbl.original')
        t_item_original = kt.read_table('t_item.tbl.original')
        t_costume = kt.read_table('t_costume.tbl')
        t_dlc = kt.read_table('t_dlc.tbl')
        t_item = kt.read_table('t_item.tbl')
        kurodlc_json = {\
            'CostumeParam': [x for x in t_costume['CostumeParam']\
                if x not in t_costume_original['CostumeParam']],\
            'DLCTableData': [x for x in t_dlc['DLCTableData']\
                if x['id'] not in [x['id'] for x in t_dlc_original['DLCTableData']]],\
            'ItemTableData': [x for x in t_item['ItemTableData']\
                if x['id'] not in [x['id'] for x in t_item_original['ItemTableData']]]}
        json_name = input("Please input name for .kurodlc.json file (e.g. \"my_mod\" for \"my_mod.kurodlc.json\") ")
        valid = '-_.[]() abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        json_name = ''.join([x if x in valid else '_' for x in json_name])
        kt.write_struct_to_json(kurodlc_json, json_name + '.kurodlc.json')
    else:
        print("The following files are missing! {}".format([x for x in ['t_costume.tbl', 't_costume.tbl.original',\
            't_dlc.tbl', 't_dlc.tbl.original', 't_item.tbl', 't_item.tbl.original'] if not os.path.exists(x)]))
        input("Press Enter to quit.")