# %%
import numpy as np
from itertools import chain
from string import digits
from stemming.porter2 import stem
import re
import time
import xml.etree.ElementTree as ET

# %% [markdown]
# # Preprocessing ___________________

# %%
# =============================== Preprocessing Methods ===============================

def parse_stopwords():  # get list of all stopwords
    with open('englishST.txt', 'r') as f:
        return [line.split('\n')[0] for line in f.readlines()]


def tokenisation(text):  # split on every non-letter character
    tokens = re.compile(r'(\w{0,})').findall(text)
    tokens = [word for word in tokens if word != '']
    return tokens


def lower_stopping_normalise(text, stop_words):
    text = [word.lower() for word in text]  # make lowercase
    text = [word for word in text if word not in stop_words]  # remove stop words
    text = [stem(word) for word in text]  # normalise / Porter stemming
    return text


# %% [markdown]
# # Indexing ____________________

# %%

# ============================ Indexing Method ========================================

def build_index():
    start = time.time()

    file = 'collections/trec.5000.xml'
    tree = ET.parse(file)
    root_xml = tree.getroot()

    stop_words = parse_stopwords()
    totalNum = 0

    unique = {}

    for document in root_xml.findall('DOC'):  # <DOC> is where a new document begins
        docNo = document.find('DOCNO').text  # get the document ID
        headline = document.find('HEADLINE').text  # get the headline
        text = document.find('TEXT').text  # get the main body text
        totalNum += 1

        full_text = headline + ' ' + text  # combine headline and text fields

        tokenised = tokenisation(full_text)
        stopped = lower_stopping_normalise(tokenised, stop_words)

        for idx, t in enumerate(stopped):
            pos = idx + 1  # start indexing at 1 and not 0

            # unique = dict(sorted(unique.items(), key=lambda item: item[0]))

            if unique.get(t) is not None:  # word already exists
                occurrence, count = unique[t]  # get stored values

                if occurrence.get(docNo) is not None:  # same word appears again in same file
                    occurrence[docNo].append(pos)  # append another word position
                    unique[t] = (occurrence, count)  # file counter stays the same
                else:  # new unique file for that word
                    occurrence[docNo] = [pos]  # store at which position the word appeared in that file
                    unique[t] = (occurrence, count + 1)  # increase the counter of number of file appearances

            else:  # new unique word
                occurrence = {docNo: [pos]}  # new dictionary with doc num and position of word
                unique[t] = (occurrence, 1)  # add new unique word and number of file appearances

    end = time.time()
    duration = end - start
    print(f'Duration for building and writing index: {duration} s')

    return unique



# ============================ write in text file =====================================
def write_txt(dic):
    with open('index.txt', 'w') as f:
        for key, value in dic.items():
            occurrence, count = value

            f.write(key + ":" + str(count))
            f.write("\n")

            for key2, value2 in occurrence.items():
                f.write("\t" + key2 + ": " + ",".join(str(x) for x in value2))
                f.write("\n")

            f.write("\n")



dic = build_index()
write_txt(dic)


# %% [markdown]
# # #Loads indexed file -> List of dictionary items________________

# %%

indexed_file = open('index.txt', 'r').readlines()

docnumbers = []

# Loads indexed file back into a list of dictionary items [{term: {document:[positions]}}...]
def format_txt_file():
    index_list = []
    term_list = []
    for line in indexed_file:
        position = {}
        index = {}
        # get the term
        # if not(line.startswith('\t')):
        if re.match(r'^[A-z0-9]+', line):    
            # term = line.replace(':', '').strip()     
            term = re.sub(":[0-9]+", "", str(line))       # 'term:178' ==> 'term'
            term = term.strip()
            term_list.append(term)

        # get the list of positions + save in donumbers
        if line.startswith('\t'):
            split_position = (line.replace('\t', '').replace('\n','').replace(' ', '')).split(':')
            docno, position_list2 = split_position[0], split_position[1]
            idxs = list(map(int, position_list2.split(',')))
            position[int(docno)] = idxs
            docnumbers.append(docno)

        # List of dictionary items [{term : {doc:[positions]}} , ...]
        if len(position)>0:
            index[term] = position
            index_list.append(index)

    return index_list


# load index
inverted_index = format_txt_file()
inverted_index


# %% [markdown]
# # #Functions1 ___________________________________________________
# ============================ utils =====================================

