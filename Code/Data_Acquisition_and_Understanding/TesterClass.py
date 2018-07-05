#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul  3 14:09:57 2018

@author: Sanjana Kapoor
"""

import text_pipeline

from Pipeline import Pipeline
from store_data import EmailDataStorage
from LDA import LDAModelMaker
from docTopicVector import DocumentTopicVectorStorage
from CoherenceTests import TestingModel

emails = EmailDataStorage()

#tokenizer = text_pipeline.Tokenizer('spacy')
#token_filter = text_pipeline.TokenFilter('spacy')
#stemmer = text_pipeline.Stemmer('spacy')
#pre_processing = text_pipeline.Pipeline(tokenizer, token_filter, stemmer)


lda = LDAModelMaker(create = False, 
                    texts_filepath = '/data1/enron/results/third_run/texts.txt', 
                    corpus_filepath = '/data1/enron/results/third_run/corpus.mm', 
                    dictionary_filepath = '/data1/enron/results/third_run/dictionary.dict', 
                    lda_filepath = '/data1/enron/results/fourth_run/ldamodel', 
                    pyldavis_filepath = '/data1/enron/results/fourth_run/pyldavis.html', 
                    database = 'mongo', 
                    num_topics = 35, 
                    minimum_probability = 0.00, 
                    passes = 5)

dtv = DocumentTopicVectorStorage(lda_model_location = '/data1/enron/results/fourth_run/ldamodel', 
                                 corpus_location = '/data1/enron/results/third_run/corpus.mm', 
                                 database = 'mongo')

cm = TestingModel(call_coherence = True, 
                  lda_filepath = '/data1/enron/results/fourth_run/ldamodel', 
                  texts_filepath = '/data1/enron/results/third_run/texts.txt', 
                  coherence_measure = 'c_v', 
                  create_cm = True, 
                  cm_filepath = '/data1/enron/results/fourth_run/cm.cv')

complete_pipeline = Pipeline(emails, lda, dtv, cm)