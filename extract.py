# -*- coding: utf-8 -*-
#!usr/bin/python3
"""
Created on Wed Apr 04 15:19:39 2018
@author: J554696
principal Financial group
"""

import sys
from importlib import reload
reload(sys)
#sys.setdefaultencoding('utf8')
import warnings
warnings.filterwarnings('ignore')
from bs4 import BeautifulSoup
import pandas as pd
import requests
import re ,os
import numpy as np
import xlsxwriter
from data_preprocessing import data_preprocessing
import configparser
import bs4
from extract_Metadata_store import metadata_handler


def read_configfile(configfile="config.ini"):
    Config = configparser.ConfigParser()
    Config.read(configfile)
    username = Config.get('SectionOne','username')
    password = Config.get('SectionOne' ,'password')
    urls_10K = Config.get('SectionTwo' ,'input_urlpath')
    output_path = Config.get('SectionTwo' ,'output_path')
    return urls_10K ,username , password,output_path


def get_url_data(url_link,uid,upassword):
    """
    Pass Input as a html url link and get html data
    @@ function takes input as url and return content of that file.
    """
    prin_px = "https://" + uid + ":" + upassword + "@pfgproxy.principal.com:80"
    r = requests.get(url_link, proxies={"https":prin_px})
    #content = r.content.lower()
    content = r.content
    return content

def html_file_read():
    """
    pass statics file of html and get html data
    """
    with open("C:/Users/G753903/Downloads/TopicModeling/Document.html" ,'r') as html_content:
        data = html_content.read()
    return data

def get_soup(doc):
    """
    @@ function take as input of html content
    return type as a soup...
    """
    soup = BeautifulSoup(doc, 'html.parser')
    return soup

def split_pages(soup):
    """
    @@ function take inputs as html soup
    and return as list of all splitted pages..
	"""
    file_buffers = soup.prettify().split("\n")
    all_pages = []
    page      = []
    for line in file_buffers:
        line = str(line)
        line1 = line
        if not line: continue
        if line.find("page-break-after:always")!= -1 or line.find("page-break-before: always")!= -1 or line.find("page-break-before") != -1:
            #print line
            page.append(line)
            all_pages.append(" ".join(page[:]))
            page = []
            page_content = []
        else:
            page.append(line)

    return all_pages

def check_toc(all_pages,str1,str2):

    all_pages = "\n".join(all_pages[1:5])
    table_of_content = BeautifulSoup(all_pages, 'html.parser')
    tables = table_of_content.findAll( "table")
    content_table = []

    for table in tables:
        all_rows = table.findAll("tr")
        for rows in all_rows:
            row = []
            columns = rows.find_all('td')
            for column in columns:
                txt = str(column.get_text().strip()).lower()
                txt = re.sub( '\s+', ' ', txt ).strip()
                row.append(txt)

            content_table.append(row)

    df = pd.DataFrame(content_table)
    #print(df)
    #print ("str1:::::" , str1,'\n')
    #print ("str1:::::" , str2,'\n')
    try:
        get_start_pageindex = df[df.apply(lambda row: row.astype(str).str.contains(str1).any(), axis=1) == True]
        get_end_pageindex = df[df.apply(lambda row: row.astype(str).str.contains(str2).any(), axis=1) == True]
        start_pageindex_list   =   get_start_pageindex.values.tolist()[0]
        end_pageindex_list     = get_end_pageindex.values.tolist()[0]
        page_start = int([ele for ele in start_pageindex_list if ele][-1]) -1
        page_end = int([ele for ele in end_pageindex_list  if ele][-1])

    except:
        page_start = 0
        page_end   = 0
    return page_start , page_end


def preprocessing_splited_html(splited_soup):
    """
    @@ function takes input as a soup and remove all tables and images
	"""
    [table.decompose() for table in splited_soup.findAll("table")]
    [img.decompose() for img in splited_soup.findAll("img")]
    return splited_soup

def read_csv_file(file_path):
    """
    @@ function takes input as a csv file and return as dataframe
    """
    df = pd.read_csv(file_path)
    return df

def mainHandler(str1,str2):
    """
    @@ function as a main handler take input as a csv file and matching strings
    return as content of betweens these two matching...
    """
    file_path,user_name, password,output_path = read_configfile()
    frames = []
    extracted_content = []
    df = read_csv_file(file_path)
    print('This is the data frame ::::::')
    print(df.head())
    print('***'*20)
    for index ,row in df.iterrows():
        #print ("Processing :%s/%s" %(str(index),str(len(df)-1)))
        try:
            """
            html Url Handler...
            """
            url_link = row["URL-Links"]
            html_content = get_url_data(url_link,user_name,password)
            soup = get_soup(html_content)
            all_pages  = split_pages(soup)

            str1 = str1.lower()
            str2 = str2.lower()

            page_index = check_toc(all_pages,str1,str2)
            page_start = page_index[0]
            page_end = page_index[1]
            if (page_start and page_end) in [0]:       # Page start  and end index is not found ..
                continue

            splited_page = "\n".join(all_pages[page_start:page_end])
            splited_soup = BeautifulSoup(splited_page, 'html.parser')
            splited_soup = preprocessing_splited_html(splited_soup)
            para = splited_soup.get_text()

            para = para.replace('\n',' ').replace('\t',' ')
            para = re.sub( '\s+', ' ', para ).strip()

            """
            Text Url Links Handler...
            """
            txt_link = row["txt-URL-Links"]
            print ("txt link----->"+str(txt_link))
            txt_content = get_url_data(txt_link,user_name,password)
            header_dict = metadata_handler(txt_content)

            companyName = header_dict.get("company conformed name")
            uniqueId = header_dict.get("uniqueId")
            preprocess_df  = data_preprocessing(para ,url_link,companyName)

            file_df = pd.DataFrame(preprocess_df)
            print (output_path+companyName+'__'+uniqueId+'__'+url_link.split('/')[-1].split('.')[0]+'.csv')
            file_df.to_csv(output_path+companyName+'__'+uniqueId+'__'+url_link.split('/')[-1].split('.')[0]+'.csv')
            
            frames.append(preprocess_df)

        except:
            pass
    result = pd.concat(frames)
    result.to_csv(os.path.join(output_path,"all_content.csv"))

if __name__== "__main__":
    str1 = "Financial Condition and Results of Operation"
    str2 = "Financial Statements and Supplementary"
    mainHandler(str1,str2)
