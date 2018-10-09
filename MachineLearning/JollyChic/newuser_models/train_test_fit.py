 #coding=utf-8
'''
Testing ROC AUC for each model fit on same training/test split
'''

'''
导入必要的library
'''
import csv
import numpy as np
from sklearn import model_selection
from sklearn.model_selection import GridSearchCV, cross_val_score, KFold, train_test_split
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, recall_score, precision_score, roc_auc_score
from sklearn.utils import shuffle
import matplotlib.pyplot as plt

from sklearn.externals import joblib
import pandas as pd
import sys
import os

path = '/home/mike.gu'
sys.path.append(path)
from imblearn.over_sampling import SMOTE

'''
指定数据的路径并输入数据
'''
Location= path + '/0808_newuser_sampled.csv'
df = pd.read_csv(Location,header=0,low_memory=False,delimiter='\t')
df_platform=df.copy()

'''
Create df_platform and set android to 0, ios to 1
'''
df_platform.loc[df_platform['platform']=='android','platform']=0
df_platform.loc[df_platform['platform']=='ios','platform']=1
'''
Create a new backup, back up the data in the first 17 columns
'''
backup=df.iloc[:,0:17].copy()
backup['is_login']=df.iloc[:,-1].copy

'''
Training data only after the 18th column
'''
df1=df.copy()
df1=df1.drop(df.columns[0:17],axis=1)
df1=df1.drop(df.columns[-1],axis=1)

'''
Insert the newly created df_platform to make the mobile platform also a feature
'''
df1.insert(loc=0, column='platform', value=df_platform['platform'])

'''
Print user distribution on two phone models
'''
print('andriod:{}'.format(len(backup[backup['platform']=='android'])))
print('ios:{}'.format(len(backup[backup['platform']=='ios'])))
print()
print('andriod=> 1:{}'.format(len(df1[(df1['platform']==0) & (df1['active_in_5_7']==1)])))
print('andriod=> 0:{}'.format(len(df1[(df1['platform']==0) & (df1['active_in_5_7']==0)])))

print('ios=> 1:{}'.format(len(df1[(df1['platform']==1) & (df1['active_in_5_7']==1)])))
print('ios=> 0:{}'.format(len(df1[(df1['platform']==1) & (df1['active_in_5_7']==0)])))

def feature_result_split(data):
    '''
Filter the last columns as labels, and feature is the rest.
    '''
    feature=data.iloc[:,:-1]
    result=data.iloc[:,-1]
    print('1 vs. 0:',len(result[result==1]), len(result[result==0]))

    '''
   Output generated features and labels
    '''
    return feature, result

'''
调用feature_result_split函数进行标签-特征分离
'''
X_1, Y_1 = feature_result_split(df1)

'''
train_test: 对输入的特征和标签做随机采样划分，feature_set为特征，result_set为标签，backup为之前备份的
此函数将输入的数据随机划分为三大类：用于训练的数据，用于调试模型的数据，用于做模型表现评估的数据
'''
def train_test(feature_set, result_set):

    rf_list = []
    gb_list = []
    print('Training models...')
    for i in [2, 3, 4]:
        X_train, X_test, Y_train, Y_test = train_test_split(feature_set, result_set, train_size=.6, random_state=i)
        print("--------------------------------------------------------")
        rf = RandomForestClassifier(max_depth=15, n_estimators=100,n_jobs=-1, random_state = 10)
        rf_fit=rf.fit(X_train, Y_train)
        rf_prediction_pro=rf_fit.predict_proba(X_test)
        rf_roc = roc_auc_score(Y_test, rf_prediction_pro[:,1])
        rf_list.append(rf_roc)

        gb = GradientBoostingClassifier(learning_rate=0.07, max_depth=13, n_estimators=100, random_state = 10)
        gb_fit=gb.fit(X_train, Y_train)
        gb_prediction_pro=gb_fit.predict_proba(X_test)
        gb_roc = roc_auc_score(Y_test, gb_prediction_pro[:,1])
        gb_list.append(gb_roc)

        print("random forest ratio (15, 100): {}".format(rf_roc))
        print("gradient boosting ratio (15, 100): {}".format(gb_roc))
        joblib.dump(rf_fit, './0820_rfGB_models/newuser_model_rf_{}_0820.pkl'.format(i))
        joblib.dump(gb_fit, './0820_rfGB_models/newuser_model_gb_{}_0820.pkl'.format(i))
        print("--------------------------------------------------------")

    mean_rf = np.mean(rf_list)
    mean_gb = np.mean(gb_list)
    print("random forest mean ratio (15, 100): {}".format(mean_rf))
    print("gradient boosting mean ratio (15, 100): {}".format(mean_gb))
    print()
    print()

    return True

train_test(X_1, Y_1)
