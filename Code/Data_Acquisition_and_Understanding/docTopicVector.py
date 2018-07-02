#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May  3 14:17:11 2018

@author: s0k00rp
"""
from gensim.corpora.mmcorpus import MmCorpus
from gensim.models import ldamodel
from gensim.test.utils import datapath
#import numpy
import os
from pymongo import MongoClient
import numpy



class DocumentTopicVectorStorage():
    
    def __init__(self, lda_model_location):
        """
        Load LDAModel and Corpus from file locations sent. 
        
        :param {str} lda_model_location:
            Filepath to the LDAModel

        self.lda:
            Stores the LDA Model generated earlier
        self.db:
            Database for the Document-Topic Vecors
        self.emailsCol:
            Collection of Enron Emails
        
        """
        self.lda = ldamodel.LdaModel.load(lda_model_location) 
        emailClient = MongoClient()
        self.db = emailClient[os.getenv('EMAIL_DATABASE_NAME')]
        self.emailsCol = self.db[os.getenv('EMAIL_COLLECTION_NAME')]
        
        
    def print_info(self):
        for c in self.corpus:
            print(c)
    
    
    def store_info(self):
        """
        Generate Document Topic Vectors and pass to method to add to database.
        
        TO-DO: 
            
        Figure out how to store num_topics here
            
        figure out how to increment counter in a synthesized for loop
        counter = 0
        vector = [(counter, 0.0) if v[0] != counter else v for v in vector]
        
        """
        print('here')
        counter = 0
        print(self.emailsCol.count())
        for email in self.emailsCol.find():
            print('one')
            vector = self.lda.get_document_topics(email['email_corpus_value'])
            # MongoDB can't store numpy stuff. 
            # Must convert the float 32 in the second spot in the tuples in vector to native float
            vector = [tuple(map(float, v)) for v in vector]
            print(counter)
            vectorIter = iter(vector)
            complete_vector = []
            topic_counter = 0
            num_topics = 50
            v = next(vectorIter)
            while topic_counter < num_topics:                     # iterating through all the tuples in the vector
                if v[0] == topic_counter:                         # this topic number exists in the list
                    complete_vector.append(v)                           # add this value. WE DON'T WANT TO LOSE IT
                    topic_counter += 1                            # increase counter so cycle continues
                    try:
                        v = next(vectorIter)                # get next tuple
                    except StopIteration:                   # we are at the end of the list 
                        if topic_counter != num_topics:           # the list ended before hitting the 24th topic
                                                                  # there were some topics left out on the end
                            while topic_counter < num_topics:
                                complete_vector.append((topic_counter, 0.00))
                                topic_counter += 1
                        else:
                            pass
                            continue
                else:
                    while topic_counter != v[0]:
                        complete_vector.append((topic_counter, 0.00))
                        topic_counter += 1
            self.add_data(email['_id'], complete_vector, email['email_counter'])
            print('done')
            counter += 1
            
    
    

    def add_data(self, docID, vector, counter):
        """
        Add data to database.
            
        :param {int} doc_id:
            ID of document being placed in the database. Will be used as _id
        :param {list of tuples} vector:
            List of tuples that indicate the topic distribution for that document
        
        """
        
        self.emailsCol.update_one({'_id': docID}, {'$set': {
                    'topic_vector': vector}},
                    upsert = False)

#        topicVectors = self.db.tVectors
#        vectorValues = {
#            '_id': docID,
#            'topic_values': vector,
#            'doc_counter': counter
#        }
#
#        topicVectors.insert_one(vectorValues)
        
        

#client = MongoClient()
#client.drop_database('DocTopicVectors')


if __name__ == "__main__":
    import argparse
    import sys
    if not len(sys.argv) > 1:
        raise ValueError("Location of LDA Model")
    parser = argparse.ArgumentParser(description='Save document topic vectors')
    parser.add_argument('-l', required = True)
    args = parser.parse_args()
    print('first')
    topic_vector_storage = DocumentTopicVectorStorage(args.l)
    print('second')
    topic_vector_storage.store_info()

