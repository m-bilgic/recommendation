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
    #t0 = time()
    # grab values to sort
    data = [(tree.set(child, col), child)         for child in tree.get_children('')]
    # if the data to be sorted is numeric change to float
    #data =  change_numeric(data)
    # now sort the data in place
    if(is_number): 
        data = [(float(d[0]), d[1]) for d in data]
    data.sort(reverse=descending)
    
    data = [(d[1], tree.item(d[1])['values']) for d in data]    
    tree.delete(*tree.get_children())
    for d in data:
        tree.insert('', 'end', iid=d[0], values=d[1])     
    
    # switch the heading so it will sort in the opposite direction
    tree.heading(col, command=lambda col=col, is_num = is_number : sortby(tree, col, int(not descending), is_number=is_num))
    
    #duration = time() - t0
    #print("Took %0.2f seconds." %duration)  
    

class DisplayFilterBooks(ttk.Frame):
    def __init__(self, parent, books, display_info, **kw):
        super().__init__(parent, **kw)
        self.display_info = display_info
        self.books = books
        
        self.removed_iids = set()
        
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        filterframe = ttk.Labelframe(self, padding="3 3 12 12", text="Filter")
        filterframe.grid(column=0, row=0, sticky="nsew")
        filterframe['borderwidth'] = 2
        filterframe['relief'] = 'sunken'


        dataframe = ttk.Labelframe(self, padding="3 3 12 12", text="Books")
        dataframe.grid(column=1, row=0, sticky="nsew")
        dataframe['borderwidth'] = 2
        dataframe['relief'] = 'sunken'

        dataframe.grid_columnconfigure(0, weight=1)
        dataframe.grid_columnconfigure(1, weight=0)
        dataframe.grid_rowconfigure(0, weight=1)
        dataframe.grid_rowconfigure(1, weight=0)
        dataframe.grid_rowconfigure(2, weight=0)       

        
        phrasefilterframe = ttk.Labelframe(filterframe, padding="3 3 12 12", text="Phrase")
        phrasefilterframe.grid(column=0, row=0, sticky="nsew")
        phrasefilterframe['borderwidth'] = 2
        phrasefilterframe['relief'] = 'sunken'
        
        self.titlephrase = StringVar()
        ttk.Label(phrasefilterframe, text="Title").grid(column=0, row=0, sticky="W")
        ttk.Entry(phrasefilterframe, textvariable=self.titlephrase).grid(column=1, row=0, sticky="nsew")        
        self.genrephrase = StringVar()
        ttk.Label(phrasefilterframe, text="Genre").grid(column=0, row=1, sticky="W")
        ttk.Entry(phrasefilterframe, textvariable=self.genrephrase).grid(column=1, row=1, sticky="nsew")
        self.authorphrase = StringVar()
        ttk.Label(phrasefilterframe, text="Author").grid(column=0, row=2, sticky="W")
        ttk.Entry(phrasefilterframe, textvariable=self.authorphrase).grid(column=1, row=2, sticky="nsew")
        
        
        trainingfilterframe = ttk.Labelframe(filterframe, padding="3 3 12 12", text="Training Instances")
        trainingfilterframe.grid(column=0, row=6, sticky="nsew")
        self.show_training = StringVar()
        self.show_training.set("Yes")
        ttk.Checkbutton(trainingfilterframe, text="Show Training Instances", onvalue = "Yes", variable=self.show_training).grid(column=0, row=0, sticky="w")
        
        buttonfilterframe = ttk.Frame(filterframe, padding="3 3 12 12")
        buttonfilterframe.grid(column=0, row=7, sticky="ne")
        
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
            
        for i in range(len(self.books)):
            item = [getattr(self.books[i], attr_name) for attr_name in self.data_attribute_names]
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
        pass

    def _filter_data(self, *args):
        remove_iids = set()
        data = self.data_tree.get_children('')

        
        for iid in data:
            m = self.books[int(iid)]

            if m.title.find(self.titlephrase.get()) == -1:
                remove_iids.add(iid)
            
            if self.genrephrase.get() != "":
                if m.genres == "":
                    remove_iids.add(iid)
                else:
                    gp = False
                    for g in m.genres:
                        if g.find(self.genrephrase.get()) != -1:
                            gp = True
                            break
                    if not gp:
                        remove_iids.add(iid)
            
            
            if self.authorphrase.get() != "":
                if m.author == "":
                    remove_iids.add(iid)
                elif  m.author.find(self.authorphrase.get()) == -1:                   
                        remove_iids.add(iid)
            
            if self.show_training.get() != "Yes":
                if m.is_in_training:
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
            item = [getattr(self.books[i], attr_name) for attr_name in self.data_attribute_names]
            self.data_tree.insert('', 'end', iid = str(i), values=item)
        #sortby(data_tree, 'Title', False)
        self.removed_iids.clear()
        #TODO Reset the fields to their default values
        self._update_filter_field_values()
        self.genrephrase.set("")
        self.authorphrase.set("")
        self.titlephrase.set("")
        self.show_training.set("Yes")

