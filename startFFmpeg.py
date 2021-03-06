import glob, os
import sqlite3
import sys, getopt

pidPath = "/var/run/mumudvb/"
conn = sqlite3.connect('channels.sqlite3')
cur = conn.cursor()

mode = int(sys.argv[1])
def findPid():
    i = 0
    for file in os.listdir(pidPath):
        if file.startswith("channels_streamed_adapter"):
            fh = open(pidPath+file)
            for stream in fh:
                i = i+1
                strm = stream.split(':')
                channelName = strm[2]
                channelName = channelName.replace(' ','_')
                cmd = '''
screen -dmS {} \\
sh -c \'mkdir -p /var/www/content/{}; \\
~/bin/ffmpeg -i "udp://@{}?overrun_nonfatal=1&fifo_size=50000000" \\
-flush_packets 0 \\
-c:v libx264  \\
-preset slow \\
-bsf:v h264_mp4toannexb \\
-vf yadif -strict -2  \\
`#-tune zerolatency` \\
-break_non_keyframes 1 \\
-preset superfast \\
-c:a libfdk_aac  \\
-map 0:0 -map 0:1 \\
-flags \\
+global_header \\
-f segment -segment_format mpegts \\
-segment_list "/var/www/content/{}/playlist.m3u8" \\
-segment_list_type m3u8 \\
-segment_list_flags live \\
`#-segment_list_size 5` \\
-segment_time 15 \\
/var/www/content/{}/segment%03d.ts -y\''''.format(channelName,channelName,\
strm[0]+':'+strm[1],\
channelName,\
channelName)
                cmd = '''screen -dmS {} sh -c 'export FFREPORT=file=/tmp/{}_ffreport.log:level=32; mkdir -p /var/www/content/{}; ~/bin/ffmpeg -report -nostats \\
-i "udp://localhost:{}?overrun_nonfatal=1&fifo_size=50000000&pkt_size=1316&buffer_size=400000" \\
-flush_packets 0 \\
-threads 0 \\
`#-c:v libx264 -tune zerolatency -preset superfast` \\
`#-c:v mpeg2video -qscale:v 2 ` \\
-c:v libx264  -profile:v baseline  -strict -2 -crf 8 -maxrate 2200k -bufsize 4835k -pix_fmt yuv420p -flags -global_header -level 4.0 -preset slow \\
-vf yadif -strict -2 -vf scale=iw*.5:ih*.5 \\
-c:a libfdk_aac \\
-bsf:v h264_mp4toannexb -map 0:0 -map 0:1 \\
-flags -global_header \\
-f segment -segment_format mpegts \\
-segment_list "/var/www/content/{}/playlist.m3u8" \\
-segment_list_type m3u8 \\
-segment_list_flags live \\
-segment_list_size 10 \\
-bsf:v h264_mp4toannexb \\
-segment_time 5 \\
/var/www/content/{}/segment_%03d.ts -y\''''.format(channelName, channelName, channelName,int(strm[1])+i,channelName,channelName)

                cmd2 = '''
screen -dmS {} sh -c \'mkdir -p /var/www/content/{}; \\
~/bin/ffmpeg -i "udp://@{}?overrun_nonfatal=1&fifo_size=50000" \\
-flush_packets 0 \\
-c:v copy \\
-c:a copy \\
-f mpegts \\
udp://encoder.cdn:{} -y\''''.format(channelName,channelName,\
strm[0]+':'+strm[1],\
int(strm[1])+i)
                if mode == 2: cmd = cmd2
                query = 'SELECT id, name, sid FROM channels WHERE name = "{}" AND fav = {} LIMIT 1'.format(strm[2], '1')
                cur.execute(query)
                #print query
                row = cur.fetchone()
                #print row
                if not row is None:
                    print cmd
    return None

findPid()



"""
cmd = 'screen -dm ~/bin/ffmpeg -i \
"udp://@{}?overrun_nonfatal=1&fifo_size=50000000" \
-flush_packets 0 -c:v libx264 -preset fast -c:a copy -map 0:0 \
-map 0:1 -flags -global_header -f hls -segment_time 10 -segment_format mpegts \
-segment_list "/var/www/manifest.m3u8" -segment_list_type m3u8 \
-hls_flags delete_segments -segment_list_flags live \
-hls_list_size 5 -bsf:v h264_mp4toannexb \
-hls_time 5 /var/www/{}.m3u8 -y'.format(strm[0]+':'+strm[1],channelName)


"""
