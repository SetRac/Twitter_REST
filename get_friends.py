# -*- coding: utf-8 -*-
import csv
import sys
import time
import cPickle
import twitter
from twitter.oauth_dance import oauth_dance
from twitter__login import login

sys.stdout.flush()

########################### Read input ################################################
doc=open('data/input_friends.csv', 'r')
r=csv.reader(doc,delimiter=';',quotechar='"')
unames=[]
idnames=[]
for column in r:
    unames+=[column[0]]
    idnames+=[column[1]]

#unames=unames[1:]
#idnames=idnames[1:]

doc.close()
#######################################################################################
w=open('data/output_friends.csv', 'a')
csv_w=csv.writer(w , delimiter=';',quotechar='"',quoting=csv.QUOTE_ALL)    


t=login()

x=0
while x < len(unames):  
    SCREEN_NAME = unames[x]

    ids = []
    wait_period = 2  # secs
    cursor = -1

    while cursor != 0:
        if wait_period > 3600:  # 1 hour
            print >> sys.stderr, \
                'Too many retries. Saving partial data to disk and exiting'
            f = file('%s.friend_ids' % str(cursor), 'wb')
            cPickle.dump(ids, f)
            f.close()
            exit()

        try:
            response = t.friends.ids(screen_name=SCREEN_NAME, cursor=cursor)
            ids.extend(response['ids'])
            wait_period = 2
        except twitter.api.TwitterHTTPError, e:
            if e.e.code in (401,404):
                print >> sys.stderr, 'User %s is protecting tweets may have changed the username or does not exist any more' % (SCREEN_NAME, )

            elif e.e.code in (502, 503):
                print >> sys.stderr, \
                    'Encountered %i Error. Trying again in %i seconds' % \
                    (e.e.code, wait_period)
                time.sleep(wait_period)
                wait_period *= 1.5
                continue
            #elif t.account.rate_limit_status()['remaining_hits'] == 0:
                #status = t.account.rate_limit_status()
                #now = time.time()  # UTC
                #when_rate_limit_resets = status['reset_time_in_seconds']  # UTC
                #sleep_time = when_rate_limit_resets - now
                #print >> sys.stderr, \
                    #'Rate limit reached. Trying again in %i seconds' % (sleep_time,)
                #time.sleep(sleep_time)
            elif e.e.code==429:
                sleep_time=900

                print time.strftime("%Y.%m.%d %H:%M:%S"),'Rate limit reached. Trying again in 900 seconds'
                time.sleep(sleep_time)
                continue
            else:
                raise e # Best to handle this on a case by case basis

        cursor = response['next_cursor']
        
    for i in ids:
        row=[idnames[x],str(i)]
        csv_w.writerow(row) 

    print "Fetched",len(ids),"ids for",SCREEN_NAME,"on line",x+1,"of",len(unames)
    x+=1

print ""
print time.strftime("%Y.%m.%d %H:%M:%S"),"Done!"
