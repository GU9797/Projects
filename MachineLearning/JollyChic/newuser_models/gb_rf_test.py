#coding=utf-8
import csv
import numpy as np
from sklearn import model_selection
from sklearn.model_selection import GridSearchCV, cross_val_score, KFold, train_test_split
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, recall_score, precision_score, roc_auc_score, roc_curve, auc
from sklearn.utils import shuffle
import matplotlib.pyplot as plt
from sklearn.externals import joblib
import pandas as pd
import sys
import os

path = '/home/mike.gu/backtesting'
sys.path.append(path)
from imblearn.over_sampling import SMOTE

Location= path + '/0204.csv'
df = pd.read_csv(Location,header=0,low_memory=False,delimiter='\t')
df_platform=df.copy()

df_platform.loc[df_platform['platform']=='android','platform']=0
df_platform.loc[df_platform['platform']=='ios','platform']=1

backup=df.iloc[:,0:17].copy()
backup['is_login']=df.iloc[:,-1].copy

df1=df.copy()
df1=df1.drop(df.columns[0:17],axis=1)
df1=df1.drop(df.columns[-1],axis=1)
df1.insert(loc=0, column='platform', value=df_platform['platform'])

print('andriod:{}'.format(len(backup[backup['platform']=='android'])))
print('ios:{}'.format(len(backup[backup['platform']=='ios'])))
print()
print('andriod=> 1:{}'.format(len(df1[(df1['platform']==0) & (df1['active_in_5_7']==1)])))
print('andriod=> 0:{}'.format(len(df1[(df1['platform']==0) & (df1['active_in_5_7']==0)])))
print('ios=> 1:{}'.format(len(df1[(df1['platform']==1) & (df1['active_in_5_7']==1)])))
print('ios=> 0:{}'.format(len(df1[(df1['platform']==1) & (df1['active_in_5_7']==0)])))

def feature_result_split(data):
    feature=data.iloc[:,:-1]
    result=data.iloc[:,-1]
    print('1 vs. 0:',len(result[result==1]), len(result[result==0]))

    return feature, result

#feature and result split
'''
调用feature_result_split函数进行标签-特征分离
'''
X_1, Y_1 = feature_result_split(df1)


def predict(feature_set, result_set, pklpath, model_name):
    print("getting models")
    pkl = open(os.path.join(pklpath,model_name),'rb')
    model = joblib.load(pkl)

    featurename=feature_set.columns
    importances=model.feature_importances_
    indices = np.argsort(importances)[::-1]
    fi = pd.DataFrame()
    fi['feature_name'] = featurename[indices]
    fi['importance'] = importances[indices]
    print("feature importances: ", fi)

    prediction_pro = model.predict_proba(feature_set)
    roc_score = roc_auc_score(result_set, prediction_pro[:,1])
    print("{} roc: {}".format(model_name, roc_score))

    print("-------------------------------------")

    fpr, tpr, thresholds = roc_curve(result_set, prediction_pro[:,1])
    roc_auc = auc(fpr, tpr)
    print("Area under the ROC curve : %f" % roc_auc)
    i = np.arange(len(tpr)) # index for df
    roc = pd.DataFrame({'fpr' : pd.Series(fpr, index=i),'tpr' : pd.Series(tpr, index = i), '1-fpr' : pd.Series(1-fpr, index = i), 'tf' : pd.Series(tpr - (1-fpr), index = i), 'thresholds' : pd.Series(thresholds, index = i)})
    roc.loc[(roc.tf-0).abs().argsort()[:1]]
    # Plot tpr vs 1-fpr
    plt.figure()
    plt.plot(roc['tpr'])
    plt.plot(roc['1-fpr'], color = 'red')
    plt.xlabel('1-False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver operating characteristic')
    plt.show()

    print("-------------------------------------")

    #accuracy
    max_accuracy = 0
    max_thresh = 0
    for threshold in np.arange(.3, .8, .05):
        binary_pred = np.where(prediction_pro[:,1] < threshold, 0, 1)
        acc = accuracy_score(result_set, binary_pred)
        if acc > max_accuracy:
            max_accuracy = acc
            max_thresh = threshold
        print("{}, threshold: {}, acc: {}".format(model_name, threshold, acc))
        print()
    print("{}, best threshold: {}, best acc: {}".format(model_name, max_thresh, max_accuracy))

    return True

#newuser_best_model_active_in_5_7_0715.pkl test in local
#newuser_model_100_15_0817_2.pkl best rf model
#newuser_model_0.07_14_100_0820.pkl best gb model
#newuser_model_gb_4_0820.pkl
#files = path + '/0820_rfGB_models/'
print('Random Forest Testing')
predict(X_1, Y_1, path, 'newuser_model_100_15_0817_2.pkl')
print('-----------------------')
'newuser_best_model_active_in_5_7_0715'
print('Gradient Boost Testing')
predict(X_1, Y_1, path, 'newuser_model_0.07_14_100_0820.pkl')
