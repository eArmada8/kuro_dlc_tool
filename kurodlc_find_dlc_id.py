# Script to find unassigned dlc ID numbers.
# Usage:  Place in a folder with t_dlc.tbl.original (or t_dlc.tbl) and all the
# .kurodlc.json files and run.
#
# Requires kurodlc_lib.py, place in the same folder.
#
# GitHub eArmada8/kuro_dlc_tool

try:
    import random, math, os, sys
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
    random.seed()

    # Read t_dlc.tbl.original (or t_dlc.tbl if original not available)
    if os.path.exists('t_dlc.tbl.original'):
        t_dlc = kt.read_table('t_dlc.tbl.original')
    else:
        t_dlc = kt.read_table('t_dlc.tbl')
        
    # Read *.kurodlc.json files and add to table (in memory)
    kt.read_all_kurodlc_jsons()
    t_dlc = kt.update_table_with_kurodlc(t_dlc)
    dlcs = {x['id']:x['name'] for x in t_dlc['DLCTableData']}

    # Dunno what the actual upper limit of DLC IDs is
    id_lower_limit, id_upper_limit = 0, 350
    available_ids = [i for i in range(id_lower_limit,id_upper_limit) if not i in dlcs.keys()]
    random.shuffle(available_ids)
    print("The current range of ID numbers is {0} to {1}.".format(min(dlcs.keys()), max(dlcs.keys())))
    if len(available_ids) > 10:
        print("10 available id numbers are {0}".format(available_ids[0:10]))
    else:
        print("{0} available id numbers are {1}".format(len(available_ids), available_ids))
    while 1:
        number_input = input("What number would you like to check? "\
            + "[Valid: {0}-{1} Press Enter to quit] ".format(id_lower_limit, id_upper_limit))
        if number_input == '':
            break
        try:
            number = int(number_input)
        except ValueError:
            print("Invalid Entry!")
        if not number in range(id_lower_limit,id_upper_limit):
            print("Invalid Entry!")
        elif number in dlcs.keys():
            print("{0} is assigned to {1}!".format(number, dlcs[number]))
        else:
            print("{} is available!".format(number))