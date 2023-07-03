# -*- coding: utf-8 -*-
"""
@author: Madhur jain
"""

import pandas as pd
import numpy as np
from rake_nltk import Rake
from nltk.corpus import stopwords
#from mallet_lda_topic import main_handler

import gensim

'''
import en_core_web_sm
nlp = en_core_web_sm.load()
nlp = en_core_web_sm.load(disable=['parser', 'ner'])
'''
def _removeNonAscii(s):
    return "".join(i for i in s if ord(i)<128)

def rake_gen(stop,df):
    r = Rake(stop);
    r.extract_keywords_from_text(df)
    r.get_ranked_phrases()
    ## taking the generated phrases from the data
    phrase_list =[ i[1] for i in r.get_ranked_phrases_with_scores()]

    return phrase_list 

def sent_to_words(sentences):
    for sentence in sentences:
        yield(gensim.utils.simple_preprocess(str(sentence), deacc=True))  # deacc=True removes punctuations



def predict_topic(text):
   
    global sent_to_words
    global lemmatization

    # Step 1: Clean with simple_preprocess
    mytext_2 = list(sent_to_words(text))
    
    # Step 2: Lemmatize
    mytext_3 = lemmatization(mytext_2, allowed_postags=['NOUN', 'ADJ', 'VERB', 'ADV'])
    
    # Step 3: Vectorize transform
    mytext_4 = vectorizer.transform(mytext_3)
    
    # Step 4: LDA Transform
    topic_probability_scores = best_lda_model.transform(mytext_4)
    topic = df_topic_keywords.iloc[np.argmax(topic_probability_scores), :].values.tolist()
    
    return topic, topic_probability_scores

def rake_main_handler(df):
    
    stop = set(stopwords.words('english'))
    clean_words = _removeNonAscii(df)
    phrase_list = rake_gen(stop,clean_words) 
    print(phrase_list[:100])
    #tmp = []  
    
    return phrase_list
    #df1 = pd.DataFrame(columns=['Phrase','Dominant topic'])
    #print(phrase_list[50:55])
    
    #for phrase in phrase_list[50:55]:
    #    topic, topic_probability_scores =   predict_topic(text = [phrase])
    #    tmp.append([phrase,topic])
    #df1 = pd.DataFrame(tmp,columns=['Phrase','Dominant topic'])
    #print(df1.head())
    
if __name__== "__main__":
    #pass
    df= "".join(pd.read_csv(r'C:\Users\madhur\Desktop\TopicModeling\10K project _27062018\all_content.csv')['Before-Cleaning-Sentences'].values.tolist())
    phrase_list = rake_main_handler(df)
    