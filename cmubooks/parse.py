from book import Book
import re

def parse_books():
    file_path = "../../book/booksummaries.txt"
    books = []
    with open(file_path, 'r') as f:
        l = "begin"
        while l:
            try:
                l = f.readline()
                parts = l.split('\t')
                if len(parts) == 7:
                    title = parts[2]
                    author = parts[3]
                    date = parts[4]
                    genres = parts[5]
                    summary = parts[6]
                    books.append(Book(title, author, date, genres, summary))
            except UnicodeDecodeError:
                pass
    for book in books:
        if book.genres != "":
            gs = re.split("\"", book.genres)
            book.genres = []
            for i in range(3, len(gs), 4):
                book.genres.append(gs[i])
        else:
            book.genres = []
    return books