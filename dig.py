#!/usr/bin/env python3

from datetime import datetime
import json
import psycopg2
from urllib.parse import urlparse
import pydig


        
conn = None
try:
    conn = psycopg2.connect(" user=acd dbname=acd ")
except Error as err:
    print ("I am unable to connect to the database ", err)
    
cur = conn.cursor()
cur.execute("""SELECT netloc from cdn group by netloc""")
rows = cur.fetchall()

for r in rows:

    netloc = r[0]
    try:
        res = pydig.query(netloc, 'A')
    except Error as err:
        print ("Dig bailed out ", err)
        
    for a_record in res:
        data = {}
        data['netloc'] = netloc
        data['a_record'] = a_record
        cur.execute("""INSERT INTO dnsmap(netloc, a_record) VALUES (%(netloc)s, %(a_record)s)""", data)
    conn.commit()
