import nltk
import os
import pandas as pd
import re
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


def summarizer_handler():
    domain_word_tokenization  = get_domain_keyword()
    main_frame = []
    for csv_file in os.listdir(path)[:20]:

        file_path = os.path.join(path,csv_file)
        all_before_clean_list,compnay     = get_corpus(file_path)
        keywords_match_sentences  = keywords_match(all_before_clean_list,domain_word_tokenization)
        keyword_summary_data      = keywords_match_summary(keywords_match_sentences)
        summary_data              = extract_summary(all_before_clean_list)
        summary_keyword_sentences = summary_match_keyword(summary_data,domain_word_tokenization)
        unrelevant_keyword_summary_data,relevant_keyword_summary_data =before_keyword_match_analysis(keywords_match_sentences,
                                                                                keyword_summary_data)
        unrelevant_summary_keyword_data,revelant_summary_keyword_data= after_keyword_match_analysis(summary_data,
                                                                                summary_keyword_sentences)

        print ("all sentences ::::", len(all_before_clean_list))
        print ('------'*30)
        print ("keywords_match_sentences:::::", len(keywords_match_sentences))
        print ("keywords_summary_data:::::", len(keyword_summary_data))
        print ("unrelevant_keyword_summary_data:::::", len(unrelevant_keyword_summary_data))
        print ("relevant_keyword_summary_data::::::", len(relevant_keyword_summary_data))
        new_list = [[relevant_sent,compnay] for relevant_sent in relevant_keyword_summary_data]
        df = pd.DataFrame(new_list, columns=["Sentence", "Company"])
        main_frame.append(df)
        print ('------'*50)
        print ("summary_data:::::", len(summary_data))
        print ("summary_keyword_sentences:::::", len(summary_keyword_sentences))


        print ("unrelevant_summary_keyword_data::::::",len(unrelevant_summary_keyword_data))
        print ("relevant_summary_keyword_sentences:::",len(revelant_summary_keyword_data))

        html_str = '<html>'
        html_str += '<body><div style="width:100%;height:50%;float:left;"><table style="border:1px solid black;">'
        html_str += '<tr><td style="border:1px solid black;background-color:#ff8000;">S no.</td>'
        html_str += '<td style="border:1px solid black;background-color:#ff8000;">Relevant Sentences (keyword Matching followed by summary)</td>'
        html_str += '<td style="border:1px solid black;background-color:#ff8000;">Relevant Sentences (text summarization followed by keyword matching)</td></tr>'

        relevant_length = max([len(relevant_keyword_summary_data),len(revelant_summary_keyword_data)])

        for i in range(0,relevant_length):
            try:
                txt1 = relevant_keyword_summary_data[i]
                #print (txt1)
            except:
                txt1 = ''
            try:
                txt2 = revelant_summary_keyword_data[i]
            except:
                txt2 = ''

            html_str += '<tr>'
            html_str += '<td style="border:1px solid black;">%s</td>'%(str(i+1))
            html_str += '<td style="border:1px solid black;">%s</td>'%(txt1)
            html_str += '<td style="border:1px solid black;">%s</td>' %(txt2)
            html_str += '</tr>'
        html_str += '</table></div></body></html>'

        html_str1 = '<html>'
        html_str1 += '<body><table style="border:1px solid black;">'
        html_str1 += '<tr><td style="border:1px solid black;background-color:#ff8000;">S no.</td>'
        html_str1 += '<td style="border:1px solid black;background-color:#ff8000;">Leftover Sentences (keyword Matching followed by summary)</td>'
        html_str1 += '<td style="border:1px solid black;background-color:#ff8000;">Leftover Sentences (text summarization followed by keyword matching)</td></tr>'


        unrelevant_length = max([len(unrelevant_keyword_summary_data),len(unrelevant_summary_keyword_data)])

        for j in range(0,unrelevant_length):
            try:
                txt_1 = unrelevant_keyword_summary_data[j]
                #print (txt1)
            except:
                txt_1 = ''
            try:
                txt_2 = unrelevant_summary_keyword_data[j]
            except:
                txt_2 = ''

            html_str1 += '<tr>'
            html_str1 += '<td style="border:1px solid black;">%s</td>'%(str(j+1))
            html_str1 += '<td style="border:1px solid black;">%s</td>'%(txt_1)
            html_str1 += '<td style="border:1px solid black;">%s</td>' %(txt_2)
            html_str1 += '</tr>'
        html_str1 += '</table></iframe></div></body></html>'


        relevant_path = os.path.join(summary_path,csv_file.split("__")[0]+"_relevant_sentence.html")
        #f = open("bank_hawaii_relevant_sentence.html","w",encoding='utf-8')
        f = open(relevant_path,"w",encoding='utf-8')
        f.write(html_str)
        f.close()

        relevant_leftover_path = os.path.join(summary_path,csv_file.split("__")[0]+"__relevant_sentence_leftover.html")
        #f = open("bank_hawaii_relevant_sentence_leftover.html","w",encoding='utf-8')
        f = open(relevant_leftover_path,"w",encoding='utf-8')
        f.write(html_str1)
        f.close()
    all_content = pd.concat(main_frame)
    all_content.to_csv("Summary_Phrase_compnay.csv")


if __name__== "__main__":
    summarizer_handler()
