# Script to use p3a_tool.exe (or sentools.exe in p3a mode) without access to the command line.
# Usage:  Place in a folder with either p3a files or folders that you want to compress and run.
#
# Requires either p3a_tool.exe or sentools.exe, place in the same folder.
#
# GitHub eArmada8/kuro_dlc_tool

import glob, os, sys, shutil, subprocess

# Default action of this shell is to extract P3A contents to a folder of the same name sans .p3a
# Change extract_to_current_directory to True to extract to the current directory instead.
extract_to_current_directory = False

def is_p3a(p3a_name):
    with open(p3a_name,'rb') as f:
        magic = f.read(8)
        if magic == b'PH3ARCV\x00':
            return True
        else:
            return False

def extract_p3a_cmd(p3a_name):
    global extract_to_current_directory
    dir_name = ".".join(p3a_name.split(".")[:-1])
    if os.path.exists('p3a_tool.exe'):
        if extract_to_current_directory == True:
            subprocess.check_call(["p3a_tool.exe", "extract", "-o", p3a_name])
        else:
            if not (os.path.exists(dir_name)
                and os.path.isdir(dir_name)):
                    os.mkdir(dir_name)
            # Why does p3a_tool not have an output folder option??
            os.chdir(dir_name)
            subprocess.check_call(["../p3a_tool.exe".format(dir_name), "extract",
                "-o", "../{}".format(os.path.basename(p3a_name))])
            os.chdir('..')
    elif os.path.exists('sentools.exe'):
        if extract_to_current_directory == True:
            subprocess.check_call(["sentools.exe", "P3A.Extract", "--output=.", p3a_name])
        else:
            if not (os.path.exists(dir_name)
                and os.path.isdir(dir_name)):
                    os.mkdir(dir_name)
            subprocess.check_call(["sentools.exe", "P3A.Extract", "--output={}".format(dir_name), p3a_name])
    else:
        input("Neither p3a_tool.exe nor sentools.exe present, aborting!  Press Enter to quit.")
        raise
    return

def pack_p3a_cmd(dir_name):
    if os.path.exists(dir_name) and os.path.isdir(dir_name):
        if os.path.exists('p3a_tool.exe'):
            os.chdir(dir_name)
            folder_list = sorted(list(set([os.path.dirname(x) for x in glob.glob('**',recursive=True)
                if not os.path.isdir(x)])))
            subprocess.check_call(["../p3a_tool.exe".format(dir_name), "archive",
                "../{}".format(os.path.basename(dir_name+'.p3a')), *folder_list])
            os.chdir('..')
        elif os.path.exists('sentools.exe'):
            subprocess.check_call(["sentools.exe", "P3A.Pack", "--output={}".format(dir_name+'.p3a'),
                 "--compression=lz4", dir_name])

if __name__ == "__main__":
    # Set current directory
    if getattr(sys, 'frozen', False):
        os.chdir(os.path.dirname(sys.executable))
    else:
        os.chdir(os.path.abspath(os.path.dirname(__file__)))
    # If argument given, attempt to export from file in argument
    if len(sys.argv) > 1:
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument('p3a_or_folder', help="Name of p3a to extract or folder to pack.")
        args = parser.parse_args()
        if os.path.isdir(args.p3a_or_folder):
            pack_p3a_cmd(args.p3a_or_folder)
        elif is_p3a(args.p3a_or_folder):
            extract_p3a_cmd(args.p3a_or_folder)
    else:
        print("Extract or Pack P3A?\n1. Extract\n2. Pack")
        option = 0
        while option == 0:
            raw_input = input("Input choice: ")
            try:
                choice = int(raw_input)
                if choice in [1,2]:
                    option = choice
            except:
                pass
            if option == 0:
                print("Invalid input!")
        if option == 1: #Extract
            p3a_files = glob.glob('*.p3a')
            print("Extract which file?")
            for i in range(len(p3a_files)):
                print("{0}. {1}".format(i+1, p3a_files[i]))
            file_option = 0
            while file_option == 0:
                raw_input = input("Input choice: ")
                try:
                    choice = int(raw_input)
                    if choice in range(1,len(p3a_files)+1):
                        file_option = choice
                except:
                    pass
                if file_option == 0:
                    print("Invalid input!")
            extract_p3a_cmd(p3a_files[file_option-1])
        else: #Pack
            dirs = [x for x in glob.glob('*') if os.path.isdir(x)]
            print("Pack which folder?")
            for i in range(len(dirs)):
                print("{0}. {1}".format(i+1, dirs[i]))
            dir_option = 0
            while dir_option == 0:
                raw_input = input("Input choice: ")
                try:
                    choice = int(raw_input)
                    if choice in range(1,len(dirs)+1):
                        dir_option = choice
                except:
                    pass
                if dir_option == 0:
                    print("Invalid input!")
            pack_p3a_cmd(dirs[dir_option-1])
