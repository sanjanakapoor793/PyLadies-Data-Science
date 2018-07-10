#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May  4 13:38:32 2018

@author: Sanjana Kapoor
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
        Adding the id returned by .addDataPoint()

        """
        
        self.emailCol.create_index([('email_counter', pymongo.ASCENDING)])
        index = nms.init(method = 'hnsw', space = 'cosinesimil')
        # need to add in all the document_topic_vectors
        # Must be sorted for when retrieving _id based on the index of the document in self.index
        for vector in self.emailCol.find( {'$query': {}, '$orderby': {'email_counter': 1} } ):
            index.addDataPoint(vector['email_counter'], vector['topic_vector'])
        index.createIndex(print_progress = True)
        return index
    
        
    def similar_from_id(self, document_id):
        """
        Runs nearest neighbors to find the closest documents given the document's id. 
            
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
        
        :param {str} filepath: 
            Location of where to save the index to. 
        
        """
        
        # save the index so we don't have to go through the long process of 'index.createIndex'
        self.index.saveIndex(filepath)


    def load_index(self, filepath):
        """ 
        Load the index from the given location
        
        :param {str} filepath: 
            Location of where to load filepath from.
                
        """
        
        index = nms.init(method = 'hnsw', space = 'cosinesimil')
        index.loadIndex(filepath)
        return index
                

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