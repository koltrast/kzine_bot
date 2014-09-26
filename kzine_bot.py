#!/usr/bin/python
import requests
import feedparser
import json
import time
import datetime
from pprint import pprint

class Reddit: 
    def __init__(self):
        self.session = requests.Session()
        self.session.headers = {'user-agent': 'headers'}

    def login(self, username, password):
        self.username = username
        self.password = password

        user_pass_dict = {'user': self.username,
                          'passwd': self.password,
                          'api_type': 'json'}

        r = self.session.post(r'http://www.reddit.com/api/login', data = user_pass_dict)
        r_json = json.loads(r.content.decode())
        
        try:
            self.modhash = r_json['json']['data']['modhash']
        except:
            pprint(r_json)

    def get_me(self):
        r = self.session.get(r'http://www.reddit.com/api/me.json')
        r_json = json.loads(r.content.decode())
        
        try:
            self.modhash = r_json['json']['data']['modhash'] # New modhash from me request
        except:
            self.modhash = 'Could not get me.json' 
        
        return r_json

    def submit_link(self, link, title, subreddit):
        submission_dict = {'kind': 'link',
                           'url': link,
                           'title': title,
                           'sr': subreddit,
                           'uh': self.modhash,
                           'api_type': 'json'}

        r = self.session.post(r'http://www.reddit.com/api/submit', data = submission_dict)
        r_json = json.loads(r.content.decode())

    def get_submissions(self):
        r = self.session.get(r'http://www.reddit.com/user/{}/submitted.json'.format(self.username))
        r_json = json.loads(r.content.decode())
        return r_json

    
def get_entries(reddit_submitted, url):
    feed = feedparser.parse(url)
    reddit_submitted_urls = []
    unsubmitted = []
    for index in range(len(reddit_submitted['data']['children'])):
        reddit_submitted_urls.append(reddit_submitted['data']['children'][index]['data']['url'])

    for index in range(len(feed['entries'])):
        if (feed['entries'][index]['links'][0]['href'] in reddit_submitted_urls) == False:
            unsubmitted.append(feed['entries'][index])
        else: 
            break   # Don't want to submit older than latest submission

    return unsubmitted

def get_current_entries(entries):
    time_now = datetime.datetime.now() 
    to_submit = []

    for entry in entries:
        entry_time = datetime.datetime.fromtimestamp(time.mktime(entry['published_parsed']))
        time_delta = time_now - entry_time

        if time_delta.days == 0:
            to_submit.append(entry)

    return to_submit

def submit_entries(reddit, entries, subreddit):
    
    while entries:
        entry = entries.pop(0)
        url = entry['links'][0]['href']
        title = entry['title'] + ' - ' + entry['author']
        reddit.submit_link(url, title, subreddit)

        if entries:
            time.sleep(60)
 
def main():
    kzine_url = r'http://www.kzine.se/feed'
    subreddit = 'subreddit'
    
    reddit = Reddit()
    reddit.login('username','password')

    submitted_reddit = reddit.get_submissions()
    entries_unsubmitted = get_entries(submitted_reddit, kzine_url)
    to_submit = get_current_entries(entries_unsubmitted)
    to_submit.reverse() # Age descending, oldest first
    
    submit_entries(reddit, to_submit, subreddit)
    
if __name__ == "__main__":
    main()
