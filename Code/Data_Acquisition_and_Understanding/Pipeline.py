#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  2 17:01:24 2018

@author: Sanjana Kapoor
"""



class Pipeline():
    
    def __init__(self, *steps):
        self.steps = steps
    
    
    def apply(self, result):
        for step in self.steps:
            result = step.apply(result)
        # probably won't need this line.
        return result