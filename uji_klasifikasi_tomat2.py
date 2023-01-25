# -*- coding: utf-8 -*-
"""Uji Klasifikasi Tomat2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1tdBjIdf8IZ2180MhYPUgMl06pjYEORnp

#Import Modul
"""

pip install streamlit

import streamlit
import tensorflow as tf
import numpy as np
import pandas as pd
import seaborn as sns
import os.path
import os
import matplotlib.pyplot as plt
from google.colab import files
from keras.preprocessing import image
from keras.utils import load_img, img_to_array
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.optimizers import Adam, RMSprop
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.layers import Dense, Flatten, BatchNormalization, Dropout, Conv2D, MaxPool2D, LSTM, Permute, TimeDistributed, Bidirectional, LeakyReLU
from tensorflow.keras.callbacks import ReduceLROnPlateau
from sklearn import metrics
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.metrics import f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split

"""#Akses Dataset"""

from google.colab import drive
drive.mount('/content/drive')

for dirname, _, filenames in os.walk('/content/drive/MyDrive/tomato') :
  for filename in filenames :
    print(os.path.join(dirname, filename))

"""#Pemisahan Dataset"""

train_data_dir='/content/drive/MyDrive/tomato/'
train_data_dir1='/content/drive/MyDrive/tomato/matang'
train_data_dir2='/content/drive/MyDrive/tomato/mentah'

name_matang = os.listdir(train_data_dir1)
name_mentah = os.listdir(train_data_dir2)

new_matang = []
new_mentah = []

for i in name_matang :
  new_matang.append('/content/drive/MyDrive/tomato/matang/'+i)
for j in name_mentah :
  new_mentah.append('/content/drive/MyDrive/tomato/mentah/'+j)

df1 = pd.DataFrame()
df2 = pd.DataFrame()
df = pd.DataFrame()

df1['Ripeness'] = new_matang
df2['Ripeness'] = new_mentah

df1['Label'] = 'matang'
df2['Label'] = 'mentah'

df = pd.concat([df1, df2], axis = 0)
df = df.sample(frac=1).reset_index(drop=True)
df

"""#Preprocessing"""

train_datagen = ImageDataGenerator(rescale=1./255,
                                   zoom_range=0.2,
                                   validation_split=0.2)

test_datagen = ImageDataGenerator(rescale=1./255,
                                   zoom_range=0.2,
                                   validation_split=0.2)

train_images = train_datagen.flow_from_dataframe(
                                dataframe=df,
                                directory=None,
                                x_col='Ripeness',
                                y_col='Label',
                                target_size=(300, 300),
                                batch_size=64,
                                subset='training',
                                shuffle = True,
                                class_mode='categorical')
test_images = test_datagen.flow_from_dataframe(
                                dataframe=df,
                                directory=None,
                                x_col='Ripeness',
                                y_col='Label',
                                target_size=(300, 300)
                                ,batch_size=64,
                                subset='validation',
                                shuffle = True,
                                class_mode='categorical')

"""#Model RNN"""

model = Sequential()
model.add(Conv2D(filters = 64, kernel_size = (3, 3), padding = 'same', activation = 'relu', input_shape = train_images.image_shape))
model.add(MaxPool2D(pool_size = (2, 2)))
model.add(Dropout(rate = 0.2))

model.add(Conv2D(filters = 128, kernel_size = (3, 3), padding = 'same', activation = 'relu'))
model.add(MaxPool2D(pool_size = (2, 2),strides=(2, 2)))
model.add(Dropout(rate = 0.2))

model.add(Conv2D(filters = 256, kernel_size = (3, 3), padding = 'same', activation = 'relu'))
model.add(MaxPool2D(pool_size = (2, 2),strides=(2, 2)))
model.add(Dropout(rate = 0.2))

model.add(TimeDistributed(Flatten()))
model.add(LSTM(64,return_sequences=True))

model.add(Flatten())
model.add(Dense(units = 64, activation = 'relu'))
model.add(Dense(units = 128, activation = 'relu'))
model.add(Dense(units = 256, activation = 'relu'))
model.add(Dense(units = len(set(train_images.classes)), activation = 'softmax'))

model.compile(optimizer = 'adam', loss = 'categorical_crossentropy', metrics = ['accuracy'])
learning_rate = ReduceLROnPlateau(monitor='val_accuracy')
model.summary()

"""#Training Model"""

History = model.fit(train_images,
                epochs = 50,
                validation_data = test_images)

"""#Evaluasi Model"""

score = model.evaluate(train_images)
print('Train loss:', score[0])
print('Train accuracy', score[1])

score = model.evaluate(test_images)
print('Test loss:', score[0])
print('Test accuracy', score[1])

"""#Grafik Model

Grafik Model Accuracy
"""

plt.plot(History.history['accuracy'])
plt.plot(History.history['val_accuracy'])
plt.title('Model Accuracy')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.legend(['Accuracy', 'Val'])
plt.grid()
plt.figure()

"""Grafik Model Loss"""

plt.plot(History.history['loss'])
plt.plot(History.history['val_loss'])
plt.title('Model Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend(['Loss', 'Val'])
plt.grid()
plt.figure()

"""#Testing Model"""

from keras.utils import load_img, img_to_array

uploaded = files.upload()
for fn in uploaded.keys():
  path = fn
  img = load_img(path, target_size=(300, 300))
  imgplot = plt.imshow(img)
  x = img_to_array(img)
  x = np.expand_dims(x, axis=0)
  images = np.vstack([x])
  classes = model.predict(images, batch_size=30)
  print(fn)
  if classes[0][0]==1:
    print('Matang')
  else:
    print('Mentah')

"""#Evaluation Matrix"""

from sklearn.metrics import f1_score, precision_score, recall_score

Y_pred = model.predict(test_images)
y_pred=[]
for i in range(len(Y_pred)):
  if Y_pred[i][0]>0.5:
    y_pred.append(1)
  else:
    y_pred.append(0)
print('Classification Report')
target_names = ['Matang', 'Mentah']
print(metrics.classification_report(test_images.classes, y_pred, target_names=target_names))
print(test_images.class_indices)

"""#Confusion Metrics"""

cm = confusion_matrix(test_images.classes, y_pred)
print(cm)
sns.heatmap(cm, annot=True, fmt='g', vmin=0)
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.title("Confusion Matrix")
plt.show()