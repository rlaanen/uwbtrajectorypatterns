#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler

def compare_trajectories(uwb, new_uwb):
    #table = patches.Rectangle((1988, 1656), 1200, 600, linewidth=1, edgecolor='g', facecolor='none')
    fig, (ax1, ax2) = plt.subplots(1,2, figsize = (12,5))

    ax1.plot(uwb.loc[:, "loc(x)"], uwb.loc[:, "loc(y)"], '-o')
    ax2.plot(new_uwb.loc[:, "loc(x)"], new_uwb.loc[:, "loc(y)"], '-o')
    ax1.set_title("Visualization of original trajectory")
    ax1.set_xlabel("x-coordinate (mm)")
    ax1.set_ylabel("y-coordinate (mm)")
    ax2.set_title("Visualization of normalized trajectory")
    ax2.set_xlabel("x-coordinate (mm)")
    ax2.set_ylabel("y-coordinate (mm)")
    plt.tight_layout()
    plt.show()
    
def min_max_normalization(data):
    X = data.iloc[:,:-1]
    y = data.iloc[:, -1]
    scaler = MinMaxScaler()
    #scale the features in X
    X = pd.DataFrame(scaler.fit_transform(X), index=X.index, columns=X.columns)
    return X, y

def compute_trajectory_features(data):

    feature_names = ["_min", "_max", "_mean", "_median", "_std", "_q_10", "_q_25", "_q_50", "_q_75", "_q_90"]
    col_names = []
    trajectory_features = []
    for col_name in list(data.columns[:-1]):
        #calculate the min value
        trajectory_features.append(data.loc[:, col_name].min())
        col_names.append(col_name+feature_names[0])
        
        #calculate the max value
        trajectory_features.append(data.loc[:, col_name].max())
        col_names.append(col_name+feature_names[1])
        
        #calculate the mean
        trajectory_features.append(data.loc[:, col_name].mean())
        col_names.append(col_name+feature_names[2])
        
        #calculate the median
        trajectory_features.append(data.loc[:, col_name].median())
        col_names.append(col_name+feature_names[3])
        
        #calculate the standard deviation
        trajectory_features.append(data.loc[:, col_name].std())
        col_names.append(col_name+feature_names[4])
        
        #calculate several percentiles (e.g. 10, 25, 50, 75 and 90)
        trajectory_features.append(data.loc[:, col_name].quantile(0.10))
        col_names.append(col_name+feature_names[5])
        trajectory_features.append(data.loc[:, col_name].quantile(0.25))
        col_names.append(col_name+feature_names[6])
        trajectory_features.append(data.loc[:, col_name].quantile(0.50))
        col_names.append(col_name+feature_names[7])
        trajectory_features.append(data.loc[:, col_name].quantile(0.75))
        col_names.append(col_name+feature_names[8])
        trajectory_features.append(data.loc[:, col_name].quantile(0.90))
        col_names.append(col_name+feature_names[9])
        
    #add label
    trajectory_features.append(str(data.loc[0, "label"]))
    col_names.append("label")
    
    #make a new dataframe with the trajectory features
    trajectory_features_df = pd.DataFrame(trajectory_features, index = col_names).T
    return trajectory_features_df

def compute_point_features(uwb_inst):
    
    uwb_inst.loc[:,"loc(x)_diff"] = uwb_inst.loc[:,"loc(x)"].diff(periods=1)
    uwb_inst.loc[:,"loc(y)_diff"] = uwb_inst.loc[:,"loc(y)"].diff(periods=1)
    #calculate the angle between two points, given their x and y coordinates
    uwb_inst.loc[:,"angle"] = np.arctan2(uwb_inst.loc[:,"loc(y)_diff"], uwb_inst.loc[:,"loc(x)_diff"])
    #create a new pandas dataframe with the point features
    new_uwb_inst = uwb_inst[["angle","label"]]
    return new_uwb_inst

def loc_normalization(uwb_inst):
    radius = 600 #maximum distance between two points
    max_time_diff = 10 #maximum time difference between two points
    new_points = [] #create an empty array which holds the new points
    
    A = np.array((uwb_inst.loc[0,"loc(x)"], uwb_inst.loc[0,"loc(y)"],0))
    new_points.append(A)
    
    while(A[2] < uwb_inst.shape[0]-1):
        best_distance = 0
        #check every remaining point
        for i in range(A[2]+1, uwb_inst.shape[0]):
            diff, time_diff = 0,0
            B = np.array((uwb_inst.loc[i,"loc(x)"], uwb_inst.loc[i,"loc(y)"],i))
            #calculate euclidean distance between point A and B
            distance = np.linalg.norm(A-B)
            #calculate the difference
            diff = radius - distance
            #calculate the time difference
            time_diff = uwb_inst.loc[i,"timestamp"] - uwb_inst.loc[A[2], "timestamp"]
            #if point B lies outside the circle or the difference in time
            if(i==A[2]+1): #is bigger than the maximum allowed difference
                if((diff < 0) or (time_diff > max_time_diff)):
                    #pick point B as the next point
                    C = B
                    break;
                    
            if(diff < 0):
                break;
            #check conditions for next best point
            if((diff >= 0) and (distance>best_distance) and (time_diff < max_time_diff)):
                best_distance = distance
                C = B
        #save next point in array
        new_points.append(C)
        A = C
    #create a new dataframe from the saved new_points array
    new_uwb_inst = pd.DataFrame(new_points, columns = ["loc(x)", "loc(y)", "idx"])
    new_uwb_inst["label"] = uwb_inst.loc[:,"label"]
    compare_trajectories(uwb_inst, new_uwb_inst)
    return new_uwb_inst
                
def preprocess(uwb_list):
    data = pd.DataFrame() #create an empty dataframe for instances
    
    for uwb_inst in uwb_list: #for every instance do:
        uwb_inst = uwb_inst.reset_index()
        #normalize the location (make data time-invariant)
        uwb_inst = loc_normalization(uwb_inst)
        #compute the point features
        uwb_inst = compute_point_features(uwb_inst)
        #compute the trajectory features
        uwb_inst = compute_trajectory_features(uwb_inst)
        #concatenate the new instance to the data set
        data = pd.concat([data, uwb_inst], ignore_index = True)
    #normalize the data set
    X, y = min_max_normalization(data)
    return X,y

def main():
    split = 5 #number of instances we would like to create from splitting original instance
    
    #parser = argparse.ArgumentParser()
    #parser.add_argument('--directory', type=str, required='test1.csv')
    #args = parser.parse_args()
    #open the data file
    #path = args.inputfile
    path = "data/session2/02_01_01_02_01_df.csv"
    
    #read the data file
    uwb_data = pd.read_csv(path)
    #select active tag
    uwb_data = uwb_data[uwb_data["tagId"]==26660].copy(deep=True)
    uwb_data = uwb_data.reset_index()
    #split the data set into instances of 1 minute
    uwb_list = np.array_split(uwb_data, split)
    #preprocess the data
    X, y = preprocess(uwb_list)
    
if __name__ == "__main__":
    main()

