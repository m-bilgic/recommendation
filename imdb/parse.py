def parse_imdb_data():
	
	import operator
	import re
	import sys
	from movie import Movie

	

	episode_re = re.compile("\(\d\d\d\d[/\S]*\)\s\{") # FIX: this does not match if the year has nondigit characters
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
			if m.find("(V)") != -1:
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
			if m.find("(V)") != -1:
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
					tandy = title+year
					if tandy in genres:
						genres[tandy].append(genre)
					else:
						genres[tandy]=[genre]
			except:
				pass
				#e = sys.exc_info()[0]
				#print( "<p>Error: %s</p>" % e )
				#print("Failed to parse movie %s " %m)
	
	# KEYWORDS FILE
	print("PARSING THE KEYWORDS FILE")
	file_path = "../../imdb/keywords.list"
	with open(file_path, 'r') as f:
		l = None
		while(l != "8: THE KEYWORDS LIST"):
			l = f.readline().strip()
		#print(l)
		# Dashes
		f.readline()
		# Empty
		f.readline()
		# Movies
		keywords = {}
		for m in f:
			#break
		#for i in range(1000):
			#m = f.readline()
			if m == "\n":
				break
			if m.find("(VG)") != -1: #skip video games
				continue
			if m.find("(V)") != -1:
				continue
			m=m.strip()
			try:
				m_list=m.split()
				#print(m_list)
				keyword = m_list[-1]
				if episode_re.search(m) is None: # if not episode                
					year_match = year_re.search(m)
					title = m[:year_match.start()-1]
					year = year_match.group()[1:]
					tandy = title+year
					if tandy in keywords:
						keywords[tandy].append(keyword)
					else:
						keywords[tandy]=[keyword]
			except:
				pass
				#e = sys.exc_info()[0]
				#print( "<p>Error: %s</p>" % e )
				#print("Failed to parse movie %s " %m)
	# MPAA Ratings
	print("PARSING THE MPAA RATINGS REASONS FILE")
	file_path = "../../imdb/mpaa-ratings-reasons.list"
	with open(file_path, 'r') as f:
		l = None
		while(l != "MPAA RATINGS REASONS LIST"):
			l = f.readline().strip()
		#print(l)
		# Double Dashes
		f.readline()
		# Single dashes
		f.readline()
		# Movies
		mpaa = {}
		for m in f:
			#break
		#for i in range(1000):
			#m = f.readline()
	#        if m == "\n":
	#            break
			if m.find("(VG)") != -1: #skip video games
				m = f.readline()
				while m[:3] == "RE:":
					m = f.readline()
				f.readline()
				continue
			if m.find("(V)") != -1:
				m = f.readline()
				while m[:3] == "RE:":
					m = f.readline()
				f.readline()
				continue
			m=m.strip()
			try:            
				if episode_re.search(m) is None:
					year_match = year_re.search(m)
					title = m[4:year_match.start()-1]
					year = year_match.group()[1:]
					tandy = title+year
					mpaar = ""
					m = f.readline()
					while m[:3] == "RE:":
						mpaar += " " + m[3:].strip()
						m = f.readline()
					mpaa[tandy] = mpaar
					f.readline()
			except:
				m = f.readline()
				while m[:3] == "RE:":
					m = f.readline()
				f.readline()
				#e = sys.exc_info()[0]
				#print( "<p>Error: %s</p>" % e )
				#print("Failed to parse movie %s " %m)
	
	# Certificates
	print("PARSING THE CERTIFICATES FILE")
	file_path = "../../imdb/certificates.list"
	with open(file_path, 'r') as f:
		l = None
		while(l != "CERTIFICATES LIST"):
			l = f.readline().strip()
		#print(l)
		# Dashes
		f.readline()
		# Movies
		certificates = {}
		for m in f:
			#break
		#for i in range(300):
		#    m = f.readline()
	#        if m == "\n":
	#            break
			m=m.strip()
		
			if m.find("(VG)") != -1: #skip video games
				continue
			if m.find("(V)") != -1:
				continue
			if m.find("USA:") == -1:
				continue
			
			try:            
				if episode_re.search(m) is None:
					year_match = year_re.search(m)
					title = m[:year_match.start()-1]
					year = year_match.group()[1:]
					tandy = title+year
					certificate = m[m.find("USA:")+4:].split('\t')[0]
					certificates[tandy] = certificate               
			except:
				pass
				#e = sys.exc_info()[0]
				#print( "<p>Error: %s</p>" % e )
				#print("Failed to parse movie %s " %m)
				
	for m in movies:
		if m.title+str(m.year) in genres:
			gs = genres[m.title+str(m.year)]        
			m.genres = gs
		if m.title+str(m.year) in keywords:
			ks = keywords[m.title+str(m.year)]        
			m.keywords = ks
		if m.title+str(m.year) in mpaa:
			m.mpaa_reason = mpaa[m.title+str(m.year)]
			mpaa_split = m.mpaa_reason.split()
			m.mpaa_rating = mpaa_split[1]
		if m.title+str(m.year) in certificates:
			m.certificate = certificates[m.title+str(m.year)]
	
	
	return movies