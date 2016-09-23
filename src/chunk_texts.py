'''
Chunks a list of files into parts for topic modeling
Uses rough word counts; nothing in this world is perfect

Mike Widner <mikewidner@stanford.edu>
'''
import os
import sys
import argparse
import metadata


def parse_options():
    parser = argparse.ArgumentParser(
        description='Chunk files into different sizes')
    parser.add_argument('-i', dest='input', required=True,
                        help='Input file of metadata as CSV')
    parser.add_argument('-o', dest='output', required=True,
                        help='Output file for results')
    parser.add_argument('-v', '--verbose', dest='verbose',
                        action='store_true', help='Verbose output')
    parser.add_argument('-m', '--min-words', dest='min_words',
                        default=250, type=int,
                        help='Minimum words in a chunk')
    parser.add_argument('-s', '--size', dest='chunk_size', default=500,
                        type=int,
                        help='Desired number of words in a chunk')
    return parser.parse_args()


def generate_filepaths(metadata_file, output_dir):
    data = metadata.read_csv(metadata_file)
    for row in data:
        output_path = output_dir + "/" + row['filename']
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        row['output_path'] = output_path
    return data


def read_text(filename):
    text = None
    try:
        fh = open(filename, 'r')
    except FileNotFoundError as err:
        print("Could not read {}: {}".format(filename, err))
    except IsADirectoryError as err:
        print(err)
    else:
        text = fh.read()
        fh.close()
    return text


def chunk_text(words, chunk_size, min_length):
    chunk_list = []
    chunk = []
    i = 0
    words.reverse()  # because we're popping
    while words:
        word = words.pop()
        chunk.append(word)
        i += 1
        if i >= chunk_size:
            chunk_list.append(chunk)
            chunk = []
            i = 0
    if (len(chunk) < min_length and len(chunk_list) > 0):
        chunk_list[len(chunk_list) - 1].extend(chunk)
    elif (chunk):
        chunk_list.append(chunk)
    return(chunk_list)


def main():
    settings = parse_options()
    metadata = generate_filepaths(settings.input, settings.output)
    for row in metadata:
        text = read_text(row['filename'])
        if text is None:
            continue
        chunks = chunk_text(text.split(), settings.chunk_size,
                            settings.min_words)
        i = 0
        for chunk in chunks:
            fh = open(row['output_path'] + '/' + str(i), "w")
            fh.write(' '.join(chunk))
            fh.write("\n")
            i += 1
            fh.close()


if __name__ == '__main__':
    if sys.version_info < (3, 0):
        print("This script requires Python 3")
        exit(-1)
    main()
