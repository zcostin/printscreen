#!/usr/bin/env python3.5

import sys
import os
import argparse
import logging
import zipfile

version = '0.2'

def uprint(*objects, sep=' ', end='\n', file=sys.stdout):
    enc = file.encoding
    if enc == 'UTF-8':
        print(*objects, sep=sep, end=end, file=file)
    else:
        f = lambda obj: str(obj).encode(enc, errors='backslashreplace').decode(enc)
        print(*map(f, objects), sep=sep, end=end, file=file)


def rename_file(source, destination, confirmation = True):

    if confirmation: 
        while True: 
            var = input("Confirm rename of file [y|n]:")

            if var == 'y':
                break
            elif var == 'n':
                return
            else:
                continue

    if os.path.exists(source):
        try:
            os.rename(source, destination)
        except OSError as e:
            err_msg = "Cannot rename file {} to {} ({})".format(source, destination, e.strerror)
            print(err_msg)
            logging.info(err_msg)
        else:
            msg = "Renamed {} to {}".format(source, destination)
            uprint(msg)
            logging.info(msg)


def rename_zip(paths, file_desc=sys.stdout):

    for path in paths:
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                full_path = os.path.join(dirpath, filename)

                if zipfile.is_zipfile(full_path):
                    file_list = zipfile.ZipFile(full_path, 'r').namelist()
                    file_list = [ os.path.basename(f) for f in file_list ]

                    file_list_modified = [ dirpath + "/" + os.path.splitext(f)[0] + ".zip" for f in file_list ]

                    # uprint("{}:\n\t{}".format(full_path, file_list_modified))

                    uprint("Rename {} to:".format(full_path))

                    for index, f in enumerate(file_list_modified):
                        uprint("\t{}) {} ".format(index, f))

                    while True: 
                        var = input("Select [0..{}] or skip [s]:".format(index))

                        if 0 <= int(var) <= index:
                            rename_file(full_path, file_list_modified[int(var)], confirmation = False)
                            break
                        elif var == 's':
                            break
                        else:
                            continue
                    

if __name__== "__main__":
    parser = argparse.ArgumentParser(
                 formatter_class=argparse.RawDescriptionHelpFormatter,
                 description='Rename archives (only .zip files supported so far).',
                 epilog="Version: {}".format(version))

    parser.add_argument('-d','--directory', type=str, nargs=1,
                        help='directory to scan for archived files')

    parser.add_argument('-l', '--log_file', type=str, nargs='?',
                        default='rename_archs.log', help='log file')

    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()

    # enable logging
    logging.basicConfig(filename=args.log_file,
                        format='%(asctime)s %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p',
                        level=logging.DEBUG)

    rename_zip(args.directory)
else:
    sys.exit(2)
