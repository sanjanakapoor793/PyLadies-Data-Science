#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May  4 13:38:32 2018

@author: s0k00rp
"""

from pymongo import MongoClient
import nmslib as nms
import numpy as np
import os
import pymongo


class SimilarDoc():
    def __init__(self, index_filepath, create_index = False):
        """ Set up all the databases that will be used 
        
        :param {str} index_filepath: 
            Location of where to load or save index from/to. 
            
        :param {bool} create_index:
            Determines whether or not a new index has to be made
        
        self.emailDB:
            Stores the database EnronEmailData
        self.emailCol:
            Collection for EnronEmailData
        self.db_index:
            Secondary index to help go through self.emailCol in ascending order according to the counter (doc_counter)
        self.index: 
            Index for NMSLIB
        """

        client = MongoClient()
        self.emailDB = client[os.getenv('EMAIL_DATABASE_NAME')]
        self.emailCol = self.emailDB[os.getenv('EMAIL_COLLECTION_NAME')]
        if type(create_index) is bool:
            if create_index: 
                self.index = self.set_up()
                self.save_index(index_filepath)
            else:
                self.index = self.load_index(index_filepath)
        else:
            if eval(create_index): 
                self.index = self.set_up()
                self.save_index(index_filepath)
            else: 
                self.index = self.load_index(index_filepath)
            
    
    """ 
    HNSW Index & Cosine Similarity
    
    """ 
    def set_up(self):
        """
        Add documents to index, create index, and then return to __init__
        Adding the id returned by .addDataPoint

        """
        
        self.emailCol.create_index([("email_counter", pymongo.ASCENDING)])
        index = nms.init(method = 'hnsw', space = 'cosinesimil')
        # need to add in all the document_topic_vectors
        # Must be sorted for when retrieving _id based on the index of the document in self.index
        for vector in self.emailCol.find( {'$query': {}, '$orderby': {'email_counter': 1} } ):
            index.addDataPoint(vector['email_counter'], vector['topic_vector'])
        index.createIndex(print_progress = True)
        return index
    
        
    def similar_from_id(self, document_id):
        """
        Runs nearest neighbors to find the num closest documents given the document's id. 
            
        :param {str} document_id:
            _id that corresponds to a document in the DocTopicVectors database 

        """
        
        curr_doc = self.emailCol.find_one({ "_id" : document_id})
        curr_vector = curr_doc['topic_vector']
        result, distances = self.similar_from_topic_vector(curr_vector)
        return result, distances
        
    
    
    def similar_from_topic_vector(self, curr_vector):
        """
        Runs nearest neighbors to find the num closest documents given the vector. 
        
        :param {list} curr_vector:
            Document topic vector for the base document (the document we start off with).
        
        :param {int} num:
            number of similar documents whose ID's should be returned
        
        """
        
        nearest_n, distances = self.index.knnQuery(curr_vector, 20)
        result = []
        for unique_number in nearest_n:
            # this is why documents must be sorted when adding them to the index!!
            result_email = self.emailCol.find_one({'email_counter': np.asscalar(unique_number)})
            result.append(result_email['_id'])
        return result, distances
        
    
    def save_index(self, filepath):
        """
        Save the index to a given location
        
        """
        # will later be a value passed in 
#        filepath = '../../../Enron/NMSLIB/index.hnsw' 
        # save the index so we don't have to go through the long process of 'index.createIndex'
        self.index.saveIndex(filepath)


    def load_index(self, filepath):
        """ 
        Load the index from the given location
                
        """
        index = nms.init(method = 'hnsw', space = 'cosinesimil')
        # this should later be a variable 
#        filepath = '../../../Enron/NMSLIB/index.hnsw'
        index.loadIndex(filepath)
        return index
    
    
    def tester_method(self, docVec):
        print(type(self.locations))
        for key, val in self.locations.items():
            if(val == docVec):
                print(key)
                

if __name__ == "__main__":
    import argparse
    import sys
    if not len(sys.argv) > 1:
        raise ValueError("Path to email index file is a required argument.")
    parse = argparse.ArgumentParser(description='Find nearest neighbors')
    parse.add_argument('-i', required = True)
    parse.add_argument('-s')
    parse.add_argument('-c')
    args = parse.parse_args()
    tester = SimilarDoc(index_filepath = args.i, create_index = args.c)
    results, distances = tester.similar_from_id(document_id = args.s)
    print(results)
    print(distances)



#tester = SimilarDoc('../../../Enron/Tester/original/index.hnsw', False)
#result, distances = tester.similar_from_topic_vector([(0, 0.010508849), (1, 0.019970758), (2, 0.00), (3, 0.00), (4, 0.00), 
#                                                      (5, 0.017709557), (6, 0.00), (7, 0.010471645), (8, 0.015099778), 
#                                                      (9, 0.014586268), (10, 0.00), (11, 0.00), (12, 0.010280435), 
#                                                      (13, 0.012380897), (14, 0.01203193), (15, 0.060243197), (16, 0.00), 
#                                                      (17, 0.019973787), (18, 0.016498648), (19, 0.00), (20, 0.00), (21, 0.00), 
#                                                      (22, 0.00), (23, 0.022730187), (24, 0.00), (25, 0.00), (26, 0.00), 
#                                                      (27, 0.012456094), (28, 0.0124316), (29, 0.011423724), (30, 0.00), 
#                                                      (31, 0.01474771), (32, 0.00), (33, 0.00), (34, 0.4723764), (35, 0.00), 
#                                                      (36, 0.00), (37, 0.00), (38, 0.010276491), (39, 0.00), (40, 0.00), 
#                                                      (41, 0.00), (42, 0.00), (43, 0.014929281), (44, 0.011724406), 
#                                                      (45, 0.00), (46, 0.00), (47, 0.00), (48, 0.025309466), (49, 0.00)], 5)
#print(result)
#for r in result:
#    print(r)
