# -*- coding: utf-8 -*-
"""
Created on Tue Jun 20 13:38:11 2017

@author: Mustafa
"""

import gzip

from book import Book

def parse(path):
    g = gzip.open(path, 'r')
    for l in g:
        yield eval(l)


def parse_books():
    file_path = "../../book/meta_Books.json.gz"
    books = []
    for b in parse(file_path):
        if 'description' in b and 'salesRank' in b and 'imUrl' in b:
            if 'Books' in b['salesRank']:
                if b['salesRank']['Books'] < 50000:
                    books.append(Book(title=b['title'], asin=b['asin'], editorial_review=b['description'], sales_rank=b['salesRank']['Books'], imUrl=b['imUrl']))
    return books
                    