#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import json
import nltk
import spacy 
from datetime import datetime
import tweepy
import re
import string
import unicodedata
from gensim import corpora
from nltk.tokenize.toktok import ToktokTokenizer


# In[ ]:


# Let's use the Twitter Stream API to get tweets in real time
# We save our tweets to a file called "cats.json"
# override tweepy.StreamListener to add logic to on_status and on_error 
class MyStreamListener(tweepy.StreamListener):
    def on_status(self, status):
        print(status._json)
        with open ("insomnia.json", "a+") as stream_f:
            json_text = json.dumps(status._json)
            stream_f.write(json_text)
            stream_f.write('\n')
            
    def on_error(self, status_code):
        print("Error detected!")
        print (status_code)
        return False


# In[ ]:


def clean_tweet(tweet): 
    processed_tweet = {}
    processed_tweet["id"] = tweet['id']
    processed_tweet["user"] = tweet['user']['screen_name']
    processed_tweet["created_at"] = datetime.strptime(tweet["created_at"],'%a %b %d %H:%M:%S +0000 %Y')
    created_at = datetime.strptime(tweet["created_at"],'%a %b %d %H:%M:%S +0000 %Y')
    processed_tweet["lang"] = tweet['lang']
    
    if tweet['lang'] != "en":
        processed_tweet["is_en"] = False
    else: 
        processed_tweet["is_en"] = True
        
    if "full_text" in tweet: 
        processed_tweet["text"] = tweet['full_text']
    elif "extended_tweet" in tweet:
        processed_tweet["text"] = tweet["extended_tweet"]["full_text"]
    elif "text" in tweet: 
        processed_tweet["text"] = tweet['text']
        
    if 'retweeted_status' in tweet:
        rt = tweet['retweeted_status']
        processed_tweet["is_rt"] = True
        processed_tweet["rt_user"] = rt['user']['screen_name']
        processed_tweet["rt_id"] = rt['id']        
        if "full_text" in rt:
            processed_tweet["rt_text"] = rt['full_text']
        elif "extended_tweet" in tweet['retweeted_status']:
            processed_tweet["rt_text"] = tweet['retweeted_status']['extended_tweet']["full_text"]
        elif "text" in rt: 
            processed_tweet["rt_text"] = rt['text']
    else: 
        processed_tweet["is_rt"] = False
            
    return processed_tweet


# In[ ]:


info = {"consumer_key": "C85NCy1PkZiRnAwnS0Abt5FlF",
        "consumer_secret": "JS17fB3b4s4BmYZ74n4EgwRjG1w7kvChU2U1f1sC2zpXMxIDa9",
        "access_token": "41218838-OVyxdHIDYAyf1EBezFy9XZaT20qFyjfPw5H6MlnFM",
        "access_secret": "gDDDmbnMPeBI3SMrRheifA8QfmOZs7f24ab718C0BtsW2"}


# In[ ]:


auth = tweepy.OAuthHandler(info['consumer_key'], info['consumer_secret'])
auth.set_access_token(info['access_token'], info['access_secret'])

api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)


# In[ ]:


#Collecting Twitter Data
myStreamListener = MyStreamListener()
myStream = tweepy.Stream(auth = api.auth, listener=myStreamListener)
myStream.filter(track=['insomnia covid19'])


# In[ ]:


# load the raw tweets found from the search and stream apis into the same list for processing
tweet_data = []

with open("insomnia.json") as stream_f:
    for line in stream_f:
        json_line = json.loads(line)
        tweet_data.append(json_line)
        
# filter all of the raw tweets by turning them into clean_tweet objects
# the filtering is taken care of in the class function
filtered_data = []
for elem in tweet_data: 
    filtered_tweet = clean_tweet(elem)
    filtered_data.append(filtered_tweet)


# In[ ]:


filtered_data


# In[10]:


# create a list of all the tweet text 
# we filter out all tweets that are not English
tweet_text = []
for tweet in filtered_data:
    if tweet["is_en"]:
        if tweet["is_rt"]: 
            tweet_text.append(tweet["rt_text"].replace("\n", " "))
        else:
            tweet_text.append(tweet["text"].replace("\n", " "))


# In[11]:


tweet_text


# In[12]:


#PreProcessing Data
# remove HTML links, mentions, hashtags, and special characters

def strip_links(text):
    link_regex    = re.compile('((https?):((//)|(\\\\))+([\w\d:#@%/;$()~_?\+-=\\\.&](#!)?)*)', re.DOTALL)
    links         = re.findall(link_regex, text)
    for link in links:
        text = text.replace(link[0], ' ')    
    return text

def strip_mentions(text):
    entity_prefixes = ['@']
    for separator in  string.punctuation:
        if separator not in entity_prefixes :
            text = text.replace(separator,' ')
    words = []
    for word in text.split():
        word = word.strip()
        if word:
            if word[0] not in entity_prefixes:
                words.append(word)
    return ' '.join(words)

def strip_hashtags(text):
    entity_prefixes = ['#']
    for separator in  string.punctuation:
        if separator not in entity_prefixes :
            text = text.replace(separator,' ')
    words = []
    for word in text.split():
        word = word.strip()
        if word:
            if word[0] not in entity_prefixes:
                words.append(word)
    return ' '.join(words)
        
def remove_special_characters(text, remove_digits=False):
    pattern = r'[^a-zA-z0-9\s]' if not remove_digits else r'[^a-zA-z\s]'
    text = re.sub(pattern, '', text)
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8', 'ignore')
    return text


# In[13]:


stripped_tweet_text = []
for elem in tweet_text:
    elem = strip_links(elem)
    elem = strip_mentions(elem)
    elem = strip_hashtags(elem)
    elem = elem.replace('RT', '')
    elem = remove_special_characters(elem)
    stripped_tweet_text.append(elem)


# In[14]:


stripped_tweet_text


# In[ ]:




