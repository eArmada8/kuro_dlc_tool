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
            files_to_extract = ['t_costume.tbl', 't_dlc.tbl', 't_item.tbl', 't_shop.tbl', 't_name.tbl']
            filenames = ['t_costume.tbl.original', 't_dlc.tbl.original', 't_item.tbl.original',
                't_shop.tbl.original', 't_name.tbl']
            try:
                entries_to_extract = [[entry for entry in entries if x in entry['name']][0] for x in files_to_extract]
            except IndexError:
                input("P3A input does not have the expected files!  Press Enter to abort.")
                raise
            for i in range(len(entries_to_extract)):
                file_data = p3a.read_file(entries_to_extract[i], p3a_dict)
                if len(file_data) > 0:
                    with open(filenames[i], 'wb') as f2:
                        f2.write(file_data)

if __name__ == "__main__":
    # Set current directory
    if getattr(sys, 'frozen', False):
        os.chdir(os.path.dirname(sys.executable))
    else:
        os.chdir(os.path.abspath(os.path.dirname(__file__)))

    if os.path.exists('script_en.p3a'):
        extract_original_tbls_from_p3a('script_en.p3a')
    elif os.path.exists('script.p3a'):
        extract_original_tbls_from_p3a('script.p3a')
    elif os.path.exists('misc.p3a'):
        extract_original_tbls_from_p3a('misc.p3a')