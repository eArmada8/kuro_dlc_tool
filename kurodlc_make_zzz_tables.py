# Script to write new dlc tables (t_costume.tbl, t_dlc.tbl, t_item.tbl, t_shop.tbl)
# by reading script_en.p3a for the originals, and .kurodlc.json files for the mods.
# A new p3a will be outputted.
#
# Usage:  Place in a folder with script_en.p3a and all the .kurodlc.json files and run.
#
# Requires kurodlc_lib.py and p3a_lib.py, place in the same folder.
#
# GitHub eArmada8/kuro_dlc_tool

try:
    import glob, os, sys
    from kurodlc_lib import kuro_tables
    from p3a_lib import p3a_class
except ModuleNotFoundError as e:
    print("Python module missing! {}".format(e.msg))
    input("Press Enter to abort.")
    raise   

def create_combined_tables_p3a (p3as_to_extract, new_p3a_filename = 'zzz_combined_tables.p3a'):
    p3a = p3a_class()
    entries_to_extract = []
    for i in range(len(p3as_to_extract)):
        with open(p3as_to_extract[i],'rb') as p3a.f:
            headers, entries, p3a_dict = p3a.read_p3a_toc()
            files_to_extract = ['t_costume.tbl', 't_dlc.tbl', 't_item.tbl', 't_recipe.tbl', 't_shop.tbl', 't_skill.tbl', 't_voice.tbl', 't_name.tbl']
            current_p3a_entries_to_extract = []
            for filename in files_to_extract:
                current_p3a_entries_to_extract.extend([entry for entry in entries if os.path.basename(filename) == os.path.basename(entry['name'])])
            for i in range(len(current_p3a_entries_to_extract)):
                file_data = p3a.read_file(current_p3a_entries_to_extract[i], p3a_dict)
                if len(file_data) > 0:
                    if not os.path.exists(os.path.dirname(current_p3a_entries_to_extract[i]['name'])):
                        os.makedirs(os.path.dirname(current_p3a_entries_to_extract[i]['name']))
                    with open(current_p3a_entries_to_extract[i]['name'], 'wb') as f2:
                        f2.write(file_data)
            entries_to_extract.extend(current_p3a_entries_to_extract)
    all_temporary_folders = sorted(list(set([os.path.dirname(x['name']) for x in entries_to_extract])))
    filenames_to_process = [x['name'] for x in entries_to_extract]
    kt = kuro_tables()
    # Read *.kurodlc.json files
    kt.read_all_kurodlc_jsons()
    for table_filename in filenames_to_process:
        kt.write_table(table_filename)
    assigned_paths = {filenames_to_process[i]:entries_to_extract[i]['name'] for i in range(len(filenames_to_process))}
    new_p3a = p3a.p3a_pack_files(filenames_to_process, assigned_paths = assigned_paths)
    with open(new_p3a_filename, 'wb') as f2:
        f2.write(new_p3a)
    files_to_remove = filenames_to_process + [x+'.original' for x in filenames_to_process]
    for file in files_to_remove:
        os.remove(file)
    for folder in all_temporary_folders:
        os.rmdir(folder)

if __name__ == "__main__":
    # Set current directory
    if getattr(sys, 'frozen', False):
        os.chdir(os.path.dirname(sys.executable))
    else:
        os.chdir(os.path.abspath(os.path.dirname(__file__)))

    original_p3as = ['script_en.p3a', 'script_eng.p3a', 'script.p3a', 'misc.p3a']
    p3as_to_extract = [os.path.basename(x) for x in glob.glob('*.p3a') if os.path.basename(x) in original_p3as]
    if len(p3as_to_extract) > 0:
        create_combined_tables_p3a(p3as_to_extract)