# %%
def sort_stopwords():
    # Converts the stopwords file into a list 
    stopwords_file = open('stopwordsfile.txt', 'r').readlines()
    stopwords = []

    for word in stopwords_file:
        stopwords.append(word.strip())

    return set(stopwords)

def preprocess_query(query):
    pp_query = []
    stopwords = sort_stopwords()
    query = query.split(' ')
    for term in query:
        if term not in stopwords:
            term = re.sub(r'\W+', '', stem(term.lower()))
            pp_query.append(term)
    return pp_query


def preprocess_term(term):
    return re.sub(r'\W+', '', stem(term.lower()))


# For a term, retrieves a list of all positions from the inverted index.
def getpositions(term):
    position_list = []
    for index in inverted_index:
        if term in index.keys():
            position_list.append(index.get(term))   # [{doc1 : [pos_list]} , {doc2 : [pos_list]} , ....]
    return position_list


# takes list of documents and returns the all documents in collection except those in list.
def getnot(lst):
    all_docs = sorted(list(set(docnumbers)))
    return [n for n in ([int(x) for x in all_docs]) if n not in lst]


# extracts the documents from a list of {doc:[position]} dictionaries
def get_docs(position_list):
    docs = []
    for position in position_list:
        for key in position.keys():
            docs.append(key)
    return docs


# %% [markdown]
# ============================ four Search methods =====================================

# # Phrase_Search ___________________________________________

# %%

def phrasesearch(i, phrase):

    # used for both phrase search and proximity search.
    # if phrase search, i=1, if proximity search, i is passed from proximity search method.

    phrase = re.sub('"', '', phrase)
    term1, term2 = phrase.split()                   # whitespace = separator
    term1_positions = getpositions(preprocess_term(term1))
    term2_positions = getpositions(preprocess_term(term2))
    results = []

    # loops through all positions that both terms occur in and adds to list if distance between terms <= i.

    for position in term1_positions:
        for key in position:                        # positions of term1
            term1_doc = key
            term1_pos = position[key]

            for position2 in term2_positions:       # positions of term2 
                for key2 in position2:
                    term2_doc = key2
                    term2_pos = position2[key2]

                    if term1_doc == term2_doc:      # term1 and term2 should be in the same document
                        for p in term1_pos:
                            for p2 in term2_pos:
                                if abs(p-p2) <= i:
                                    results.append(position)
                                    results.append(position2)

    return results # return list of postions


# %% [markdown]
# # Proximity_Search ___________________________________________

# %%
def proximitysearch(query):

    # format query and send to phrase search with i being the distance given.

    query = re.sub('#', '', query)
    i, query = query.split('(')
    query = re.sub(r',', ', ', query)
    query = re.sub(r'([^\s\w]|_)+', '', query)
    results = phrasesearch(int(i), query)

    return list(set(get_docs(results)))


# %% [markdown]
# # Boolean_Search ___________________________________________

# %%

def boolean_search(query):

    # Gets type of boolean query, splits into the two terms mentioned.

    results = []

    if 'AND NOT' in query:
        idx1 = query.index('AND')
        idx2 = idx1 + 7
    elif 'OR NOT' in query:
        idx1 = query.index('OR')
        idx2 = idx1 + 6
    elif 'AND' in query:
        idx1 = query.index('AND')
        idx2 = idx1 + 3
    elif 'OR' in query:
        idx1 = query.index('OR')
        idx2 = idx1 + 2

    term1 = query[:idx1].strip()
    term2 = query[idx2:].strip()

    # If either term is a phrase search then get results from phrase method.

    if term1.startswith('"') and term1.endswith('"'):
        term1_positions = phrasesearch(1, term1)
    else:
        term1_positions = getpositions(preprocess_term(term1))
        
    if term2.startswith('"') and term2.endswith('"'):
        term2_positions = phrasesearch(1, term2)
    else:
        term2_positions = getpositions(preprocess_term(term2))

    # Convert to list of documents without indexes

    term1_positions = get_docs(term1_positions)
    term2_positions = get_docs(term2_positions)


    if 'NOT' in query:
        term2_positions = getnot(term2_positions) # revert list
    if 'AND' in query:
        results = list(set(term1_positions) & set(term2_positions))
    if 'OR' in query:
        results = list(set(term1_positions) | set(term2_positions))

    return results


# %% [markdown]
# # RankedIR_Search ___________________________________________