class BrowseAllBooks(DisplayFilterBooks):
    def double_click(self, e):
        selected_iid = self.data_tree.selection()[0]
        #print("Double click on %s"  %self.movies[int(selected_iid)])
        tl = Toplevel(self)
        SingleBook(tl, self.books[int(selected_iid)]).grid(column=0, row=0, sticky="nsew")

class BrowseRecommendations(DisplayFilterBooks):
    
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
        
        SingleBook(tl, self.books[int(iid)]).grid(column=0, row=0, sticky="nsew")
        
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
        

        

class SingleBook(ttk.Frame):
    def __init__(self, parent, b, **kw):
        super().__init__(parent, **kw)
        ttk.Label(self, text=b.title + " BY " + b.author, font=font.Font(family='Helvetica', size=14, weight='bold')).grid(column=0, row=0, sticky="W")
        info_frame = ttk.Frame(self, padding="3 3 12 12")
        info_frame.grid(column=0, row=1, sticky="nsew")
        
        self.book = b
        
        row_i = 0
        
        if b.genres is not None:
            g = ", ".join(b.genres)
            ttk.Label(info_frame, text="Genres: " + g).grid(column=0, row=row_i, sticky="W")
            row_i += 1

        if b.summary is not None:
            ttk.Label(info_frame, text="Summary" ).grid(column=0, row=row_i, sticky="W")
            row_i += 1
            pt = Text(info_frame, height = 7, wrap='word')
            pt.insert('1.0', b.summary)
            pt.grid(column=0, row=row_i, sticky="nsew")
            row_i += 1
        
        if b.summary_terms is not None:            
            row_i = self._add_list_boxes(info_frame, "Summary Terms", "summary_terms", row_i)
    
    
    def _add_list_boxes(self, info_frame, label_text, movie_field, row_i):
        
        b = self.book
        
        ttk.Label(info_frame, text=label_text).grid(column=0, row=row_i, sticky="W")
        
        row_i += 1
        
        
        non_rationale_entries = set()        
        rationale_entries = set()
        
        non_rationale_entries.update(getattr(b, movie_field))
        
        if b.is_in_training:
            ti = b.training_instance
            if getattr(ti, "rationale_"+movie_field, None) is not None:
                rationale_entries.update(getattr(ti, "rationale_"+movie_field))
                non_rationale_entries.difference_update(rationale_entries)
        
        nrk_var = StringVar(value=sorted(list(non_rationale_entries)))
        kl = Listbox(info_frame, listvariable=nrk_var, height=8)
        kl.grid(column=0, row=row_i, rowspan = 4, sticky="nsew")
        
        vs = ttk.Scrollbar(info_frame, orient=VERTICAL, command=kl.yview)
        kl.configure(yscrollcommand=vs.set)
        vs.grid(column=1, row=row_i, rowspan = 4, sticky="nsew")            
        
        rk_var = StringVar(value=sorted(list(rationale_entries)))
        rkl= Listbox(info_frame, listvariable=rk_var, height=8)
        rkl.grid(column=3, row=row_i, rowspan = 4, sticky="nsew")
        
        ttk.Button(info_frame, text=">", command=lambda nv=nrk_var, rv=rk_var, nrlb=kl, rlb=rkl: self.make_it_rationale(nv, rv, nrlb, rlb, "rationale_"+movie_field)).grid(column=2, row=row_i+1, sticky = "W")
        ttk.Button(info_frame, text="<", command=lambda nv=nrk_var, rv=rk_var, nrlb=kl, rlb=rkl: self.make_it_nonrationale(nv, rv, nrlb, rlb, "rationale_"+movie_field)).grid(column=2, row=row_i+2, sticky = "W")

        
        vs = ttk.Scrollbar(info_frame, orient=VERTICAL, command=rkl.yview)
        rkl.configure(yscrollcommand=vs.set)
        vs.grid(column=4, row=row_i, rowspan = 4, sticky="nsew")            
        
        row_i += 4
        
        hs = ttk.Scrollbar(info_frame, orient=HORIZONTAL, command=kl.xview)
        kl.configure(xscrollcommand=hs.set)
        hs.grid(column=0, row=row_i, sticky="nsew")
        row_i += 1
        return row_i
    
    
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
            
            if self.book.is_in_training:            
                setattr(self.book.training_instance, att_name, ra_list)
                
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
            
            if self.book.is_in_training:            
                setattr(self.book.training_instance, att_name, ra_list)