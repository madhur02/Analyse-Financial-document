# -*- coding: utf-8 -*-
"""
Created on Thu Jul  5 18:14:34 2018

@author: J554696
"""

import numpy as np
import pandas as pd
import re, gensim
import xlsxwriter
# Plotting tools
import pyLDAvis
import pyLDAvis.gensim  # don't skip this
import matplotlib.pyplot as plt

# Sklearn
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import GridSearchCV
from pprint import pprint
import warnings
warnings.filterwarnings("ignore",category=DeprecationWarning)

import en_core_web_sm
nlp = en_core_web_sm.load(disable=['parser', 'ner'])

from rake_nltk import Rake
from nltk.corpus import stopwords


def _removeNonAscii(s):
    return "".join(i for i in s if ord(i)<128)

def rake_gen(stop,df):
    r = Rake(stop);
    r.extract_keywords_from_text(df)
    r.get_ranked_phrases()
    ## taking the generated phrases from the data
    phrase_list =[ i[1] for i in r.get_ranked_phrases_with_scores()]

    return phrase_list


def preprocessing_data(sheet_content):
    '''
    preprocessing data like remove email and multiple spaces ..
    '''
    new_data = []
    for index,row in sheet_content.iterrows():
        sent = row['Before-Cleaning-Sentences']
        sent = re.sub('\S*@\S*\s?', '', sent)
        sent = re.sub('\s+', ' ', sent)
        sent = re.sub("\'", "", sent)
        new_data.append(sent)
    return new_data

## Tokenize word and text clean up
def sent_to_words(sentences):
    for sentence in sentences:
        yield(gensim.utils.simple_preprocess(str(sentence), deacc=True))  # deacc=True removes punctuations


def lemmatization(texts, allowed_postags=['NOUN', 'ADJ', 'VERB', 'ADV']):
    """https://spacy.io/api/annotation"""
    #nlp = spacy.load('en', disable=['parser', 'ner'])
    nlp = en_core_web_sm.load()
    texts_out = []
    for sent in texts:
        doc = nlp(" ".join(sent))
        texts_out.append(" ".join([token.lemma_ if token.lemma_ not in ['-PRON-'] else '' for token in doc if token.pos_ in allowed_postags]))
    return texts_out


def data_vizualization(best_lda_model,data_vectorized,vectorizer):
     # Visualize the topics
      #pyLDAvis.enable_notebook()
      print ("Best Lda model1::::",best_lda_model)
      print ("Best Lda model2::::",data_vectorized)
      print ("Best Lda model3::::",vectorizer)
      pyLDAvis.display(pyLDAvis.gensim.prepare(best_lda_model, data_vectorized, vectorizer))
      #vis = pyLDAvis.gensim.prepare(best_lda_model, data_vectorized, vectorizer,mds='tsne')

      pyLDAvis.show()

def build_lda_with_scikit_learn(data_vectorized):

    # Build LDA Model
    lda_model = LatentDirichletAllocation(n_topics=10,               # Number of topics
                                          max_iter=10,               # Max learning iterations
                                          learning_method='online',
                                          random_state=100,          # Random state
                                          batch_size=128,            # n docs in each learning iter
                                          evaluate_every = -1,       # compute perplexity every n iters, default: Don't
                                          n_jobs = -1,               # Use all available CPUs
                                          )
    lda_output = lda_model.fit_transform(data_vectorized)

    # Log Likelyhood: Higher the better
    print("Log Likelihood: ", lda_model.score(data_vectorized))

    # Perplexity: Lower the better. Perplexity = exp(-1. * log-likelihood per word)
    print("Perplexity: ", lda_model.perplexity(data_vectorized))

    # See model parameters
    #best_lda_model = lda_model.get_params()
    return lda_model

