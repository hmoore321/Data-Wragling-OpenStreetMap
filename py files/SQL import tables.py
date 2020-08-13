#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# Make the tabels...
#https://datatofish.com/create-database-python-using-sqlite3/#:~:text=%20Steps%20to%20Create%20a%20Database%20in%20Python,2%3A%20Import%20the%20Data%20using%20Pandas%20More%20


import sqlite3
import csv
db = sqlite3.connect("OpenStreetMapSqlite.db")
cursor = db.cursor()
cursor.executescript('''
DROP TABLE IF EXISTS Nodes;
DROP TABLE IF EXISTS Nodes_tags;
DROP TABLE IF EXISTS Ways;
DROP TABLE IF EXISTS Ways_tags;
DROP TABLE IF EXISTS Ways_nodes;

CREATE TABLE nodes (
    id INTEGER PRIMARY KEY NOT NULL,
    lat REAL,
    lon REAL,
    user TEXT,
    uid INTEGER,
    version INTEGER,
    changeset INTEGER,
    timestamp TEXT
);

CREATE TABLE ways (
    id INTEGER PRIMARY KEY NOT NULL,
    user TEXT,
    uid INTEGER,
    version TEXT,
    changeset INTEGER,
    timestamp TEXT
);

CREATE TABLE nodes_tags (
    id INTEGER,
    key TEXT,
    value TEXT,
    type TEXT,
    FOREIGN KEY (id) REFERENCES nodes(id)
);

CREATE TABLE ways_tags (
    id INTEGER NOT NULL,
    key TEXT NOT NULL,
    value TEXT NOT NULL,
    type TEXT,
    FOREIGN KEY (id) REFERENCES ways(id)
);

CREATE TABLE ways_nodes (
    id INTEGER NOT NULL,
    node_id INTEGER NOT NULL,
    position INTEGER NOT NULL,
    FOREIGN KEY (id) REFERENCES ways(id),
    FOREIGN KEY (node_id) REFERENCES nodes(id)
);
''')

db.commit()
cursor.close()


# ### Imported .csv files using sqlite on my computer

# sqlite> .mode csv   <br>
# sqlite> .import nodes.csv nodes   <br>
# 
# Same process followed for the 4 remaining tabels:  <br>
# ways.csv  <br>
# nodes_tags.csv  <br>
# ways_tags.csv  <br>
# ways_nodes.csv  <br>
# 
# Next we will run some queries (I decided to run the queries from sqlite directly).  

# In[46]:


db = sqlite3.connect("OpenStreetMapSqlite.db")
c = db.cursor()
QUERY = "SELECT count(*) FROM nodes;"
c.execute(QUERY)
rows = c.fetchall()
print(f"Node count {rows}")
cursor.close()


# In[42]:


QUERY = "SELECT * FROM Nodes limit 5"
c.execute(QUERY)
results = c.fetchall()
print(results)


# In[48]:


db = sqlite3.connect("OpenStreetMapSqlite.db")
c = db.cursor()
QUERY = "SELECT count(*) FROM ways;"
c.execute(QUERY)
rows = c.fetchall()
print(f"Way count {rows}")
cursor.close()


# ### Function to find file sizes
# 
# Reference: https://appdividend.com/2020/05/15/three-ways-to-get-file-size-in-python/

# In[4]:


import os

def get_file_size(filename):
    file_size = os.path.getsize(filename)
    file_size_mb = file_size / (1024*1024)
    file_size_mb_r = round(file_size_mb, 2)
    note = f'{file_size_mb_r} MB {filename}'
    print(note)
    


# ### File Sizes

# In[5]:


get_file_size('example.osm')
get_file_size('OREM.osm')
get_file_size('OpenStreetMapSqlite.db')
get_file_size('nodes.csv')
get_file_size('nodes_tags.csv')
get_file_size('ways.csv')
get_file_size('ways_tags.csv')
get_file_size('ways_nodes.csv')


# In[ ]:




