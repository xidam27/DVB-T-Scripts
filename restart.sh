#!/bin/bash
killall ffmpeg -9; python startFFmpeg.py 2 | sh
echo "killall ffmpeg" |ssh encoder.cdn ; sleep 2 ;python startFFmpeg.py 1 | ssh encoder.cdn
python genPlayer.py | ssh encoder.cdn 'cat > /var/www/index.html'
python genPlayer.py | ssh tv-head.cdn 'cat > /var/www/index.html'
sleep 2
#echo 'screen -r | grep -v screen | grep -v ONE| cut -d. -f 1 | xargs kill' | ssh encoder.cdn

