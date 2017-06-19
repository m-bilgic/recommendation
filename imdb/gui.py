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

import os
import pickle
from pathlib import Path


# In[]:


os.chdir("C:\\Users\\Mustafa\\Documents\\recommendation\\recommendation\\imdb")
from movie import Movie, TrainingInstance
from parse import parse_imdb_data
from displayfiltermovies import BrowseAllMovies, sortby, BrowseRecommendations

# In[]:

from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.preprocessing import normalize
from sklearn import svm


# In[]:

import numpy as np
from scipy.sparse import csr_matrix, vstack, hstack, diags

# In[]
def construct_matrices(movies, use_keywords=True, use_genre=True, use_plot=True, use_actors=True, use_actresses=True):
    global plot_terms_begin, plot_terms_end
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
        plot_terms_begin = len(vocabulary)
        vocabulary = vocabulary + vect.get_feature_names()
        plot_terms_end = len(vocabulary)
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
    
# In[]:
m_ = movies
#m_= list(filter(lambda m: m.year>2000, m_))
m_= list(filter(lambda m: m.num_ratings>10, m_))
#m_= list(filter(lambda m: m.mean_rating>8.3, m_))
m_= list(filter(lambda m: m.keywords is not None or m.plot is not None, m_))
#m_= list(filter(lambda m: m.plot is not None, m_))
m_= list(filter(lambda m: m.actors is not None or m.actresses is not None, m_))
#m_= list(filter(lambda m: m.actresses is not None, m_))
m_ = list(filter(lambda m: m.genres is not None and "Short" not in m.genres, m_))

m_ = np.array(m_) # For multiindexing
print(len(m_))


# In[]

plot_terms_begin = plot_terms_end = None

X, vocabulary = construct_matrices(m_, use_plot=True, use_genre=False)
print(X.shape)

if plot_terms_begin is not None:
    for i in range(len(m_)):
        m = m_[i]
        pt = []
        pi = list(filter(lambda f: f>=plot_terms_begin and f<plot_terms_end, X[i].indices))
        for p in pi:
            pt.append(vocabulary[p])
        m.plot_terms = pt        

# In[]

# In case the TrainingInstance class changed since last pickle
#tis = {}
#for tik in training_instances:
#    ti = training_instances[tik]
#    new_ti = TrainingInstance(ti.id)
#    new_ti.rationale_keywords = ti.rationale_keywords
#    new_ti.rationale_actors = ti.rationale_actors
#    new_ti.rationale_actresses = ti.rationale_actresses
#    new_ti.rationale_plot_terms = None
#    tis[new_ti.id] = new_ti
#training_instances = tis

# In[] Load a profile

training_instances = {}
training_set_iids = set()
active_profile = None

def load_a_profile(name, movies):
    global training_instances
    global training_set_iids
    global active_profile
    
    if active_profile is not None:
        pickle.dump(training_instances, open('profile_'+active_profile+'.p', "wb" ))
    
    if os.path.isfile('profile_'+name+'.p'):
        training_instances = pickle.load(open('profile_'+name+'.p', "rb"))        
    else:
        training_instances = {}    
        pickle.dump(training_instances, open('profile_'+name+'.p', "wb" ))        
    
    active_profile = name
    
    training_set_iids = set()
    
    for i in range(len(movies)):
        m = movies[i]
        if m.title+m.year in training_instances:
            training_set_iids.add(i)
            m.is_in_training = True
            m.training_instance = training_instances[m.title+m.year]
        else:
            m.is_in_training = False
            m.training_instance = None


# In[]

from operator import itemgetter

def get_possible_rationales(training_set_iids, movie_field):

    pr = {}
    
    for iid in training_set_iids:
        m = m_[iid]
        fv = getattr(m, movie_field, None)
        if fv is not None:
            for v in fv:
                if v in pr:
                    pr[v] += 1
                else:
                    pr[v] = 1
    
    prts = [(r, pr[r]) for r in pr]
    
    
    
    prts_sorted = sorted(prts, key=itemgetter(1), reverse=True)
    
    return prts_sorted

# In[]

root = Tk()
root.title("IMDB MOVIE RECOMMENDER SYSTEM")


root.option_add('*tearOff', FALSE)
menubar = Menu(root)
root['menu'] = menubar

menu_profile = Menu(menubar)
menubar.add_cascade(menu=menu_profile, label='Profile')

profile = StringVar()

def change_profile():    
    print("Profile changed to: %s" %profile.get())
    load_a_profile(profile.get(), m_)
    

def add_new_profile_menu(name):
    menu_profile.add_radiobutton(label=name, variable=profile, value=name, command=change_profile)
    # Change the profile to the new profile    
    profile.set(name)
    change_profile()


def new_profile(parent):
    
    tl = Toplevel(parent)
    tl.title("New Profile")
    tl.grab_set()
    
    new_profile_name = StringVar()
    
    profile_entry = ttk.Entry(tl, width=20, textvariable=new_profile_name)    
    profile_entry.pack(padx=5)
    
    def submit(*args):
        add_new_profile_menu(new_profile_name.get())
        tl.destroy()
        
    b = ttk.Button(tl, text="Submit", command=submit)
    b.pack(pady=5)
    
    profile_entry.focus()
    tl.bind('<Return>', submit)

menu_profile.add_command(label='New', command=lambda p = root: new_profile(p))

menu_profile.add_separator()

p = Path('.')
available_profiles = [f.name[8:-2] for f in p.glob('**/profile_*.p')]

for pname in available_profiles:    
    menu_profile.add_radiobutton(label=pname, variable=profile, value=pname, command=change_profile)

if len(available_profiles) > 0: # Load the first available profile
    profile.set(available_profiles[0])
    load_a_profile(available_profiles[0], m_)        
else:
    new_profile(root)
    



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
        ti = TrainingInstance(tid)
        training_instances[tid] = ti
        m.is_in_training = True
        m.training_instance = ti
        
    

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
            training_tree.delete(iid)
            m.is_in_training = False
            m.training_instance = None
    

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
    # The same features are multiplied over and over.
    # Make a copy of X first.
    Xc = X.copy()
    for iid in training_set_iids:
        m = m_[iid]
        if m.is_in_training:
            ti = m.training_instance
            if ti.rationale_keywords is not None:
                for k in ti.rationale_keywords:
                    try:
                        vi = vocabulary.index("Keyword:"+k)
                        Xc[iid, vi] *= 10
                    except ValueError:
                        pass
            if ti.rationale_plot_terms is not None:
                for pt in ti.rationale_plot_terms:
                    try:
                        vi = vocabulary.index(pt)
                        Xc[iid, vi] *= 10
                    except ValueError:
                        pass
            
            
    
    num_movies = len(m_)
    y = np.zeros(num_movies)
    for iid in dataset:
        y[int(iid)] = 1
    clf = svm.OneClassSVM(kernel='linear')
    clf.fit(Xc[np.where(y==1)])
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
    
    
    
    df = (clf.decision_function(Xc)).flatten()
    
    for i in range(len(m_)):
        m_[i].pred_score = df[i]
    
    top_ids = np.argsort(df)[::-1]
    
    di = (("Title", "title", False), ("Year", "year", False), ('Num Ratings', 'num_ratings', True), 
      ('Mean Rating', 'mean_rating', True), ('USA Certificate', 'certificate', False), ('Score', 'pred_score', True))

    dfm = BrowseRecommendations(rec_movies_frame, m_[top_ids], di, padding="3 3 12 12")
    dfm.setExplanation(X[top_ids]*coefs_diags, vocabulary)
    dfm.grid(column=0, row=0, sticky="nsew")
    
