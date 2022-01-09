import pandas as pd
import pickle

data = pd.read_csv('Crop_recommendation.csv')
data.head()

data.isnull().sum()

data['label'].value_counts()

X = data.drop(['label'], axis = 1)
y = data['label']

from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X,y,test_size = 0.2,random_state = 0)

from sklearn.ensemble import RandomForestClassifier
rf_model = RandomForestClassifier()
rf_model.fit(X_train,y_train)


pickle.dump(rf_model, open('score.pkl', 'wb'))

