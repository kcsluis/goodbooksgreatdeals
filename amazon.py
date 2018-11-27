import os
import bottlenose
from bs4 import BeautifulSoup
import requests

class AmazonParser:

	def lookupISBN(self, isbn, title):
		thisbook = {}
		thisbook['isbn'] = isbn
		thisbook['title'] = title

		response = self.amazon.ItemLookup(
			ItemId=isbn,
			IdType='ISBN',
			SearchIndex='All',
			ResponseGroup='Large'
		).find_all('Item') # sometimes there are multiple items in response, this likely gets best match
		
		best_response = max(response, key=len)

		#TODO: rewrite the if statements below
		if hasattr(best_response.ISBN, 'string'):
			thisbook['amazon_isbn'] = best_response.ISBN.string
		if hasattr(best_response.Author, 'string'):
			thisbook['author'] = best_response.Author.string
		if hasattr(best_response.Binding, 'string'):
			thisbook['binding'] = best_response.Binding.string
		if hasattr(best_response.OfferListing, 'Price'):
			if hasattr(best_response.OfferListing.Price, 'Amount'):
				if hasattr(best_response.OfferListing.Price.Amount, 'string'):
					thisbook['price'] = best_response.OfferListing.Price.Amount.string
		if hasattr(best_response.OfferListing, 'PercentageSaved'):
			if hasattr(best_response.OfferListing.PercentageSaved, 'string'):
				thisbook['percent_off'] = best_response.OfferListing.PercentageSaved.string
		if hasattr(best_response.NumberOfPages, 'string'):
			thisbook['page_count'] = best_response.NumberOfPages.string
		if hasattr(best_response.DetailPageURL, 'string'):
			thisbook['url'] = best_response.DetailPageURL.string
		if hasattr(best_response.LargeImage, 'URL'):
			if hasattr(best_response.LargeImage.URL, 'string'):
				thisbook['img'] = best_response.LargeImage.URL.string
		if hasattr(best_response.EditorialReviews, 'Content'):
			if hasattr(best_response.EditorialReviews.Content, 'string'):
				thisbook['description'] = best_response.EditorialReviews.Content.string

		return thisbook

	def __init__(self, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_ASSOCIATE_TAG):
		self.amazon = bottlenose.Amazon(
			AWS_ACCESS_KEY_ID, 
			AWS_SECRET_ACCESS_KEY, 
			AWS_ASSOCIATE_TAG, 
			Parser=lambda text: BeautifulSoup(text, 'xml'),
			MaxQPS=0.5
		)

class GoodreadsParser:

	def lookupISBN(self, isbn):
		thisbook = {}
		thisbook['isbn'] = isbn

		url = 'https://www.goodreads.com/book/review_counts.json?isbns=%s&key=%s' % (isbn, self.GOODREADS_KEY)
		response = requests.get(url)

		if response.status_code == 200:
			result = response.json()
			thisbook['rating'] = result['books'][0]['average_rating']
			thisbook['rating_count'] = result['books'][0]['work_ratings_count']
		
		return thisbook

	def __init__(self, GOODREADS_KEY):
		self.GOODREADS_KEY = GOODREADS_KEY

