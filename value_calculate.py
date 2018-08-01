from model import *
import pandas as pd
df = pd.read_csv('./samples.txt',
                 names=('label', 'turn_around', 'vehicle_class', 'over_weight1', 'light_weight',
                        'over_delay', 'axis_number', 'strange_marks', 'lost_marks', 'fee_length', 'weight',
                        'over_weight2'))
print(df.info())

model = Model()
model.model(df)