import pandas as pd

import numpy as np

class Analysis_pandas():

    def __init__(self):
        self.column_dict = {'lab':0.2,'lost_marks':0.20242468772961059,'strange_marks':0.0091176274129984632,'turn_around':0.0061452140805557413}
        self.prob_license = 0.26028 #重新测定
        self.prob_lost_marks= 0.20242468772961059
        self.prob_strange_marks = 0.0091176274129984632
        self.prob_turn_around = 0.0061452140805557413 # 重新测定
        self.exp_factor =-0.09

    def prob_diff(self,df,column,p):
        grouped = df.groupby('ex')[column].sum()
        df1 = grouped.reset_index()
        if column =='lab' or column =='lost_marks' or column =='turn_around':
            count = 1
        else:
            count = 0
        df1['prob'] = df1[column].apply(lambda x:np.power(p,x) if x>count else 1)
        df1['scores'] = df1[column].apply(lambda x: 350*np.exp(self.exp_factor*x)+300)

        return df1



    def make_scores(self,df):
        for column,p in  self.column_dict.items():
            print(column,p)
            df1 = analysis.prob_diff(df, column, p)
            df1.to_csv('./scores/{column}.csv'.format(column=column),index=False)


analysis = Analysis_pandas()
df = pd.read_csv('./samples.txt',names=(['lab','en','ex','vehicle_class','turn_around','strange_marks','lost_marks',
                         'over_weight','light_weight','over_delay','axis_number','fee_length','weight','over_weight_original',
                         'cost_time',
                         'speed']

                       ))

analysis.make_scores(df)