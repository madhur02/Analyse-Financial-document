# -*- coding: utf-8 -*-
"""
Created on Mon Oct  1 11:30:12 2018

@author: J554696
"""
import pandas as pd
import numpy as np
import configparser
import requests
import re ,os
import glob
import errno


def read_configfile(configfile="config.ini"):
    Config = configparser.ConfigParser()
    Config.read(configfile)
    username = Config.get('SectionOne','username')
    password = Config.get('SectionOne' ,'password')
    input_path = Config.get('SectionTwo' ,'input_path')
    output_path = Config.get('SectionTwo' ,'output_path')
    return input_path,output_path

def read_csv_file(fileName):
    sentence_list = []
    content  = open(fileName,"r",encoding = "UTF-8").readlines()
    content = " ".join(content)
    #for line in content[:]:
    #line = line.strip("\n").strip()
    content = content.replace('\n',' ').replace('\t',' ')
    content = re.sub( '\s+', ' ', content ).strip()
    punctuation_character = '"#%&\'()*+,-/<=>[\\]^_`{|}~'
    translator = str.maketrans('', '',punctuation_character)
    content = content.translate(translator)
    sent_list = sent_tokenize(content)

    sentence_list +=sent_list
    return sentence_list

def main_function():
    input_path,output_path  = read_configfile()
    all_files= os.listdir(input_path)
    #print(all_files)
    count = 1
    for filename in all_files:
        companyName = filename.split("__")[0]
        print('Processing ::',str(count)+"/",str(len(all_files)))
        count += 1

        print('Working on file::',filename)
        sheet_content = pd.read_excel(os.path.join(path,filename),sheet_name = 'Sheet1')
        #data = preprocessing_data(sheet_content)
        
        



path = 'C:\\Users\\J554696\\Desktop\\files\\*.txt'

def read_all_text_files(path):
    
    files = glob.glob(path)
    for name in files:
        print(" Found {} file in folder ::.format(name)")
        try:
            with open(name,"r",encoding = "UTF-8") as f:
                 for line in f:
                     split = line.split()
                     if split:
                        print(line.split())
        except IOError as exc: #Not sure what error this is
            if exc.errno != errno.EISDIR:
                raise
read_all_text_files(path)           