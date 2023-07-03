# -*- coding: utf-8 -*-
# encoding: utf-8
#!usr/bin/python3
"""
author: Madhur jain
"""

import sys
from importlib import reload
reload(sys)
#sys.setdefaultencoding('utf8')
import warnings
import re
warnings.filterwarnings('ignore')
import string
import nltk
from nltk import sent_tokenize
from nltk import word_tokenize
from nltk.corpus import stopwords
stop_words = set(stopwords.words('english'))
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import wordnet
from collections import Counter
#from ner_preprocessing import main_parse_Handler
import pandas as pd
lemmatizer = WordNetLemmatizer()
#from compound_Entity import get_compoundEntity


def sent_tokenization(para):
    """
    @@ function takes input as a paragraph and its return
    list of splitted Sentences
    """
    sent_tokenize_list = sent_tokenize(para)
    return sent_tokenize_list

def clean_txt(sent):
    """
    @@ function takes input as a sentence convert into lowercase
    and remove string punctuation from the sentence
    """
    sent = sent.lower() # Sent convert into lowercase
    punctuation_character = '!"#%&\'()*+,-./:<=>?[\\]^_`{|}~'
    #translator = str.maketrans('', '', string.punctuation)
    translator = str.maketrans('', '',punctuation_character)
    sent = sent.translate(translator)
           
    return sent

def get_pos_tagger(sent):
    """
    @@ function takes input as a sentence return list of tuple
    associated with part-of-speech tags
    """
    pos_tagger = nltk.pos_tag(word_tokenize(sent))
    return pos_tagger

def get_word_tokenization(sent):
    """
    @@ function takes input as a sent return word tokenizes form
    """
    word_tokenization = nltk.word_tokenize(sent)
    return word_tokenization



def get_lemma_form(filtered_word):
    """
    @@ function take input as a word and return its lemma form
    """
    filtered_word = filtered_word.replace("’",'')
    try:
        lemma_form = lemmatizer.lemmatize(filtered_word, wordnet.VERB)
    except:
        lemma_form = filtered_word
    return lemma_form

def remove_currency_unit(sent):
    """
    @@ function takes input as a list of tuple of word and pos tag filter out no
    """
    filtered_list = []
    for word, pos_tag in sent:
        if pos_tag == 'CD':
            continue
        filtered_list.append((word,pos_tag))
    return filtered_list



def data_preprocessing(para,url_link,company_name):

    entity_extracted_data = []

    #main_data = { 'Before-Cleaning-Sentences':[],'After-Cleaning-Sentences':[],'Sentence-Unique-Count':[],
                 #'Sentence-POS-Count':[] }
    main_data = { 'Before-Cleaning-Sentences':[],'After-Cleaning-Sentences':[],'Company':[]}


    #header_data = {'Content':[para] ,'url_link':[url_link],'before_cleanCorpus':[],'after_cleanCorpus':[],'total_corpus_size':0}

    sent_tokenize_list = sent_tokenization(para)

    para_lemmaform = []
    word_tokenize_para = []
    before_cleanCorpus = []
    after_cleanCorpus  = []
    word_pos_tokenize = []

    for sent in sent_tokenize_list:
        sent = str(sent)
        sent = re.sub("\d+\stable of contents","",sent.lower())
        sent = re.sub("\d+\stable of content","",sent.lower())
        
        if (len(sent.split()) < 6 or len(sent.split()) > 60) :
             continue
        
        word_tokenize_sent = []
        pos_tokenize_sent = []
        #print ('####'*20)
        #print ("Before Cleanning Sentence :::\n"+str([sent]))
        clean_sent = clean_txt(sent)
        #if sent != " ":
        main_data['Before-Cleaning-Sentences'].append(str(sent))
        
        '''
        try:
            # Remove all the entities from the sentence..
            sent1 = main_parse_Handler(clean_sent)
        except:
            sent1 = sent

        try:
            # find compound entity in the sentence...
            sent2 = get_compoundEntity(sent1)
        except:
            sent2 = sent1
        '''
        sent2 = clean_sent

        #entity_extracted_data.append([sent,sent1])

        '''Before Cleaning sentence'''
        #before_clean_word_tokenization = get_word_tokenization(sent)
        #before_cleanCorpus += before_clean_word_tokenization


        '''After Cleaning sentence '''
        pos_tagger = get_pos_tagger(sent2)

        #print pos_tagger

        ''' Remove all stop words after cleaning '''
        filtered_sentence = [w for w in pos_tagger if not w[0] in stop_words]
        after_clean_word_tokenization = [w[0] for w in filtered_sentence]
        after_cleanCorpus += (" ,".join(after_clean_word_tokenization))


        for filtered_word , pos_tag in filtered_sentence:

            filtered_word = str(filtered_word)
            pos_tag = str(pos_tag)


            lemma_form = str(get_lemma_form(filtered_word))

            word_tokenize_sent.append(lemma_form)
            pos_tokenize_sent.append(pos_tag)
            word_pos_tokenize.append((lemma_form,pos_tag))

        word_count = dict(Counter(word_tokenize_sent))

        word_count = word_count.items()

        sorted_by_second = sorted(word_count, key=lambda tup: tup[1],reverse=True)

        #main_data['Sentence-Unique-Count'].append(str(sorted_by_second))
        #pos_count = dict(Counter(pos_tokenize_sent))
        #print pos_count
        #main_data['Sentence-POS-Count'].append(str(pos_count))
        main_data['After-Cleaning-Sentences'].append(" ".join(word_tokenize_sent))
        main_data["Company"].append(company_name)



    #print "before_cleanCorpus=====:::::" ,before_cleanCorpus[:20]
    #print "\n\n after_cleanCorpus=======::::" ,after_cleanCorpus[:20]
    #corpus_count_beforeCleaning = dict(Counter(before_cleanCorpus))
    #corpus_count_afterCleaning = dict(Counter(after_cleanCorpus))

    #header_data['before_cleanCorpus'].append(str(corpus_count_beforeCleaning))
    #header_data['after_cleanCorpus'].append(str(corpus_count_beforeCleaning))
    #header_data['total_corpus_size'] =  len(str(before_cleanCorpus))
    #header_data['total_clean_corpus_size'] = len(str(after_cleanCorpus))


    #small_df = pd.DataFrame(header_data)

    #word_pos_freq_dict = dict(Counter(word_pos_tokenize))
    #word_pos_freq_list = [[str(k[0]),str(k[1]),str(v)]for k, v in word_pos_freq_dict.items()]


    #word_pos_df = pd.DataFrame(word_pos_freq_list ,columns= ['Token','Pos-tagging','Frequency'])

    df = pd.DataFrame(main_data)
    #entity_df = pd.DataFrame(entity_extracted_data)

    #return small_df , df , word_pos_df , entity_df
    return df




if __name__== "__main__":
    para = "item 8\xa0\xa0\xa0\xa0financial statements and supplementary data report of \
    independent registered public accounting firm on consolidated financial statements the \
    board of directors and stockholders occidental petroleum corporation: we have audited the accompanying \
    consolidated balance sheets of occidental petroleum corporation and\xa0subsidiaries as of december\xa031, 2016 and 2015, \
    and the related consolidated statements of operations, comprehensive income, stockholders\u2019 equity, and cash flows \
    for each of the years in the three\u2011year period ended december\xa031, 2016. in connection with our audits of the \
    consolidated financial statements ,\ we also have audited financial statement schedule ii - valuation and qualifying accounts."
    data_preprocessing(para)
