#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import feedparser
import json
import time
from datetime import datetime
from operator import attrgetter

class Reddit: 
    def __init__(self, headers):
        self.session = requests.Session()
        self.session.headers = {'user-agent': headers}

    def login(self, username, password):
        self.username = username
        self.password = password

        user_pass_dict = {
            'user': self.username,
            'passwd': self.password,
            'api_type': 'json'
        }

        r = self.session.post(r'http://www.reddit.com/api/login',
            data = user_pass_dict)
        r_json = json.loads(r.content.decode())
        
        try:
            self.modhash = r_json['json']['data']['modhash']
        except:
            print(r_json)

    def submit_link(self, link, title, subreddit):
        submission_dict = {
            'kind': 'link',
            'url': link,
            'title': title,
            'sr': subreddit,
            'uh': self.modhash,
            'api_type': 'json'
        }

        r = self.session.post(r'http://www.reddit.com/api/submit',
            data = submission_dict)
        r_json = json.loads(r.content.decode())

    def get_submissions(self):
        r = self.session.get(
            r'http://www.reddit.com/user/{}/submitted.json'.format(
            self.username))
        r_json = json.loads(r.content.decode())
        return r_json

def load_config():
    with open('.kzbconf') as f:
        config = json.load(f)

    headers = config['headers']
    username = config['username']
    password = config['password']
    feed_url = config['feed_url']
    subreddit = config['subreddit']

    return headers, username, password, feed_url, subreddit

def get_entries(reddit_submitted, url):
    feed = feedparser.parse(url)
    reddit_submitted_urls = []
    unsubmitted = []
    for index in range(len(reddit_submitted['data']['children'])):
        reddit_submitted_urls.append(
            reddit_submitted['data']['children'][index]['data']['url'])

    for index in range(len(feed['entries'])):
        if (feed['entries'][index]['links'][0]['href'] 
                in reddit_submitted_urls) == False:
            unsubmitted.append(feed['entries'][index])
        else: 
            break

    return unsubmitted

def get_current_entries(entries):
    time_now = datetime.now() 
    to_submit = []

    for entry in entries:
        entry_time = datetime.fromtimestamp(
            time.mktime(entry['published_parsed']))
        time_delta = time_now - entry_time

        if time_delta.days < 1:
            to_submit.append(entry)

    return to_submit

def submit_entries(reddit, entries, subreddit):
    while entries:
        entry = entries.pop(0)
        url = entry['links'][0]['href']

        try:
            title = entry['title'] + ' - ' + entry['author']
        except KeyError:
            title = entry['title']

        reddit.submit_link(url, title, subreddit)

        if entries:
            time.sleep(600)

def sort_age(to_submit):
    to_submit = sorted(to_submit, key=attrgetter('published_parsed'))
    return to_submit
 
def main():
    headers, username, password, feed_url, subreddit = load_config()

    reddit = Reddit(headers)
    reddit.login(username, password)

    submitted_reddit = reddit.get_submissions()
    entries_unsubmitted = get_entries(submitted_reddit, feed_url)
    to_submit = get_current_entries(entries_unsubmitted)
    to_submit = sort_age(to_submit)
    
    submit_entries(reddit, to_submit, subreddit)
    
if __name__ == "__main__":
    main()

