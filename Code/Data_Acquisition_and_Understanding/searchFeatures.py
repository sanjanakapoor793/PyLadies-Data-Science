#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 17 13:53:01 2018

@author: Sanjana Kapoor
"""

from pymongo import MongoClient
#from pymongo import Connection
from gensim import models
from gensim.models import ldamodel
from gensim.corpora import Dictionary
from similarDoc import SimilarDoc
import operator

class SearchFeatures():
    
    def __init__(self, keyword, topic_search, words, dict_filepath = None, lda_filepath = None, 
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

#        self.similarSearch = similar
        if type(words) == str:
            self.words = words.split()
        else:
            self.words = words
        
        client = MongoClient()
        self.emailDB = client['EnronEmailData']
        self.emailCol = self.emailDB.emails
        
        self.emailCol.create_index([('content', 'text')])
#        self.emailCol.create_index([('_id', 'text')])
        
        
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

        
#        for r in results:
#            print(self.topicCol.find_one({'_id': r})['topic_values'])


        
    def word_topic_search(self, filepath, num):
        """
        Returns documents according to the prevalent topics in them. 

        :param {str} filepath: 
            Location of LDA Model
        
        :param {int} num:
            Number of documents to return. 
        
        Process: 
            1. Generate word topic vectors to see the topics most common in the words user inputs
            2. Consolidate them into one list that is sorted by the prevalence of the topic
            3. Generate the documents that are returned by keyword search with the entered words
            4. Gather the document topic vectors for those documents
            5. Sort topics for each document by highest prevalence
            6. Go through and compare the ideal word topic vectors to the document topic vectors. 
            7. If there is a match within the first 5 (or whatever it is later set to), add it to a 
            dict that records these matches and the frequency at which they occur
            8. Sort the dict so that the most frequent are at the top and then print out the top 
            self.num documents
        
        """
        print(self.words)
        # load LDA model for future use
        self.lda = models.ldamodel.LdaModel.load('../../../Enron/LDAResult/ldaModel', mmap = 'r')
        topics = [self.lda.get_term_topics(word) for word in self.words]
        contains_topics = False
        for topic in topics:
            if topic:
                contains_topics = True
        if not contains_topics:
            print('The words you searched for are not generating any related topics. ' + 
                  'Recommend doing a keyword search')
        else: 
            if len(self.words) == 1:
                # if there was only one word passed in, then we just need to go through the topics
                # found for that word
                ideal_topics = sorted(topics[0], key = lambda vector: vector[1], reverse = True)
                print(ideal_topics)   
            else:
                # if there are multiple words being passed in then we must sort all the topics out
                frequency = {}
                for topic in topics:
                    for element in topic:
                        try:
                            frequency[element[0]] += element[1]
                        except KeyError:
                            frequency[element[0]] = element[1]
                
                ideal_topics = sorted(frequency.items(), key = operator.itemgetter(1))
            
            rel_doc = self.generate_doc()
            good_doc = {}
            for list_doc in rel_doc:
                for doc_id_key, vector in rel_doc[list_doc].items():
                    # store the topic vectors for that document in the list
                    t = self.topicCol.find_one({'_id': doc_id_key})                        # retrieve the correct vector from the database
                    value = t['topic_values']                                             # grab the list of vectors                                                # print out
                                                        # store as 'score' in the dict                       
                    # sort to have most prominent topics in front 
                    value = sorted(value, key = lambda topic: topic[1], reverse = True)                                                    # place all prominent topics in a diff list
                    for counter in range(num):
                        one_topic = value[counter]
                        for topic in ideal_topics:
                            if one_topic[0] == topic[0]:
                                try:
                                    good_doc[doc_id_key] += 1
                                ## rewrite so it's more specific to the actual exception
                                except KeyError:
                                    good_doc[doc_id_key] = 1
                                break
                    
            if not good_doc:
                print('The words you searched for yielded many documents via keyword search. However, ' +
                      'the topics relevant to those documents did not match up with any of the ideal topics ' +
                      'your search words generated. Recommend using keyword search.')
            good_doc = sorted(good_doc.items(), key = operator.itemgetter(1), reverse = True)
            for counter in range(self.num):
                print(good_doc[counter][0])
                    

    def print_some_elements(self, list_elements, num_print):
        """
        Print a specific number of elements in the provided list.
        
        :param {list} list_elements:
            Sorted list of the elements to print
        
        :param {int} num_print:
            Number of elements from the list to print
        
        """
        list_iter = iter(list_elements)
        for counter in range(num_print):
            print(next(list_iter))


    def and_search(self):
        """
        Return documents that contain the words searched for. 
        
        Process:
            1. Generate the documents for which each word occurs
            2. Consolidate the 2D to a list that contains the documents
            in which all the words searched for occur. 
            3. Return the content for each of those documents
        
        """

        total_words = self.generate_doc()
        total_words_iter = iter(total_words)
        # set up result_keys with the first piece of data
        result_keys = total_words[next(total_words_iter)].keys()
        # grab the next word's data

        for passThru in range(len(total_words) - 1):
            temp_keys = total_words[next(total_words_iter)].keys()
            result_keys = result_keys & temp_keys
            # result_keys should contain the intersection of the keys in all the emails and the current email

        # at this point, result_keys is a set containing the _id's of the documents that contain all the words.  
        result = {}
        for key in result_keys:
            sum_key = 0
            # go through and sum up the relationship between word and document for each word in self.words
            # this will be that document's score
            for word_doc in total_words:
                sum_key += total_words[word_doc][key]
            result[key] = sum_key

        # sort the results
        f_result = sorted(result.items(), key = operator.itemgetter(1), reverse = True)
        f_result_iter = iter(f_result)
        for f_result_counter in range(self.num):
            print(next(f_result_iter))


        
    def generate_doc(self):
        """
        Place the documents that contain the word and their respective scores in a dict
        with the word as the key and the document/score distribution as a dict in the value
        
        :local {dict} total_word_doc: 
            Key: word (from self.texts)
            Value: word_doc
        
        :local {dict} word_doc: 
            Key: document_id
            Value: that document's score
        
        """
        total_word_doc = {}
        
        for word in self.words:
            result = self.emailCol.find({'$text': {'$search': word}}, {'score': {'$meta': 'textScore'}, "_id":1})
            # result is a large datastructure of dicts. Each dict contains the _id of the email and its score
            # for that word. 
            word_doc = {}
            # putting the data from result into word_doc
            # result is a cursor
            for doc_score in result:
                word_doc[doc_score['_id']] = doc_score['score']
            # add this to total_word_doc which is the final thing to be returned in this method
            total_word_doc[word] = word_doc
        return total_word_doc
    
    
    def intersection(self, list_docs):
        result = list_docs[0]
        counter = 1
        print('test2')
        while counter < len(list_docs):
            result = [doc for doc in list_docs[counter] if doc in result]
            counter += 1
         
            
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

# Example search
#x = SearchFeatures(False, True, 'game updated week team play', '../../../Enron/Tester/original/dictionary.dict', 
#                   '../../../Enron/Tester/ldamodel_topics_35/ldamodel_topics_35', '../../../Enron/Tester/original/index.hnsw')