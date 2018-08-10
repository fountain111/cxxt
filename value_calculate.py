from model import *
import pandas as pd

df = pd.read_csv('./samples.txt',
                 names=(['lab', 'en', 'ex', 'vehicle_class', 'turn_around', 'strange_marks', 'lost_marks',
                         'over_weight', 'light_weight', 'over_delay', 'axis_number', 'fee_length', 'weight',
                         'over_weight_original',
                         'cost_time',
                         'speed'])
                 )
#df = df[df.speed !='None']


df_train=df.drop(['turn_around','strange_marks','lost_marks','en','ex'],axis=1)
print(df_train.info(),print(df_train.head()))

model = Model()
rf,_ = model.model(df_train)
df_pre = df.drop(['turn_around','strange_marks','lost_marks','en'],axis=1)
df['prob'] = rf.predict_proba(df_pre.iloc[:,2:])[:,1]
df['scores'] = df['prob'].apply(lambda x:1-x)*350+300
df.to_csv('./scores/{column}.csv'.format(column='rf'), index=False)


