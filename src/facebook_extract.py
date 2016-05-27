'''
Read data from Facebook posts for given user(s)

Mike Widner <mikewidner@stanford.edu>
'''

import os
import re
import csv
import json
import argparse
import facebook
import requests

settings = None

def get_settings():
  parser = argparse.ArgumentParser(description='Extract data from Facebook feeds')
  parser.add_argument('-f', dest='feed', required=True, action='append', help='A facebook ID')
  parser.add_argument('-i', '--app-id', required=True, dest='app_id',
                   help='The application ID')
  parser.add_argument('-s', '--app-secret', required=True, dest='app_secret', help='The application secret')
  parser.add_argument('-o', '--outputdir', required=True, dest='outputdir', help='Output directory to store results')
  parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', required=False, help='Provide verbose output')
  return parser.parse_args()

def get_facebook_graph(app_id, app_secret):
  graph = facebook.GraphAPI()
  access_token = graph.get_app_access_token(app_id, app_secret)
  graph = facebook.GraphAPI(access_token=access_token)
  return graph

def write_followed_link(link, data):
  filename = re.sub(r'^https?:\/\/', '', link) + '.html'
  outfile = os.path.join(settings.outputdir, filename)
  if not os.path.isdir(os.path.dirname(outfile)):
    os.makedirs(os.path.dirname(outfile))
  with open(outfile, 'w') as f:
    f.write(data)

def get_facebook_data(graph, feed_url):
  data = list()
  first_page = True
  while(True):
    try:
      if first_page:
        posts = graph.get_object(feed_url)
        first_page = False
      else:
        posts = requests.get(posts['paging']['next']).json()
      for post in posts['data']:
        if post['status_type'] == 'shared_story':
          data.append(graph.get_object(post['id']))
          if post['link']:
            try:
              r = requests.get(post['link'])
              r.encoding = 'utf-8'
              write_followed_link(post['link'], r.text)
            except:
              # Couldn't retrieve the link, don't sweat it
              pass
    except KeyError:
      # No more pages
      break
  return data

def generate_header(data):
  return ['id', 'created_time', 'message', 'link']

def write_results(feed_id, data, outputdir):
  outfile = os.path.join(outputdir, feed_id + '.csv')
  if not os.path.isdir(outputdir):
    os.makedirs(outputdir)
  with open(outfile, 'w') as f:
    csvfile = csv.writer(f, quotechar='|')
    keys = generate_header(data)
    csvfile.writerow(keys)
    for item in data:
      row = list()
      for key in keys:
        try:
          row.append(item[key])
        except KeyError:
          row.append('')
      csvfile.writerow(row)

def main():
  global settings
  settings = get_settings()
  graph = get_facebook_graph(settings.app_id, settings.app_secret)
  for feed_id in settings.feed:
    data = get_facebook_data(graph, feed_id + '/feed')
    write_results(feed_id, data, settings.outputdir)

if __name__ == "__main__":
  main()
