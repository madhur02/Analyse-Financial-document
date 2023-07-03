# -*- coding: utf-8 -*-
#!usr/bin/python3

import nltk
from nltk.util import ngrams
import pandas as pd
import json
import random

def phrase_matcing():
    word_tokenization = []
    matching_phrases = ["overview bioclinica provides integrated clinical research technology solutions",
    "current foreign exchange rate risk management policy",
    "operational data interchange among different software applications",
    "dollar spot exchange rate would result",
     "millionincrease investment work capital noncurrent operate assets",
     "chief executive officer effective",
     "lower effective tax rate",
     "stock price performance graph",
     "contents stock price performance",
     "feasible tax planning strategies",
     "generally accepted accounting principles",
     "leased back computer equipment",
     "lower effective tax rate",
     "included expenses resulting directly",
     "although experience movement selfpay patients medicaid payer mix prior",
     "population become eligible medicare coverage experience shift payer ",
     "average balance interestbearing deposit decrease",
     "offset decrease interest expense",
     "interest income expense net interest income fully tax equivalent basis year",
     "payer mix inclusive tscf base number transport follow exclude effect tscf private",
     "certain insurance company also increase reimbursement rat proportionately",
     "one primary goals ppaca decrease number uninsured americans",
     "payer mix inclusive tscf base number transport",
     "financial data read conjunction consolidate financial statements note",
     "undertake obligation update forwardlooking statements except require law",
     "actual result achieve may differ materially discuss forwardlooking statements",
     "develop comprehensive io portfolio drive follow ",
     "arrangement takeda include amendment refer arrangement",
     "second amend complaints assert claim decedent",
     "suit reassert allegations make claim",
     "pursuant settlement agreement subject court approval agree",
     "takeda decide reintroduce omontys highly uncertain eligible "

     ]
    for phrase in matching_phrases:
        word_list = nltk.word_tokenize(phrase)
        word_tokenization.append(word_list)
    return word_tokenization


def phraseMatching_Handler():

    map_dict = {}
    reverse_map_dict = {}
    word_tokenization = phrase_matcing()
    dataset = pd.read_csv(r"C:/Users/madhur/Downloads/Topic_Modelling_18072018/a13-1355_110k_demo_visulation.csv")

    for index , row in dataset.iterrows():
        companyName = row["Company"]
        phrase      = row["Phrases"]
        print ("phrase::::", phrase)
        phrase_word = nltk.word_tokenize(phrase)
        #print ("phrase_word:::", phrase_word)
        result = [list(filter(lambda x: x in phrase_word, sublist)) for sublist in word_tokenization]
        result  = [True for res in result if len(res) > 2]
        if True in result :
            if companyName not in map_dict:
                map_dict[companyName] = [phrase]
            else:
                map_dict[companyName].append(phrase)
            if phrase not in reverse_map_dict:
                reverse_map_dict[phrase] = [companyName]
            else:
                reverse_map_dict[phrase].append(companyName)

    print ("--"*50)
    print (map_dict)
    print ("--"*50)
    print (reverse_map_dict)
    print ("--"*50)

    convert_Company_format(map_dict)
    convert_Phrase_format(reverse_map_dict)

def convert_Company_format(map_dict):
    new_json = []

    new_json.append(['ID', 'Range', 'count', 'phrase'])
    index = 1
    for company , phrase in  map_dict.items():
        range = random.randint(1,101)
        count = len(phrase)
        new_json.append([company,range,count,"\n".join(phrase)])
        #range += 2
        #index += 1

    #print (new_json)
    with open('company_phrase.json', 'w') as outfile:
        json.dump(new_json, outfile)

def convert_Phrase_format(reverse_map_dict):
    new_json = []
    new_json.append(['ID', 'Range', 'count', 'Companies'])
    index = 1
    for phrase , companies in  reverse_map_dict.items():
        range = random.randint(1,3000)
        count = len(companies)
        phrase = " ".join(phrase.split(" ")[:3])
        print ("phrase:::",phrase)
        new_json.append([phrase,range,count,"\n".join(companies)])
    with open('phrase_Company.json', 'w') as outfile:
        json.dump(new_json, outfile)



if __name__== "__main__":
    phraseMatching_Handler()
