import sys
import numpy as np
import pandas as pd
import collections

import keras
from keras.preprocessing.text import Tokenizer
from keras.preprocessing import sequence
from sklearn.preprocessing import LabelEncoder
from keras.models import model_from_json

import pickle

import time
import gzip

i=1

def predict_category(content, query):
    '''
    path = "./data/NC_70mb.json.gz"
    with gzip.open(path, 'rb') as f:
        content = f.read()
    content = content.decode('utf-8')
    '''

    df = pd.read_json(content, typ='series', orient='records')

    labels = []
    for news in df:
        if news['category'] != '':
            labels.append(news['category'])

    le = LabelEncoder()
    trafomed_labels = le.fit_transform(labels)

    # Load LSTM Classification Model
    json_file = open('model/LSTM_classifier_binary.json', 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    model = model_from_json(loaded_model_json)
    model.compile(loss='binary_crossentropy',
				  optimizer='adam',
				  metrics=['accuracy'])
    model.load_weights("model/LSTM_classifier_binary_weights.h5")
    with open('./model/LSTM_tokenizer_binary.pickle', 'rb') as handle:
        tokenizer = pickle.load(handle)
    t = tokenizer.texts_to_sequences(query)
    t = sequence.pad_sequences(t, maxlen=50)
    prediction = model.predict_classes(np.array(t))
    predicted_category = le.inverse_transform(prediction)

    return predicted_category
