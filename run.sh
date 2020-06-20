$PATH=$PATH:/home/acd/.local/bin
pip3 install mitmproxy 
pip3 install psycopg2 

mitmproxy -s save_headers.py

