
import pandas as pd
import numpy as np
import sklearn as sk
from sklearn.ensemble import RandomForestClassifier
import xgboost
import matplotlib.pyplot as plt
from sklearn.metrics import explained_variance_score
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error
import metrics as me

class Model:

    def __init__(self):
        self.algorithm = ['rf_algorithm','xgboost_algorithm']
        self.test_size = 0.3
        self.seed = 10
        self.random_state = 42
        self.label_position = 1




    def model(self, new_df_label,grid_search=False,algorithm = 'rf_algorithm'):



            print('grid_search_status:', grid_search)
            algorithm_list = ['rf_algorithm','xgboost_algorithm']





            def rf_algorithm( x_train, x_test, y_train, y_test,grid_search):

                rf = RandomForestClassifier(oob_score=False,
                                                       n_estimators=200,
                                                       max_features='sqrt',
                                                       min_samples_leaf=13,
                                                       min_samples_split=50,
                                                       #max_depth=20,
                                                       random_state=self.random_state,
                                                       n_jobs=-1
                                                       # class_weight={0:3,1:30}

                                                       )
                if grid_search:
                    param_test1 = {'n_estimators': range(10, 301, 10)}
                    #param_test2 = {'max_depth': range(19, 50, 2),
                                   #}
                    param_test3 = { 'min_samples_split': range(50, 201, 20)}

                    gsearch1 = sk.model_selection.GridSearchCV(
                        estimator=rf,
                        param_grid=param_test1, scoring='neg_mean_squared_error', cv=5,n_jobs=-1)
                        #neg_mean_squared_error,incase of roc or other score,the high
                        #score is better,but in case of loss or error,lower is better,
                        # to handle them both in same way by adding negative.
                    gsearch1.fit(x_train, y_train)
                    df = pd.DataFrame(gsearch1.cv_results_).to_csv(
                        './log/grid_search{param}.csv'.format(param=param_test1), index=False)
                    print(pd.DataFrame(gsearch1.cv_results_))
                    return
                else:
                    rf.fit(x_train, y_train)
                    print(x_train.head())
                    y_scores = rf.predict_proba(x_test)[:,1]
                    y_scores_train = rf.predict_proba(x_train)[:,1]
                    #print('oobscore:', rf.oob_score_)
                    print('variavle importance:', pd.concat((pd.DataFrame(x_train.columns, columns=['variable']),
                                                     pd.DataFrame(rf.feature_importances_, columns=['importance'])),
                                                    axis=1).sort_values(by='importance', ascending=False)[:50])

                    m = me.Metrics_plot()
                    m.plot(y_test,[y_scores])
                    m.plot(y_train,[y_scores_train])
                    #print('test_variance=', explained_variance_score(y_true=y_test, y_pred=y_scores))
                    #print('train_variance=', explained_variance_score(y_true=y_train, y_pred=y_scores_train))
                    #print('MSE', mean_squared_error(y_true=y_test, y_pred=y_scores))
                    #print('train_MSE=', mean_squared_error(y_true=y_train, y_pred=y_scores_train))

                    #print('absolute_error', mean_absolute_error(y_true=y_test, y_pred=y_scores))
                    #print('train_absolute_error=', mean_absolute_error(y_true=y_train, y_pred=y_scores_train))
                return rf,y_scores,y_scores_train,y_test,y_train



            def xgboost_algorithm(x_train, x_test, y_train, y_test, grid_search):

                xgb = xgboost.XGBRegressor(
                    learning_rate=0.1,
                    #n_estimators=1000,
                    # max_depth=5,
                    min_child_weight=7,
                    gamma=0,
                    subsample=0.8,
                    colsample_bytree=0.8,
                    objective='reg:linear',
                    #scale_pos_weight=1,
                    # tree_method='gpu_hist',
                    seed=self.seed,
                    #n_jobs=4
                )
                if grid_search:
                    print('grid_records:', x_train.shape[0])
                    param_test1 = {
                        'n_estimators':range(10,10000,10)
                        #'max_depth': range(9, 30, 2),
                        #'min_child_weight': range(1, 100, 2)
                        #'n_estimators': range(10, 1000, 10)
                    }
                    # best {'min_child_weight': 5, 'max_depth': 3} 0.666090154470345


                    gsearch1 = sk.model_selection.GridSearchCV(
                        estimator=xgb,
                        param_grid=param_test1,
                        cv=5,
                        n_jobs=-1,
                        scoring = 'neg_mean_squared_error',
                        return_train_score = True

                    )

                    gsearch1.fit(x_train, y_train)
                    df = pd.DataFrame(gsearch1.cv_results_).to_csv('./log/grid_search{param} {algorithm}.csv'.format(param=param_test1,algorithm=algorithm),index=False)
                    print(pd.DataFrame(gsearch1.cv_results_))

                    return
                else:


                    #x_train = xgboost.DMatrix(x_train)
                    #y_train = xgboost.DMatrix(y_train)
                    #bst = xgboost.train(dtrain=x_train)
                    xgb.fit(x_train,y_train)

                    #x_test = xgb.DMatrix(x_test)
                    y_scores = xgb.predict(data=x_test)
                    y_scores_train = xgb.predict(data=x_train)
                    print('test_variance=',explained_variance_score(y_true=y_test,y_pred=y_scores))
                    print('train_variance=',explained_variance_score(y_true=y_train,y_pred=y_scores_train))
                    print('MSE',mean_squared_error(y_true=y_test,y_pred=y_scores))
                    print('train_MSE=',mean_squared_error(y_true=y_train,y_pred=y_scores_train))

                    print('absolute_error',mean_absolute_error(y_true=y_test,y_pred=y_scores))
                    print('train_absolute_error=',mean_absolute_error(y_true=y_train,y_pred=y_scores_train))


                return xgb, y_scores


            if grid_search:
                x_train = new_df_label.iloc[:, self.label_position + 1:]
                y_train = new_df_label.iloc[:, self.label_position]
                x_test = None
                y_test = None
                eval(algorithm)(x_train, x_test, y_train, y_test, grid_search)

                return

            else:
                x_train, x_test, y_train, y_test = sk.model_selection.train_test_split(new_df_label.iloc[:, 1:],
                                                                                       new_df_label.iloc[:, 0],
                                                                                       test_size=self.test_size,
                                                                                       random_state=self.random_state)

            return_algorithm, y_scores,y_scores_train,y_test,y_train = eval(algorithm)(x_train, x_test, y_train, y_test, grid_search)
            print(return_algorithm)

            return return_algorithm, y_scores



