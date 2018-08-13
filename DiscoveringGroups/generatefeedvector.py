# -*- coding: utf-8 -*-
"""
Created on Thu Aug  9 16:11:36 2018

@author: Administrator
"""

import feedparser
import re

def getwordcounts(url):
    
    d = feedparser.parse(url)
    wc = {}
    
    for e in d.entries:
        if 'summary' in e:
            summary = e.summary
        else:
            summary = e.description
    
        words = getwords(e.title+' '+summary)
        for word in words:
            wc.setdefault(word,0)
            wc[word] += 1
    return d.feed.title,wc

def getwords(html):
    txt = re.compile(r'<[^>]+>').sub('',html)
    words = re.compile(r'[^A-Z^a-z]+').split(txt)
    return [word.lower() for word in words if word!='']



apcount = {}
wordcounts = {}
with open('feedlist.txt') as f:
    feedlist = f.readlines()
    
for feedurl in feedlist:
    print(feedurl)
    title,wc = getwordcounts(feedurl)
    wordcounts[title] = wc
    for word, count in wc.items():
        apcount.setdefault(word,0)
        if count > 1:
            apcount[word] += 1
                   
wordlist = []
for w,bc in apcount.items():
    frac=float(bc)/len(feedlist)
    if frac>0.2 and frac<0.5:
        wordlist.append(w)
    
with open('blogdata.txt','w') as f1:
    f1.write('Blog')
    for word in wordlist:
        f1.write('\t%s' %word)
    f1.write('\n')
    for blog,wc in wordcounts.items():
        f1.write(blog)
        for word in wordlist:
            if word in wc:
                f1.write('\t%d' %wc[word])
            else:
                f1.write('\t0')
        f1.write('\n')
    
    
    