import pandas as pd
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

#Building proper numerical csv file
df = pd.read_csv("train.csv")
df.drop(['PassengerId','Name','Ticket','Cabin'],axis = 1,inplace = True)
df['Embarked'] = df['Embarked'].fillna('S')
df['Embarked'].replace(['S','C','Q'],[0,1,2],inplace = True)
df['Sex'].replace(['female','male'],[0,1],inplace = True)
df['Age'] = df['Age'].fillna(df['Age'].median())

#Using RandomForestClassifier
X = df.drop('Survived',axis = 1)
y = df['Survived']

X_train, X_test, y_train, y_test = train_test_split(X,y,test_size= 0.2, random_state=100)

rf_model = RandomForestClassifier(class_weight='balanced',criterion='gini',min_samples_leaf=1,min_samples_split=16,n_estimators=700)
rf_model.fit(X_train,y_train)

pickle.dump(rf_model,open('static/model.pkl', 'wb'))
