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


os.chdir("C:\\Users\\Mustafa\\Documents\\recommendation\\recommendation\\amazonbooks")
from book import Book, TrainingInstance
from parse import parse_books
from displayfilterbooks import BrowseAllBooks, sortby, BrowseRecommendations

# In[]:

from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.preprocessing import normalize
from sklearn import svm


# In[]:

import numpy as np
from scipy.sparse import csr_matrix, vstack, hstack, diags

# In[]
def construct_matrices(books, use_editorial_review=True):
    global editorial__review_terms_begin, editorial__review_terms_end
    De = []
    
    for b in books:
        if b.editorial_review is not None:
            De.append(b.editorial_review)
        else:
            De.append("")        
    
    vocabulary = []
    
    X = None
    
    # Plot
    if use_editorial_review:
        vect = TfidfVectorizer(token_pattern = r'\b\S+\b', min_df=5, ngram_range=(1, 2), stop_words='english')
        Xp = vect.fit_transform(De)
        editorial__review_terms_begin = len(vocabulary)
        vocabulary = vocabulary + vect.get_feature_names()
        editorial__review_terms_end = len(vocabulary)
        if X is None:
            X = Xp
        else:
            X = hstack((X, Xp)).tocsr()
    
    return (X, vocabulary)


# In[]:
    
if os.path.isfile("books.p"):
    books = pickle.load(open("books.p", "rb"))
else:
    books = parse_books()
    pickle.dump(books, open( "books.p", "wb" ))
    
# In[]:
m_ = books

m_ = np.array(m_) # For multiindexing
print(len(m_))


# In[]

editorial__review_terms_begin = editorial__review_terms_end = None

X, vocabulary = construct_matrices(m_, use_editorial_review=True)
print(X.shape)

if editorial__review_terms_begin is not None:
    for i in range(len(m_)):
        m = m_[i]
        pt = []
        pi = list(filter(lambda f: f>=editorial__review_terms_begin and f<editorial__review_terms_end, X[i].indices))
        for p in pi:
            pt.append(vocabulary[p])
        m.editorial_review_terms = pt        

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

def load_a_profile(name, books):
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
    
    for i in range(len(books)):
        m = books[i]
        if m.asin in training_instances:
            training_set_iids.add(i)
            m.is_in_training = True
            m.training_instance = training_instances[m.asin]
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
root.title("BOOK RECOMMENDER SYSTEM")


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

di = (("Title", "title", False),  ("Sales Rank", "sales_rank", True))

dfm = BrowseAllBooks(root, m_, di, padding="3 3 12 12")
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
        tid = m.asin
        ti = TrainingInstance(tid)
        training_instances[tid] = ti
        m.is_in_training = True
        m.training_instance = ti
        
    

def edit_training_data():
    tl = Toplevel(root)
    tl.title("Training Set")
    
    di = (("Title", "title", False),  ("Sales Rank", "sales_rank", True))
    
    rated_movies = []
    original_iids = []
    
    for iid in training_set_iids:
        rated_movies.append(m_[int(iid)])
        original_iids.append(iid)
    
    dfm = BrowseAllBooks(tl, rated_movies, di, padding="3 3 12 12")
    dfm.grid(column=0, row=0, sticky="nsew")
    training_tree = dfm.get_tree()
    
    def remove_selected_from_training_set():
        selected_iids = training_tree.selection()
        for iid in selected_iids:
            training_set_iids.remove(original_iids[int(iid)])            
            m = m_[original_iids[int(iid)]]
            training_instances.pop(m.asin, None)
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
            if ti.rationale_editorial_review_terms is not None:
                for pt in ti.rationale_editorial_review_terms:
                    try:
                        vi = vocabulary.index(pt)
                        Xc[iid, vi] *= 10
                    except ValueError:
                        pass
            
            
    
    num_books = len(m_)
    y = np.zeros(num_books)
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
    
    model_window.title("Recommended Books")
    
    features_frame = ttk.Labelframe(model_window, padding="3 3 12 12", text="Features")
    features_frame.grid(column=0, row=0, sticky="nsew")
    rec_movies_frame = ttk.Labelframe(model_window, padding="3 3 12 12", text="Recommended Books")
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
    
    di = (("Title", "title", False),  ("Sales Rank", "sales_rank", True), ('Score', 'pred_score', True))

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
    editorial_review_rationales = get_possible_rationales(training_set_iids, "editorial_review_terms")
    _add_lb_and_button("editorial_review_terms", rationale_window, 2, 0, editorial_review_rationales)
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

