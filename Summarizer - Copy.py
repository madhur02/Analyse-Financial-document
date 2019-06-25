import nltk
import os
import pandas as pd
import re
from nltk import word_tokenize
from nltk import pos_tag
from gensim.summarization.summarizer import summarize
path = r"C:\Users\G753903\Downloads\Topic_Modelling_18072018\v2.1  20180718\Output_Result"
summary_path = r"C:\Users\G753903\Downloads\Topic_Modelling_18072018\v2.1  20180718\Summary_output"

def get_domain_keyword(file_name ="domain_keyword.txt"):
    word_tokenization = []
    content = open(file_name,"r").readlines()
    matching_phrases = list(map(lambda x : x.strip("\n").strip("").lower(),content))
    for phrase in matching_phrases:
         word_list = nltk.word_tokenize(phrase)
         word_tokenization.append(word_list)
    return word_tokenization

def get_corpus(csv_file):
    all_before_clean_list = []
    path_file_name = os.path.join(path,csv_file)
    csv_data = pd.read_csv(path_file_name)
    compnay = ''
    for index , row in csv_data.iterrows():
        sentence = row["Before-Cleaning-Sentences"]
        company = row["Company"]
        sentence = re.sub("\d+\stable of contents","",sentence)
        all_before_clean_list.append(sentence)
    all_before_clean_list = list(set(all_before_clean_list))
    return all_before_clean_list , company

def keywords_match(all_before_clean_list,word_tokenization):
    keywords_match_sentences = []
    for sentence in all_before_clean_list:
        sent_word = nltk.word_tokenize(sentence)
        result = [list(filter(lambda x: x in sent_word, sublist)) for sublist in word_tokenization]
        result1  = [True for res in result if len(res) >= 1]
        if True in result1:
            keywords_match_sentences.append(sentence)
    return keywords_match_sentences

def keywords_match_summary(keywords_match_sentences):
    keywords_match_txt = " ".join(keywords_match_sentences)
    keyword_summary_data = summarize(keywords_match_txt,ratio=0.3,split=True)
    return keyword_summary_data

def extract_summary(all_before_clean_list):
    before_clean_txt = " ".join(all_before_clean_list)
    summary_data = summarize(before_clean_txt,ratio=0.3,split=True)
    return summary_data

def summary_match_keyword(summary_data,word_tokenization):
    summary_keyword_sentences = []
    for sentence in summary_data:
        sent_word = nltk.word_tokenize(sentence)
        result = [list(filter(lambda x: x in sent_word, sublist)) for sublist in word_tokenization]
        result1  = [True for res in result if len(res) >= 1]
        if True in result1:
            summary_keyword_sentences.append(sentence)
    return summary_keyword_sentences

def before_keyword_match_analysis(keywords_match_sentences,keyword_summary_data):
    keywords_match_sentences  = keywords_match_sentences
    relevant_keyword_summary_data = keyword_summary_data
    unrelevant_keyword_summary_data = list(set(keywords_match_sentences) - set(keyword_summary_data))
    return unrelevant_keyword_summary_data , relevant_keyword_summary_data

def after_keyword_match_analysis(summary_data,summary_keyword_sentences):
    summary_data = summary_data
    relevant_summary_keyword_sentences = summary_keyword_sentences
    unrelevant_summary_keyword_data = list(set(summary_data) - set(relevant_summary_keyword_sentences))
    return unrelevant_summary_keyword_data,summary_keyword_sentences

def phrase_extractor(tagged_sent):

    grammar=r'KT: {(<JJ>* <NN.*>+ <IN>)? <JJ>* <NN.*>+}'
    chunker = nltk.RegexpParser(grammar, loop=2)
    chunker_sent = [chunker.parse(tagged_sent)]
    all_chunks = get_chunks(chunker_sent)
    return all_chunks

def get_chunks(chunked_sents, chunk_type='KT'):
    all_chunks = []
    # chunked sentences are in the form of nested trees
    for tree in chunked_sents:
        chunks = []
        raw_chunks = [subtree.leaves() for subtree in tree.subtrees()
                      if subtree.label() == chunk_type]
        for raw_chunk in raw_chunks:
            chunk = []
            for word_tag in raw_chunk:
                chunk.append(word_tag[0])
            chunks.append(' '.join(chunk))
        all_chunks.append(chunks)
    all_chunks1 =list(filter(lambda x: len(x.split(" "))>3,all_chunks[0]))
    print ("All_chunks1-----------",all_chunks1)
    return all_chunks1

def summarizer_handler():
    domain_word_tokenization  = get_domain_keyword()
    main_frame = []
    for csv_file in os.listdir(path)[:50]:
        file_path = os.path.join(path,csv_file)
        all_before_clean_list,compnay     = get_corpus(file_path)
        keywords_match_sentences  = keywords_match(all_before_clean_list,domain_word_tokenization)
        keyword_summary_data      = keywords_match_summary(keywords_match_sentences)
        unrelevant_keyword_summary_data,relevant_keyword_summary_data =before_keyword_match_analysis(keywords_match_sentences,
                                                                                keyword_summary_data)


        print ("all sentences ::::", len(all_before_clean_list))
        print ('------'*30)
        print ("keywords_match_sentences:::::", len(keywords_match_sentences))
        print ("keywords_summary_data:::::", len(keyword_summary_data))
        print ("unrelevant_keyword_summary_data:::::", len(unrelevant_keyword_summary_data))
        print ("relevant_keyword_summary_data::::::", len(relevant_keyword_summary_data))
        #new_list = [[relevant_sent,compnay] for relevant_sent in relevant_keyword_summary_data[:5]]
        new_list = []
        for relevant_sent in relevant_keyword_summary_data[:5]:
             word_sent_tokenize = word_tokenize(relevant_sent)
             pos_sent_tagger    = pos_tag(word_sent_tokenize)
             all_chunks = phrase_extractor(pos_sent_tagger)
             new_list.append((relevant_sent,all_chunks,compnay))

        df = pd.DataFrame(new_list, columns=["Sentence","Phrases","Company",])
        main_frame.append(df)
        print ('------'*50)

    all_content = pd.concat(main_frame)
    all_content.to_csv("Summary_Phrase_compnay.csv")


if __name__== "__main__":
    summarizer_handler()
