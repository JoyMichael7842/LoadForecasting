# -*- coding: utf-8 -*-
"""
Created on Mon Jul  8 22:55:55 2019

@author: Joy
"""
from datetime import datetime,timedelta
import util
import dbdao
import modelutil
import time
import numpy as np

t1 = datetime.now()
weekd = t1.weekday()
tempweekday=-1
tempday=-1
t1 = datetime.now()
date_time_str = '2018-06-29 00:00:00'  
t2 = datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')
minlist = [dt.strftime('%H:%M') for dt in 
               util.datetime_range(t2,t2+timedelta(days = 1) ,timedelta(minutes=2))]
while(True):
    if(tempday != weekd):
        print('changing model')
        totlist = []
        model = dbdao.load_model_from_db(weekd)
        tempday = weekd        
        
    t1 = datetime.now()
    weekd = t1.weekday()
    if  t1.hour == 00 and t1.minute == 00 and t1.second == 00:
        print("&&&&&&&&&&&&&&&&& Zero Condition inside")
        yesterday = t1.today() - timedelta(days = 1)    
        
        yesdf = dbdao.load_data_from_db(yesterday,t1)
        x_input = yesdf[-60:].values
        
        ans = modelutil.make_pred(x_input,model)
        
        prediction =  util.add_time_to_pred(ans)
        
        for x in prediction:
            totlist.append(x)           
        
        today = t1.today()
        dbdao.insert_into_db(today,totlist)
        time.sleep(5)
    
    if t1.hour == 1 and t1.minute == 00 and t1.second == 00:
        print("******************** One Hour Condition inside")
        today = t1.today()
    
        yesterday =  today-timedelta(days=1)
        
        realdf = dbdao.load_data_from_db(today,t1)
        
        yesdf = dbdao.load_data_from_db(yesterday,t1)
        
        
        x_input = [np.append(yesdf[-30:].values,realdf[:30].values)]
        x_input = np.array(x_input)
        x_input =x_input.T
        
        ans = modelutil.make_pred(x_input,model)
        prediction = util.add_time_to_pred(ans)
               
        
        existdatalist =  dbdao.append_pred(prediction)
        
        dbdao.insert_into_db(today,existdatalist)
        
        time.sleep(5)
        
    if t1.hour == 2 and t1.minute == 00 and t1.second == 00:
        print("******************** Tne Hour Condition inside")
        today = t1.today()
    
        
        realdf = dbdao.load_data_from_db(today,t1)
    
        
        x_input = realdf[-60:].values
        
        ans = modelutil.make_pred(x_input,model)
        
        prediction =  util.add_time_to_pred(ans)
        
        
        ans = modelutil.make_pred(x_input,model)
        prediction = util.add_time_to_pred(ans)
               
        
        existdatalist =  dbdao.append_pred(prediction)
        
        dbdao.insert_into_db(today,existdatalist)
        
        time.sleep(5)
        
    if  t1.hour!=1 and t1.hour!= 00 and t1.hour!=2 and t1.minute == 00 and t1.second == 00:
        print("################ Not One Hour Condition inside")
        today = t1.today()    
        
        realdf = dbdao.load_data_from_db(today,t1)        
        
        training_set = realdf.values
        
        model = modelutil.train_data(training_set,model)
        
        x_input = realdf[-60:].values
        ans = modelutil.make_pred(x_input,model)
        
        prediction = util.add_time_to_pred(ans)   
    
        
        existdatalist =  dbdao.append_pred(prediction,today)
    
         
        dbdao.insert_into_db(today,existdatalist)
        
        time.sleep(30*60)
        
