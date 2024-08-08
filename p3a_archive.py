# Script to archive files into a P3A archive.
# Usage:  Drag a folder onto the script, or place in a folder with the folder to archive and run.
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
        parser.add_argument('folder_name', help="Name of folder to compress (required).")
        parser.add_argument('-a', '--output_name', help="Name of output p3a file (optional)", default=None)
        parser.add_argument('-o', '--overwrite', help="Overwrite existing files", action="store_true")
        parser.add_argument('-c', '--compression', help="Compression format",
            choices = ['none', 'lz4', 'zstd', 'zstd-dict'], default='lz4')
        parser.add_argument('-v', '--version', help="P3A version", choices = ['1100', '1200'], default='1100')
        args = parser.parse_args()
        if os.path.exists(args.folder_name):
            p3a.pack_folder(args.folder_name, args.output_name, overwrite = args.overwrite,
            cmp_type = {'none':0, 'lz4':1, 'zstd':2, 'zstd-dict':3}[args.compression], p3a_ver = int(args.version))
    else:
        all_folders = [x for x in glob.glob('*', recursive = False) if os.path.isdir(x)]
        all_folders = [x for x in all_folders if x != '__pycache__']
        for i in range(len(all_folders)):
            p3a.pack_folder(all_folders[i])


