import os

def find_empty_dirs(root_dir='.'):
    for dirpath, dirs, files in os.walk(root_dir):
        if not dirs and not files:
            yield dirpath

for i in list(find_empty_dirs("D:/")):
    print(i)