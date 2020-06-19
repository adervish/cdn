from datetime import datetime
import json
import psycopg2
from urllib.parse import urlparse


class AddHeader:
    def __init__(self):
        self.num = 0

    def response(self, flow):
        
        try:
            conn = psycopg2.connect(" host='localhost' ")
        except:
            print ("I am unable to connect to the database")
        
        f = open("headers.log", "w")
        #print (flow.request.url, file=f)
        headers = flow.response.headers 
        cdn = None
        for h in headers: 
            if h == 'x-cache':
                cdn = headers[h];
        cur = conn.cursor()
        url = urlparse(flow.request.url)
        data = {'time':datetime.now().isoformat(), 'cdn':cdn, 'url':flow.request.url, 'netloc':url.netloc, 'size':str(len(flow.response.raw_content))}
        
        #log to file 
        print(json.dumps(data), file=f)
        
        #insert to PG
        cur.execute("""INSERT INTO cdn(t,cdn,url,netloc,size) VALUES (%(time)s, %(cdn)s, %(url)s, %(netloc)s, %(size)s)""", data)
        conn.commit()
                #print ( "\t".join(data), file=f)

addons = [
    AddHeader()
]