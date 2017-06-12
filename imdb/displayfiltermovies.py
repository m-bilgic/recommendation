# -*- coding: utf-8 -*-
"""
Created on Thu Jun  8 14:41:18 2017

@author: Mustafa
"""

from tkinter import ttk
from tkinter import StringVar, IntVar, DoubleVar, Listbox, Text, Toplevel, VERTICAL, HORIZONTAL, END
import tkinter.font as tkFont
from tkinter import font

from scipy.sparse import diags

def sortby(tree, col, descending, is_number=False):
    """sort tree contents when a column header is clicked on"""
    # grab values to sort
    data = [(tree.set(child, col), child)         for child in tree.get_children('')]
    # if the data to be sorted is numeric change to float
    #data =  change_numeric(data)
    # now sort the data in place
    if(is_number): 
        data = [(float(d[0]), d[1]) for d in data]
    data.sort(reverse=descending)
    for ix, item in enumerate(data):
        tree.move(item[1], '', ix)
    # switch the heading so it will sort in the opposite direction
    tree.heading(col, command=lambda col=col, is_num = is_number : sortby(tree, col, int(not descending), is_number=is_num))  
    

class DisplayFilterMovies(ttk.Frame):
    def __init__(self, parent, movies, display_info, **kw):
        super().__init__(parent, **kw)
        self.display_info = display_info
        self.movies = movies
        
        self.removed_iids = set()
        
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        filterframe = ttk.Labelframe(self, padding="3 3 12 12", text="Filter")
        filterframe.grid(column=0, row=0, sticky="nsew")
        filterframe['borderwidth'] = 2
        filterframe['relief'] = 'sunken'


        dataframe = ttk.Labelframe(self, padding="3 3 12 12", text="Movies")
        dataframe.grid(column=1, row=0, sticky="nsew")
        dataframe['borderwidth'] = 2
        dataframe['relief'] = 'sunken'

        dataframe.grid_columnconfigure(0, weight=1)
        dataframe.grid_columnconfigure(1, weight=0)
        dataframe.grid_rowconfigure(0, weight=1)
        dataframe.grid_rowconfigure(1, weight=0)
        dataframe.grid_rowconfigure(2, weight=0)
        
        
        
        yearfilterframe = ttk.Labelframe(filterframe, padding="3 3 12 12", text="Year")
        yearfilterframe.grid(column=0, row=0, sticky="nsew")
        yearfilterframe['borderwidth'] = 2
        yearfilterframe['relief'] = 'sunken'
        ttk.Label(yearfilterframe, text="MIN").grid(column=0, row=0, sticky="W")
        self.minyear=StringVar()        
        ttk.Entry(yearfilterframe, textvariable=self.minyear).grid(column=1, row=0, sticky="E")
        ttk.Label(yearfilterframe, text="MAX").grid(column=0, row=1, sticky="W")
        self.maxyear=StringVar()        
        ttk.Entry(yearfilterframe, textvariable=self.maxyear).grid(column=1, row=1, sticky="E")
        
        numratingfilterframe = ttk.Labelframe(filterframe, padding="3 3 12 12", text="# of Ratings")
        numratingfilterframe.grid(column=0, row=1, sticky="nsew")
        numratingfilterframe['borderwidth'] = 2
        numratingfilterframe['relief'] = 'sunken'
        ttk.Label(numratingfilterframe, text="MIN").grid(column=0, row=0, sticky="E")
        self.minratingcount=IntVar()        
        ttk.Entry(numratingfilterframe, textvariable=self.minratingcount).grid(column=1, row=0, sticky="W")
        ttk.Label(numratingfilterframe, text="MAX").grid(column=0, row=1, sticky="E")
        self.maxratingcount=IntVar()        
        ttk.Entry(numratingfilterframe, textvariable=self.maxratingcount).grid(column=1, row=1, sticky="W")
        
        
        meanratingfilterframe = ttk.Labelframe(filterframe, padding="3 3 12 12", text="Average Rating")
        meanratingfilterframe.grid(column=0, row=2, sticky="nsew")
        meanratingfilterframe['borderwidth'] = 2
        meanratingfilterframe['relief'] = 'sunken'
        ttk.Label(meanratingfilterframe, text="MIN").grid(column=0, row=0, sticky="W")
        self.minrating=DoubleVar()        
        ttk.Entry(meanratingfilterframe, textvariable=self.minrating).grid(column=1, row=0, sticky="E")
        ttk.Label(meanratingfilterframe, text="MAX").grid(column=0, row=1, sticky="W")
        self.maxrating=DoubleVar()        
        ttk.Entry(meanratingfilterframe, textvariable=self.maxrating).grid(column=1, row=1, sticky="E")
        
        phrasefilterframe = ttk.Labelframe(filterframe, padding="3 3 12 12", text="Phrase")
        phrasefilterframe.grid(column=0, row=3, sticky="nsew")
        phrasefilterframe['borderwidth'] = 2
        phrasefilterframe['relief'] = 'sunken'
        
        self.titlephrase = StringVar()
        ttk.Label(phrasefilterframe, text="Title").grid(column=0, row=0, sticky="W")
        ttk.Entry(phrasefilterframe, textvariable=self.titlephrase).grid(column=1, row=0, sticky="nsew")
        self.keywordphrase = StringVar()
        ttk.Label(phrasefilterframe, text="Keyword").grid(column=0, row=1, sticky="W")
        ttk.Entry(phrasefilterframe, textvariable=self.keywordphrase).grid(column=1, row=1, sticky="nsew")
        self.genrephrase = StringVar()
        ttk.Label(phrasefilterframe, text="Genre").grid(column=0, row=2, sticky="W")
        ttk.Entry(phrasefilterframe, textvariable=self.genrephrase).grid(column=1, row=2, sticky="nsew")
        self.plotphrase = StringVar()
        ttk.Label(phrasefilterframe, text="Plot").grid(column=0, row=3, sticky="W")
        ttk.Entry(phrasefilterframe, textvariable=self.plotphrase).grid(column=1, row=3, sticky="nsew")
        self.actorphrase = StringVar()
        ttk.Label(phrasefilterframe, text="Actor").grid(column=0, row=4, sticky="W")
        ttk.Entry(phrasefilterframe, textvariable=self.actorphrase).grid(column=1, row=4, sticky="nsew")
        self.actressphrase = StringVar()
        ttk.Label(phrasefilterframe, text="Actress").grid(column=0, row=5, sticky="W")
        ttk.Entry(phrasefilterframe, textvariable=self.actressphrase).grid(column=1, row=5, sticky="nsew")
        
        certfilterframe = ttk.Labelframe(filterframe, padding="3 3 12 12", text="USA Certificate")
        certfilterframe.grid(column=0, row=6, sticky="nsew")
        certfilterframe['borderwidth'] = 2
        certfilterframe['relief'] = 'sunken'
        
        
        left_certificates = ["Approved", "Passed", "G", "PG", "PG-13", "R", "Unrated", "Not Rated"]
        right_certificates = ["TV-G", "TV-PG", "TV-Y", "TV-Y7", "TV-14", "TV-MA"]
        self.cert_vars = []
        self.cert_values = []
        i=0
        
        for cert in left_certificates:
            cv = StringVar()
            cv.set(cert)
            ttk.Checkbutton(certfilterframe, text=cert, onvalue = cert, variable=cv).grid(column=0, row=i, sticky="w")
            self.cert_vars.append(cv)
            self.cert_values.append(cert)
            i += 1
        
        i=0
        
        for cert in right_certificates:    
            cv = StringVar()
            cv.set(cert)
            ttk.Checkbutton(certfilterframe, text=cert, onvalue = cert, variable=cv).grid(column=2, row=i, sticky="w")
            self.cert_vars.append(cv)
            self.cert_values.append(cert)
            i += 1
        
        cert_Unk = StringVar()
        cert_Unk.set("Unknown")
        ttk.Checkbutton(certfilterframe, text='Unknown', onvalue = "Unknown", variable=cert_Unk).grid(column=1, 
                                                                                                    row=max((len(right_certificates),len(left_certificates)))+1, sticky="w")
        self.cert_vars.append(cert_Unk)
        self.cert_values.append("Unknown")
        
        buttonfilterframe = ttk.Frame(filterframe, padding="3 3 12 12")
        buttonfilterframe.grid(column=0, row=5, sticky="ne")
        
        ttk.Button(buttonfilterframe, text="Filter", command=self._filter_data).grid(column=0, row=0, sticky = "W")
        ttk.Button(buttonfilterframe, text="Reset", command=self._reset_filters).grid(column=1, row=0, sticky = "E")
        
        self._update_filter_field_values()
        
        data_header = [e[0] for e in self.display_info]
        self.data_attribute_names = [e[1] for e in self.display_info]
        is_float = [e[2] for e in self.display_info]
        
        
        # some of the following code is borrowed from https://www.daniweb.com/programming/software-development/threads/350266/creating-table-in-python

        self.data_tree = ttk.Treeview(dataframe, columns=data_header, show="headings", selectmode='extended')
        
        vsb = ttk.Scrollbar(dataframe, orient="vertical", command=self.data_tree.yview)
        hsb = ttk.Scrollbar(dataframe, orient="horizontal", command=self.data_tree.xview)
        
        self.data_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.data_tree.grid(column=0, row=0, sticky='nsew')
        
        self.data_tree.bind("<Double-1>", self.double_click)
        
        vsb.grid(column=1, row=0, sticky='ns')
        hsb.grid(column=0, row=1, sticky='ew')
        
        for i in range(len(data_header)):
            col = data_header[i]            

            self.data_tree.heading(col, text=col.title(), command=lambda c=col, is_num=is_float[i]: sortby(self.data_tree, c, 0, is_number=is_num))            
            # adjust the column's width to the header string
            self.data_tree.column(col, width=tkFont.Font().measure(col.title()))
            
        for i in range(len(self.movies)):
            item = [getattr(self.movies[i], attr_name) for attr_name in self.data_attribute_names]
            #item = [m_[i].title, m_[i].year, m_[i].num_ratings, m_[i].mean_rating, m_[i].certificate]
            self.data_tree.insert('', 'end', iid = str(i), values=item)
            # adjust column's width if necessary to fit each value
            #for ix, val in enumerate(item):
             #   col_w = tkFont.Font().measure(val)
             #   if data_tree.column(data_header[ix],width=None)<col_w:
             #       data_tree.column(data_header[ix], width=col_w)
        
        

    def get_tree(self):
        return self.data_tree
    
    def double_click(self):
        pass # Override

    def _update_filter_field_values(self):
        
        min_year = "2100"
        min_rating_count = min_mean_rating = float('inf')
        max_year = "1800"
        max_rating_count = max_mean_rating = float('-inf')
        avail_certificates = set()
        for i in range(len(self.movies)):
            m = self.movies[i]
            if len(self.removed_iids) > 0:
                if str(i) in self.removed_iids:
                    continue
            min_year = min((min_year, m.year))
            max_year = max((max_year, m.year))
            min_rating_count = min((min_rating_count, m.num_ratings))
            max_rating_count = max((max_rating_count, m.num_ratings))
            min_mean_rating = min((min_mean_rating, m.mean_rating))
            max_mean_rating = max((max_mean_rating, m.mean_rating))
            avail_certificates.add(m.certificate)
        
        self.minyear.set(min_year)
        self.maxyear.set(max_year)
        self.minratingcount.set(min_rating_count)
        self.maxratingcount.set(max_rating_count)
        self.minrating.set(min_mean_rating)
        self.maxrating.set(max_mean_rating)
        
        for i in range(len(self.cert_values)):
            if self.cert_values[i] in avail_certificates:
                self.cert_vars[i].set(self.cert_values[i])
            else:
                self.cert_vars[i].set(0)




    def _filter_data(self, *args):
        remove_iids = set()
        data = self.data_tree.get_children('')
        #print(data_tree.set(data[0]))
        display_certificates = set()
        
        for cv in self.cert_vars:
            if cv.get() != "0":
                display_certificates.add(cv.get())    
        
        for iid in data:
            m = self.movies[int(iid)]
            # Year
            if m.year < self.minyear.get():
                remove_iids.add(iid)
            if m.year > self.maxyear.get():
                remove_iids.add(iid)
            # Rating Count
            if m.num_ratings < self.minratingcount.get():
                remove_iids.add(iid)
            if m.num_ratings > self.maxratingcount.get():
                remove_iids.add(iid)
            # MEAN RATING
            if m.mean_rating < self.minrating.get():
                remove_iids.add(iid)
            if m.mean_rating > self.maxrating.get():
                remove_iids.add(iid)
            if m.title.find(self.titlephrase.get()) == -1:
                remove_iids.add(iid)
            
            if self.genrephrase.get() != "":
                if m.genres == None:
                    remove_iids.add(iid)
                else:
                    gp = False
                    for g in m.genres:
                        if g.find(self.genrephrase.get()) != -1:
                            gp = True
                            break
                    if not gp:
                        remove_iids.add(iid)
            if self.keywordphrase.get() != "":
                if m.keywords == None:
                    remove_iids.add(iid)
                else:
                    kp = False
                    for k in m.keywords:
                        if k.find(self.keywordphrase.get()) != -1:
                            kp = True
                            break
                    if not kp:
                        remove_iids.add(iid)
            if self.plotphrase.get() != "":
                if m.plot is None:
                    remove_iids.add(iid)
                else:
                    m_plot_lower = m.plot.lower()
                    if m_plot_lower.find(self.plotphrase.get().lower()) == -1:
                        remove_iids.add(iid)
            
            if self.actorphrase.get() != "":
                if m.actors is None:
                    remove_iids.add(iid)
                else:
                    actor_present = False
                    for actor in m.actors:
                        if actor.lower().find(self.actorphrase.get().lower()) != -1:
                            actor_present = True
                            break
                    if not actor_present:
                        remove_iids.add(iid)
            
            if self.actressphrase.get() != "":
                if m.actresses is None:
                    remove_iids.add(iid)
                else:
                    actress_present = False
                    for actress in m.actresses:
                        if actress.lower().find(self.actressphrase.get().lower()) != -1:
                            actress_present = True
                            break
                    if not actress_present:
                        remove_iids.add(iid)
            
                        
            if m.certificate not in display_certificates:
                remove_iids.add(iid)
            
        #data_tree.delete(list(remove_iids))
        for iid in remove_iids:
            self.data_tree.delete(iid)
        self.removed_iids.update(remove_iids)
        
        self._update_filter_field_values()
        #TODO
        # 1. Update the other fields based on the new filtered data
        # 2. There is no way to go back in filtering right now
    
    def _reset_filters(self, *args):
        for iid in self.removed_iids:
            i = int(iid)
            item = [getattr(self.movies[i], attr_name) for attr_name in self.data_attribute_names]
            self.data_tree.insert('', 'end', iid = str(i), values=item)
        #sortby(data_tree, 'Title', False)
        self.removed_iids.clear()
        #TODO Reset the fields to their default values
        self._update_filter_field_values()
        self.genrephrase.set("")
        self.keywordphrase.set("")
        self.actorphrase.set("")
        self.actressphrase.set("")
        self.titlephrase.set("")
        self.plotphrase.set("")

