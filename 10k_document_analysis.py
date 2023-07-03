# -*- coding: utf-8 -*-
#!usr/bin/python3

import sys
from importlib import reload
reload(sys)
import warnings
warnings.filterwarnings('ignore')
from bs4 import BeautifulSoup
import requests
import numpy as np
from nltk.tokenize import sent_tokenize
import spacy
nlp = spacy.load('en_core_web_sm')
from duckling import DucklingWrapper
duckling_wrapper = DucklingWrapper()


def get_url_data(url_link):
    """
    Pass Input as a html url link and get html data
    @@ function takes input as url and return content of that file.
    """
    uid = ""
    upassword = ""
    prin_px = "https://" + uid + ":" + upassword + "xyz.com:80"
    r = requests.get(url_link, proxies={"https":prin_px})
    content = r.content.lower()
    return content

def get_soup(doc):
    """
    @@ function take as input of html content
    return type as a soup...
    """
    soup = BeautifulSoup(doc, 'html.parser')
    return soup

def entity_Extractor(content1,content2):
    dict1 = {}
    dict2 = {}
    for sent1 in content1[:]:
        replace_sent1 = ''
        replace_sent1 = sent1
        org_sent1 = ''
        org_sent1 = sent1
        replace_sent1 = replace_sent1.replace(",",'')

        tmp1 = []
        parseMoney1 = duckling_wrapper.parse_money(sent1)

        if parseMoney1:
            for i in parseMoney1:
                text = i['text']
                unit = i.get('value',{}).get('unit',None)
                start = str(i.get('start',''))
                end = str(i.get('end',''))

                if (unit == None):
                    continue
                replace_sent1 = replace_sent1.replace(text,'APPLE').strip()
                tmp1.append(text)

        doc = nlp(replace_sent1)
        for ent in doc.ents:
            text1       = ent.text
            label       = ent.label_
            start_ind   = ent.start_char
            end_ind   = ent.end_char
            if text1 in ['_' ,""," "," "] or label in ["ORG"]:
                continue
            replace_sent1 = replace_sent1.replace(text1,'APPLE').strip()
            tmp1.append(text1)

        org_sent1 = ''
        dict1[replace_sent1] = [tmp1 ,sent1,org_sent1]

    for sent2 in content2[:]:
        tmp2 = []
        replace_sent2 = ''
        replace_sent2 = sent2
        org_sent2 = ''
        org_sent2 = sent2
        replace_sent2 = replace_sent2.replace(",",'')
        #parseTime2 = duckling_wrapper.parse_time(sent2)
        parseMoney2 = duckling_wrapper.parse_money(sent2)
        if parseMoney2:
            for i in parseMoney2:
                text = i['text']
                unit = i.get('value',{}).get('unit',None)
                start = str(i.get('start',''))
                end = str(i.get('end',''))

                if (unit == None):
                    continue
                replace_sent2 = replace_sent2.replace(text,'APPLE').strip()
                org_sent2  = org_sent2.replace(text,'<span style = "color:FF3393">'+text+ '</span>')
                tmp2.append(text)

        doc = nlp(replace_sent2)

        for ent in doc.ents:

            text2 = ent.text
            label       = ent.label_
            start_ind   = ent.start_char
            end_ind   = ent.end_char

            if text2 in ['_' ,""," "," "] or label in ["ORG"]:
                    continue
            replace_sent2 = replace_sent2.replace(text2,'APPLE').strip()
            tmp2.append(text2)

        org_sent2 = ''
        dict2[replace_sent2] = [tmp2,sent2,org_sent2]

    return dict1 , dict2


