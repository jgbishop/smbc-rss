# Saturday Morning Breakfast Cereal RSS Generator

This small project allows users to generate a simple RSS feed for the [Saturday
Morning Breakfast Cereal](https://www.smbc-comics.com/index.php) web comic.
This particular RSS feed includes the primary comic, the hover text joke, and
the hidden comic all inline. No more visiting the SMBC website to get an extra
joke!

## Requirements

This is a Python 3 script which relies on the following third-party libraries:

* beautifulsoup4
* feedparser
* lxml
* requests
* rfeed

## Installation

1. Clone this repo to a folder of your choice.
2. Copy the configuration file template (_smbc-config-template.json_) to a new
file named _smbc-config.json_.
3. Update the configuration file (_smbc-config.json_) to your liking (see below
for more on how to do this).
4. Set up a cron job to run the script once per day.
5. Enjoy!

## Configuration

The configuration file template (_smbc-config-template.json_) has the following
components that need to be filled out. Note that this is a JSON file, so JSON
syntax is expected.

**feed_dir** (Required)  
The absolute path to a folder in which the RSS feeds themselves will live.
Example: `/home/myuser/mywebsite.com/smbc`

**feed_url** (Required)  
The absolute URL that corresponds to the RSS feed directory above (internet
visible). Example: `https://mywebsite.com/smbc`

**source_feed** (Required)  
The URL of the source RSS feed to be read in (defaults to
`https://www.smbc-comics.com/comic/rss`). This should only need to change if the
URL of the official RSS feed changes.
