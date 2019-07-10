# -*- coding: utf-8 -*-
"""
Created on Mon Jul  8 20:36:39 2019

@author: Joy
"""
from datetime import timedelta
import pandas as pd
import json

def create_date_list(today):
    ddtttf=today.strftime("%Y-%m-%d")
    weekd=today.weekday() 
    print("Weekday",weekd)    
    previousday = today + timedelta(days=-1)
    previousdayf=previousday.strftime("%Y-%m-%d")    
    print ("Previous Day",previousdayf)
    dayfirst = previousday + timedelta(days=-366)    
    print ("Data between Start Date",dayfirst.strftime("%Y-%m-%d"),"End Date",previousdayf)
    delta=previousday-dayfirst
    dates_list = []
    for i in range(delta.days + 1):
        mydate=dayfirst + timedelta(i)
        weekdayvalue=mydate.weekday()
        if(weekdayvalue==weekd ):
            stringDate=mydate.strftime("%Y-%m-%d")
            dates_list.append(stringDate)
    dates_list.append(previousdayf)    
    dates_list.append(ddtttf)    
    
    return dates_list

def convert_date_list_to_string(dates_list):
    ss=''
    for i in dates_list:
        ss=ss+"'"+i+"',"
    strql=ss[:len(ss)-1]
    
    return strql

def create_timelist(interval,today):
    timelist=[]

    intvalue=0
    for ii in range(0,720):
        nine_hours_from_now = today +timedelta(minutes=intvalue)
        timelist.append(nine_hours_from_now.strftime("%H:%M"))
        intvalue=intvalue+interval
    return timelist   

def create_dataarray_from_dataframe(df,timelist,today):
    previousdaydataset=[]
    dataarray=[]
    previousday = today + timedelta(days=-1)
    previousdayf=previousday.strftime("%Y-%m-%d")
    
    for index, row in df.iterrows():
        recorddate=row['date']
       # print(recorddate)
        #valuedddd=row['rtudata']
        datastore = json.loads(str(row['rtudata']))
        #print(recorddate,"data--->",datastore)
        
        it=0
        tempid=0
        print(recorddate,previousdayf)
        if recorddate==previousdayf:
            previousdaydataset.append(datastore)
            print("previous day",recorddate)
        else:
            for timettt in timelist:
                ittemp=0
                tempmw=0
                datavalues={}
                #print(timettt)
                for timemm in datastore:
                    if timemm['recordTime']==timettt:
                        datavalues['recordTime']=recorddate+' '+timemm['recordTime']
                        tempmw=timemm['recordValue']
                        datavalues['recordValue']=tempmw
                        dataarray.append(datavalues)
                        #print("I am inside")
                        ittemp=1
                if ittemp==1:
                    it=it+1
            
    
    return dataarray

def remove_outliers(dataarray):
    mydf = pd.DataFrame()
    timelist = []
    vallist = []
    for  x in dataarray:
        if(x['recordValue']>12000):
            timelist.append(x['recordTime'])
            vallist.append(7958.89)
        else:
            timelist.append(x['recordTime'])
            vallist.append(x['recordValue'])
                
    mydf['timelist'] = timelist
    mydf['value'] = vallist            
    mydf.timelist = pd.to_datetime(mydf.timelist,format = '%Y-%m-%d %H:%M')            
    mydf = mydf.set_index('timelist')
    
    return mydf

def datetime_range(start, end, delta):
    current = start
    while current < end:
        yield current
        current += delta

