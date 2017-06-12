# -*- coding: utf-8 -*-
"""
Created on Thu Jun  8 16:20:45 2017

@author: Mustafa
"""

# coding: utf-8

# In[]:

from tkinter import *
from tkinter import ttk
import tkinter.font as tkFont
from tkinter import font


# In[]:

from movie import Movie, TrainingInstance
from parse import parse_imdb_data
from displayfiltermovies import BrowseAllMovies, sortby, BrowseRecommendations


# In[]:

import os
import pickle


# In[]:

from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.preprocessing import normalize
from sklearn import svm


# In[]:

import numpy as np
from scipy.sparse import csr_matrix, vstack, hstack, diags

# In[]
def construct_matrices(movies, use_keywords=True, use_genre=True, use_plot=True, use_actors=True, use_actresses=True):
    Dk = []
    Dg = []
    Dp = []
    Da1 = []
    Da2 = []
    
    
    for m in movies:
        ms = ''
        if m.keywords is not None:
            #ms = " ".join(m.keywords)
            ms = " ".join(["Keyword:"+k for k in m.keywords])
        Dk.append(ms)
        mg = ''
        if m.genres is not None:
            mg = " ".join(["Genre:"+g for g in m.genres])
        Dg.append(mg)
        if m.plot is not None:
            #plot = m.plot.split()
            #plot = " ".join(["Plot:"+p for p in plot])
            #Dp.append(plot)
            Dp.append(m.plot)
        else:
            Dp.append("")
        if m.actors is not None:
            a = ""
            for actor in m.actors:
                a = a + " Actor:" + actor.replace(" ", "")
            Da1.append(a)
        else:
            Da1.append("")
        if m.actresses is not None:
            a = ""
            for actress in m.actresses:
                a = a + " Actress:" + actress.replace(" ", "")
            Da2.append(a)
        else:
            Da2.append("")
    
    vocabulary = []
    
    X = None
    
    # Genre
    if use_genre:
        vect = CountVectorizer(token_pattern = r'\b\S+\b', lowercase=False, binary=True)
        #vect = TfidfVectorizer(token_pattern = r'\b\S+\b', lowercase=False)
        Xg = vect.fit_transform(Dg)
        Xg = normalize(Xg) # Some movies have a lot of genres
        vocabulary = vocabulary + vect.get_feature_names()
        X = Xg
    
    # Keywords
    if use_keywords:
        vect = CountVectorizer(token_pattern = r'\b\S+\b', min_df=5, lowercase=False, binary=True, dtype=np.float)
        #vect = TfidfVectorizer(token_pattern = r'\b\S+\b', min_df=5)
        Xk = vect.fit_transform(Dk)
        Xk = normalize(Xk)
        vocabulary = vocabulary + vect.get_feature_names()
        if X is None:
            X = Xk
        else:
            X = hstack((X, Xk)).tocsr()
        
    
    
    # Plot
    if use_plot:
        vect = TfidfVectorizer(token_pattern = r'\b\S+\b', min_df=5, stop_words='english')
        Xp = vect.fit_transform(Dp)
        vocabulary = vocabulary + vect.get_feature_names()
        if X is None:
            X = Xp
        else:
            X = hstack((X, Xp)).tocsr()
    
    # Actors
    if use_actors:
        vect = CountVectorizer(token_pattern = r'\b\S+', lowercase=False, binary=True, dtype=np.float)
        Xa1 = vect.fit_transform(Da1)
        Xa1 = normalize(Xa1)
        vocabulary = vocabulary + vect.get_feature_names()
        if X is None:
            X = Xa1
        else:
            X = hstack((X, Xa1)).tocsr()
    
    # Actresses
    if use_actresses:
        vect = CountVectorizer(token_pattern = r'\b\S+', lowercase=False, binary=True, dtype=np.float)
        Xa2 = vect.fit_transform(Da2)
        Xa2 = normalize(Xa2)
        vocabulary = vocabulary + vect.get_feature_names()
        if X is None:
            X = Xa2
        else:
            X = hstack((X, Xa2)).tocsr()
    
    return (X, vocabulary)

