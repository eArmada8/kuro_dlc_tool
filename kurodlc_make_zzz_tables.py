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
    import os, sys
    from kurodlc_lib import kuro_tables
    from p3a_lib import p3a_class
except ModuleNotFoundError as e:
    print("Python module missing! {}".format(e.msg))
    input("Press Enter to abort.")
    raise   

def create_combined_tables_p3a (original_p3a_filename, new_p3a_filename = 'zzz_combined_tables.p3a'):
    p3a = p3a_class()
    if os.path.exists(original_p3a_filename):
        with open(original_p3a_filename,'rb') as p3a.f:
            headers, entries, p3a_dict = p3a.read_p3a_toc()
            files_to_extract = ['t_costume.tbl', 't_dlc.tbl', 't_item.tbl', 't_recipe.tbl', 't_shop.tbl', 't_skill.tbl', 't_voice.tbl', 't_name.tbl']
            entries_to_extract = []
            for filename in files_to_extract:
                entries_to_extract.extend([entry for entry in entries if os.path.basename(filename) == os.path.basename(entry['name'])])
            for i in range(len(entries_to_extract)):
                file_data = p3a.read_file(entries_to_extract[i], p3a_dict)
                if len(file_data) > 0:
                    if not os.path.exists(os.path.dirname(entries_to_extract[i]['name'])):
                        os.makedirs(os.path.dirname(entries_to_extract[i]['name']))
                    with open(entries_to_extract[i]['name'], 'wb') as f2:
                        f2.write(file_data)
            all_temporary_folders = sorted(list(set([os.path.dirname(x['name']) for x in entries_to_extract])))
            kt = kuro_tables()
            # Read *.kurodlc.json files
            kt.read_all_kurodlc_jsons()
            filenames_to_process = [x['name'] for x in entries_to_extract]
            for table_filename in filenames_to_process:
                kt.write_table(table_filename)
            assigned_paths = {filenames_to_process[i]:entries_to_extract[i]['name'] for i in range(len(filenames_to_process))}
            new_p3a = p3a.p3a_pack_files(filenames_to_process[:-1], assigned_paths = assigned_paths)
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

    if os.path.exists('script_en.p3a'):
        create_combined_tables_p3a('script_en.p3a')
    if os.path.exists('script_eng.p3a'):
        create_combined_tables_p3a('script_eng.p3a')
    elif os.path.exists('script.p3a'):
        create_combined_tables_p3a('script.p3a')
    elif os.path.exists('misc.p3a'):
        create_combined_tables_p3a('misc.p3a')