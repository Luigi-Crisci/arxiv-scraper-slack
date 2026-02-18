A simple Slack bot for [Arxiv](https://arxiv.org) that checks for new papers matching a set of keywords.

Ideal use is to set up a `crontab` and run it every day/week.  
The following example runs it every day at 9 a.m.
```bash
0 9 * * * /usr/bin/python3 /path/to/archive_scraper.py
```