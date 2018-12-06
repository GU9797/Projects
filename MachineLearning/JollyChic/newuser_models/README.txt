New user model selection and testing
Mike Gu

Goal: Predict user activity 5 to 7 days after installation based on user data from 1 to 4 days after installation

Dataset: 3,000,000 lines,  1 GB

Motivation:
The first week after installation is critical to building loyal customers. 2/3 users drop off activity in the first week.
Interested in feature importance and users who fall in activity.

Models:

Random Forest
(mike_randomforest_100_15_0817_2.pkl)
Overall highest roc score
Optimal max depth of 15, number of estimators is 100

Gradient Boosting
(mike_gradientboost_0.07_12_100_0817.pkl)
Optimal max depth of 12, number of estimators is 100

Code:

rf_build.py
Hypertuning parameters for random forest. Used kfold cross validation to validate parameters

gb_build.py
Hypertuning parameters for gradient boosting

train_test_fit.py
Testing ROC AUC for each model fit on same training/test split

gb_rf_test.py
Testing ROC AUC, Accuracy, plotting ROC curve, printing feature importances for preloaded models
