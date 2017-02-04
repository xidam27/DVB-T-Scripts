from jinja2 import Environment, FileSystemLoader
import sqlite3

env= Environment(loader=FileSystemLoader('templates'))
lsyncd_template = env.get_template('lsyncd.conf')

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

print lsyncd_template.render(streamlst=streamlst2)