class BrowseAllMovies(DisplayFilterMovies):
    def double_click(self, e):
        selected_iid = self.data_tree.selection()[0]
        #print("Double click on %s"  %self.movies[int(selected_iid)])
        tl = Toplevel(self)
        SingleMovie(tl, self.movies[int(selected_iid)]).grid(column=0, row=0, sticky="nsew")

class BrowseRecommendations(DisplayFilterMovies):
    
    def setExplanation(self, decision_matrix, vocabulary):
        self.decision_matrix = decision_matrix
        self.vocabulary = vocabulary
    
    def double_click(self, e):
        iid = self.data_tree.selection()[0]        
        
        
        dm = self.decision_matrix[int(iid)]
        
        explanation = []
        for j in range(len(dm.indices)):
            explanation.append((dm.data[j], self.vocabulary[dm.indices[j]]))
            
        explanation = sorted(explanation)[::-1]
        
        #print("Double click on %s"  %self.movies[int(selected_iid)])
        tl = Toplevel(self)
        tl.title("Explanation of the Recommendation")
        
        tl.columnconfigure(0, weight=1)
        tl.columnconfigure(1, weight=1)
        tl.rowconfigure(0, weight=1)
        
        SingleMovie(tl, self.movies[int(iid)]).grid(column=0, row=0, sticky="nsew")
        
        explanation_header = ['Feature', 'Score']    
        explanation_tree = ttk.Treeview(tl, columns=explanation_header, show="headings", selectmode='browse')
        explanation_tree.grid(column=1, row=0, sticky="nsew")
    
        vsb = ttk.Scrollbar(tl, orient="vertical", command=explanation_tree.yview)
        explanation_tree.configure(yscrollcommand=vsb.set)
        vsb.grid(column=2, row=0, sticky='ns')
        
        for col in explanation_header:
            if col == "Score":
                explanation_tree.heading(col, text=col.title(), command=lambda c=col: sortby(explanation_tree, c, 0, True))
            else:
                explanation_tree.heading(col, text=col.title(), command=lambda c=col: sortby(explanation_tree, c, 0, False))
            # adjust the column's width to the header string
            explanation_tree.column(col, width=tkFont.Font().measure(col.title()))

        for e in explanation:
            item = [e[1], e[0]]
            explanation_tree.insert('', 'end', values=item)
        

        

