# Script to extract dlc tables (t_costume.tbl, t_dlc.tbl, t_item.tbl, t_shop.tbl)
# by reading script_en.p3a for the originals.
#
# Usage:  Place in a folder with script_en.p3a and run.
#
# Requires p3a_lib.py, place in the same folder.
#
# GitHub eArmada8/kuro_dlc_tool

try:
    import os, sys
    from p3a_lib import p3a_class
except ModuleNotFoundError as e:
    print("Python module missing! {}".format(e.msg))
    input("Press Enter to abort.")
    raise   

def extract_original_tbls_from_p3a (original_p3a_filename):
    p3a = p3a_class()
    if os.path.exists(original_p3a_filename):
        with open(original_p3a_filename,'rb') as p3a.f:
            headers, entries, p3a_dict = p3a.read_p3a_toc()
            files_to_extract = ['t_costume.tbl', 't_dlc.tbl', 't_item.tbl', 't_recipe.tbl', 't_shop.tbl', 't_skill.tbl', 't_voice.tbl', 't_name.tbl']
            filenames = ['t_costume.tbl.original', 't_dlc.tbl.original', 't_item.tbl.original',
                't_recipe.tbl.original', 't_shop.tbl.original', 't_skill.tbl.original', 't_voice.tbl.original', 't_name.tbl']
            entries_to_extract = []
            for filename in files_to_extract:
                matching_entries = [entry for entry in entries if os.path.basename(filename) == os.path.basename(entry['name'])]
                if len(matching_entries) > 0:
                    if len(matching_entries) > 1:
                        print("More than one {} found, extract which file?".format(filename))
                        for i in range(len(matching_entries)):
                            print("{0}. {1}".format(i+1, matching_entries[i]['name']))
                        choice = -1
                        while choice == -1:
                            raw_input = input("Input choice: ")
                            if raw_input.isdigit() and int(raw_input)-1 in range(len(matching_entries)):
                                choice = int(raw_input)-1
                            else:
                                print("Invalid choice!")
                        entries_to_extract.append(matching_entries[choice])
                    else:
                        entries_to_extract.append(matching_entries[0])
            print("files: {}".format([x['name'] for x in entries_to_extract]))
            for i in range(len(entries_to_extract)):
                file_data = p3a.read_file(entries_to_extract[i], p3a_dict)
                if len(file_data) > 0:
                    with open(filenames[files_to_extract.index(os.path.basename(entries_to_extract[i]['name']))], 'wb') as f2:
                        f2.write(file_data)

if __name__ == "__main__":
    # Set current directory
    if getattr(sys, 'frozen', False):
        os.chdir(os.path.dirname(sys.executable))
    else:
        os.chdir(os.path.abspath(os.path.dirname(__file__)))

    if os.path.exists('script_en.p3a'):
        extract_original_tbls_from_p3a('script_en.p3a')
    elif os.path.exists('script_eng.p3a'):
        extract_original_tbls_from_p3a('script_eng.p3a')
    elif os.path.exists('script.p3a'):
        extract_original_tbls_from_p3a('script.p3a')
    elif os.path.exists('misc.p3a'):
        extract_original_tbls_from_p3a('misc.p3a')