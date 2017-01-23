from jinja2 import Environment, FileSystemLoader
import os
import sqlite3

env = Environment(loader=FileSystemLoader('templates'))
template = env.get_template('index.html')

conn = sqlite3.connect('/home/xx/channels.sqlite3')
cur = conn.cursor()
query = 'SELECT id, name, sid FROM channels WHERE fav = {} LIMIT 40'.format('1')
cur.execute(query)

streamlst2 = dict()
with conn:
    rows = cur.fetchall()
    for i,n,s in rows:
        #print i,n,s
        n = n.replace(' ', '_')
        streamlst2[i] = [n,s]



pidPath = "/var/run/mumudvb/"
i = 0

streamlst = list()
for file in os.listdir(pidPath):
    if file.startswith("channels_streamed_adapter"):
        fh = open(pidPath+file)
        for stream in fh:
            strm = stream.strip().split(':')
            channelName = strm[2]
            strm[2] = channelName.replace(' ','_')
            #strm[2] = strm[2].replace('+','\+')
            streamlst.append(strm)

#for i in streamlst2:
#    print i

#print template.render(streamlst=streamlst2)

template = env.get_template('bs.html')
print template.render(streamlst=streamlst2)
