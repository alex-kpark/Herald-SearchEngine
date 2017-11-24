import numpy as np
import pandas as pd

import keras
from keras.models import Sequential
from keras.layers import Dense, LSTM
from keras.layers import Embedding
from keras.preprocessing.text import Tokenizer
from keras.preprocessing import sequence
from sklearn.preprocessing import LabelEncoder
from keras.models import model_from_json

import pickle
import time
import re
import gzip

i=1

MAX_FEATURES = 20000
MAX_LEN = 80  # cut texts after this number of words (among top max_features most common words)
BATCH_SIZE = 32
VALIDATION_SPLIT = 0.2


# Load data
path = "./data/NC_70mb.json.gz"
with gzip.open(path, 'rb') as f:
    content = f.read()
df = pd.read_json(content.decode('utf-8'), typ='series', orient='records')

texts = []
labels = []
for news in df:
    if news['category'] != '':
        text = re.sub('[!"#%\'()*+,./:;<=>?@\[\]\\xa0$^_`{|}~’”“′‘\\\]',' ', news['title'].lower()+"."+news['article'].lower())
        texts.append(text)
        labels.append(news['category'])
num_classes = len(list(set(labels)))
#print(list(set(labels)))

# 기사 원문 Tokenization
tokenizer = Tokenizer(num_words=MAX_FEATURES)
tokenizer.fit_on_texts(texts)
sequences = tokenizer.texts_to_sequences(texts)
data = sequence.pad_sequences(sequences, maxlen=MAX_LEN)

# 카테고리 바이너리화 (binary) -> Target
le = LabelEncoder()
trafomed_labels = le.fit_transform(labels)
labels = keras.utils.to_categorical(np.asarray(trafomed_labels))

# 트레이닝 & 테스트 데이터셋 추출 8:2 비율
indices = np.arange(data.shape[0])
np.random.shuffle(indices)
data = data[indices]
labels = labels[indices]
nb_validation_samples = int(VALIDATION_SPLIT * data.shape[0])

x_train = data[:-nb_validation_samples]
y_train = labels[:-nb_validation_samples]
x_test = data[-nb_validation_samples:]
y_test = labels[-nb_validation_samples:]

#print(x_train)
#print(y_train)

print('Build model...')
model = Sequential()
model.add(Embedding(MAX_FEATURES, 128))
model.add(LSTM(128, dropout=0.2, recurrent_dropout=0.2))
model.add(Dense(num_classes, activation='softmax'))

#model.compile(loss='categorical_crossentropy',
#              optimizer='rmsprop',
#              metrics=['accuracy'])
model.compile(loss='binary_crossentropy',
              optimizer='adam',
              metrics=['accuracy'])

print('Train...')
model.fit(x_train, y_train,
          batch_size=BATCH_SIZE,
          epochs=5,
          validation_data=(x_test, y_test))
score, acc = model.evaluate(x_test, y_test,
                            batch_size=BATCH_SIZE)
print('Test score:', score)
print('Test accuracy:', acc)


# Save Classification Model
model_json = model.to_json()
with open("model/LSTM_classifier_binary.json", "w") as json_file:
    json_file.write(model_json)
model.save_weights("model/LSTM_classifier_binary_weights.h5")
print("Saved model to disk")

# Save Tokenizer
with open('./model/LSTM_classifier_tokenizer_binary.pickle', 'wb') as handle:
    pickle.dump(tokenizer, handle, protocol=pickle.HIGHEST_PROTOCOL)
