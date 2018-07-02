#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 19 11:09:38 2018

@author: s0k00rp
"""

from gensim.models import ldamodel
from gensim.models.coherencemodel import CoherenceModel
import pickle
from pymongo import MongoClient
from similarDoc import SimilarDoc


class TestingModel():
    
    def __init__(self, call_coherence, call_email_algebra, lda_filepath = None, texts_filepath = None, 
                 coherence_measure = None, create_cm = False, cm_filepath = None, 
                 first_id = None, second_id = None, addition = True, num = None):
        
        """
        Method that launches testing process. 
        
        :param {boolean} call_coherence:
            Determines whether or not we are checking the coherence model
        
        :param {boolean} call_email_algebra: 
            Determines whether or not we are checking the email algebra tests
        
        :param {str} lda_filepath: 
            Location of where LDA model is saved.
            
        :param {str} texts_filepath: 
            Location of where texts is saved. 
            
        :param {str} coherence_measure: 
            User passes in the measure they would like to use for the coherence model. 
        
        :param {boolean} create_cm:
            Whether or not a new coherence model must be made. 
            
        :param {str} cm_filepath: 
            Location of where to save or load the coherence model from. 
        
        :param {list of tuples} first_id: 
            ID of one of the email vectors that we are comparing. 
        
        :param {list of tuples} second_id: 
            ID of one of the email vectors that we are comparing. 
        
        :param {boolean} addition: 
            Determines whether or not we are doing addition or subtraction. 
            True: Doing addition
            False: Doing subtraction
        
        :param {int} num:
            Number of similar emails to return.
        
        """
         
        if eval(call_coherence): 
            self.lda = ldamodel.LdaModel.load(lda_filepath) 
            self.load_texts(texts_filepath)
            self.coherence_test(coherence_measure, cm_filepath, create_cm)
        
        if eval(call_email_algebra):
            client = MongoClient()
            document_topic_vectors = client['DocTopicVectors'].tVectors
            similar_emails_finder = SimilarDoc()
            self.email_algebra(document_topic_vectors, similar_emails_finder, first_id, second_id, addition, num)       
        
        
    def load_texts(self, filepath):
        """
        Load self.texts from a file it was saved to earlier.
        
        :param {str} filepath:
            Filepath of where to load information from. 

        """
        # filepath = '../../../Enron/Texts/texts.txt'
        
        with open(filepath, 'rb') as save:
            self.texts = pickle.load(save)
    
    
    def coherence_test(self, coherence_measure, cm_filepath, create_cm):
        """
        Generate coherence model and coherence for model and topics. 
        
        :param {str} coherence_measure: 
            Coherence measure the user wants to try. 
        
        :param {str} cm_filepath:
            Location of where the coherence model should be saved to. 
        
        :param {boolean} create_cm: 
            Whether or not a new coherence model must be made. 
        
        """
        
        if eval(create_cm):
            cm = CoherenceModel(model = self.lda, texts = self.texts, coherence = coherence_measure)
            cm.save(cm_filepath)
        else:
            cm = CoherenceModel.load(cm_filepath)
        model_coherence = cm.get_coherence()
        model_topics_coherence = cm.get_coherence_per_topic()
        print(model_coherence)
        print(model_topics_coherence)
    
    
    def test_model(self, cm_filepath, coherence_measure):
        cm1 = CoherenceModel(model = self.lda, texts = self.texts, coherence = coherence_measure)
        cm2 = CoherenceModel.load(cm_filepath)
        
        cm_equal = cm1.get_coherence() == cm2.get_coherence()
        print(cm_equal)


    def email_algebra(self, document_topic_vectors, similar_emails_finder, first_id, second_id, addition, num):
        """
        Start off email_algebra process. 
        
        :param {Collection} document_topic_vectors:
            Collection of document topic vectors from data stored in MongoDB. 
            
        :param {SimilarDoc} similar_emails_finder:
            Object to determine the similar emails. 
        
        :param {list of tuples} first_id: 
            ID of one of the email vectors that we are comparing. 
        
        :param {list of tuples} second_id: 
            ID of one of the email vectors that we are comparing. 
        
        :param {boolean} addition: 
            Determines whether or not we are doing addition or subtraction. 
            True: Doing addition
            False: Doing subtraction
        
        :param {int} num:
            Number of similar emails to return.
        
        """
        
        first_vec, second_vec = self.get_vectors(document_topic_vectors, first_id, second_id)
        
        diff_vec = self.vec_add_sub(first_vec, second_vec, addition)
        similar_emails, distances = similar_emails_finder.similar_from_topic_vector(diff_vec, num)
        
        for sim in similar_emails:
            print(sim)
        
        
    def get_vectors(self, document_topic_vectors, first_id, second_id):
        """
        Return the document topic vectors for the ID's passed in. 
        
        :param {Collection} document_topic_vectors:
            Collection of document topic vectors from data stored in MongoDB. 
            
        :param {list of tuples} first_id: 
            ID of one of the email vectors that we are comparing. 
        
        :param {list of tuples} second_id: 
            ID of one of the email vectors that we are comparing. 
        
        """
        first_vec = document_topic_vectors.find_one({'_id': first_id})
        second_vec = document_topic_vectors.find_one({'_id': second_id})
        return first_vec, second_vec
        
        
    def vec_add_sub(self, first_vec, second_vec, addition):
        """
        Determine the new vector we get by adding or subtraction the 2 starting vectors. 
        
        :param {list of tuples} first_vec: 
            One of the email vectors that we are comparing. 
        
        :param {list of tuples} second_vec: 
            One of the email vectors that we are comparing. 
        
        :param {boolean} addition: 
            Determines whether or not we are doing addition or subtraction. 
            True: Doing addition
            False: Doing subtraction
        
        """
        
        if addition:
            diff_vec = first_vec + second_vec
        else:
            diff_vec = first_vec - second_vec
        
        return diff_vec


if __name__ == "__main__":
    import argparse
    import sys
    if not len(sys.argv) > 1:
        raise ValueError("Whether or not creating new texts is a required argument")
    parser = argparse.ArgumentParser(description='Test LDA Model')
    parser.add_argument('-c', required = True)
    parser.add_argument('-y', required = True)
    parser.add_argument('-l', required = True)
    parser.add_argument('-t', required = True)
    parser.add_argument('-m')
    parser.add_argument('-mc')
    parser.add_argument('-cf')
    parser.add_argument('-f')
    parser.add_argument('-s')
    parser.add_argument('-a')
    parser.add_argument('-n')
    args = parser.parse_args()
    tester = TestingModel(call_coherence = args.c, call_email_algebra = args.a, lda_filepath = args.l, texts_filepath = args.t, 
                          coherence_measure = args.m, create_cm = args.mc, cm_filepath = args.cf, first_id = args.f, 
                          second_id = args.s, addition = args.a, num = args.n)
#    print("THE SAVING HAS FINISHED")
#    tester.fit_LDA(lda_filepath = args.l, pyldavis_filepath = args.p, num_topics = args.n)
#    print('finished')

#tester = TestingModel(True, False, lda_filepath = '../../../Enron/Tester/ldamodel_topics_35_folder/ldamodel_topics_35', 
#                      texts_filepath = '../../../Enron/Texts/original/texts.txt',
#                      coherence_measure = 'c_v', create_cm = True, 
#                      cm_filepath = '../../../Enron/Coherence/cv_topics_35.cv')
#tester.coherence_test('u_mass', '../../../Enron/Coherence/co1.cv')
