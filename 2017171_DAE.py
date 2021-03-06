# -*- coding: utf-8 -*-
"""SML_project (DAE implementation)

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1uLbwlTW970EOT0bXYc1D-7_3fnH98N-B
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from matplotlib import pyplot as plt
from sklearn.preprocessing import StandardScaler
import seaborn as sns
from sklearn.manifold import TSNE
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTE
import keras
from keras.layers import Input, Dense
from keras.models import Model, Sequential
from keras import regularizers
from sklearn.metrics import classification_report, accuracy_score
import itertools
from sklearn.metrics import confusion_matrix,roc_auc_score,roc_curve,recall_score,auc,accuracy_score



data=pd.read_csv('/content/drive/My Drive/creditcard.csv')

"""A brief description of the dataset

Time: Number of seconds elapsed between this transaction and the first transaction in the dataset
Amount: Transaction amount
Class: 1 for fraudulent transactions, 0 otherwise
"""

data.shape

data.isnull().values.any()

data  #original data

data.describe()

count_classes=pd.value_counts(y_train, sort = True)
count_classes.plot(kind = 'bar', rot=1)

count_classes

"""Data Pre-processing and Visualization"""

fig, ax = plt.subplots(1, 2, figsize=(18,4))

amount_val = data['Amount'].values
time_val = data['Time'].values

sns.distplot(amount_val, ax=ax[0], color='r')
ax[0].set_title('Distribution of Transaction Amount', fontsize=14)
ax[0].set_xlim([min(amount_val), max(amount_val)])

sns.distplot(time_val, ax=ax[1], color='b')
ax[1].set_title('Distribution of Transaction Time', fontsize=14)
ax[1].set_xlim([min(time_val), max(time_val)])



plt.show()

non_fraud=data[data['Class']==0]
fraud=data[data['Class']==1]


#Scaling of data- Time and amount values need to be scaled wrt other values to have same distributions
#one way to do this is to first scale time and amount (normalization) then applying SMOTE on them to correct the imbalance distribution. 
#Scaling the data- use robust scaler -  Because it is less prone to outliers



rob_scaler=StandardScaler()
non_fraud=data[data['Class']==0].sample(1000)
fraud=data[data['Class']==1]
df1 = non_fraud.append(fraud).sample(frac=1).reset_index(drop=True)
df1['Amount'] = rob_scaler.fit_transform(df1['Amount'].values.reshape(-1,1))

X=df1.drop(['Class'],axis=1).values
labels=df1['Class'].values
print(pd.DataFrame(X))
print(pd.DataFrame(labels))

'''What is t-SNE? t-Distributed Stochastic Neighbor Embedding (t-SNE) is an unsupervised,
 non-linear technique primarily used for data exploration and visualizing high-dimensional data. 
 In simpler terms, t-SNE gives you a feel or intuition of how the data is arranged in a high-dimensional space'''

def tsne_plot(x1, y1, name="graph.png"):
    tsne = TSNE(n_components=2, random_state=0)
    X_t = tsne.fit_transform(x1)

    plt.figure(figsize=(12, 8))
    plt.scatter(X_t[np.where(y1 == 0), 0], X_t[np.where(y1 == 0), 1], marker='o', color='g', linewidth='1', alpha=0.8, label='Non Fraud')
    plt.scatter(X_t[np.where(y1 == 1), 0], X_t[np.where(y1 == 1), 1], marker='o', color='r', linewidth='1', alpha=0.8, label='Fraud')

    plt.legend(loc='best');
    plt.savefig(name);
    plt.title('t-SNE plot of 1000 non fraud cases vs fraud cases')
    plt.show()


tsne_plot(X,labels)

#Train Test Split 
scaler=StandardScaler()
datacopy=data.copy()
labels=datacopy['Class']
datacopy=datacopy.drop(['Class','Time'],axis=1)
#datacopy=datacopy.drop(['Time'],axis=1)
datacopy['Amount']=scaler.fit_transform(datacopy['Amount'].values.reshape(-1,1))
#datacopy['Time']=scaler.fit_transform(datacopy['Time'].values.reshape(-1,1))

X_train, X_test, y_train, y_test= train_test_split(datacopy,labels, test_size=0.2,random_state=42)

"""SMOTE Oversampling"""

sm = SMOTE(sampling_strategy='not majority',random_state=42)
X_train_res,y_train_res=sm.fit_resample(X_train,y_train)

"""Addition of Gaussian noise"""

X_train_noisy = X_train_res +  np.random.normal(loc=0.0, scale=0.1, size=X_train_res.shape)

pd.DataFrame(X_train_noisy)

pd.DataFrame(X_train_res)

def change_batch_y(batch_y):
  batch_y = batch_y
  batch_y = np.array([batch_y == 0, batch_y == 1], dtype=np.float32)
  batch_y = np.transpose(batch_y)
  return batch_y


input_layer = Input(shape=(X_train_noisy.shape[1],))
func=keras.layers.LeakyReLU(alpha=0.1)
encoded = Dense(22, activation=func, activity_regularizer=regularizers.l1(10e-5))(input_layer)
encoded2 = Dense(15, activation =func, activity_regularizer=regularizers.l1(10e-5))(encoded)
encoded3= Dense(10, activation =func, activity_regularizer=regularizers.l1(10e-5))(encoded2)
decoded1= Dense(15, activation =func, activity_regularizer=regularizers.l1(10e-5))(encoded3)
decoded2= Dense(22, activation =func, activity_regularizer=regularizers.l1(10e-5))(decoded1)
output=  Dense(X_train_noisy.shape[1], activation =func, activity_regularizer=regularizers.l1(10e-5))(decoded2)
autoencoder = Model(input_layer, output)
adam=keras.optimizers.Adam(learning_rate=0.001, beta_1=0.9, beta_2=0.999, amsgrad=False)
autoencoder.compile(optimizer=adam, loss="mse")
autoencoder.summary()

pd.DataFrame(X_train_noisy)

print(X_train_noisy.shape)

autoencoder.fit(X_train_noisy, X_train_res, 
                batch_size =64, epochs = 30, 
                shuffle = True, validation_split = 0.20,);

#from keras.models import load_model
#autoencoder.save('Autoencoder with 100 ep.h5')

denoised_dataset=autoencoder.predict(X_train_noisy)

#classifier 

#get number of columns in training data
n_cols = 29
input_layer_1=Input(shape=(29,))
#add model 
func=keras.layers.LeakyReLU(alpha=0.1)
layer1 = Dense(22, activation=func, activity_regularizer=regularizers.l1(10e-5))(input_layer_1)
layer2 = Dense(15, activation =func, activity_regularizer=regularizers.l1(10e-5))(layer1)
layer3= Dense(10, activation =func, activity_regularizer=regularizers.l1(10e-5))(layer2)
layer4= Dense(5, activation =func, activity_regularizer=regularizers.l1(10e-5))(layer3)
output_layer= Dense(2, activation ='softmax')(layer4)
#output=  Dense(X_train_noisy.shape[1], activation ='tanh', activity_regularizer=regularizers.l1(10e-5))(decoded2)
classifier= Model(input_layer_1, output_layer)
classifier.compile(optimizer="adam", loss="categorical_crossentropy",metrics=['accuracy'])

classifier.summary()

change=change_batch_y(y_train_res)
classifier.fit(denoised_dataset, change, 
                batch_size =64, epochs = 30, 
                shuffle = True, validation_split = 0.20)

y_test_pred=classifier.predict(autoencoder.predict(X_test))
y_test_pred_max=np.argmax(y_test_pred, axis=-1)



def plot_confusion_matrix(cm, classes,
                          normalize=False,
                          title='Confusion matrix',
                          cmap=plt.cm.Blues):
    """
    This function prints and plots the confusion matrix.
    Normalization can be applied by setting `normalize=True`.
    """
    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=0)
    plt.yticks(tick_marks, classes)

    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        #print("Normalized confusion matrix")
    else:
        1#print('Confusion matrix, without normalization')

    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, cm[i, j],
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black")

    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')

cnf_matrix = confusion_matrix(y_test,y_test_pred_max)
np.set_printoptions(precision=2)

print("Recall metric in the testing dataset: ", cnf_matrix[1,1]/(cnf_matrix[1,0]+cnf_matrix[1,1]))

# Plot non-normalized confusion matrix
class_names = [0,1]
plt.figure()
plot_confusion_matrix(cnf_matrix
                      , classes=class_names
                      , title='Confusion matrix')
plt.show()    

fpr, tpr, thresholds = roc_curve(y_test,y_test_pred_max)
roc_auc = auc(fpr,tpr)

# Plot ROC
plt.title('Receiver Operating Characteristic')
plt.plot(fpr, tpr, 'b',label='AUC = %0.2f'% roc_auc)
plt.legend(loc='lower right')
plt.plot([0,1],[0,1],'r--')
plt.xlim([-0.1,1.0])
plt.ylim([-0.1,1.01])
plt.ylabel('True Positive Rate')
plt.xlabel('False Positive Rate')
plt.show()

#print(classification_report(y_test_pred,y_test))
print ("Accuracy Score: ", accuracy_score(y_test,y_test_pred_max))

y_test_change=change_batch_y(y_test)

evaluate_results = []
for threshold in np.arange(0, 1.01, 0.01):
  TP, FN, FP, TN = 0, 0, 0, 0
  for i in range(len(y_test)):
      prediction = y_test_pred[i]
      actual = y_test_change[i]
      if prediction[1] >= threshold and actual[1] == 1:
          TP += 1
      elif prediction[1] >= threshold and actual[1] == 0:
          FP += 1
      elif prediction[1] < threshold and actual[1] == 1:
          FN += 1
      elif prediction[1] < threshold and actual[1] == 0:
          TN += 1
  result = dict()
  result['threshold'] = threshold
  result['TP'] = TP
  result['FP'] = FP
  result['FN'] = FN
  result['TN'] = TN
  result['recall'] = TP / (TP + FN)
  result['precision'] = TP / (TP + FP)
  result['accuracy'] = (TP + TN) / (TP + FN + FP + TN)
  evaluate_results.append(result)
  print(result)

threshold_array = [result['threshold'] for result in evaluate_results]
recall_array = [result['recall'] for result in evaluate_results]
precision_array = [result['precision'] for result in evaluate_results]
accuracy_array = [result['accuracy'] for result in evaluate_results]
plt.plot(threshold_array, recall_array, label='recall')
plt.plot(threshold_array, precision_array, label='precision')
plt.plot(threshold_array, accuracy_array, label='accuracy')
plt.xlabel('Threshold 0~1')
plt.ylabel('recall & precision & accuracy')
plt.legend()
plt.show()

