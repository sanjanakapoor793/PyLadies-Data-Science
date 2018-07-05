#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  2 17:01:24 2018

@author: s0k00rp
"""



class Pipeline():
    
    def __init__(self, *args):
        self.steps = args
    
    
    def apply(self, result):
        for step in self.steps:
            result = step.apply(result)
        # probably won't need this line. just so i can get rid of that warning
        return result