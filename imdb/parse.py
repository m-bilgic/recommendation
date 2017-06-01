def parse_imdb_data():
	
	import operator
	import re
	import sys
	from movie import Movie

	

	episode_re = re.compile("\(\d\d\d\d\)\s\{") # FIX: this does not match if the year has nondigit characters
	year_re = re.compile("\(\d\d\d\d")
	
	movies = []
	
	print("PARSING THE RATINGS FILE")
	#RATINGS FILE
	file_path = "../../imdb/ratings.list"
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
			if m.find("(VG)") != -1: #skip video games
				continue
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
				pass
				#e = sys.exc_info()[0]
				#print( "<p>Error: %s</p>" % e )
				#print("Failed to parse movie %s " %m)
	# GENRES FILE
	print("PARSING THE GENRES FILE")
	file_path = "../../imdb/genres.list"
	with open(file_path, 'r') as f:
		l = None
		while(l != "8: THE GENRES LIST"):
			l = f.readline().strip()
		#print(l)    
		# Dashes
		f.readline()
		# Empty
		f.readline()
		# Movies
		genres = {}
		for m in f:			
		#for i in range(1000):
			#m = f.readline()
			if m == "\n":
				break
			if m.find("(VG)") != -1: #skip video games
				continue
			m=m.strip()
			try:
				m_list=m.split()
				#print(m_list)
				genre = m_list[-1]
				if episode_re.search(m) is None: # if not episode                
					year_match = year_re.search(m)
					title = m[:year_match.start()-1]
					year = year_match.group()[1:]
					#movies.append(Movie(title, year, rating_distribution, num_ratings, mean_rating))
					#print("%s \t %d \t %s" %(title, year, genre))
					tandy = title+year
					if tandy in genres: # FIX: TWO OR MORE TITLES IN SEPARATE YEARS, GETS MATCHED TO THE SAME GENRE
						genres[tandy].append(genre)
					else:
						genres[tandy]=[genre]
			except:
				pass
				#e = sys.exc_info()[0]
				#print( "<p>Error: %s</p>" % e )
				#print("Failed to parse movie %s " %m)
	
	for m in movies:
		if m.title+str(m.year) in genres:			
			genre = genres[m.title+str(m.year)]        
			m.genre = genre
	
	return movies