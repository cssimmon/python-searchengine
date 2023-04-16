import os.path
import requests

from download import download_wikipedia_abstracts
from load import load_documents
from search.timing import timing
from search.index import Index


@timing
def index_documents(documents, index):
    for i, document in enumerate(documents):
        index.index_document(document)
        if i % 5000 == 0:
            print(f'Indexed {i} documents', end='\r')
        # testing only
        if i == 100000:
            break
    return index


if __name__ == '__main__':
    # this will only download the xml dump if you don't have a copy already;
    # just delete the file if you want a fresh copy
    if not os.path.exists('data/enwiki-latest-abstract.xml.gz'):
        download_wikipedia_abstracts()

    #Default first pass = true
    firstPass = True
    while True:
        # Prompt user for search terms
        searchTerms = str(input("Enter AND search terms:"))
        # Prompt user for search Type
        searchType = str(input("Enter AND search type(AND/OR) will default to AND:"))

        # default to AND if OR not entered
        if searchType.lower() == "or":
            searchType = "OR"
        else:
            searchType = "AND"

        # Make sure user entered search terms before indexing
        if len(searchTerms) > 0:
            # index the first time only - takes 15 minutes
            if firstPass:
                firstPass = False
                index = index_documents(load_documents(), Index())
                print(f'Index contains {len(index.documents)} documents')

            # index based on prompted search terms and search type
            # rank = True will provide sorted list of docs using rank function provided
            docs = index.search(searchTerms, search_type=searchType, rank=True)
            print(f'{len(docs)} documents found with the terms {searchTerms} and search type {searchType}')

            # print the top N titles - default to 10
            top = 10
            if len(docs) < 10: top = len(docs)
            print(f'Here are the first {top} abstracts ')

            #Loop tuple  0 = document, 1 = rank
            for doc in docs[:top]:
                #~ delimiter to make text to column extract easier in excel
                print(f'~Title:~{doc[0].title}~URL:~{doc[0].url}~Rank:~{doc[1]}')

            #continue to top of while
            continue

        # No terms entered so exit while
        else:
            print(f'No Search Terms Entered')
            break

    print(f'All Done!')

    # Old Code from Example
    # index.search('London Beer Flood', search_type='AND')
    # index.search('London Beer Flood', search_type='OR')
    # index.search('London Beer Flood', search_type='AND', rank=True)
    # index.search('London Beer Flood', search_type='OR', rank=True)
