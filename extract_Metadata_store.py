# -*- coding: utf-8 -*-
#!usr/bin/python3
import configparser
import sys
from pymongo import MongoClient

def read_configfile(configfile="config.ini"):
    """
    from config file read Mongodb host and port no
    """
    Config = configparser.ConfigParser()
    Config.read(configfile)
    hostname = Config.get('MongoSetting','host')
    port = Config.get('MongoSetting' ,'port')
    return hostname,port

def Connection(host,port):
    """
    @@ Mongo db collection
    """
    client = MongoClient(host,int(port))
    return client

def sec_txtFile_parsing(content):
    """
    @@ parse sec text file content
    and extracted header data
    """
    content = str(content)
    content = content.split("\\n")
    header_content = []
    header_flag    = False
    for line in content[:60]:
        line = line.lower()
        if line.find('<SEC-HEADER')!= -1 or line.find('<sec-header')!= -1:
            header_flag = True
            header_content.append(line)
        elif (line.find('</SEC-HEADER')!= -1 or line.find('</sec-header')!= -1) and header_flag:
            header_content.append(line)
            header_flag = False
        elif header_flag:
            header_content.append(line)
    header_dict = processing_header(header_content)
    return header_dict

def processing_header(header_content):
    """
    @@ header content convert into json
    """
    header_dict = {}
    for line in header_content:
        header_info = line.split(":")
        if header_info[0].endswith("hdr.sgml ") or header_info[0].endswith("hdr.sgml") :
            continue
        header_info = list(map(lambda x: x.replace("\\t","\t"),header_info))
        header_info = [header.strip("\t") for header in header_info if header]
        if len(header_info) >1:
            header_dict[header_info[0]] = "@@".join(header_info[1:])
    print (header_dict)
    header_dict["uniqueId"] = header_dict['accession number'].replace('-','')
    return header_dict

def delte_all_metaData():
    """
    @@ Remove all the document from database..
    """
    host,port = read_configfile()
    client = Connection(host,port)
    db = client['pymongo_test']
    posts = db.SEC_FILING
    x = posts.delete_many({})
    print(x.deleted_count, " documents deleted.")

def retrive_metaData():
    """
    @@ retrive metadata on the basis of uniqueId
    """
    host,port = read_configfile()
    print (host,port)

    client = Connection(host,port)
    db = client['pymongo_test']
    posts = db.SEC_FILING

    for post in posts.find({'uniqueId': '000071367618000032'}):
        print ("Hi i am Here::" ,post)

def store_metaData(client,header_data):
    """
    @@ store meta data into mongodb DB name is SEC_FILING
    """
    db = client['pymongo_test']
    posts = db.SEC_FILING
    result = posts.insert_one(header_data)
    if result:
        print('Succesfully Inserted: {0}'.format(result.inserted_id))
    else:
        print('Please Check Mongo Connection \n Mongo Connection Error..')

def metadata_handler(fileContent):
    """
    @@ input take as a fileContent extract header and store into mongodb..
    """
    header_dict = sec_txtFile_parsing(fileContent)
    host,port = read_configfile()
    client = Connection(host,port)
    store_metaData(client,header_dict)
    return header_dict
    #retrive_metaData(client)

if __name__== "__main__":
    retrive_metaData()
    print (delte_all_metaData())
    print (retrive_metaData())
    pass
