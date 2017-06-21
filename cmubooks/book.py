class Book(object):
    def __init__(self, title, author, date, genres, summary):
        self.title = title
        self.author = author
        self.date = date
        self.genres = genres
        self.summary = summary
        
        self.iid = None
        
        self.summary_terms = None
        
        self.is_in_training = False
        self.training_instance = None
    
    
    def __repr__(self):
        return self.title + " BY " + self.author

class TrainingInstance(object):
    def __init__(self, id):
        self.id = id
        self.rationale_summary_terms = None
        