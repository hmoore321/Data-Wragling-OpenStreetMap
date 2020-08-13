#!/usr/bin/env python
# coding: utf-8

# # Audit State & Clean State

# This is the auditing and cleaning function for the State. This checks the "addr:state" element attribute to see what was entered. We want only "UT" to be entered.
# <br>
# However, upon running this code, we found 3 other variations had been used and needed to be cleaned.

# In[ ]:


#auditing

import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

#Reference: https://www.tutorialspoint.com/counters-in-python

def audit_states(osmfile):
    state_list =[]
    osm_file = open(osmfile, "r")
    for event,element in ET.iterparse(osmfile):      
        for elem in element.iter("tag"):
            if elem.attrib['k'] == "addr:state":
                state_list.append(elem.attrib['v'])
    pprint.pprint(Counter(state_list))
    osm_file.close()


# In[ ]:


#Checking our data with our new function
audit_states('example.osm')


# In[ ]:


#Cleaning the data, we have an expected list, which in this case only has 1 item == UT
#Then we have our mapping dictionary. We map out the incorrect entries ("Utah", "Ut", and "ut") and will change them to "UT"

state_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

expected_states = ["UT"]

mapping_states = { "Utah": "UT", "Ut": "UT", "ut": "UT"}

def update_state(name, mapping_states):
    m = state_re.search(name)
    if m.group() in mapping_states.keys():
        name = name[:len(name)-len(m.group())] + mapping_states[m.group()]
    return name
    
def update_state_name(state_name, mapping_states):
    m = state_re.search(state_name)
    if m:
        state = m.group()
        if state not in expected_states:
            print state
            state_name = update_name(state_name, mapping_states)
            print state_name
    return state_name

