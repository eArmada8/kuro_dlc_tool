# Script to extract files from a P3A archive.
# Usage:  Drag a P3A archive onto the script, or place in a folder with a P3A archive and run.
#
# Requires p3a_lib.py, place in the same folder.
#
# GitHub eArmada8/kuro_dlc_tool

try:
    import os, sys, glob
    from p3a_lib import p3a_class
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

    # If argument given, attempt to export from file in argument
    p3a = p3a_class()
    if len(sys.argv) > 1:
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument('p3a_archive', help="Name of file to decompress (required).")
        parser.add_argument('-f', '--output_folder', help="Name of output folder (optional)", default=None)
        parser.add_argument('-o', '--overwrite', help="Overwrite existing files", action="store_true")
        args = parser.parse_args()
        if os.path.exists(args.p3a_archive):
            p3a.extract_all_files(args.p3a_archive, output_dir = args.output_folder, overwrite = args.overwrite)
    else:
        all_files = glob.glob('*.p3a', recursive = False)
        for i in range(len(all_files)):
            p3a.extract_all_files(all_files[i])


