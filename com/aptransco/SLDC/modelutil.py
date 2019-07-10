# -*- coding: utf-8 -*-
"""
Created on Mon Jul  8 22:22:33 2019

@author: Joy
"""
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense,Dropout
from tensorflow.keras.layers import LSTM
from sklearn.preprocessing import MinMaxScaler
import numpy as np
from datetime import datetime,timedelta
import util


def scale_training_set(training_set):
    sc = MinMaxScaler(feature_range = (0, 1))
    training_set_scaled = sc.fit_transform(training_set)
    
    return training_set_scaled

def create_timesteps(training_set_scaled):
    X_train = []
    y_train = []
    for i in range(60, len(training_set_scaled)):
        X_train.append(training_set_scaled[i-60:i, 0])
        y_train.append(training_set_scaled[i, 0])
        X_train, y_train = np.array(X_train), np.array(y_train)
    return X_train,y_train

def buid_model(X_train):
    regressor = Sequential()

    # Adding the first LSTM layer and some Dropout regularisation
    regressor.add(LSTM(units = 50, return_sequences = True, input_shape = (X_train.shape[1], 1)))
    regressor.add(Dropout(0.2))
    
    # Adding a second LSTM layer and some Dropout regularisation
    regressor.add(LSTM(units = 50, return_sequences = True))
    regressor.add(Dropout(0.2))
    
    # Adding a third LSTM layer and some Dropout regularisation
    regressor.add(LSTM(units = 50, return_sequences = True))
    regressor.add(Dropout(0.2))
    
    # Adding a fourth LSTM layer and some Dropout regularisation
    regressor.add(LSTM(units = 50))
    regressor.add(Dropout(0.2))
    
    # Adding the output layer
    regressor.add(Dense(units = 1))
    
    # Compiling the RNN
    regressor.compile(optimizer = 'adam', loss = 'mean_squared_error')

    return regressor

def make_pred(x_input,model):
    sc = MinMaxScaler(feature_range = (0, 1))
    dataset_total = x_input.copy() 
    n_future_preds = 30
    preds_moving = []
    moving_test_window = dataset_total[-60:]
    moving_test_window = sc.fit_transform(moving_test_window)
    moving_test_window = np.array(moving_test_window)
    moving_test_window = moving_test_window.reshape(1,60,1)
    for i in range(n_future_preds):
        preds_one_step = model.predict(moving_test_window)
        preds_moving.append(preds_one_step[0,0])
        preds_one_step = preds_one_step.reshape(1,1,1)
        moving_test_window = np.concatenate((moving_test_window[:,1:,:],preds_one_step),axis = 1)
    
    myarr = np.array(preds_moving)
    myarr = myarr.reshape(-1,1)
    ans = sc.inverse_transform(myarr)
    
    return ans

def add_time_to_pred(ans):
    t3 = datetime.now() 
    date_time_str1 = '2018-06-29 '+str(t3.hour)+':00:00'  
    t4 = datetime.strptime(date_time_str1, '%Y-%m-%d %H:%M:%S')
    minlist2 = [dt.strftime('%H:%M') for dt in 
       util.datetime_range(t4,t4+timedelta(hours = 1) ,timedelta(minutes=2))]

    
    prediction = []
    for i in range(len(ans)):
        predictarray = {}
        predictarray['recordTime'] = minlist2[i]
        predictarray['recordValue'] = ans[i][0]
        prediction.append(predictarray)
    
    print('prediction at '+str(t3.hour)+':'+str(prediction))
    return prediction

def train_data(training_set,model):
    sc = MinMaxScaler(feature_range = (0, 1))
    training_set_scaled = sc.fit_transform(training_set)
    X_train = []
    y_train = []
    for i in range(60, len(training_set_scaled)):
        X_train.append(training_set_scaled[i-60:i, 0])
        y_train.append(training_set_scaled[i, 0])
    X_train, y_train = np.array(X_train), np.array(y_train)
    X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))
    model.compile(optimizer = 'adam', loss = 'mean_squared_error')
    model.fit(X_train, y_train, epochs = 30, batch_size = 32)

    return model

    