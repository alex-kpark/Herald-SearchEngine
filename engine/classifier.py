import sys
import numpy as np
import pandas as pd
import collections

import keras
from keras.models import Sequential
from keras.layers import Dense, LSTM
from keras.preprocessing.text import Tokenizer
from keras.preprocessing import sequence
from sklearn.preprocessing import LabelEncoder
from keras.models import model_from_json

import pickle

import time
import gzip
import re

def predict_category(query):

    # Load data
    path = "./data/NC_70mb.json.gz"
    with gzip.open(path, 'rb') as f:
        content = f.read()
    df = pd.read_json(content.decode('utf-8'), typ='series', orient='records')

    labels = []
    for news in df:
        if news['category'] != '':
            labels.append(news['category'])

    le = LabelEncoder()
    trafomed_labels = le.fit_transform(labels)

    # Load LSTM Classification Model
    json_file = open('model/LSTM_classifier.json', 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    model = model_from_json(loaded_model_json)
	model.compile(loss='binary_crossentropy',
				  optimizer='adam',
				  metrics=['accuracy'])
    model.load_weights("model/LSTM_classifier_weights.h5")
    with open('./model/LSTM_tokenizer.pickle', 'rb') as handle:
        tokenizer = pickle.load(handle)
    t = tokenizer.texts_to_sequences(query)
    t = sequence.pad_sequences(t, maxlen=50)
    
    prediction = model.predict_classes(np.array(t))
    label = le.inverse_transform(prediction)
    print("Category Label : ",label)

    return label


def get_argument():
    input_argument=[]
    for i in range(len(sys.argv)-1):
        text = re.sub('[!"#%\'()*+,./:;<=>?@\[\]\\xa0$^_`{|}~’”“′‘\\\]',' ', sys.argv[i+1].lower())
        input_argument.append(text)
    return input_argument

if __name__ == "__main__":

    input_query = get_argument()
    category = predict_category(input_query)

    #print(category)
