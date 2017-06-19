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
        self.plot_terms = None
        self.actors = None
        self.actresses = None
        
        self.iid = None
        
        self.is_in_training = False
        self.training_instance = None
    
    
    def __repr__(self):
        #return self.title + "\t" + str(self.year) + "\t" + self.rating_distribution + "\t" + str(self.num_ratings) + "\t" + str(self.mean_rating)
        return self.title + "\t" + "(" + self.year + ")" + "\t" + "(" + self.certificate + ")"

class TrainingInstance(object):
    def __init__(self, id):
        self.id = id
        self.rationale_keywords = None
        self.rationale_actors = None
        self.rationale_actresses = None
        self.rationale_plot_terms = None
    
    def add_rationales(self, field, rationales):
        fv = getattr(self, field, None)
        if fv is None:
            fv = []
            setattr(self, field, fv)
        fv += rationales
            
    
    def add_rationale_keywords(self, keywords):
        if self.rationale_keywords is None:
            self.rationale_keywords = []
        self.rationale_keywords += keywords
    
    def add_rationale_plot_terms(self, plot_terms):
        if self.rationale_plot_terms is None:
            self.rationale_plot_terms = []
        self.rationale_plot_terms += plot_terms        
    
    def add_rationale_actors(self, actors):
        if self.rationale_actors is None:
            self.rationale_actors = []
        self.rationale_actors += actors
    
    def add_rationale_actresses(self, actresses):
        if self.rationale_actresses is None:
            self.rationale_actresses = []
        self.rationale_actresses += actresses
        