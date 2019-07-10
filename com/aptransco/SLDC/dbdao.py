# -*- coding: utf-8 -*-
"""
Created on Mon Jul  8 21:49:24 2019

@author: Joy
"""
import psycopg2
import pandas as pd
import json
import numpy as np
import ast
from tensorflow.keras.models import model_from_json

def retrieve_database(strql):
    con = psycopg2.connect(database="SLDCREP", user="postgres", password="createdon16082018", host="192.168.168.125", port="5432")
    print("Database opened successfully")  
    cur = con.cursor()  
    cur.execute("SELECT rtu_data_date, rtu_point_record from sldcsch.rtu_point_data where rtu_data_date in ("+strql+") and rtu_point_id ='13008'")
    rows = cur.fetchall()
    print(len(rows))
    #rtudataset=[]
    df = pd.DataFrame(columns=['date','rtudata'])
    i=1
    for row in rows:
        df.loc[i, 'date'] = str(row[0])
        df.loc[i, 'rtudata'] = str(row[1])
        i=i+1
        
    df.date = pd.to_datetime(df.date, format='%Y-%m-%d') 
    df = df.sort_values(by=['date'])
    df.date = df.date.dt.strftime('%Y-%m-%d')
    
    return df

def save_model_in_database(regressor,dates_list,weekd):
    weights_list = regressor.get_weights()
    modeljson = regressor.to_json()
    modeljson = modeljson.replace('\'','\"')
    anlist = []
    for i,weights in enumerate(weights_list):
        dataaa = np.ndarray.tolist(weights)
        anlist.append(dataaa)

    weightsjson = json.dumps(anlist)
    con = psycopg2.connect(database="SLDCREP", user="postgres", password="createdon16082018", host="192.168.168.125", port="5432")
    print("Database opened successfully")  
    cur = con.cursor()  
    cur.execute("insert into sldcsch.fcast_model_weights(rtu_point_id,model_json,weights,trained_from_date,trained_to_date,trained_for_day,training_execute_date) values('13008','"+modeljson+"','"+weightsjson+"','"+dates_list[0]+"','"+dates_list[-2]+"','"+str(weekd)+"','2019-06-26')")
    con.commit()

    regressor.save('mondaymodel')

def load_model_from_db(weekd):
    con = psycopg2.connect(database="SLDCREP", user="postgres", password="createdon16082018", host="192.168.168.125", port="5432")
    print("Database opened successfully")  
    cur = con.cursor() 
    cur.execute("select model_json,weights,trained_for_day,max(rec_inserted_time) from sldcsch.fcast_model_weights where trained_for_day="+str(weekd)+"group by model_json,weights,trained_for_day")
    rows = cur.fetchall()        
    df = pd.DataFrame(columns=['weekday','modeljson','weights'])
    i=1
    for row in rows:
        df.loc[i, 'modeljson'] = str(row[0])
        df.loc[i, 'weights'] = str(row[1])
        df.loc[i,'weekday'] = str(row[2])
        i=i+1
        
    print(df)

    json_string_2 = df.iloc[0,1]
    model = model_from_json(json_string_2)
    
    json_string = df.iloc[0,2]
    datastore = json.loads(json_string)
    anlist2 = []
    for i,weights in enumerate(datastore):
        dataaa = np.array(weights)
        anlist2.append(dataaa)    
    
    anl = []
    for j in range(len(anlist2)):
        an = np.array([np.float32(i) for i in anlist2[j]])
        anl.append(an)
    model.set_weights(anl)

    return model

def load_data_from_db(date,t1):
    con = psycopg2.connect(database="SLDCREP", user="postgres", password="createdon16082018", host="192.168.168.125", port="5432")
    print("Database opened successfully")  
    cur = con.cursor() 
    cur.execute("SELECT rtu_data_date, rtu_point_record from sldcsch.rtu_point_data where rtu_data_date='"+str(date)+"' and rtu_point_id ='13008'")
    yrows = cur.fetchall()
    print(len(yrows))
    dfcyesterday = pd.DataFrame(columns=['date','rtudata'])
    l=1
    for row in yrows:
        dfcyesterday.loc[l, 'date'] = str(row[0])
        dfcyesterday.loc[l, 'rtudata'] = str(row[1])
        l=l+1  
                      
    todaystr = t1.today().strftime('%Y-%m-%d')        
    anlist2 =  pd.Series.tolist(dfcyesterday['rtudata'])
    anlist2 = ast.literal_eval(anlist2[0])
    timelist2 = []                
    anvalue2 =[]
    for x in anlist2:
        anvalue2.append(x['recordValue'])
        string = x['recordTime']
        string = todaystr + " " + string
        timelist2.append(string)
    df = pd.DataFrame()        
    df['timelist'] = timelist2
    df['value'] = anvalue2
    df = df.set_index('timelist')
    
    return df

def insert_into_db(today,totlist):
    con = psycopg2.connect(database="SLDCREP", user="postgres", password="createdon16082018", host="192.168.168.125", port="5432")
    print("Database opened successfully")  
    cur = con.cursor() 
    cur.execute("select RTU_POINT_RECORD from sldcsch.rtu_point_real_fcast_data where RTU_DATA_DATE='"+str(today)+"' and rtu_point_id='13008'")
    rfrows = cur.fetchall()
    if len(rfrows) > 0:
        cur.execute("update sldcsch.rtu_point_real_fcast_data set rtu_point_record='"+str(totlist).replace('\'','\"')+"' where rtu_point_id='13008' and rtu_data_date='"+str(today)+"'")
        print("updated record")
    else:
        cur.execute("insert into sldcsch.rtu_point_real_fcast_data (rtu_point_id,rtu_data_date,rtu_point_record) values('13008','"+str(today)+"','"+str(totlist).replace('\'','\"')+"')")
        print("inserted record")
    con.commit()
    
def append_pred(prediction,today):
    con = psycopg2.connect(database="SLDCREP", user="postgres", password="createdon16082018", host="192.168.168.125", port="5432")
    print("Database opened successfully")  
    cur = con.cursor() 
    cur.execute("select RTU_POINT_RECORD from sldcsch.rtu_point_real_fcast_data where RTU_DATA_DATE='"+str(today)+"' and rtu_point_id='13008'")
    rfrows = cur.fetchall()
    existdatalist=[]
    for row in rfrows:
        existdatalist.append(str(row[0]))
    existdatalist = ast.literal_eval(existdatalist[0])
    print(existdatalist)
    for x in prediction:
        existdatalist.append(x)
    
    return existdatalist

