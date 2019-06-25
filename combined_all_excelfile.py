# -*- coding: utf-8 -*-
# encoding: utf-8
#!usr/bin/python3



import os
import pandas as pd
import sys

all_dataFrame = []
path = r"C:\Users\G753903\Downloads\Topic_Modelling_18072018\v2.1  20180718\Phrase"
all_files = os.listdir(path)
for file in all_files[:100]:
    try:
        file_name = os.path.join(path,file)
        print (file_name)
        df = pd.read_excel(file_name)
        df.dropna(subset=['Company'], inplace=True)
        all_dataFrame.append(df)
    except:
        pass
print (all_dataFrame)
all_dataFrame = pd.concat(all_dataFrame)
#all_df = pd.DataFrame(all_dataFrame)
all_dataFrame.to_csv("all_dataFrame.csv")
