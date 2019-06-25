# -*- coding: utf-8 -*-
#!usr/bin/python3
import pandas as pd
import requests
from bs4 import BeautifulSoup
import configparser

def read_configfile(configfile="config.ini"):
    """
    @@ function take input as a config file
    and read config parameter from the file..
    """
    Config = configparser.ConfigParser()
    Config.read(configfile)
    username = Config.get('SectionOne','username')
    password = Config.get('SectionOne' ,'password')
    input_path = Config.get('SectionTwo' ,'input_path')
    return input_path ,username , password

def get_all_cik(csv_file):
    """
    @@@ function take input as csv file and read
    all cik no from that csv file
    """
    cik_series = pd.read_csv(csv_file)['CIK']
    return cik_series

def get_url_content(url,uid,upassword):
    """
    Pass input as a HTML url
    output as a content of that url.
    """
    prin_px = "https://" + uid + ":" + upassword + "@pfgproxy.principal.com:80"
    r = requests.get(url,proxies={"https":prin_px})
    content = r.content
    return content

def get_soup(doc):
    """
    @@@ function take input as html and convert
    into soup object
    """
    soup = BeautifulSoup(doc, 'html.parser')
    return soup

def identified_table_extracted_annual_filing(html_content,attribute):
    """
    @@@ function take input as html_content and properties
    find 10-K and urls (first label)
    """
    soup = get_soup(html_content)
    table = soup.findAll("table",attribute)[0]
    rows  = table.findAll('tr')
    annual_filing_10k = []
    for row in rows:
        if row.findAll('td'):
            filings,format,description,filing_date,film_no = row.findAll('td')
            filings = filings.get_text().lower()
            if filings in ['10-k','form 10-k']:
                url_10k ="https://www.sec.gov"+format.find('a').get('href')
                annual_filing_10k.append(url_10k)
    return annual_filing_10k

def identified_table_extracted_annual_filing_new(html_content,attribute):
    """
    @@@ function take input as html_content and properties
    find 10-K and urls (second label)
    """
    soup = get_soup(html_content)
    table = soup.findAll("table",attribute)[0]
    rows  = table.findAll('tr')
    annual_filing_10k = []
    annual_filing_txt_10K = []
    for row in rows:
        if row.findAll('td'):
            s_no,description,document,type,size = row.findAll('td')
            filings = description.get_text().lower()
            if filings.find('10-k')!= -1 or filings.find('form 10-k') != -1:
                url_10k ="https://www.sec.gov"+document.find('a').get('href')
                if url_10k.endswith('.html') or url_10k.endswith('.htm'):
                    annual_filing_10k.append(url_10k)
            elif filings in ['complete submission text file']:
                    complete_submission_txt_file ="https://www.sec.gov"+document.find('a').get('href')
                    annual_filing_10k.append(complete_submission_txt_file)
    #print (annual_filing_10k)
    #print ("------------------Garg ------------------")
    #sys.exit()
    if len(annual_filing_10k) < 2:
        return []
    return annual_filing_10k

def get_10K_document_link(annual_filing_10k,username,password):
    """
    @@ function take input as list of all first label 10-K and identified
    main 10-K urls
    """
    all_10K_url_txt_urls = []
    for filing_document_url in annual_filing_10k:
        html_content = get_url_content(filing_document_url,username,password)
        attr = {"class":"tableFile"}
        tmp = identified_table_extracted_annual_filing_new(html_content,attr)
        #all_10K_urls += tmp
        if tmp:
            all_10K_url_txt_urls.append(tmp)
    #print (all_10K_urls)
    return all_10K_url_txt_urls


def main_cik_handler():
    """
    @@@ function take input as csv file and output is all
    10-K document of that CIK no.
    """
    csv_file ,username , password = read_configfile()
    all_cik_no = get_all_cik(csv_file)
    all_cik_map = {}
    all_data = []
    all_urls_links = {"10-URL-Links":[],"txt-URL-Links":[]}
    for cik_no in all_cik_no:
        cik_no = int(str(cik_no).strip())
        """
        Pass CIK no in below url and get all 10-K filing (first lavel)
        """
        url = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=%s&type=10-K&dateb=&owner=exclude&count=100" %(str(cik_no).strip())
        html_content = get_url_content(url,username,password)
        attr = {"class":"tableFile2"}
        annual_filing_10k = identified_table_extracted_annual_filing(html_content,attr)
        all_10K_urls = get_10K_document_link(annual_filing_10k,username,password)

        #all_10K_urls = all_10K_urls[:1]
        all_cik_map[cik_no] = all_10K_urls
        #print ("Hey Rahul I am Here.....")
        #if (all_10K_urls):
            #print (all_10K_urls[0])
        #continue
        #sys.exit()
        if (all_10K_urls):
            all_data += [all_10K_urls[0]]

    print ("all_urls_links::::" ,all_data)
    #url_df = pd.DataFrame(all_urls_links)
    url_df = pd.DataFrame(all_data ,columns= ["URL-Links","txt-URL-Links"])
    url_df.to_csv("Extracted_Annual_filing.csv")

if __name__== "__main__":
    #csv_file = 'CIK_file.csv'
    #main_cik_handler(csv_file)
    main_cik_handler()
