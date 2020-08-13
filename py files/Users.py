#!/usr/bin/env python
# coding: utf-8

# # Explore Users

# Code from the case study in the lesson. We used this code to explore the unique users in the dataset.

# In[ ]:


import xml.etree.cElementTree as ET
import pprint
import re

def get_user(element):
    return 
#    return element.get('user')

def process_map_users(filename):
    users = set()
    for _, element in ET.iterparse(filename):
        for x in element:
            if "user" in x.attrib:
                users.add(x.attrib["user"])
    return users

def find_users(filename):

    users = process_map_users(filename)
    pprint.pprint(len(users))
    pprint.pprint(users)
#    assert len(users) == 6