class SingleMovie(ttk.Frame):
    def __init__(self, parent, m, **kw):
        super().__init__(parent, **kw)
        ttk.Label(self, text=m.title + " (" + str(m.year) + ")", font=font.Font(family='Helvetica', size=14, weight='bold')).grid(column=0, row=0, sticky="W")
        info_frame = ttk.Frame(self, padding="3 3 12 12")
        info_frame.grid(column=0, row=1, sticky="nsew")
        
        self.movie = m
        
        row_i = 0
        
        if m.genres is not None:
            g = ", ".join(m.genres)
            ttk.Label(info_frame, text="Genres: " + g).grid(column=0, row=row_i, sticky="W")
            row_i += 1
        if m.keywords is not None:
            
            ttk.Label(info_frame, text="Keywords" ).grid(column=0, row=row_i, sticky="W")
            row_i += 1
            
            non_rationale_keywords = set()
            rationale_keywords = set()
            
            non_rationale_keywords.update(m.keywords)
            
            if m.is_in_training:
                ti = m.training_instance
                if ti.rationale_keywords is not None:
                    rationale_keywords.update(ti.rationale_keywords)
                    non_rationale_keywords.difference_update(rationale_keywords)
            
            nrk_var = StringVar(value=sorted(list(non_rationale_keywords)))
            kl = Listbox(info_frame, listvariable=nrk_var, height=5)
            kl.grid(column=0, row=row_i, rowspan = 4, sticky="nsew")
            
            vs = ttk.Scrollbar(info_frame, orient=VERTICAL, command=kl.yview)
            kl.configure(yscrollcommand=vs.set)
            vs.grid(column=1, row=row_i, rowspan = 4, sticky="nsew")            
            
            rk_var = StringVar(value=sorted(list(rationale_keywords)))
            rkl= Listbox(info_frame, listvariable=rk_var, height=5)
            rkl.grid(column=3, row=row_i, rowspan = 4, sticky="nsew")
            
            ttk.Button(info_frame, text=">", command=lambda nv=nrk_var, rv=rk_var, nrlb=kl, rlb=rkl: self.make_it_rationale(nv, rv, nrlb, rlb, "rationale_keywords")).grid(column=2, row=row_i+1, sticky = "W")
            ttk.Button(info_frame, text="<", command=lambda nv=nrk_var, rv=rk_var, nrlb=kl, rlb=rkl: self.make_it_nonrationale(nv, rv, nrlb, rlb, "rationale_keywords")).grid(column=2, row=row_i+2, sticky = "W")

            
            vs = ttk.Scrollbar(info_frame, orient=VERTICAL, command=rkl.yview)
            rkl.configure(yscrollcommand=vs.set)
            vs.grid(column=4, row=row_i, rowspan = 4, sticky="nsew")            
            
            row_i += 4
            
            hs = ttk.Scrollbar(info_frame, orient=HORIZONTAL, command=kl.xview)
            kl.configure(xscrollcommand=hs.set)
            hs.grid(column=0, row=row_i, sticky="nsew")
            row_i += 1
        if m.plot is not None:
            ttk.Label(info_frame, text="Plot" ).grid(column=0, row=row_i, sticky="W")
            row_i += 1
            pt = Text(info_frame, wrap='word')
            pt.insert('1.0', m.plot)
            pt.grid(column=0, row=row_i, sticky="nsew")
            row_i += 1
        if m.actors is not None:
            ttk.Label(info_frame, text="Actors" ).grid(column=0, row=row_i, sticky="W")
            row_i += 1
            al= Listbox(info_frame, listvariable=StringVar(value=m.actors), height=5)
            al.grid(column=0, row=row_i, sticky="nsew")
            vs = ttk.Scrollbar(info_frame, orient=VERTICAL, command=al.yview)
            al.configure(yscrollcommand=vs.set)
            vs.grid(column=1, row=row_i, sticky="nsew")
            row_i += 1
            hs = ttk.Scrollbar(info_frame, orient=HORIZONTAL, command=al.xview)
            al.configure(xscrollcommand=hs.set)
            hs.grid(column=0, row=row_i, sticky="nsew")
            row_i += 1
            
        if m.actresses is not None:
            ttk.Label(info_frame, text="Actresses" ).grid(column=0, row=row_i, sticky="W")
            row_i += 1
            al= Listbox(info_frame, listvariable=StringVar(value=m.actresses), height=5)
            al.grid(column=0, row=row_i, sticky="nsew")
            vs = ttk.Scrollbar(info_frame, orient=VERTICAL, command=al.yview)
            al.configure(yscrollcommand=vs.set)
            vs.grid(column=1, row=row_i, sticky="nsew")
            row_i += 1
            hs = ttk.Scrollbar(info_frame, orient=HORIZONTAL, command=al.xview)
            al.configure(xscrollcommand=hs.set)
            hs.grid(column=0, row=row_i, sticky="nsew")
    
    def make_it_rationale(self, nr_var, ra_var, nrlb, rlb, att_name):
        idxs = nrlb.curselection()
        if len(idxs) == 1:
            idx = int(idxs[0])
            k = nrlb.get(idx)
            
            nr_list = list(nrlb.get(0, END))
            ra_list = list(rlb.get(0, END))
            
            nr_list.remove(k)
            ra_list.append(k)            
            
            nr_var.set(sorted(nr_list))
            ra_var.set(sorted(ra_list))
            
            if self.movie.is_in_training:            
                setattr(self.movie.training_instance, att_name, ra_list)
                
    def make_it_nonrationale(self, nr_var, ra_var, nrlb, rlb, att_name):
        idxs = rlb.curselection()
        if len(idxs) == 1:
            idx = int(idxs[0])
            k = rlb.get(idx)
            
            nr_list = list(nrlb.get(0, END))
            ra_list = list(rlb.get(0, END))
            
            ra_list.remove(k)
            nr_list.append(k)            
            
            nr_var.set(sorted(nr_list))
            ra_var.set(sorted(ra_list))
            
            if self.movie.is_in_training:            
                setattr(self.movie.training_instance, att_name, ra_list)