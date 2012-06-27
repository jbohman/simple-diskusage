#!/usr/bin/env python
import os
import sys
import stat
import operator

def convert_bytes(in_bytes):
    """
    Convert bytes into TiB/GiB/MiB/KiB.
    """
    if in_bytes >= 1099511627776:
        return (in_bytes / 1099511627776.0, 'TiB')
    elif in_bytes >= 1073741824:
        return (in_bytes / 1073741824.0, 'GiB')
    elif in_bytes >= 1048576:
        return (in_bytes / 1048576.0, 'MiB')
    elif in_bytes >= 1024:
        return (in_bytes / 1024.0, 'KiB')
    return (in_bytes, 'bytes')

def walk(directory):
    try:
        content = os.listdir(directory)
    except OSError:
        return

    for item in content:
        new_item = os.path.join(directory, item)
        try:
            item_stat = os.lstat(new_item)
            if stat.S_ISREG(item_stat.st_mode):
                yield (item, item_stat)
            elif stat.S_ISDIR(item_stat.st_mode):
                for x in walk(new_item):
                    yield x
                yield (item, item_stat)
        except OSError:
            return

if __name__ == '__main__':
    root_directory = os.getcwd()
    if len(sys.argv) >= 2:
        root_directory = os.path.realpath(sys.argv[1])

    root_directories = {}
    try:
        root_directory_stat = os.lstat(root_directory)
        if not stat.S_ISDIR(root_directory_stat.st_mode):
            sys.stderr.write('Argument is not a directory\n')
            sys.exit(1)

        for item in os.listdir(root_directory):
            item_path = os.path.join(root_directory, item)
            item_stat = os.lstat(item_path) 
            if stat.S_ISREG(item_stat.st_mode) or stat.S_ISDIR(item_stat.st_mode):
                root_directories[item] = item_stat.st_size + sum(x[1].st_size for x in walk(item_path))

    except OSError:
        sys.stderr.write('Could not read directory\n')
        sys.exit(1)

    if len(root_directories) == 0:
        sys.stderr.write('No files or directories in selected path\n')
        sys.exit(1)

    print 'Total size for items in %s' % (root_directory,)
    name_count = max(len(x) for x in root_directories.iterkeys())
    byte_count = max(len(str(int(convert_bytes(x)[0]))) for x in root_directories.itervalues())
    for item, size in sorted(root_directories.iteritems(), key=operator.itemgetter(1), reverse=True):
        byte_tuple = convert_bytes(size)
        print '%s: %s %s' % (item.ljust(name_count + 3), ('%.2f' % (byte_tuple[0],)).rjust(byte_count + 3), byte_tuple[1])
