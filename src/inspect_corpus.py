'''
Compare metadata file list to actual files
'''
import os
import re
import sys
import argparse
import metadata
import unicodedata
from collections import defaultdict


def get_settings():
    parser = argparse.ArgumentParser(
        description='Inspect metadata and files for corpus')
    parser.add_argument('-t', '--text', dest='text_path', required=True,
                        help='Path to text files')
    parser.add_argument('-m', '--metadata', dest='metadata_path',
                        required=True, help='Path to metadata files')
    parser.add_argument('-o', '--output', dest='output_path', required=True,
                        help='Output filename for joined metadata')
    return parser.parse_args()


def normalize_filename(filename):
    import re
    basename, ext = os.path.splitext(filename)
    if ext != '.txt' and ext != '.docx':
        basename = filename   # deal with . near the end of a filename
    basename = basename.translate(str.maketrans(' ', ' '))
    basename = re.sub(' +', ' ', basename)
    basename = unicodedata.normalize('NFC', basename).strip()
    return basename


def get_text_filenames(path):
    ''' Return list of all files in directory '''
    all_files = list()
    for root, subdirs, files in os.walk(path):
        for filename in files:
            all_files.append(normalize_filename(filename))
    return all_files


def get_metadata_filenames(metadata):
    all_files = list()
    for row in metadata:
        if row['filename'] is not None:
            all_files.append(normalize_filename(row['filename']))
    return all_files


def read_all_metadata(columns, path):
    all_metadata = list()
    files = find_metadata_files(path)
    for filename in files:
        m = metadata.read_csv(os.path.join(path, filename))
        for row in m:
            try:
                all_metadata.append({col: row[col] for col in columns})
            except KeyError as err:
                print('Missing column: {}- {}'.format(row, err))
    return all_metadata


def compare_file_lists(metadata, metadata_path, text_path):
    metadata_filenames = set(get_metadata_filenames(metadata))
    filenames = set(get_text_filenames(text_path))

    diff1 = metadata_filenames - filenames
    print('{} rows of metadata; {} total files'.format(len(metadata_filenames),
                                                       len(filenames)))
    print('-------- {} files missing'.format(len(diff1)))
    for filename in diff1:
        print('"{}"'.format(filename))
    diff2 = filenames - metadata_filenames
    print('-------- {} metadata rows missing'.format(len(diff2)))
    for filename in diff2:
        print('"{}"'.format(filename))
    diff3 = diff1 | diff2
    print('----- COMPARISON -----')
    for filename in sorted(diff3):
        print('"{}"'.format(filename))


def fix_filenames(data, path):
    all_metadata = list()
    for row in data:
        filename = row['filename']
        basename, ext = os.path.splitext(filename)
        if (not len(ext) or ext == '.docx') and len(basename):
            ext = '.txt'
            filename = basename + ext
        if not os.path.isfile(os.path.join(path, filename)):
            print('File not found: "{}"'.format(filename))
        row['filename'] = os.path.join(path, filename)
        all_metadata.append(row)
    return all_metadata


def find_metadata_files(path):
    ''' Looks specifically for CSV files '''
    metadata_files = list()
    for root, subdirs, files in os.walk(path):
        for filename in files:
            if filename.endswith('csv'):
                metadata_files.append(filename)
    return metadata_files


def get_common_columns(path):
    headers = dict()
    common = list()
    header_counts = defaultdict(int)
    metadata_files = find_metadata_files(path)
    for filename in metadata_files:
        data = metadata.read_csv(os.path.join(path, filename))
        headers[filename] = data[0]

    for filename, columns in headers.items():
        for col in columns:
            # col = col.lower().strip()
            header_counts[col] += 1

    for name, count in header_counts.items():
        if count == len(metadata_files):
            common.append(name)
    return common


def check_for_duplicates(data):
    counts = defaultdict(int)
    duplicates = list()
    for row in data:
        counts[row['filename']] += 1
        if counts[row['filename']] > 1:
            duplicates.append(row['filename'])
    return set(duplicates)


def main():
    settings = get_settings()
    columns = get_common_columns(settings.metadata_path)
    all_metadata = read_all_metadata(columns, settings.metadata_path)
    all_metadata = fix_filenames(all_metadata, settings.text_path)
    # metadata.write_csv(settings.output_path, all_metadata)
    dupes = check_for_duplicates(all_metadata)
    print(dupes)
    # compare_file_lists(all_metadata, settings.metadata_path, settings.text_path)


if __name__ == '__main__':
    if sys.version_info[0] != 3:
        print("This script requires Python 3")
        exit(-1)
    main()
