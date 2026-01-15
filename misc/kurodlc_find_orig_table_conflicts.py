# Script to search original tables (t_dlc.tbl, t_item.tbl) to find if there are
## conflicting IDs in all present .kurodlc.json files.
# Usage:  Place in a folder with the original tables (t_dlc.tbl.original,
# t_item.tbl.original or t_dlc.tbl, t_item.tbl) and all the
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

    print("Searching for t_item.tbl conflicts...")

    # Read t_item.tbl.original (or t_item.tbl if original not available)
    if os.path.exists('t_item.tbl.original'):
        t_item = kt.read_table('t_item.tbl.original')
    else:
        t_item = kt.read_table('t_item.tbl')

    # Find originals
    items = {x['id']:x['name'] for x in t_item['ItemTableData']}
    
    # Find conflicts with original item table
    item_conflicts = [x for x in kt.new_entries['ItemTableData'] if x['id'] in items.keys()]
    if len(item_conflicts) > 0:
        print("The following item conflicts were found:")
        for i in range(len(item_conflicts)):
            matches = [kt.new_entries_sources['ItemTableData_primary_key'][j][item_conflicts[i]['id']]
                for j in range(len(kt.new_entries_sources['ItemTableData_primary_key']))
                if item_conflicts[i]['id'] in kt.new_entries_sources['ItemTableData_primary_key'][j]]
            print("{}. {} - {} in {} conflicts with {} in t_item!".format(i+1, item_conflicts[i]['id'],
                item_conflicts[i]['name'], matches, items[item_conflicts[i]['id']]))
    else:
        print("No conflicts with t_item.tbl!")
    input("Press Enter to Continue.")

    print("Searching for t_dlc.tbl conflicts...")

    # Read t_dlc.tbl.original (or t_dlc.tbl if original not available)
    if os.path.exists('t_dlc.tbl.original'):
        t_dlc = kt.read_table('t_dlc.tbl.original')
    else:
        t_dlc = kt.read_table('t_dlc.tbl')

    # Find originals
    dlcs = {x['id']:x['name'] for x in t_dlc['DLCTableData']}
    
    # Find conflicts with original item table
    dlc_conflicts = [x for x in kt.new_entries['DLCTableData'] if x['id'] in dlcs.keys()]
    if len(dlc_conflicts) > 0:
        print("The following dlc conflicts were found:")
        for i in range(len(dlc_conflicts)):
            matches = [kt.new_entries_sources['DLCTableData_primary_key'][j][dlc_conflicts[i]['id']]
                for j in range(len(kt.new_entries_sources['DLCTableData_primary_key']))
                if dlc_conflicts[i]['id'] in kt.new_entries_sources['DLCTableData_primary_key'][j]]
            print("{}. {} - {} in {} conflicts with {} in t_dlc!".format(i+1, dlc_conflicts[i]['id'],
                dlc_conflicts[i]['name'], matches, dlcs[dlc_conflicts[i]['id']]))
    else:
        print("No conflicts with t_dlc.tbl!")
    input("Press Enter to Continue.")