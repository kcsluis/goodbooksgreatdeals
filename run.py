import os
import csv
import pandas as pd
from numpy import interp
from amazon import AmazonParser
from amazon import GoodreadsParser

def parseAndEnrichList(amazon_parser, goodreads_parser, tsvin):
	tsvin = csv.reader(tsvin, delimiter='\t')
	iterrows = iter(tsvin)
	next(iterrows) #skip the first row which is our header
	booklist = []				
	for row in iterrows:
		title = row[0]
		isbn = row[1]
		print 'Looking up %s (ISBN  %s) on amazon.com...' % (title, isbn)
		amazon_book_data = amazon_parser.lookupISBN(isbn, title)
		print 'Looking up %s (ISBN  %s) on goodreads.com...' % (title, isbn)
		goodreads_book_data = goodreads_parser.lookupISBN(isbn)

		#merge
		book_data = dict(amazon_book_data.items() + goodreads_book_data.items())
		booklist.append(book_data)

	return booklist


def scoreBooks(df):
	pd.set_option('mode.chained_assignment', None)
	df = df.dropna(subset=['price'])
	df['price_i'] = interp(df['price'].astype(float),[500,3000],[100,0])
	df['rating_i'] = interp(df['rating'].astype(float),[3.0,5.0],[0,100])
	df['rating_count_i'] = interp(df['rating_count'].astype(float),[100,10000],[0,100])
	df['new_score'] = df['price_i'] + df['rating_i'] + df['rating_count_i']
	df = df.sort_values(by='new_score', ascending=False)
	return df

def writeBookListToCSV(filename, booklist):
	df = pd.DataFrame(booklist)
	df = scoreBooks(df)
	fullpath = os.getcwd()+'/output/'+filename
	df.to_csv(fullpath, sep='\t', encoding='utf-8')
	print 'Done writing %s :)' % filename

if __name__ == '__main__':

	AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
	AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
	AWS_ASSOCIATE_TAG = os.getenv('AWS_ASSOCIATE_TAG')
	GOODREADS_KEY = os.getenv('GOODREADS_KEY')

	amazon_parser = AmazonParser(
		AWS_ACCESS_KEY_ID,
		AWS_SECRET_ACCESS_KEY,
		AWS_ASSOCIATE_TAG
	)
	goodreads_parser = GoodreadsParser(GOODREADS_KEY)

	for root, subFolders, files in os.walk(os.getcwd()+'/input'):
		for i in files:
			with open('%s/%s' % (root,i)) as data:
				booklist = parseAndEnrichList(amazon_parser, goodreads_parser, data)
				writeBookListToCSV(i, booklist)





