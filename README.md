kzine_bot
=========

Reddit bot that posts news from http://www.kzine.se/ (and potentially other sources).

Note that feedparser 5.1.3 may not work due to a bug, the latest version from git (see LICENSE) is required.

The config file should be named .kzbconf and located in the same directory as kzine_bot.py. 

Example contents:
```json
{
"username":     "reddit_username",
"password":     "reddit_password",
"headers":      "/u/reddit_username's bot",
"feed_url":     "http://www.example.com/feed",
"subreddit":    "example_com"
}
```
