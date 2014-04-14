import tweepy
import time

consumer_key="ikeSbERBHes9nrQbZoriA"
consumer_secret="zRQWthjQPnrCthY8lO2JXgAQIEwa3tLSYNiHYNy3hU"

access_token="251535413-Qfi75rcBd2BD6prboV6g3WoLu8PBmuVkPTjPzxJo"
access_token_secret="xEXN11jZVCFy7hqFNFmUUVRq2OJcQW1pLXuxH74XB0"

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth) # Don't forget to use authentication for private lists/users.


for page in tweepy.Cursor(api.list_members,'Europarl_EN','all-meps-on-twitter').pages():
    for member in page:
        print member.screen_name, member.id
    time.sleep(60)
