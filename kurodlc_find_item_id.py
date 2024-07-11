# Script to find unassigned item ID numbers.
# Usage:  Place in a folder with t_item.tbl.original (or t_item.tbl) and all the
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

    # Read t_item.tbl.original (or t_item.tbl if original not available)
    if os.path.exists('t_item.tbl.original'):
        t_item = kt.read_table('t_item.tbl.original')
    else:
        t_item = kt.read_table('t_item.tbl')
        
    # Read *.kurodlc.json files and add to table (in memory)
    kt.read_all_kurodlc_jsons()
    t_item = kt.update_table_with_kurodlc(t_item)
    items = {x['id']:x['name'] for x in t_item['ItemTableData']}

    # Dunno what the actual upper limit of item IDs is
    id_lower_limit, id_upper_limit = 1, 5000
    available_ids = [i for i in range(id_lower_limit,id_upper_limit) if not i in items.keys()]
    random.shuffle(available_ids)
    print("The current range of ID numbers is {0} to {1}.".format(min(items.keys()), max(items.keys())))
    if len(available_ids) > 10:
        print("10 available id numbers are {0}".format(available_ids[0:10]))
    else:
        print("{0} available id numbers are {1}".format(len(available_ids), available_ids))
    while 1:
        number_input = input("What number would you like to check?  "\
            + "[Valid: {0}-{1} Press Enter to quit] ".format(id_lower_limit, id_upper_limit))
        if number_input == '':
            break
        try:
            number = int(number_input)
        except ValueError:
            print("Invalid Entry!")
        if not number in range(id_lower_limit,id_upper_limit):
            print("Invalid Entry!")
        elif number in items.keys():
            print("{0} is assigned to {1}!".format(number, items[number]))
        else:
            print("{} is available!".format(number))
