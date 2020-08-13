#!/usr/bin/env python
# coding: utf-8

# # Import libraries

# In[1]:


import csv
import codecs
import pprint
import re
from collections import defaultdict
from collections import Counter
import xml.etree.cElementTree as ET
import cerberus
import schema
import sqlite3

#FILENAME = "example.osm" #real file is OREM.OSM


# # Audit State & Clean State

# In[13]:


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


# In[14]:


audit_states('example.osm')


# Update/Clean up states

# In[15]:


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


# # audit & update - street names

# In[16]:


#import xml.etree.cElementTree as ET
#from collections import defaultdict
#import re
#import pprint

#osmfile = "example.osm"
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)


expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons"]

# UPDATE THIS VARIABLE
mapping = { "St": "Street", "St.": "Street", "street": "Street",
            "Ave": "Avenue", 
            "Rd": "Road", "Rd.": "Road",
            "Dr": "Drive", "DrIve": "Drive",
            "Pkwy": "Parkway",
            "lane": "Lane",
            "Grove)": "Grove",
            "N.": "North", "N": "North",
            "E": "East",
            "S": "South",
            "W": "West"
          }

def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)

def audit_street_type2(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        street_types[street_type] += 1
            
def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")

def is_street_name2(elem):
    return (elem.tag == "tag") and (elem.attrib['k'] == "addr:street")

def print_sorted_dict(d):
    keys = d.keys()
    keys = sorted(keys, key=lambda s: s.lower())
    for k in keys:
        v = d[k]
        print("%s: %d" % (k, v))
    
def audit(osmfile):    #All street shown in a dictionary (to see all values)
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])             
    osm_file.close()
    return street_types

def audit2(osmfile):    #The different street types and how often they appear in the data (to see summary)
    osm_file = open(osmfile, "r")
    street_types = defaultdict(int)
    for event, elem in ET.iterparse(osm_file):
        if is_street_name2(elem):
            audit_street_type2(street_types, elem.attrib['v'])    
    print_sorted_dict(street_types)    
    osm_file.close()

#if __name__ == '__main__':
#    audit('example.osm')


# Check how many street types we are working with, and run the audits (full detail & Summary level).

# In[19]:


audit2('example.osm')   #Summary detail


# Update/Clean for street type

# In[20]:


def update_name(name, mapping):
    m = street_type_re.search(name)
    if m.group() in mapping.keys():
        name = name[:len(name)-len(m.group())] + mapping[m.group()]
    return name
    
def update_street_type(street_name, mapping):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            print street_type
            street_name = update_name(street_name, mapping)
            print street_name
    return street_name


# # data.py  (shape_element function, etc...)

# In[275]:


#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
After auditing is complete the next step is to prepare the data to be inserted into a SQL database.
To do so you will parse the elements in the OSM XML file, transforming them from document format to
tabular format, thus making it possible to write to .csv files.  These csv files can then easily be
imported to a SQL database as tables.

The process for this transformation is as follows:
- Use iterparse to iteratively step through each top level element in the XML
- Shape each element into several data structures using a custom function
- Utilize a schema and validation library to ensure the transformed data is in the correct format
- Write each data structure to the appropriate .csv files

We've already provided the code needed to load the data, perform iterative parsing and write the
output to csv files. Your task is to complete the shape_element function that will transform each
element into the correct format. To make this process easier we've already defined a schema (see
the schema.py file in the last code tab) for the .csv files and the eventual tables. Using the 
cerberus library we can validate the output against this schema to ensure it is correct.
"""
#ALREADY IMPORTED THESE AT THE TOP, LEAVING THESE IN JUST IN CASE WE RUN THIS SEPARATE.
import csv
import codecs
import pprint
import re
import xml.etree.cElementTree as ET
import cerberus
import schema

#OSM_PATH = "OREM.osm"   #real file
OSM_PATH = "example.osm" #sample file 

NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

SCHEMA = schema.schema

# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']


def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way elements

    # YOUR CODE HERE

    #node field, loop node field header looking for key properties which will be placed in the node attribs dictionary.
    if element.tag == 'node':
        for x in NODE_FIELDS:
            node_attribs[x] = element.attrib[x]
    #looping through the child to the tag element values. 
        for child in element:
            ca_k = child.attrib["k"]
            ca_v = child.attrib["v"]
            ea_id = element.attrib["id"]
            n_tags = {} 
#another way - per google sheet
#            if PROBLEMCHARS.match[ca_k]):
            if re.match(PROBLEMCHARS,ca_k):   
                continue 
            elif re.match(LOWER_COLON,ca_k):  
                n_tags["id"] = ea_id
                n_tags["key"] = ca_k.split(":",1)[1]

# next 6 lines are the cleaning function
                if ca_k == "addr:street":       #use cleaning function
                    n_tags["value"] = update_street_type(ca_v, mapping)
                elif ca_k == "addr:state":
                    n_tags["value"] = update_state_name(ca_v, mapping_states)  
                else:  #otherwise process as normal
                    n_tags["value"] = ca_v 
                n_tags["type"] = ca_k.split(":",1)[0]
                tags.append(n_tags)
            else:
                n_tags["id"] = ea_id
                n_tags["key"] = ca_k
                n_tags["value"] = ca_v
                n_tags["type"] = 'regular'
                tags.append(n_tags)

    elif element.tag == 'way':
        for x in WAY_FIELDS:
            way_attribs[x] = element.attrib[x]
        w_position = 0 
        for child in element:
            nd_w_nodes = {} 
            w_tags = {}  
            ea_id = element.attrib["id"]
            if child.tag == 'nd':
                nd_w_nodes["id"] = ea_id
                nd_w_nodes["node_id"] = child.attrib["ref"]
                nd_w_nodes["position"] = w_position
                w_position = w_position+1
                way_nodes.append(nd_w_nodes)
            elif child.tag == 'tag':
                ca_k = child.attrib["k"]
                ca_v = child.attrib["v"]
                if re.match(PROBLEMCHARS,ca_k):
                    continue  #do nothing!
                elif re.match(LOWER_COLON,ca_k):
                    w_tags["id"] = ea_id
                    w_tags["key"] = ca_k.split(":",1)[1]
# next lines are my cleaning function
                    if ca_k == "addr:street":       #use cleaning function
                        w_tags["value"] = update_street_type(ca_v, mapping)
                    elif ca_k == "addr:state":
                        w_tags["value"] = update_state_name(ca_v, mapping_states)  
                    else:  #otherwise process as normal
                        w_tags["value"] = ca_v
                    w_tags["type"] = ca_k.split(":",1)[0]
                    tags.append(w_tags)
                else:
                    w_tags["id"] = ea_id
                    w_tags["key"] = ca_k
                    w_tags["value"] = ca_v
                    w_tags["type"] = 'regular'
                    tags.append(w_tags)

    if element.tag == 'node':
        return {'node': node_attribs, 'node_tags': tags}
    elif element.tag == 'way':
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}


# ================================================== #
#               Helper Functions                     #
# ================================================== #
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)
        
        raise Exception(message_string.format(field, error_string))


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file,          codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file,          codecs.open(WAYS_PATH, 'w') as ways_file,          codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file,          codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


if __name__ == '__main__':
    # Note: Validation is ~ 10X slower. For the project consider using a small
    # sample of the map when validating.
    process_map(OSM_PATH, validate=True)

