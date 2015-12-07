'''
Download tweets and metadata from given accounts

2015, Mike Widner <mikewidner@stanford.edu>
'''

import os
import csv
import sys
import tweepy
import argparse
import configparser

def get_options():
  parser = argparse.ArgumentParser(description='Extract data from Twitter feeds')
  parser.add_argument('-s', '--screenames', dest='screen_names', required=True, help='List of Twitter screen_names to download tweets')
  parser.add_argument('-c', '--config', dest='config', required=True, help='Configuration settings ini')
  parser.add_argument('-o', '--output', dest='output', required=True, help='Output file for results')
  parser.add_argument('-n', '--num', dest='num_tweets', default = 50, help = 'Number of tweets to download per user')
  return parser.parse_args()

def get_screen_names(filename):
  '''
  Read a list of Twitter screen_names from a plain text file
  '''
  with open(filename, 'r') as f:
    accounts = f.read().split('\n')
  return accounts

def read_config(filename):
  '''
  Read the configuration file
  Return config object
  '''
  config = configparser.ConfigParser()
  config.read(filename)
  return config

def twitter_authenticate(login):
  '''
  Receive settings from login dict
  Returns an authenticated api object
  '''
  auth = tweepy.OAuthHandler(login['consumer_key'], login['consumer_secret'])
  auth.set_access_token(login['access_token'], login['access_token_secret'])
  api = tweepy.API(auth_handler = auth, wait_on_rate_limit = True, wait_on_rate_limit_notify = True)
  return api

def write_tweets(filename, rows):
  if not os.path.isfile(filename):
    csvfile = open(filename, 'w')
  else:
    csvfile = open(filename, 'a')
  tweet_data = csv.writer(csvfile, quotechar='|', quoting=csv.QUOTE_ALL)
  tweet_data.writerows(rows)

def get_tweets(api, screen_name, count, columns):
  rows = list()
  for tweet in tweepy.Cursor(api.user_timeline, id=screen_name).items(int(count)):
    row = [screen_name]
    for column in columns:
      row.append(getattr(tweet, column))
    rows.append(row)
  return rows

def main():
  options = get_options()
  config = read_config(options.config)
  api = twitter_authenticate(config['Auth'])
  columns = config['App']['columns'].split(',')
  write_tweets(options.output, [['name'] + columns]) # initialize output file
  for screen_name in get_screen_names(options.screen_names):
    if not len(screen_name):
      continue
    tweets = get_tweets(api, screen_name, options.num_tweets, columns)
    write_tweets(options.output, tweets)

if __name__ == '__main__':
  if sys.version_info[0] != 3:
    print("This program requires Python 3.")
    exit(-1)
  main()
