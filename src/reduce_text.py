'''
Reduce texts to the lemmas for only given parts-of-speech

Mike Widner <mikewidner@stanford.edu>
'''

import os
import sys
import argparse
import metadata as m  # So I can use 'metadata' as a variable name
import wordfreqs as wf
import treetaggerwrapper as ttw

def get_settings():
  parser = argparse.ArgumentParser(description='Reduce texts to given parts-of-speech')
  parser.add_argument('-p', '--pos', dest='pos_list', action='append', required=True, help='Reduce texts to only given parts-of-speech')
  parser.add_argument('-i', '--input', dest='input', required=True, help='Metadata input file as CSV')
  parser.add_argument('-o', '--output', dest='output_dir', required=True, help='Output directory for reduced texts')
  parser.add_argument('-l', '--language', dest='language', required=True, help='Language in which the texts were written', choices=wf.lang_codes.keys(), type = str.lower)
  return parser.parse_args()

def reduce(tagged_text, pos_list):
  reduction = list()
  for tag in tagged_text:
    if not isinstance(tag, ttw.Tag):
      continue
    if tag.pos in pos_list:
      reduction.append(tag.lemma.split('|')[0].lower())
  return ' '.join(reduction)

def get_new_path(filename, output_dir):
  return os.path.join(output_dir, os.path.basename(filename))

def main():
  settings = get_settings()
  metadata = m.read_csv(settings.input)
  if (not os.path.exists(settings.output_dir)):
    os.makedirs(settings.output_dir)
  for row in metadata:
    filename = row['filename']
    try:
      text = wf.get_text_from_file(filename)
    except FileNotFoundError as err:
      print('Skipping: {}'.format(err))
      continue
    except IsADirectoryError:
      continue  # bad metadata, ignore
    outfile = wf.output_filename(settings.output_dir, filename)
    pos_tagged_text = wf.tag_pos(text, settings.language)
    reduced_text = reduce(pos_tagged_text, settings.pos_list)
    new_filename = get_new_path(filename, settings.output_dir)
    row['filename'] = new_filename
    fh = open(new_filename, 'w')
    fh.write(reduced_text)
    fh.close()
  new_filename = get_new_path(settings.input, settings.output_dir)
  m.write_csv(new_filename, metadata)

if __name__ == '__main__':
  if sys.version_info < (3,0):
    print("This script requires Python 3")
    exit(-1)
  main()
