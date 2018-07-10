#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May  3 14:17:11 2018

@author: Sanjana Kapoor
"""
from gensim import corpora
from gensim.corpora.mmcorpus import MmCorpus
from gensim.models import ldamodel
import os


class DocumentTopicVectorStorage():
    
    def __init__(self, lda_model_location, corpus_location, database = 'mongo'):
        """
        Load LDAModel and Corpus from file locations sent. 
        
        :param {str} lda_model_location:
            Filepath to the LDAModel.
        
        :param {str} corpus_location:
            Filepath to the corpus.
        
        :param {str} database:
            Type of database used. 

        self.lda:
            Stores the LDA Model generated earlier
        self.db:
            Database for the Document-Topic Vecors
        self.emailsCol:
            Collection of Enron Emails
        
        """
        
        self.next_steps = {'mongo': self.mongo}
        self.lda = ldamodel.LdaModel.load(lda_model_location) 
        self.corpus_location = corpus_location
        
        if database == 'mongo': 
            from pymongo import MongoClient
        
            emailClient = MongoClient()
            self.db = emailClient[os.getenv('EMAIL_DATABASE_NAME')]
            self.emailsCol = self.db[os.getenv('EMAIL_COLLECTION_NAME')]
            
        self.database = self.next_steps[database]

    
    def apply(self):
        """
        Generate Document Topic Vectors and pass to method to add to database.
        
        TO-DO: 
            
        vector = [(counter, 0.0) if v[0] != counter else v for v in vector]
        
        """

        counter = 0
        corpus = corpora.MmCorpus(self.corpus_location)
        
        for row in corpus:
            vector = self.lda.get_document_topics(row)
            # MongoDB can't store numpy stuff. 
            # Must convert the float 32 in the second spot in the tuples in vector to native float
            vector = [tuple(map(float, v)) for v in vector]
            self.database(counter, vector)
            counter += 1
            

    def mongo(self, email_counter, vector):
        """
        Add data to database.
            
        :param {int} email_counter:
            Way of identifying a document being placed in the database. Will be used as email_counter in database
        :param {list of tuples} vector:
            List of tuples that indicate the topic distribution for that document
        
        """
        
        self.emailsCol.update_one({'email_counter': email_counter}, {'$set': {
                    'topic_vector': vector}},
                    upsert = False)


if __name__ == "__main__":
    import argparse
    import sys
    if not len(sys.argv) > 1:
        raise ValueError("Location of LDA Model")
    parser = argparse.ArgumentParser(description='Save document topic vectors')
    parser.add_argument('-l', required = True)
    args = parser.parse_args()
    topic_vector_storage = DocumentTopicVectorStorage(args.l)
    topic_vector_storage.store_info()

