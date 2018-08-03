from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import sklearn as sk
import pandas as pd
import matplotlib.pyplot as plt
class Metrics_plot:

    def threshold_r1_r0_precision1(self,df,predict_label,true_label,plot=False,threshold_range=50):
        '''

        :param df: 目前只适合2分类问题,predict_label默认取正类
        :param predict_label:
        :param true_label:
        :return:
        :example

        temp = plot_.threshold_r1_r0_precision1(df,'predict1','churn_flg')
        predict1 :positive column in dataframe,
        churn_flg : true label
        '''
        positive = 1
        negative = 0
        threshold_list =[]
        recall0_list = []
        recall1_list = []
        precision1_list = []
        tp_fp_sum_list = []


        for i in range(threshold_range):

            threshold = i/threshold_range
            r1 = sum(df[df[predict_label] > threshold][true_label] == positive) / sum(df[true_label] == positive)
            r0 = sum(df[df[predict_label] < threshold][true_label] == negative) / sum(df[true_label] == negative)

            tp_fp_sum = sum(df[predict_label] > threshold)
            precision1 = sum(df[df[predict_label] > threshold][true_label] == positive) /tp_fp_sum

            recall0_list.append(r0)
            recall1_list.append(r1)
            precision1_list.append(precision1)
            threshold_list.append(threshold)
            tp_fp_sum_list.append(tp_fp_sum)
            print(threshold,r1,r0,precision1,tp_fp_sum)
            print(len(threshold_list),len(recall0_list),len(recall1_list),len(precision1_list),len(tp_fp_sum_list))
        return_df = pd.DataFrame({'threshold':threshold_list,'recall0':recall0_list,'recall1':recall1_list,
                                  'precision1':precision1_list,'tp_fp_sum':tp_fp_sum_list})
        print(return_df)

        if plot:
            return_df.plot()
            plt.show()

        return return_df



    def plot(self,y_test, y_scores_list):

        for y_scores in y_scores_list:
            y_true = y_test
            print('positive records in validation', sum(y_test))
            print('validation_records:', y_test.shape[0])

            fpr, tpr, thresholds = sk.metrics.roc_curve(y_true, y_scores, drop_intermediate=False)
            precision, recall, thresholds_pr = sk.metrics.precision_recall_curve(y_true, y_scores)

            print('auc under roc:{roc}, auc under pr: {pr}'.format( roc = sk.metrics.roc_auc_score(y_true, y_scores),pr=sk.metrics.auc(recall,precision)))

            roc_curve = pd.DataFrame({'fpr': fpr, 'tpr': tpr, 'thresholds': thresholds})
            p_r_curve = pd.DataFrame({'precision': precision, 'recall': recall})
            p_r_curve = p_r_curve.iloc[:-1, :]  # 第一个数recall = 0，计算面积时会很大
            roc_curve.plot(x='fpr', y='tpr')
            p_r_curve.sort_values('recall', inplace=True)
            p_r_curve.plot(x='recall', y='precision')


            print(roc_curve)
            print(p_r_curve)

            threshold_df = pd.DataFrame({'y_scores': y_scores, 'y_true': y_true})
            plt.show()
        return