# In[]:

if os.path.isfile("movies.p"):
    movies = pickle.load(open("movies.p", "rb"))
else:
    movies = parse_imdb_data()
    pickle.dump(movies, open( "movies.p", "wb" ))

if os.path.isfile("training_instances.p"):
    training_instances = pickle.load(open("training_instances.p", "rb"))
else:
    training_instances = {}
    
# In[]:
m_ = movies
#m_= list(filter(lambda m: m.year>2000, m_))
m_= list(filter(lambda m: m.num_ratings>1000, m_))
#m_= list(filter(lambda m: m.mean_rating>9.3, m_))
m_= list(filter(lambda m: m.keywords is not None, m_))
print(len(m_))

X, vocabulary = construct_matrices(m_, use_plot=False, use_genre=False)
print(X.shape)

# In[]

training_set_iids = set()

for i in range(len(m_)):
    m = m_[i]
    if m.title+m.year in training_instances:
        training_set_iids.add(i)
        m.is_in_training = True
        m.training_instance = training_instances[m.title+m.year]
    else:
        m.is_in_training = False
        m.training_instance = None

# In[]


root = Tk()
root.title("IMDB MOVIE RECOMMENDER SYSTEM")

root.rowconfigure(0, weight=1)
root.rowconfigure(1, weight=0)
root.columnconfigure(0, weight=1)

di = (("Title", "title", False), ("Year", "year", False), ('Num Ratings', 'num_ratings', True), 
      ('Mean Rating', 'mean_rating', True), ('USA Certificate', 'certificate', False))

dfm = BrowseAllMovies(root, m_, di, padding="3 3 12 12")
dfm.grid(column=0, row=0, sticky="nsew")

data_tree = dfm.get_tree()

modeling_frame = ttk.Labelframe(root, padding="3 3 12 12", text="Modeling")
modeling_frame.grid(column=0, row=1, sticky = "nsew")

modeling_frame.columnconfigure(0, weight=1)
modeling_frame.columnconfigure(1, weight=1)


def add_selected_to_training_data():
    selected_iids = data_tree.selection()    
    for iid in selected_iids:
        m = m_[int(iid)]
        training_set_iids.add(int(iid))
        tid = m.title+m.year
        training_instances[tid] = TrainingInstance(tid)        
    

def edit_training_data():
    tl = Toplevel(root)
    tl.title("Training Set")
    
    di = (("Title", "title", False), ("Year", "year", False), ('Num Ratings', 'num_ratings', True), 
      ('Mean Rating', 'mean_rating', True), ('USA Certificate', 'certificate', False))
    
    rated_movies = []
    original_iids = []
    
    for iid in training_set_iids:
        rated_movies.append(m_[int(iid)])
        original_iids.append(iid)
    
    dfm = BrowseAllMovies(tl, rated_movies, di, padding="3 3 12 12")
    dfm.grid(column=0, row=0, sticky="nsew")
    training_tree = dfm.get_tree()
    
    def remove_selected_from_training_set():
        selected_iids = training_tree.selection()
        for iid in selected_iids:
            training_set_iids.remove(original_iids[int(iid)])            
            m = m_[original_iids[int(iid)]]
            training_instances.pop(m.title + m.year, None)
        training_tree.delete(selected_iids)
    

    ttk.Button(tl, text="Remove Selected from Training Set", command=remove_selected_from_training_set).grid(column=0, row=1, sticky = "nsew")
    
    
    ttk.Button(tl, text="Remove Selected from Training Set", command=remove_selected_from_training_set).grid(column=0, row=1, sticky = "nsew")
    

    
    tl.columnconfigure(0, weight=1)
    tl.rowconfigure(0, weight=1)

def train_a_model_on_displayed_data():
    data = data_tree.get_children('')    
    dataset = set()    
    for iid in data:
       dataset.add(iid)
    train_a_model(dataset)

def train_a_model_on_training_set():
    train_a_model(training_set_iids)

