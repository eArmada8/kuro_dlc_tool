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
    kt.write_table('t_costume.tbl')
    kt.write_table('t_dlc.tbl')
    kt.write_table('t_item.tbl')