# %%
def rankedir_search(query):

    # gets list of positions for each term in the query and calculates tfidf score for each document

    N = len(list(set(docnumbers)))  # 5000
    tfidfs = {} # Dictionary to store {docnumber: tfidf_score}

    def tfidf(tf, df):
        return (1 + np.log10(tf)) * (np.log10(N/df))

    for term in query:
        positions = getpositions(term)  # [ {docnumber : [positions]} , ... ]
        docfreq = len(positions)        # number of docs contains the word 'term'  

        for position in positions:                # {docnumber : [positions]} , ...
            for doc in position:                  # docnumber 
                termfreq = len(position[doc])     # the frequency of term in doc
                t = tfidf(termfreq, docfreq)

                if doc not in tfidfs.keys():    # if document not exits in tfidfs{} -> add it and assign the score
                    tfidfs[doc] = t             # else | add the value of (t) to the existant doc score  
                else:
                    newval = tfidfs[doc].__add__(t)     # score __ because we have bunch of words in the query 
                    tfidfs[doc] = newval
                    
    return tfidfs


# %% [markdown]
# ============================ display methods =====================================
# # #Functions2__Affichage _____________________________________

# %%

# formats the list of results per query to TREC format for boolean, phrase and proximity queries
def print_results(queryno, results):        #results = doc numbers
    query_results = []
    if len(results) > 0:
        for documentnumber in results:
            output_string = "{} , {}".format(queryno, documentnumber)
            query_results.append(output_string)

    return query_results

# formats the list of results per query to TREC format for rank queries
def print_results_IR(queryno, results):   
    query_results = []
    results_c = results.copy()
    for doc, score in results_c.items():
        if score == 0.0:
            results.pop(doc)
    results = (sorted(results.items(), key=lambda kv: kv[1], reverse=True))
    for item in results:
        doc, score = item
        output = "{} , {} , {}".format(queryno, doc, round(score, 3))
        query_results.append(output)

    return query_results


# %% [markdown]
# ============================ Generate Results =====================================

# %% [markdown]
# # ______________________________________________________

# %% [markdown]
# ## Generate : results.boolean.txt

# %%
query_file = open("queries.boolean.txt", 'r').readlines()

print("\nANSWERING QUERIES\n...")

output = []

for query in query_file:
    queryno = int(query.split()[0])
    query = query.lstrip(digits).strip()

    results = []    # list of positions
    results_string = []

    # check structure of query to send to appropriate search method
    # don't apply preprocess_query when using the 3 first search methods, only in rankedIR because we deal with special character

    if 'AND' in query or 'OR' in query:
        results = boolean_search(query)

    elif query.startswith('#') and query.endswith(")"):
        results = proximitysearch(query)

    elif query.startswith('"') and query.endswith('"'):
        positions = phrasesearch(1, query)
        t = []
        for p in positions:
            for key in p:
                t.append(key)
        results.extend(list(set(t)))

    elif len(query.split(' ')) == 1: # single word query
        query = preprocess_term(query)  ###
        for item in getpositions(query):
            for key in item.keys():
                results.append(key)
    else:
        continue
    

    results_string.append(print_results(queryno, results))
    results_string = list(chain.from_iterable(results_string))

    if len(results_string) > 1000: # only print out first 1000 queries
        results_string = results_string[:1000]

    if len(results_string)>0:
        output.append(results_string)

# save to file

output = list(chain.from_iterable(output))
f = open('results.boolean.txt', 'w')

for line in output:
    f.write(line + "\n")
f.close()

print("QUERYING COMPLETE\n")


# %% [markdown]
# ## Generate : results.ranked.txt

# %%
query_file = open("queries.ranked.txt", 'r').readlines()

print("\nANSWERING QUERIES\n...")

output = []

for query in query_file:
    queryno = int(query.split()[0])
    query = query.lstrip(digits).strip()

    results = []                  # list of documents
    results_string = []           # final result

    query = preprocess_query(query)
    results = rankedir_search(query)
    
    results_string.append(print_results_IR(queryno, results))
    results_string = list(chain.from_iterable(results_string))

    if len(results_string) > 1000: # only print out first 1000 queries
        results_string = results_string[:1000]

    if len(results_string)>0:
        output.append(results_string)

# save to file

output = list(chain.from_iterable(output))
f = open('results.ranked.txt', 'w')

for line in output:
    f.write(line + "\n")
f.close()

print("QUERYING COMPLETE\n")

# %%



