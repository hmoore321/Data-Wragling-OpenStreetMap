#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import xml.etree.cElementTree as ET
import pprint

def count_tags(filename):  #(filename)
    my_tags = {}
    for event, child in ET.iterparse(filename):
        tag = child.tag
        if tag not in my_tags.keys():
            my_tags[tag] =1
        else:
            my_tags[tag] +=1
    return my_tags

count_tags('example.osm')

