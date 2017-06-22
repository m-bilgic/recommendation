class Book(object):
    def __init__(self, title, asin, editorial_review, sales_rank, imUrl):
        self.title = title
        self.asin = asin
        self.editorial_review = editorial_review
        self.sales_rank = sales_rank
        self.imUrl = imUrl
        
        self.editorial_review_terms = None
        self.is_in_training = False
        self.training_instance = None
    
    
    def __repr__(self):
        return self.title + " (" + self.asin + ")"

class TrainingInstance(object):
    def __init__(self, id):
        self.id = id
        self.rationale_editorial_review_terms = None
    
    def add_rationales(self, field, rationales):
        fv = getattr(self, field, None)
        if fv is None:
            fv = []
            setattr(self, field, fv)
        fv += rationales
        