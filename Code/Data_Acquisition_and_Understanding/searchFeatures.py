#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 17 13:53:01 2018

@author: Sanjana Kapoor
"""

from pymongo import MongoClient
from gensim.models import ldamodel
from gensim.corpora import Dictionary
from similarDoc import SimilarDoc


class SearchFeatures():
    
    def __init__(self, keyword, topic_search, *words, dict_filepath = None, lda_filepath = None, 
                 index_filepath = None, create_index = False):
        """
        Record what kind of search to do. 
        
        :param {boolean} keyword: 
            True if user wants to do a keyword search for the exact word in the text. 
            
        :param {boolean} topic_search:
            True if user wants to do a topic search for the exact word in the text
            
        :param {varies} *words:
            Words that the user wants to search by. 
            
        :param {str} dict_filepath: 
            Where to load dictionary from
        
        :param {str} lda_filepath: 
            Where to load LDA Model from
        
        :param {str} index_filepath: 
            Where to load/save index to. 
        
        :param {str} create_index:
            Whether or not we need to create a new index. 
        
        """

        if type(words) == str:
            self.words = words.split()
        else:
            self.words = words
        
        client = MongoClient()
        self.emailDB = client['EnronEmailData']
        self.emailCol = self.emailDB.emails
        
        self.emailCol.create_index([('content', 'text')])
         
        if eval(keyword):
            self.and_search()
        if eval(topic_search):
            self.semantic_search(dict_filepath, lda_filepath, index_filepath, create_index)
        
    
    def semantic_search(self, dict_filepath, lda_filepath, index_filepath, create_index):
        """
        Generates a topic vector based off the words inputted by the user. Use this topic vector to 
        find num nearest neighbors. 
        
        :param {str} dict_filepath: 
            Where to load dictionary from
        
        :param {str} lda_filepath: 
            Where to load LDA Model from
        
        :param {str} index_filepath: 
            Where to load/save index to. 
        
        :param {str} create_index:
            Whether or not we need to create a new index. 

        
        """
        # load dictionary and lda_model from the filepaths passed in 
        dictionary = Dictionary().load(dict_filepath)
        lda_model = ldamodel.LdaModel.load(lda_filepath) 
        docs_bow = dictionary.doc2bow(self.words)
        docs_topic_distribution = lda_model[docs_bow]
        print(docs_topic_distribution)
        
        find_nearest_n = SimilarDoc(index_filepath, create_index)
        results, distances = find_nearest_n.similar_from_topic_vector(docs_topic_distribution)
        print(results)
   
            
if __name__ == "__main__":
    import argparse
    import sys
    if not len(sys.argv) > 4:
        raise ValueError("Need paths to dictionary, ldamodel, and index.")
    parse = argparse.ArgumentParser(description='Search Features')
    parse.add_argument('-k', required = True)
    parse.add_argument('-s', required = True)
    parse.add_argument('-w', required = True, nargs = '+')
    parse.add_argument('-d')
    parse.add_argument('-l')
    parse.add_argument('-i')
    parse.add_argument('-c')
    
    args = parse.parse_args()
    tester = SearchFeatures(keyword = args.k, topic_search = args.s, words = args.w, 
                            dict_filepath = args.d, lda_filepath = args.l, 
                            index_filepath = args.i, create_index = args.c)