#!/bin/bash
LOGFILE=~/ecoguard/db-persister.log  
MAXLOGSIZE=8*1024000 # 8 MiB
MAXLOGDAYS=90  

# Rotate the log if it's larger than MAXLOGSIZE
if [[ $(stat -c%s "$LOGFILE") -ge $MAXLOGSIZE ]]; then
    mv "$LOGFILE" "$LOGFILE.$(date +'%Y%m%d')"  
    gzip "$LOGFILE.$(date +'%Y%m%d')"  
fi

# Remove logs older than MAXLOGDAYS
find $(dirname "$LOGFILE") -name "$(basename "$LOGFILE").*" -mtime +$MAXLOGDAYS -exec rm {} \;

unbuffer python3 ~/ecoguard/db-persister.py 2>&1 | unbuffer -p ts '%Y-%m-%d %H:%M:%S' | tee -a ~/ecoguard/db-persister.log
