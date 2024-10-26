# Script to write new dlc tables (t_costume.tbl, t_dlc.tbl, t_item.tbl) by reading
# new entries from all .kurodlc.json files.
# Usage:  Place in a folder with the original tables (which will be renamed to
# t_costume.tbl.original, t_dlc.tbl.original, t_item.tbl.original) and all the
# .kurodlc.json files and run.
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
    
    # Read *.kurodlc.json files
    kt.read_all_kurodlc_jsons()
    
    # Write the new tables
    if os.path.exists('t_costume.tbl') or os.path.exists('t_costume.tbl.original'):
        kt.write_table('t_costume.tbl')
    if os.path.exists('t_dlc.tbl') or os.path.exists('t_dlc.tbl.original'):
        kt.write_table('t_dlc.tbl')
    if os.path.exists('t_item.tbl') or os.path.exists('t_item.tbl.original'):
        kt.write_table('t_item.tbl')
    if os.path.exists('t_recipe.tbl') or os.path.exists('t_recipe.tbl.original'):
        kt.write_table('t_recipe.tbl')
    if os.path.exists('t_shop.tbl') or os.path.exists('t_shop.tbl.original'):
        kt.write_table('t_shop.tbl')