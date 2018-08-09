# -*- coding: utf-8 -*-
"""
Created on Wed Aug  8 16:24:40 2018

@author: Administrator
"""
import numpy as np

critics = {
        'Lisa':{'Lady in the water':2.5, 'Snake on a Plane':3.5,
                'Just my luck':3.0, 'Superman returns':3.5,
                'You,me and dupree':2.5, 'The night listener':3.0},
        'Gene':{'Lady in the water':3.0, 'Snake on a Plane':3.5,
                'Just my luck':1.5, 'Superman returns':5.0,
                'You,me and dupree':3.5, 'The night listener':3.0},
        'Michael':{'Lady in the water':2.5, 'Snake on a Plane':3.0,
                'Superman returns':3.5, 'The night listener':4.0},
        'Claudia':{'Snake on a Plane':3.5,
                'Just my luck':3.0, 'Superman returns':4.0,
                'You,me and dupree':2.5, 'The night listener':4.5},
        'Mick':{'Lady in the water':3.0, 'Snake on a Plane':4.0,
                'Just my luck':2.0, 'Superman returns':3.0,
                'You,me and dupree':2.0, 'The night listener':3.0},
        'Jack':{'Lady in the water':3.0, 'Snake on a Plane':4.0,
                'Superman returns':5.0,
                'You,me and dupree':3.5, 'The night listener':3.0},
        'Toby':{'Snake on a Plane':4.5, 'Superman returns':4.0,
                'You,me and dupree':1.0}
        }
        
        
def sim_distance(prefs,p1,p2):
    si = {}
    for item in prefs[p1]:
        if item in prefs[p2]:
                si[item]=1
    if len(si)==0:
        return 0
    sum_of_squares = sum([pow(prefs[p1][item]-prefs[p2][item],2)
                        for item in prefs[p1] if item in prefs[p2]])
    return 1/(1+np.sqrt(sum_of_squares))


def sim_pearson(prefs,p1,p2):
    si = {}
    for item in prefs[p1]:
        if item in prefs[p2]:
            si[item]=1
    if len(si)==0:
        return 0
    p1_filter = [prefs[p1][it] for it in si]
    p2_filter = [prefs[p2][it] for it in si]
    return np.corrcoef(p1_filter,p2_filter)[1,0]

#Ranking the Critics
def top_matches(prefs, person, n=5, similarity=sim_pearson):
    others = [it for it in prefs if it!=person]
    scores = [(similarity(prefs,person,other),other) for other in others]
    scores.sort()
    scores.reverse()
    return scores[0:n]

#Recommending items
def getRecommendations(prefs, person, similarity=sim_pearson):
    '''Grade unseen items and make recommendaions'''
    totals = {}
    weights = {}
    for other in prefs:
        if other == person:
            continue
        sim = similarity(prefs, person, other)
        if sim<=0:
            continue
        
        for item in prefs[other]:
            #Only comment on unseen movies
            if item not in prefs[person] or prefs[person][item]==0:
                totals.setdefault(item,0)
                totals[item] += prefs[other][item]*sim
                weights.setdefault(item,0)
                weights[item] += sim
    
    rankings = [(totals[item]/weights[item],item) for item in totals]
    rankings.sort()
    rankings.reverse()
    return rankings
                

#Matching products
def transformPrefs(prefs):
    '''This function is used to transform keys and values in prefs
    so as to evaluate similarity of items and matching products using 
    top_matches(prefs, person, ...) '''
    result = {}
    for person in prefs:
        for item in prefs[person]:
            result.setdefault(item,{})
            result[item][person] = prefs[person][item]
    return result
    