def file_Comprator(file_path1,file_path2):
    """
    @@ function as a main handler take input as a csv file and matching strings
    return as content of betweens these two matching...
    """

    ## File Content 1 ####
    html_content1 = get_url_data(file_path1)
    soup1 = get_soup(html_content1)
    content1 = soup1.prettify().split("\n")


    ## File Content 2 ####
    html_content2 = get_url_data(file_path2)
    soup2 = get_soup(html_content2)
    content2 = soup2.prettify().split("\n")



    matching_count = 0

    str1 = ''
    # Join the Corpus of the first file
    content1 = " ".join([BeautifulSoup(cont, 'html.parser').get_text().strip() for cont in content1
                    if BeautifulSoup(cont, 'html.parser').get_text().strip()])

    # Join the Corpus of the second file
    content2 = " ".join([BeautifulSoup(cont, 'html.parser').get_text().strip() for cont in content2
                    if BeautifulSoup(cont, 'html.parser').get_text().strip()])

    # Content split into sentences
    content1 = sent_tokenize(content1)

    # Content split into sentences
    content2 = sent_tokenize(content2)

    dict1,dict2 = entity_Extractor(content1,content2)

    content1 = list(dict1.keys())
    content2 = list(dict2.keys())

    i = 0
    main_str = '<html><body><div style="width:100%;height:100%;float:left;">'
    str1 += '<div style="width:100%;height:80%;float: left;">'
    str1 += '<table style="width:100%;height:98%;float:left;border:1px solid black;border-collapse: collapse;">'
    str1 += '<tr style="background-color:burlywood;color:white">'
    str1 += '<th style= "border: 1px solid black;">S no</th><th style= "border: 1px solid black;">Matching Index</th>'
    #str1 += '<th style= "border: 1px solid black;">S no</th>'
    str1 += '<th style= "border: 1px solid black;">Document1 (%s)</th>' %(file_path1)
    str1 += '<th style= "border: 1px solid black;">Document2 (%s)</th>'%(file_path2)
    str1 += '</tr>'

    new_index  = 1
    entity_match_count = 0
    plain_match_count = 0

    for index in range(0,len(content1)):
        try:
            data1 = content1[index]
            replace_string1 = data1
            list_of_replacer1 = dict1[data1][0]
            org_data1 = dict1[data1][1]
            heightled_text1 = dict1[data1][2]

        except:
            data1 = ''
            heightled_text1 = ''

        try:
            data2 = content2[index]
            replace_string2 = data2
            #list_of_replacer2 = dict2[data2][0]
            org_data2 = dict2[data2][1]
            heightled_text2 = dict2[data2][2]


        except:
            data2 = ''
            heightled_text2 = ''

        if data1 =='' and data2 == '':
            continue

        elif data1 in content2:
           
            match_ind = content2.index(data1)
            org_data2 = dict2[data1][1]
            list_of_replacer2 = dict2[data1][0]
            matching_count += 1
            if (i%2 == 0):
                str1 += '<tr style="background-color: #f1f1c1;">'
            else:
                str1 += '<tr">'

            str1 += '<td style= "border: 1px solid black;">%s</td>' %(str(new_index))
            str1 += '<td style= "border: 1px solid black;">%s</td>' %("--".join([str(index),str(match_ind)]))

            for entity_text1 in list_of_replacer1:
                if entity_text1 not in list_of_replacer2:
                    org_data1=  org_data1.replace(entity_text1,'<span style = "color:red;">'+entity_text1+ '</span>')

            for entity_text2 in list_of_replacer2:
                if entity_text2 not in list_of_replacer1:
                    org_data2=  org_data2.replace(entity_text2,'<span style = "color:red;">'+entity_text2+ '</span>')



            #str1 += '<td style= "border: 1px solid black;">%s</td>' %(heightled_text1)
            if ('<span style = "color:red;">' in org_data1 or '<span style = "color:red;">' in org_data2):
                str1 += '<td style= "border: 1px solid black;">%s</td>' %(org_data1)
                str1 += '<td style= "border: 1px solid black;">%s</td>' %(org_data2)
                entity_match_count += 1
            else:
                str1 += '<td style= "border: 1px solid black;">%s</td>' %(org_data1)
                str1 += '<td style= "border: 1px solid black;">%s</td>' %(org_data2)
                plain_match_count += 1
            #str1 += '<td style= "border: 1px solid black;">%s</td>' %(dict2[data1][2])
            #str1 +='<td style= "border: 1px solid black;">%s</td>'  %(heightled_text2)
            str1 += '</tr>'
            i += 1
            new_index += 1
        else:
            try:
                str1 += '<tr style="background-color:orange;">'
                str1 += '<td style= "border: 1px solid black;">%s</td>' %(index)
                str1 += '<td style= "border: 1px solid black;"> </td>' %()
                #str1 +='<td style= "border: 1px solid black;">%s</td>' %(heightled_text1)
                #str1 +='<td style= "border: 1px solid black;">%s</td>' %(heightled_text2)
                str1 +='<td style= "border: 1px solid black;">%s</td>' %(dict1[data1][2])
                str1 +='<td style= "border: 1px solid black;">%s</td>' %(dict1[data2][2])
                str1 += '</tr>'
            except:
                pass
            #pass

    str1 += '</table></div>'


    str2 = ''
    str2 += '<div style="width:100%;height:20%;float:left;">'
    str2 += '<table style="width:35%;height:70%;border:1px solid black;border-collapse: collapse;float: left;">'
    str2 += '<caption>10-K (Annual Filing Analysis..)</caption>'
    str2 += '<tr style="background-color: #f1f1c1;">'
    str2 += '<th style= "border: 1px solid black;">1</th>'
    str2 += '<th style= "border: 1px solid black;">Document1 Count</th>'
    str2 += '<td style= "border: 1px solid black;"> %s</td></tr>' %(str(len(content1)))

    str2 += '<tr><th style= "border: 1px solid black;">2</th>'
    str2 +='<th style= "border: 1px solid black;">Document2 Count</th>'
    str2 +='<td style= "border: 1px solid black;"> %s</td></tr>' %(str(len(content2)))

    str2 += '<tr style="background-color: #f1f1c1;"><th style= "border: 1px solid black;">3</th>'
    str2 += '<th style= "border: 1px solid black;"> Sentence Matching Count</th>'
    str2 += '<td style= "border: 1px solid black;"> %s </td</tr>' % (str(plain_match_count))

    str2 += '<tr style="background-color: #f1f1c1;"><th style= "border: 1px solid black;">4</th>'
    str2 += '<th style= "border: 1px solid black;"> Entity Matching Count</th>'
    str2 += '<td style= "border: 1px solid black;"> %s </td</tr>' % (str(entity_match_count))


    str2 += '<tr><th style= "border: 1px solid black;">5</th>'
    str2 += '<th style= "border: 1px solid black;">Unmatched Count</th>'
    str2 += '<td style= "border: 1px solid black;"> %s</td</tr>' %(str(len(content1)-(plain_match_count + entity_match_count)))
    str2 += '</table></div>'

    main_str += str2
    main_str += '<hr style="color: #8c8b8b;">'
    main_str += str1
    main_str += '</div></body></html>'

    with open("10K_Document_Analysis_Matching.html" ,"w",encoding='utf-8') as file_handler:
        file_handler.write(main_str)



if __name__== "__main__":
    #file_path1 = 'https://www.sec.gov/Archives/edgar/data/1326801/000132680115000006/fb-12312014x10k.htm'
    file_path1 = 'https://www.sec.gov/Archives/edgar/data/46195/000004619517000013/bankofhawaii10k12312016.htm'
    #file_path2 = 'https://www.sec.gov/Archives/edgar/data/1326 Sentence Matching 32680118000009/fb-12312017x10k.htm'
    file_path2 = 'https://www.sec.gov/Archives/edgar/data/46195/000004619518000025/bankofhawaii10k12312017.htm'
    #file_path2 = 'https://www.sec.gov/Archives/edgar/data/1326 Sentence Matching 32680118000009/fb-12312017x10k.htm'
    file_Comprator(file_path1,file_path2)
