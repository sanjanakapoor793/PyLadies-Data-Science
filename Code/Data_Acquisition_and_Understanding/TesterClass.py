#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul  3 14:09:57 2018

@author: Sanjana Kapoor
"""


filepath = 'filepath'


import text_pipeline
from Pipeline import Pipeline
from store_data import EmailDataStorage
from LDA import LDAModelMaker
from docTopicVector import DocumentTopicVectorStorage
from CoherenceTests import TestingModel

emails = EmailDataStorage()

tokenizer = text_pipeline.Tokenizer('spacy')
token_filter = text_pipeline.TokenFilter('spacy')
stemmer = text_pipeline.Stemmer('spacy')
pre_processing = text_pipeline.Pipeline(tokenizer, token_filter, stemmer)


lda = LDAModelMaker(create = True, 
                    texts_filepath = filepath, 
                    corpus_filepath = filepath, 
                    dictionary_filepath = filepath, 
                    lda_filepath = filepath, 
                    pyldavis_filepath = filepath, 
                    database = 'mongo', 
                    num_topics = 35, 
                    minimum_probability = 0.00, 
                    passes = 5)

pyladies_pipeline = Pipeline(emails, pre_processing, lda)


# =============================================================================
# You can add more steps to your Pipeline. 
# Adding these 2 classes will remove 2 steps you will probably end up having to do. 
#
#
#
# doc_topic_v = DocumentTopicVectorStorage(lda_model_location = filepath, 
#                                  corpus_location = filepath, 
#                                  database = 'mongo')
# 
# cm = TestingModel(call_coherence = True, 
#                   lda_filepath = filepath, 
#                   texts_filepath = filepath, 
#                   coherence_measure = 'c_v', 
#                   create_cm = True, 
#                   cm_filepath = filepath)
# =============================================================================
