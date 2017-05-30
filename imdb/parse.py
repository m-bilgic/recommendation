def parse_imdb_data():
	
	import operator
	import re
	import sys
	from movie import Movie

	file_path = "../../imdb/ratings.list"

	episode_re = re.compile("\(\d\d\d\d\)\s\{") # FIX: this does not match if the year has nondigit characters
	year_re = re.compile("\(\d\d\d\d")
	
	movies = []

	with open(file_path, 'r') as f:
		l = None
		while(l != "MOVIE RATINGS REPORT"):
			l = f.readline().strip()
		#print(l)
		# empty line
		f.readline()
		# header
		f.readline()
		# Movies
		
		for m in f:
		#for i in range(100):
		#    m = f.readline()
			if m == "\n":
				break
			m=m.strip()
			try:
				m_list=m.split()
				rating_distribution = m_list[0]
				num_ratings = int(m_list[1])
				mean_rating = float(m_list[2])
				rest = " " . join(m_list[3:])
				if episode_re.search(rest) is None: # if not episode                
					year_match = year_re.search(rest)
					title = rest[:year_match.start()-1]
					year = int(year_match.group()[1:])
					movies.append(Movie(title, year, rating_distribution, num_ratings, mean_rating))
			except:
				#e = sys.exc_info()[0]
				#print( "<p>Error: %s</p>" % e )
				print("Failed to parse movie %s " %m)
	
	return movies