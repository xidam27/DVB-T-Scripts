import glob
import os, os.path
import sqlite3
from collections import defaultdict

head_id = 1

mhz = dict()
mumu_conf = dict()

channels = '/usr/local/etc/channels_w_scan.list'
mumu_config_default_config_file = '/etc/default/mumudvb'
devpath = '/dev/dvb/adapters/'
mumu_conf_template = '''card={card}
card_dev_path=/dev/dvb/adapters/%card
freq={freq}
bandwidth=8MHz
autoconfiguration=full
multicast=0
multicast_ipv4=0
multicast_ipv6=0
unicast=1
ip_http=0.0.0.0
port_http={port}
autoconf_sid_list={sids}
'''
import MySQLdb

fh = open(channels)
#conn = sqlite3.connect('channels.sqlite3')
conn = MySQLdb.connect(user="root", passwd="x",db="seedious")

cur = conn.cursor()
cur.execute("SELECT hostname FROM heads WHERE id = %s", (head_id ,))
row = cur.fetchone()
print "Your Hostname is: ", row[0]

for line in fh:
    values = line.strip().split(':')
    if int(values[10].split('=')[0]) > 1:
        #print values
        sid = values[9]
        #print values[1]
        if int(values[1]) != 498000: continue
        print values[1] ## generating config based on DB entries
        
        channelName = values[0].replace(";(null)","")
        query=("SELECT name,sid FROM channels WHERE name = '{}'").format(channelName)
        cur.execute(query)
        if cur.rowcount == 0:
            query = ('INSERT INTO channels (name,freq,sid) VALUES\
            ("{}", {}, {})'.format(channelName,int(values[1]),sid))
            cur.execute(query)
conn.commit()

freqs = dict()
string = 'SELECT name,sid,freq FROM channels WHERE status = 1'
cur.execute(string)
for row in cur: # adding SIDs to their corresponding freq 
    freq = row[2]
    sid = row[1]
    if freq in freqs:
        # append the new number to the existing array at this slot
        freqs[freq].append(sid)
    else:
        # create a new array in this slot
        freqs[freq] = [sid]


tuners = glob.glob("/dev/dvb/adapters/*")

def generateConfig():
    i = 0
    global mumu_conf_template
    for mhz in freqs:
        if i >= len(tuners): break
        dev = tuners[i][-1:] # get the int id from /dev/dvb/adapterX
        sids = freqs[mhz]
        sids = ' '.join(str(x) for x in sids) # iterating the sids into a joined comma separated string
        conf = mumu_conf_template.format(freq=mhz, card=dev, port=str(8000+i), sids=sids, dev=tuners[i]) 
        mumu_conf['tuner'+str(i)] = conf
        i = i + 1
    return mumu_conf
mumu_conf = generateConfig()


adapters= ' '.join(str(x) for x in range(len(tuners)))
mumu_default_config = """
DAEMONUSER="_mumudvb"
ADAPTERS="{}"
""".format(adapters)



for adapter in tuners:
    adapter = adapter.split("/")[-1]
    mumu_config_file="/etc/mumudvb/mumu_adapter{}.conf".format(adapter)
    mumu_default_config = mumu_default_config + \
        "MUMUDVB_CONF_{}={}\n".format(adapter,mumu_config_file)
    fh = open(mumu_config_file,'w+l')
    fh.write(mumu_conf['tuner'+str(adapter)])
    fh.close()


fh = open(mumu_config_default_config_file,'w+')
fh.write(mumu_default_config)
fh.close()
