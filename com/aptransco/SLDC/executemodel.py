# -*- coding: utf-8 -*-
"""
Created on Mon Jul  8 21:27:36 2019

@author: Joy
"""
import util
import dbdao
import modelutil
from datetime import datetime
import numpy as np

today = datetime.today()
print("Today",today)

dates_list = util.create_date_list(today)

strql = util.convert_date_list_to_string(dates_list)

interval = 2
timelist = util.create_timelist(interval,today)

df = dbdao.retrieve_database(strql)

dataarray = util.create_dataarray_from_dataframe(df,timelist,today)

mydf = util.remove_outliers(dataarray)

training_set = mydf.values

training_set_scaled = modelutil.scale_training_set(training_set)

X_train, y_train = modelutil.create_timesteps(training_set_scaled)

X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))

regressor = modelutil.buid_model(X_train)

regressor.fit(X_train, y_train, epochs = 100, batch_size = 32)

dbdao.save_model_in_database(regressor)