'''
Tweets-to-text

Read in an CSV file of tweets
Organize and combine the text files for analysis and further processing

Mike Widner <mikewidner@stanford.edu>
'''
import os
import re
import csv
import sys
import time
import datetime
import argparse

def get_options():
	parser = argparse.ArgumentParser(description='Join tweet texts into single file')
	parser.add_argument('-i', dest='input', required=True, help='Input file as CSV where tweet data exists')
	parser.add_argument('-o', dest='output', required=True, help='Output filename for results')
	parser.add_argument('-s', '--start', dest='start_date', help='Start date for tweets, formatted YYYY-MM-DD', default=None)
	parser.add_argument('-e', '--end', dest='end_date', help='End date for tweets, formatted YYYY-MM-DD')
	parser.add_argument('--hashtag', dest='hashtag', help='Hashtag to search for. Omit the leading #')
	parser.add_argument('-c', '--clean', dest='clean', action='store_true', help='Remove all URLs and hashtags from tweet text before saving.')
	return parser.parse_args()

def read_tweet_data(filename):
	with open(filename) as csvfile:
		reader = csv.DictReader(csvfile, skipinitialspace=True, delimiter=',', quotechar="|")
		tweet_data = [row for row in reader]
	return tweet_data

def get_date_tuple(string):
	'''
	Get only the year, month, and day
	Ignore time
	'''
	return time.strptime(string[:10], '%Y-%m-%d')

def filter_by_date(tweets, start, end):
	if start is None and end is None:
		return tweets
	if start is None:
		start = '1000-01-01'
	start = get_date_tuple(start)
	if end is None:
		end = datetime.date.today().strftime('%Y-%m-%d')
	end = get_date_tuple(end)
	date_filtered_tweets = list()
	for tweet in tweets:
		created_at = get_date_tuple(tweet['created_at'])
		if created_at >= start and created_at <= end:
			date_filtered_tweets.append(tweet)
	return date_filtered_tweets

def filter_by_hashtag(tweets, hashtag):
	return [tweet for tweet in tweets if '#' + hashtag.lower() in tweet['text'].lower()]

def clean_text(text):
	# Remove URLs
	text = re.sub('https?:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*', '', text, flags=re.MULTILINE)
	# Remove hash tags
	text = re.sub('#\w+', '', text, flags=re.MULTILINE)
	return text

def write_text(tweets, filename, clean = False):
	'''
	Write out all words in tweets a single text file
	'''
	dirname = os.path.dirname(filename)
	if len(dirname) and not os.path.isdir(dirname):
		os.makedirs(dirname)
	words = ''
	for tweet in tweets:
		text = tweet['text']
		if clean:
			text = clean_text(text)
		words += text + '\n'
	with open(filename, 'w') as f:
		f.write(words)

def main():
	'''
	Process metadata
	Organize by different slicings
	'''
	options = get_options()
	tweets = read_tweet_data(options.input)
	if options.start_date or options.end_date:
		tweets = filter_by_date(tweets, options.start_date, options.end_date)
	if options.hashtag:
		tweets = filter_by_hashtag(tweets, options.hashtag)
	write_text(tweets, options.output, options.clean)


if __name__ == '__main__':
	if sys.version_info[0] != 3:
		print("This program requires Python 3.")
		exit(-1)
	main()
