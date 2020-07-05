# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START gae_python38_app]
from flask import Flask
from flask import request
import json
import pprint
import sys
from urllib.parse import urlparse
from flask import render_template
from google.cloud import storage
import time
import argparse
import pprint
pp = pprint.PrettyPrinter(indent=4)

from haralyzer import HarParser, HarPage

def linkify(url):
    """takes a URL and returns the HTML for a link to the URL"""
    # url = "url to make into an HTML link"
    hyperlink_format = '<a href="{link}">{text}</a>'
    return hyperlink_format.format(link=url, text=url)
    
def upload_blob(bucket_name, stuff, destination_blob_name):
    """Uploads a file to the bucket."""
    # bucket_name = "your-bucket-name"
    # source_file_name = "local/path/to/file"
    # destination_blob_name = "storage-object-name"

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_string(stuff)
    
def parse_file(f):
    har_parser = HarParser(json.loads(f))

    rows = [['X-CACHE-HEADER', 'BYTES', 'URL']]

    hosts = {}
    size = {}
    total_bytes = 0 #total bytes for all content across the entire thing 

    for page in har_parser.pages:
        assert isinstance(page, HarPage)
        for entry in page.entries:
            cdn = []
            headers = entry['response']['headers']
            #print(entry['response'], file=sys.stderr)
            cdn_str = None
            total_bytes += entry['response']['content']['size']
            #pp.pprint(entry['request'])
            url = urlparse(entry['request']['url'])
            for h in headers: 
                if( h['name'] == 'x-cache'):
                    hosts[url.netloc] = 1
                    #print(url, file=sys.stderr)
                    cdn_str = h['value']
                    cdn.append(cdn_str)
            
            if( cdn_str in size ):
                size[cdn_str] = size[cdn_str] + entry['response']['content']['size']
            else:
                size[cdn_str] = entry['response']['content']['size']
            print("\t".join([str(cdn), str(entry['response']['content']['size']), entry['request']['url'], url.netloc]))
            rows.append([cdn, entry['response']['content']['size'], linkify(entry['request']['url'])])
    
    bysize = [['CACHE TAG', '% OF BYTES']]
    for sk in size.keys():
        bysize.append( [sk,  "{:.1%}".format(size[sk] / total_bytes)] )
        
        bysize_t = list(map(list, zip(*bysize))) 
        hosts_t = list(map(list, zip(*[hosts.keys()]))) 
    return {'total_bytes':total_bytes, 'hosts_t':hosts_t, 'bysize':bysize, 'rows':rows}    
    #return json.dumps([hosts, size, rows])
    

# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = Flask(__name__)

@app.route('/')
def write_form():
    """Render landing page with instructions and form to upload an HAR file"""
    return render_template('form.html', title='Home')
    
@app.route('/upload_file', methods=['POST'])
def upload_file():
    """Process the uploaded file. Save a copy to a cloud bucket. Then parse out the headers and grab the x-cache headers that show which CDN it loaded from"""
    f = request.files['yourFileName'].read()
    try:
        ts = time.time()
        upload_blob('cdninfolyzer.appspot.com', f, "data/" + str(ts))
    except Exception as e:
        print (e)
    r = parse_file(f)
    return render_template('results.html', titles=['', 'Total bytes', 'Hosts', 'By Service', 'Results' ], tables=[[['Total bytes:', r['total_bytes']]],r['hosts_t'], r['bysize'], r['rows']])
    
@app.route('/list_files')
def do_list_files():
    """Lists all buckets."""


    """Lists all the blobs in the bucket."""
    # bucket_name = "your-bucket-name"

    storage_client = storage.Client()

    # Note: Client.list_blobs requires at least package version 1.17.0.
    blobs = storage_client.list_blobs("cdninfolyzer.appspot.com" ,prefix="data/")

    blist = []

    for blob in blobs:
        blist.append(blob.name)

    return str(blist)
    
@app.route('/results')
def do_results():
    """display static results page"""
    return render_template('all_results.html', title='Home')

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='process session files')
    parser.add_argument('--bulk', nargs='+', type=open, help='upload all files matching to database')
    args = parser.parse_args()

    
    if args.bulk:
        print ("bulk")
        
        for a in args.bulk:
        
            #print ( parse_file (a.read())['bysize'] , file=sys.io.stderr)
            try: 
                print ( parse_file (a.read())['bysize'] , file=sys.io.stderr)
            except Exception as e:
                print (e)
            
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    else:
        app.run(host='127.0.0.1', port=8080, debug=True)
# [END gae_python38_app]
