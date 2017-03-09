#!/usr/bin/env python3.5

import sys
import os
import argparse
import hashlib
import logging

version = '0.2'

#python duplicate_files.py D:/fotografii C:/Users/Costin/Downloads/fotografii_duplicates.txt

def chunk_reader(fobj, chunk_size=1024):
    """Generator that reads a file in chunks of bytes"""
    while True:
        chunk = fobj.read(chunk_size)
        if not chunk:
            return
        yield chunk
        
def uprint(*objects, sep=' ', end='\n', file=sys.stdout):
    enc = file.encoding
    if enc == 'UTF-8':
        print(*objects, sep=sep, end=end, file=file)
    else:
        f = lambda obj: str(obj).encode(enc, errors='backslashreplace').decode(enc)
        print(*map(f, objects), sep=sep, end=end, file=file)


def get_hash(filename, first_chunk_only=False, hash=hashlib.sha1):
    hashobj = hash()
    try:
        file_object = open(filename, 'rb')
    except:
        uprint("Cannot open {}".format(filename))
    else:
        if first_chunk_only:
            hashobj.update(file_object.read(1024))
        else:
            for chunk in chunk_reader(file_object):
                hashobj.update(chunk)
        hashed = hashobj.digest()

        file_object.close()
        return hashed
        
        
def move_file(duplicate1, duplicate2, destination, suffix='mp3'):
    while True: 
        var = input("Move first|second [1|2] duplicate or skip [s]:")

        if var == '1':
            file = duplicate1
            break
        elif var == '2':
            file = duplicate2
            break
        elif var == 's':
            return
        else:
            continue

    #if os.path.exists(file) and file.endswith(suffix):
    if os.path.exists(file):
        try:
            d_path = destination + "/" + os.path.basename(file)
            os.rename(file, d_path)
        except OSError as e:
            err_msg = "Cannot move file {} to {} ({})".format(file, d_path, e.strerror)
            print(err_msg)
            logging.info(err_msg)
        else:
            logging.info("Moved file {} to {}.".format(file, d_path))


def check_for_duplicates(paths, destination, hash=hashlib.sha1):
    hashes_by_size = {}
    hashes_on_1k = {}
    hashes_full = {}

    for path in paths:
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                full_path = os.path.join(dirpath, filename)
                # uprint("{}".format(full_path))
                try:
                    file_size = os.path.getsize(full_path)
                except OSError as e:
                    # not accessible (permissions, etc) - pass on
                    pass
                else:
                    duplicate = hashes_by_size.get(file_size)

                    if duplicate:
                        hashes_by_size[file_size].append(full_path)
                    else:
                        hashes_by_size[file_size] = []  # create the list for this file size
                        hashes_by_size[file_size].append(full_path)

    # For all files with the same file size, get their hash on the 1st 1024 bytes
    for __, files in hashes_by_size.items():
        if len(files) < 2:
            continue # this file size is unique, no need to spend cpu cycles on it

        for filename in files:
            small_hash = get_hash(filename, first_chunk_only=True)

            duplicate = hashes_on_1k.get(small_hash)
            if duplicate:
                hashes_on_1k[small_hash].append(filename)
            else:
                hashes_on_1k[small_hash] = [] # create the list for this 1k hash
                hashes_on_1k[small_hash].append(filename)

    # For all files with the hash on the 1st 1024 bytes,
    # get their hash on the full file - collisions will be duplicates
    for __, files in hashes_on_1k.items():
        if len(files) < 2:
            continue # this hash of fist 1k file bytes is unique, no need to spend cpu cycles on it

        for filename in files:
            full_hash = get_hash(filename, first_chunk_only=False)

            duplicate = hashes_full.get(full_hash)
            if duplicate:
                uprint ("Duplicate found:\n1] {}\n2] {}".format(filename, duplicate))
                move_file(filename, duplicate, destination)
            else:
                hashes_full[full_hash] = filename


if __name__== "__main__":
    parser = argparse.ArgumentParser(
                 formatter_class=argparse.RawDescriptionHelpFormatter,
                 description='Find duplicate files and move them to specified directory.',
                 epilog="Version: {}".format(version))

    parser.add_argument('-d','--directory', type=str, nargs='+',
                        help='directory to scan for duplicate files. \
                              Multiple directories can be specified.')

    parser.add_argument('-l', '--log_file', type=str, nargs='?',
                        default='duplicate_files.log', help='log file')

    parser.add_argument('-m', '--move_to_directory', type=str, nargs='?',
                        help='directory where duplicates are moved')

    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()

    # enable logging
    logging.basicConfig(filename=args.log_file,
                        format='%(asctime)s %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p',
                        level=logging.DEBUG)

    check_for_duplicates(args.directory, args.move_to_directory[0])
else:
    sys.exit(2)
