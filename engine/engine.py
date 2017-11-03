import sys
import gensim
import nltk
import os
import numpy as np
import operator
from nltk.corpus import stopwords
import json
import string
import json_parser as jp

def read_docs(whole_news):

    docs2 = []
    doc_names2 = []
    stopwrds = stopwords.words('english')
    for news in whole_news:
        article = nltk.word_tokenize(news['article'])
        article = [token for token in article if token not in stopwrds]
        docs2.append(article)
        doc_names2.append(news['url'])

    return doc_names2, docs2

def index_doc(docs,doc_names):
    index = {}
    inverse_index = {}
    for doc,doc_name in zip(docs,doc_names):
        word_count={}
        for word in doc:
            if word in word_count.keys():
                word_count[word]+=1
            else:
                word_count[word]=1
        index[doc_name] = word_count
        #index[doc_name]=nltk.Text(doc).vocab()
    for doc in index.keys():
        doc_index = index[doc]
        for word in doc_index.keys():
            if word in inverse_index.keys():
                inverse_index[word].append(doc)
            else:
                inverse_index[word] = [doc]
    return index, inverse_index

def build_dictionary(index):
    dictionary = {}
    for word in index.keys():
        dictionary[word]=len(dictionary)
    return dictionary

def compute_tfidf(index,word_dictionary,doc_dictionary):
    vocab_size = len(word_dictionary)
    doc_size = len(doc_dictionary)
    tf = np.zeros((doc_size,vocab_size))
    for doc in index:
        index_per_doc = index[doc]
        vector = np.zeros(vocab_size)
        for word in index_per_doc:
            vector[word_dictionary[word]] = index_per_doc[word]
        vector = np.log(vector+1)
        tf[doc_dictionary[doc]] = vector
    idf_numerator = doc_size
    idf_denominator = np.sum(np.sign(tf),0)
    idf = np.log(idf_numerator/idf_denominator)
    tfidf = tf*idf
    return tfidf

def cosine_similarity(x,y):
    normalizing_factor_x = np.sqrt(np.sum(np.square(x)))
    normalizing_factor_y = np.sqrt(np.sum(np.square(y)))
    return np.matmul(x,np.transpose(y))/(normalizing_factor_x*normalizing_factor_y)

def query_matching(inverse_dictionary,query):

    set_list = [set(inverse_dictionary[word]) for word in query]

    return set.intersection(*set_list)

def query_dot(query,word_dictionary,doc_dictionary):
    vocab_size = len(word_dictionary)
    doc_size=len(doc_dictionary)
    vector = np.zeros(vocab_size)
    for word in query:
        if(word in word_dictionary):
            vector[word_dictionary[word]] = 1
    vector = np.log(vector+1)
    idf_numerator = doc_size
    idf_denominator = np.sum(np.sign(vector),0)

    if(not(idf_denominator ==0)):
        idf = np.log(idf_numerator/idf_denominator)
        tfidf = vector*idf
        return tfidf
    else: ## if there is no match result
        return []


def dictionary_vector(vector,doc_dictionary):
    dictionary={}
    result=[]
    doc_size=len(doc_dictionary)

    for a in range(doc_size):
        for key in doc_dictionary.keys():
            if doc_dictionary[key]==a:
                dictionary[key] = vector[a]
    vector = sorted(dictionary.items(), key=operator.itemgetter(1), reverse = True)
    for a in range(5):
        result.append(vector[a])
    return result

def score(tfidf,word_dictionary,doc_dictionary,matched_document,query):
    result={}
    result2=[]
    for a in matched_document:
        score=0
        for b in query:
            wordnum = word_dictionary[b]
            score += tfidf[doc_dictionary[a]][wordnum]
        result[a]=score

    result = sorted(result.items(), key=operator.itemgetter(1),reverse=True)
    for a in range(5):
        result2.append(result[a])

    return result2


def search_engine(query):

    path = "./Data2/newsCrawl_s.json"
    whole_news = jp.read_news(path)

    doc_names, docs = read_docs(whole_news)

    index, inverted_index = index_doc(docs,doc_names)
    #matched_document = query_matching(inverted_index,query)
    word_dictionary = build_dictionary(inverted_index)
    doc_dictionary = build_dictionary(index)

    tfidf = compute_tfidf(index,word_dictionary,doc_dictionary)

    #score2= score(tfidf,word_dictionary,doc_dictionary,matched_document,query)

    dot = query_dot(query,word_dictionary,doc_dictionary)

    if(len(dot)==0):
        return [] ## no match result
    cos = cosine_similarity(tfidf,dot)
    vector = dictionary_vector(cos,doc_dictionary)

    result2 =[]

    for a in range(len(vector)):
        result2.append(vector[a][0])

    return result2


if __name__ == "__main__":

    model = gensim.models.Word2Vec.load('model/word2vec.model')

    input_query = []
    for i in range(len(sys.argv)-1):
        input_query.append(sys.argv[i+1])

    print('Input query : ', input_query)

    result = []
    stopwrds = stopwords.words('english')

    if(not(input_query=="")):
        tokens=[]
        for c in range(len(input_query)):
            tokens.append(input_query[c])
        query=[]

        for c in range(len(tokens)):
            if(tokens[c] in model.wv.vocab):
                query.append(tokens[c].lower())

        if(not(len(query)==0)):
            similar_word = model.most_similar(positive=query,topn=10)

            if(len(similar_word)==0):
                query = search_engine(query)
            else:
                print('hidden layer')
                print(similar_word)

                for c in range(len(similar_word)):
                    if(similar_word[c][0] not in stopwrds):
                        query.append(similar_word[c][0])

                print('New query')
                print(query)

                for c in range(len(query)):
                    query[c]= query[c].lower() ## Lower case

                documents = search_engine(query)
        else:
            documents = search_engine(tokens)

        if(len(query)==0):
            print('No result...')
        else:
            print('Most similar documents : ', documents)
