 #coding=utf-8
'''
This random forest model is active for new users 5 to 7 days. The input is characterized by the performance of the new user in the first 4 days.
The result is whether the user has activity in 5 to 7 days (0 And 1, expressed by probability, 1 means there is activity)
The input characteristics are based on the performance of the new user in the previous 4 days,
with the second day as an example, and the remaining six days are the same.

Input characteristics:
1. Time spent on the JollyChic platform on Day 2
2. The number of pages viewed on the second day
3. Whether to register on the second day
4. Day 2 purchases
5. Day 2 Searches
6. The number of times the track was buried on the second day
7. How many times to visit the details page on the second day (the details page of a single product is counted multiple times)
8. How many products were accessed on the second day, subject to the details page (multiple visits for the same product)
9. How many major categories are involved in the product accessed on the second day?
10. How many orders were placed on the second day?
11. Day 2 order total

Model construction generally follows:
Input data--random sampling--training characteristics--tuning parameters--evaluating prediction results--entering new data for prediction

=================================================================================
'''

'''
导入必要的library
'''
import csv
import numpy as np
from sklearn import model_selection
from sklearn.model_selection import cross_val_score, KFold, train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, roc_auc_score
from sklearn.utils import shuffle
import matplotlib.pyplot as plt
from sklearn.externals import joblib
from imblearn.over_sampling import SMOTE
import pandas as pd
import sys
import os

path = '/home/mike.gu'
sys.path.append(path)

'''
指定数据的路径并输入数据
'''
Location= path + '/0808_newuser.csv'
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
    return feature, result

'''
调用feature_result_split函数进行标签-特征分离
'''
X_1, Y_1 = feature_result_split(df1)

def train_test(feature_set, result_set, backup):

    #do the train test data split randomly
    X_train, X_test, y_train, y_test = train_test_split(feature_set, result_set, train_size=.6, random_state=1)
    backup_train, backup_test = train_test_split(backup, train_size=.6, random_state=1)
    return X_train, y_train, X_test, y_test, backup_test


X1_train, Y1_train, X1_test, Y1_test, backup1_test = train_test(X_1, Y_1, backup)


'''
Train: function used to train the model (here with random forest)
X_train: characteristics of the training data
Y_train: the label of the training data
Name: the name of the tag
'''

def train(X_train, Y_train, name):
    print('Training models...')
    best_model = None
    rf, best_ratio, best_ne, best_md = 0, 0, 0, 0
    kf = KFold(n_splits=4, shuffle=True)
    smt=SMOTE(ratio='auto', random_state=10, k=None, k_neighbors=5, m=None, m_neighbors=10, out_step=0.5, kind='regular', svm_estimator=None, n_jobs=-1)
    train_list = []
    for train_index, test_index in kf.split(X_train):
        X_tr, X_ts = X_train.loc[X_train.index.intersection(train_index)], X_train.loc[X_train.index.intersection(test_index)]
        y_tr, y_ts = Y_train.loc[Y_train.index.intersection(train_index)], Y_train.loc[Y_train.index.intersection(test_index)]
        training_f_af, training_r_af=smt.fit_sample(X_tr, y_tr)
        train_list.append([training_f_af, training_r_af, X_ts, y_ts])
    for ne in [100]:
        for md in [2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 14]:
            roc_list = []
            for train_f, train_r, test_f, test_r in train_list:
                rf = RandomForestClassifier(max_depth=md, n_estimators=ne,n_jobs=-1, random_state = 10)
                rf_fit=rf.fit(train_f, train_r)
                prediction=rf_fit.predict(test_f)
                prediction_pro=rf_fit.predict_proba(test_f)
                '''
                用ROC_AUC作为指标调参数
                '''
                roc = roc_auc_score(test_r, prediction_pro[:,1])
                roc_list.append(roc)
            ratio = np.mean(roc_list)
            model = RandomForestClassifier(max_depth=md, n_estimators=ne,n_jobs=-1, random_state = 10).fit(X_train, Y_train)
            print('-----------------------------------------------------------')
            if ratio > best_ratio:
                best_md = md
                best_ne = ne
                best_ratio = ratio
                best_model = model
            print('n_estimators:  max_depth:',(ne, md))
            print('ratio:{0}'.format(ratio))
            joblib.dump(rf_fit, './0817_rf3_models/newuser_model_{}_{}_0817.pkl'.format(ne, md))
            print('newuser_model_{}_{} written to file!'.format(ne, md))
            print()
            print()
    print('best_n:{0}, best_depth:{1}'.format(best_ne, best_md))
    print('best_ratio using validation set:{0}'.format(best_ratio))

    '''
    输出最佳模型（共三个模型，名称被储存在name变量里）
    '''
    return best_model

'''
evaluate: 用来评估模型的函数 （这里用random forest)
X_test: 评估数据的特征
Y_test: 评估数据的标签
backup_test: 评估数据对应的备份特征
'''

def evaluate(model, X_test, Y_test, backup_test):
    print('Evaluating models...')
    prediction_pro=model.predict_proba(X_test)
    prediction=model.predict(X_test)
    '''
    得到ROC_AUC score
    '''
    roc = roc_auc_score(Y_test, prediction_pro[:,1])
    ratio=roc
    print('The ratio using evaluation set:{0}'.format(ratio))

    outfile=pd. DataFrame()
    outfile=backup_test.copy()
    outfile['label']=Y_test
    outfile['prob']=prediction_pro[:,1]

    print('Evaluate Done!')
    return outfile


'''
三次调用train函数训练模型
'''

model1 = train(X1_train, Y1_train,'active_in_5_7')

'''
三次调用evaluate函数进行模型评估，得到三个dataframe
'''
out_file1 = evaluate(model1, X1_test, Y1_test, backup1_test)