def train_a_model(dataset):    
    for iid in training_set_iids:
        m = m_[iid]
        if m.is_in_training:
            ti = m.training_instance
            if ti.rationale_keywords is not None:
                for k in ti.rationale_keywords:
                    try:
                        vi = vocabulary.index("Keyword:"+k)
                        X[iid, vi] *= 10
                    except ValueError:
                        pass
    
    num_movies = len(m_)
    y = np.zeros(num_movies)
    for iid in dataset:
        y[int(iid)] = 1
    clf = svm.OneClassSVM(kernel='linear')
    clf.fit(X[np.where(y==1)])
    clf_coefs = clf.coef_.toarray()[0]
    coefs_diags = diags(clf_coefs, 0)
    #feat_indices = np.argsort(np.abs(clf_coefs))[::-1]
    #for i in feat_indices[:30]:
    #    print(vocabulary[i])
    #print()
    model_window = Toplevel(root)
    
    model_window.title("Recommended Movies")
    
    features_frame = ttk.Labelframe(model_window, padding="3 3 12 12", text="Features")
    features_frame.grid(column=0, row=0, sticky="nsew")
    rec_movies_frame = ttk.Labelframe(model_window, padding="3 3 12 12", text="Recommended Movies")
    rec_movies_frame.grid(column=1, row=0, sticky="nsew")
    
    model_window.columnconfigure(0, weight=1)
    model_window.columnconfigure(1, weight=3)
    model_window.rowconfigure(0, weight=1)
    
    
    features_frame.columnconfigure(0, weight=1)
    features_frame.rowconfigure(0, weight=1)
    
    rec_movies_frame.columnconfigure(0, weight=1)
    rec_movies_frame.rowconfigure(0, weight=1) 
    
    features_header = ['Feature', 'Weight']
    
    features_tree = ttk.Treeview(features_frame, columns=features_header, show="headings", selectmode='browse')
    features_tree.grid(column=0, row=0, sticky="nsew")    
    
    vsb = ttk.Scrollbar(features_frame, orient="vertical", command=features_tree.yview)
    features_tree.configure(yscrollcommand=vsb.set)
    vsb.grid(column=1, row=0, sticky='ns')

    
    for col in features_header:
        if col == "Weight":
            features_tree.heading(col, text=col.title(), command=lambda c=col: sortby(features_tree, c, 0, True))
        else:
            features_tree.heading(col, text=col.title(), command=lambda c=col: sortby(features_tree, c, 0, False))
        # adjust the column's width to the header string
        features_tree.column(col, width=tkFont.Font().measure(col.title()))
    
    for i in range(len(vocabulary)):
        if abs(clf_coefs[i]) > 0.01:
            item = [vocabulary[i], clf_coefs[i]]
            features_tree.insert('', 'end', iid = str(i), values=item)
    
    
    
    df = (clf.decision_function(X)).flatten()
    
    for i in range(len(m_)):
        m_[i].pred_score = df[i]    
    
    di = (("Title", "title", False), ("Year", "year", False), ('Num Ratings', 'num_ratings', True), 
      ('Mean Rating', 'mean_rating', True), ('USA Certificate', 'certificate', False), ('Score', 'pred_score', True))

    dfm = BrowseRecommendations(rec_movies_frame, m_, di, padding="3 3 12 12")
    dfm.setExplanation(X*coefs_diags, vocabulary)
    dfm.grid(column=0, row=0, sticky="nsew")
    
    



ttk.Button(modeling_frame, text="Add Selected to Training Set", command=add_selected_to_training_data).grid(column=0, row=0, sticky = "nsew")
ttk.Button(modeling_frame, text="Edit Training Set", command=edit_training_data).grid(column=1, row=0, sticky = "nsew")
ttk.Button(modeling_frame, text="Train a Model on Training Set", command=train_a_model_on_training_set).grid(column=0, row=1, sticky = "nsew")
ttk.Button(modeling_frame, text="Train a Model on Displayed Data", command=train_a_model_on_displayed_data).grid(column=1, row=1, sticky = "nsew")


root.mainloop()

# In[]

pickle.dump(training_instances, open( "training_instances.p", "wb" ))

