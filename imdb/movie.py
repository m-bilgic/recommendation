class Movie(object):
	def __init__(self, title, year, rating_distribution, num_ratings, mean_rating):
		self.title = title
		self.year = year
		self.rating_distribution = rating_distribution
		self.num_ratings = num_ratings
		self.mean_rating = mean_rating
		self.genres = None
		self.keywords = None
		self.certificate = "Unknown"
		self.mpaa_rating = "Unknown"
		self.mpaa_reason = None
		self.plot = None
		self.actors = None
		self.actresses = None
		
	def __repr__(self):
		#return self.title + "\t" + str(self.year) + "\t" + self.rating_distribution + "\t" + str(self.num_ratings) + "\t" + str(self.mean_rating)
		return self.title + "\t" + "(" + self.year + ")" + "\t" + "(" + self.certificate + ")"