def dominant_topic(lda_model,data_vectorized,data):

    # Create Document - Topic Matrix
    lda_output = lda_model.fit_transform(data_vectorized)

    # column names
    topicnames = ["Topic" + str(i) for i in range(lda_model.n_components)]

    # index names
    docnames = ["Doc" + str(i) for i in range(len(data))]

    # Make the pandas dataframe
    df_document_topic = pd.DataFrame(np.round(lda_output, 2), columns=topicnames, index=docnames)

    # Get dominant topic for each document
    dominant_topic = np.argmax(df_document_topic.values, axis=1)
    df_document_topic['dominant_topic'] = dominant_topic

    # Styling
    def color_green(val):
        color = 'green' if val > .1 else 'black'
        return 'color: {col}'.format(col=color)

    def make_bold(val):
        weight = 700 if val > .1 else 400
        return 'font-weight: {weight}'.format(weight=weight)

    # Apply Style
    df_document_topics = df_document_topic.head(15).style.applymap(color_green).applymap(make_bold)
    #print(df_document_topics)

def predict_topic(text,vectorizer,df_topic_keywords,best_lda_model, nlp=nlp):

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

def show_topics(vectorizer, lda_model, n_words=20):
    keywords = np.array(vectorizer.get_feature_names())
    topic_keywords = []
    for topic_weights in lda_model.components_:
        top_keyword_locs = (-topic_weights).argsort()[:n_words]
        topic_keywords.append(keywords.take(top_keyword_locs))
    return topic_keywords

def rake_main_handler(df):

    stop = set(stopwords.words('english'))
    clean_words = _removeNonAscii(df)
    phrase_list = rake_gen(stop,clean_words)
    #print(phrase_list[:100])
    #tmp = []

    return phrase_list[:100]

def main_scikit_learn(sheet_content):

    data = preprocessing_data(sheet_content)
    data_words = list(sent_to_words(data))
    data_lemmatized = lemmatization(data_words, allowed_postags=['NOUN', 'ADJ', 'VERB', 'ADV'])

    vectorizer = CountVectorizer(analyzer='word',
                             min_df=10,                        # minimum reqd occurences of a word
                             stop_words='english',             # remove stop words
                             lowercase=True,                   # convert all words to lowercase
                             token_pattern='[a-zA-Z0-9]{3,}',  # num chars > 3
                             # max_features=50000,             # max number of uniq words
                            )

    data_vectorized = vectorizer.fit_transform(data_lemmatized)
    best_lda_model = build_lda_with_scikit_learn(data_vectorized)

    dominant_topic(best_lda_model,data_vectorized,data)

    topic_keywords = show_topics(vectorizer=vectorizer, lda_model=best_lda_model, n_words=15)

    # Topic - Keywords Dataframe
    df_topic_keywords = pd.DataFrame(topic_keywords)
    df_topic_keywords.columns = ['Word '+str(i) for i in range(df_topic_keywords.shape[1])]
    df_topic_keywords.index = ['Topic '+str(i) for i in range(df_topic_keywords.shape[0])]
    data_vizualization(best_lda_model,data_vectorized,vectorizer)

    ## Dataset for generating the phrases
    df= "".join(sheet_content['Before-Cleaning-Sentences'].values.tolist())
    mytext = rake_main_handler(df)

    out_dataframe = pd.DataFrame()

    for i in mytext:
           topic, topic_probability_scores = predict_topic([i],vectorizer,df_topic_keywords,best_lda_model, nlp=nlp)
           #print(topic)
           out_dataframe = out_dataframe.append({'Phrase': i, 'Topic': topic, 'Topic probability scores': topic_probability_scores}, ignore_index=True)

    neww_dict  = {}
    for index , row in out_dataframe.iterrows():
        phrase = row["Phrase"]
        topic = ", ".join(row["Topic"])

        if topic not in neww_dict:
            neww_dict[topic] = [phrase]
        else:
            neww_dict[topic].append(phrase)
    print(neww_dict)

    #save_dataframe = pd.DataFrame(neww_dict)
    ## Saving the output file in csv format.
    workbook = xlsxwriter.Workbook('data.xlsx')
    worksheet = workbook.add_worksheet()
    row = 0
    col = 0
    for key in neww_dict.keys():
        row += 1
        worksheet.write(row, col, key)
        for item in neww_dict[key]:
            worksheet.write(row, col + 1, item)
            row += 1

    workbook.close()



if __name__== "__main__":
    sheet_content = pd.read_csv("all_content.csv")
    #content = pd.read_csv(r'C:\Users\J554696\Desktop\TopicModeling\10K project _27062018\all_content.csv')['Before-Cleaning-Sentences']
    main_scikit_learn(sheet_content)
