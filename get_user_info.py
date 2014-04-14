# -*- coding: utf-8 -*-
import time
import sys
import csv
import json
import codecs
import cStringIO


from recipe__oauth_login import oauth_login
from recipe__make_twitter_request import make_twitter_request

sys.stdout.flush()

##this script has been modified to fullfill my needs for dmi Summer School and later for more general pruposes 01.08.2013



###########################################################################################
###########################################################################################

#this class is added in order to print descriptions and other fields usually containing unicode characters
class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect,delimiter=';',quotechar='"',quoting=csv.QUOTE_ALL, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])

        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

###########################################################################################
###########################################################################################


# Assume ids have been fetched from a scenario such as the
# one presented in recipe__get_friends_followers.py and that
# t is an authenticated instance of twitter.Twitter

def get_info_by_id(t, ids):

    id_to_info = {}

    while len(ids) > 0:

        # Process 100 ids at a time...

        ids_str = ','.join(ids)

        response = make_twitter_request(t, 
                                      getattr(getattr(t, "users"), "lookup"),
                                      user_id=ids_str)
     
        if response is None:
            break

        if type(response) is dict:  # Handle Twitter API quirk
            response = [response]

        for user_info in response:
            id_to_info[user_info['id']] = user_info

        return id_to_info

# Similarly, you could resolve the same information by screen name 
# using code that's virtually identical. These two functions
# could easily be combined.

def get_info_by_screen_name(t, screen_names):

    sn_to_info = {}

    while len(screen_names) > 0:

        # Process 100 ids at a time...

        screen_names_str = ','.join(screen_names)

        response = make_twitter_request(t, 
                                      getattr(getattr(t, "users"), "lookup"),
                                      screen_name=screen_names_str)
     
        if response is None:
            break

        if type(response) is dict:  # Handle Twitter API quirk
            response = [response]

        for user_info in response:
            sn_to_info[user_info['screen_name']] = user_info

        return sn_to_info

if __name__ == '__main__':

    # Be sure to pass in any necessary keyword parameters
    # if you don't have a token already stored on file



########################### Read input ################################################
    doc=open('data/input_userInfo.csv', 'r')
    r=csv.reader(doc,delimiter=';')#,quotechar='')

    unames=[]
    for column in r:
        unames+=[column[0]]

    unames=unames[1:]

    doc.close()
#######################################################################################


    #info.update(get_info_by_id(t, ['2384071']))

    # Do something useful with the profile information like store it to disk

    query =['id','screen_name','followers_count','friends_count','statuses_count','created_at','lang','time_zone','url','verified','location','description']

    # Be sure to pass in any necessary keyword parameters
    # if you don't have a token already stored on file

    t = oauth_login()


    #csv unicode schreiben
    ff = open('data/output_userInfo.csv', 'w')
    ff.write(codecs.BOM_UTF8)
    writer = UnicodeWriter(ff) 
    
    writer.writerow(query)
    
    #write input for friends retrieve
    wfr=open('data/input_friends.csv', 'w')
    wfo=open('data/input_followers.csv', 'w')
    csv_wfr=csv.writer(wfr , delimiter=';',quotechar='"',quoting=csv.QUOTE_ALL)    
    csv_wfo=csv.writer(wfo , delimiter=';',quotechar='"',quoting=csv.QUOTE_ALL)    





    # Basic usage...
    

    x=0
    steps=100
    total=0
    while x<len(unames):
        names=unames[0+x:steps+x]
        info = {}
        try:
            info.update(get_info_by_screen_name(t, names))
        except TypeError:
            print "No Results"
            x+=steps
            continue

        for element in info:
            line=[]
            for item in query:
                elm=info[element][item]
                if isinstance(elm,int):
                    elm=str(elm)
                elif elm is None:
                    elm=''

                line=line+[elm]

            writer.writerow(line)
            csv_wfr.writerow([info[element]['screen_name'],info[element]['id']])
            csv_wfo.writerow([info[element]['screen_name'],info[element]['id']])
        
        print time.strftime("%Y.%m.%d %H:%M:%S"),"Retrieved Info for usernames",x,"to",x+len(names),". Successful in ",len(info)," of ",len(names)," cases."
        x+=steps
        total+=len(info)


ff.close()
print ""
print time.strftime("%Y.%m.%d %H:%M:%S"),"Succesfully Retrieved Info for",total,"of",len(unames),"requested users.",str(float(total)/float(len(unames))*100)[0:5],"%."


