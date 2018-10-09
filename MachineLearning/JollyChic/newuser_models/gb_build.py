 #coding=utf-8
'''
This gradient boost model is active for new users 5 to 7 days. The input is characterized by the performance of the new user in the first 4 days.
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
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, roc_auc_score
from sklearn.utils import shuffle
import matplotlib.pyplot as plt
from sklearn.externals import joblib
import pandas as pd
import sys
import os

#path = 'C:/Users/tonyf/projects/MachineLearning/JollyChic/newuser_model_3days'
path = '/home/mike.gu'
sys.path.append(path)
from imblearn.over_sampling import SMOTE

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

'''
Feature_result_split: This function is used to separate features and labels (note that there are three labels),
data is the raw data obtained above, and df_num indicates the type of label
'''
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
train_test_smote: 对输入的特征和标签做随机采样划分，feature_set为特征，result_set为标签，backup为之前备份的
此函数将输入的数据随机划分为三大类：用于训练的数据，用于调试模型的数据，用于做模型表现评估的数据
'''
def train_test_smote(feature_set, result_set, backup):

    smt=SMOTE(ratio='auto', random_state=10, k=None, k_neighbors=5, m=None, m_neighbors=10, out_step=0.5, kind='regular', svm_estimator=None, n_jobs=-1)

    #do the train test data split randomly

    '''
    对特征和标签做SMOTE采样（Synthetic Minority Over-sampling Technique），目的是让不平衡的数据（标签为0的数据大于标签为1的数据）平衡
    这里采用K nearest neighbors 的方法
    注：SMOTE只能针对训练数据做数据扩充，否则会造成Data Leakage
    这里，60%数据用来训练模型
    20%的数据用来调试模型
    20%的数据用来评估
    '''
    subset=np.floor(len(feature_set)*0.6).astype('int')

    '''
    training_f:训练用的特征
    training_r:训练用的标签
    validate_f:调模型用的特征
    validate_r:调模型用的标签
    test_f:评估用的特征
    test_r:评估用的标签
    '''
    np.random.seed(1)
    index_whole=np.random.choice(feature_set.index,subset,replace=False)

    np.random.seed(1)
    index_validate=np.random.choice(pd.Index(index_whole), np.floor(subset/2).astype('int'), replace=False)

    index_test=pd.Index(index_whole).difference(pd.Index(index_validate))

    index_train=feature_set.index.difference(pd.Index(index_whole))

    training_f=feature_set.loc[index_train,:]
    training_r=result_set.loc[index_train]

    validate_f=feature_set.loc[index_validate,:]
    validate_r=result_set.loc[index_validate]
    backup_validate=backup.loc[index_validate,:]

    test_f=feature_set.loc[index_test,:]
    test_r=result_set.loc[index_test]
    backup_test=backup.loc[index_test,:]

    print(training_r)
    #SMOTE
    '''

SMOTE is only performed on the previously divided training data, and training_f_and_training_r_af is generated after training_f and training_r are sampled.
    '''
    training_f_af, training_r_af=smt.fit_sample(training_f, training_r)

    '''
    打印做过SMOTE的训练数据和未做过SMOTE的剩余数据
    '''
    print('balanced data ratio in training set:')
    print(len(training_r_af[training_r_af==0]) / len(training_r_af[training_r_af==1]))
    print('balanced data ratio in test set:')
    print(len(validate_r[validate_r==0]) / len(validate_r[validate_r==1]))

    return training_f_af, training_r_af, validate_f, validate_r, backup_validate, test_f, test_r, backup_test


'''
针对三个标签分别三次调用train_test_smote函数进行采样
'''
X1_train, Y1_train, X1_validate, Y1_validate, backup1_validate, X1_test, Y1_test, backup1_test = train_test_smote(X_1, Y_1, backup)


'''

Train: function used to train the model (here with random forest)
X_train: characteristics of the training data
X_test: Characteristics of the data used to tune the model
Y_train: the label of the training data
Y_test: the label of the data used to adjust the model
Backup_test: Backup feature corresponding to the data used by the model
Name: the name of the tag
'''

def train(X_train, X_test, Y_train, Y_test, backup_test,name):
    print('Training models...')
    best_model = None
    best_ratio, best_rate, best_md, best_ne = 0, 0, 0, 0
    for ne in [100]:
        for md in [15]:
            for rate in [0.07]:
                rf = GradientBoostingClassifier(learning_rate=rate, max_depth=md, n_estimators=ne, random_state = 10)
                rf_fit=rf.fit(X_train, Y_train)
                prediction=rf_fit.predict(X_test)
                prediction_pro=rf_fit.predict_proba(X_test)
                '''
                用ROC_AUC作为指标调参数
                '''
                roc = roc_auc_score(Y_test, prediction_pro[:,1])
                ratio=roc
                print('-----------------------------------------------------------')
                if ratio > best_ratio:
                    best_rate = rate
                    best_md = md
                    best_ne = ne
                    best_ratio = ratio
                    best_model = rf_fit
                print('learning_rate:', rate)
                print('confusion matrix\n', confusion_matrix(Y_test,prediction))
                print('ratio:{0}'.format(ratio))
                joblib.dump(rf_fit, './0817_GBM_models/newuser_model_{}_{}_{}_0817.pkl'.format(rate, md, ne))
                print('newuser_model_{}_{}_{} written to file!'.format(rate, md, ne))
                #print('roc_auc',roc_auc_score(Y_test, prediction_pro[:,1]))
                #print('accuracy',accuracy_score(Y_test,prediction))
                print()
                print()
    print('best_rate:{}'.format(best_rate))
    print('best_md:{}'.format(best_md))
    print('best_ne:{}'.format(best_ne))
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

model1 = train(X1_train, X1_validate, Y1_train, Y1_validate, backup1_validate,'active_in_5_7')


'''
三次调用evaluate函数进行模型评估，得到三个dataframe
'''
out_file1 = evaluate(model1, X1_test, Y1_test, backup1_test)