def bulk_add_rationales():    
    rationale_window = Toplevel(root)
    rationale_window.title("Bulk Add Rationales")
    
    rationale_window.columnconfigure(0, weight=1)
    rationale_window.columnconfigure(2, weight=1)
    rationale_window.rowconfigure(1, weight=1)    
    rationale_window.rowconfigure(4, weight=1)
    
    
    def _add_lb_and_button(field, frame, col_i, row_i, possible_rationales):
        
        def _add_chosen_rationales_to_movies(tree, col):
            selected_iids = tree.selection()
            data = [tree.set(iid, col) for iid in selected_iids]
            for iid in training_set_iids:
                m = m_[iid]
                for d in data:
                    if d in getattr(m, col):
                        print("Adding %s to %s" %(d, m))
                        m.training_instance.add_rationales("rationale_"+col, [d])
            
        
        ttk.Label(frame, text=field).grid(column=col_i, row=row_i, sticky="W")
        
        row_i += 1
        
        field_header = [field, 'Weight']
    
        rationales_tree = ttk.Treeview(frame, columns=field_header, show="headings")
        rationales_tree.grid(column=col_i, row=row_i, sticky="nsew")
        
        vsb = ttk.Scrollbar(frame, orient="vertical", command=rationales_tree.yview)
        rationales_tree.configure(yscrollcommand=vsb.set)
        vsb.grid(column=col_i+1, row=row_i, sticky='ns')
    
        
        for col in field_header:
            if col == "Weight":
                rationales_tree.heading(col, text=col.title(), command=lambda c=col: sortby(rationales_tree, c, 0, True))
            else:
                rationales_tree.heading(col, text=col.title(), command=lambda c=col: sortby(rationales_tree, c, 0, False))
            # adjust the column's width to the header string
            rationales_tree.column(col, width=tkFont.Font().measure(col.title()))
        
        for pr in possible_rationales:            
            item = [pr[0], pr[1]]
            rationales_tree.insert('', 'end', values=item)
        
        row_i += 1
        
        ttk.Button(frame, text="Add Selected " + field +" Rationales to All Applicable Movies", command=lambda rt=rationales_tree, col=field: _add_chosen_rationales_to_movies(rt, col)).grid(column=col_i, row=row_i, sticky = "nsew")
        
    
    keyword_rationales = get_possible_rationales(training_set_iids, "keywords")    
    _add_lb_and_button("keywords", rationale_window, 0, 0, keyword_rationales)
    plot_rationales = get_possible_rationales(training_set_iids, "plot_terms")
    _add_lb_and_button("plot_terms", rationale_window, 2, 0, plot_rationales)
    actor_rationales = get_possible_rationales(training_set_iids, "actors")
    _add_lb_and_button("actors", rationale_window, 0, 3, actor_rationales)
    actress_rationales = get_possible_rationales(training_set_iids, "actresses")
    _add_lb_and_button("actresses", rationale_window, 2, 3, actress_rationales)
    
    
    
    



ttk.Button(modeling_frame, text="Add Selected to Training Set", command=add_selected_to_training_data).grid(column=0, row=0, sticky = "nsew")
ttk.Button(modeling_frame, text="Edit Training Set", command=edit_training_data).grid(column=1, row=0, sticky = "nsew")
ttk.Button(modeling_frame, text="Bulk Add Rationales", command=bulk_add_rationales).grid(column=0, row=1, columnspan = 2, sticky = "nsew")
ttk.Button(modeling_frame, text="Train a Model on Training Set", command=train_a_model_on_training_set).grid(column=0, row=2, columnspan = 2, sticky = "nsew")
ttk.Button(modeling_frame, text="Train a Model on Displayed Data", command=train_a_model_on_displayed_data).grid(column=0, row=3, columnspan = 2, sticky = "nsew")


root.mainloop()

# In[]

if active_profile is not None:
    pickle.dump(training_instances, open('profile_'+active_profile+'.p', "wb" ))

