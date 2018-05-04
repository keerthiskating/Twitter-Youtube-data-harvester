#### Feed data harvester for Twitter/Youtube


Feed data harvester can be used to fetch tweets from Twitter, comments on a Youtube video.

###### Usage:



```
SentimentAnalysisWrapper.py -h
```

###### Requires:




1. [Python 2.7.x](https://www.python.org/download/releases/2.7/)
2. [Twitterscraper](https://github.com/taspinar/twitterscraper/#2-installation-and-usage)
3. [Geocoder](https://pypi.python.org/pypi/geocoder/1.8.0)
4. [Google APIs Client Library for Python](https://developers.google.com/youtube/v3/quickstart/python)
5. [Pandas](https://pandas.pydata.org/pandas-docs/stable/install.html#installation)
6. [Tweepy](https://github.com/tweepy/tweepy#installation)
7. [nltk](https://www.nltk.org/install.html)
8. [vaderSentiment](https://github.com/cjhutto/vaderSentiment#installation)

###### Arguments:



1. credential-file-name - JSON file that contains credentials that are required to connect to Twitter / Youtube APIs. Look under src folder for sample_credential.json
2. input-file-name - JSON file that contains input configurations. Look under src folder for sample_input.json and input_parameters_explained.txt



###### Output:



1. Feed data fetched, will be saved into 'src/out/feed_data.csv'.
2. If "Dump" parameter is set for Youtube in the input file, raw API response is saved into 'src/out/youtube_dump.json'.
3. If twitterscraper is included in the input file, raw JSON data for each keyword will be saved into 'src/out/keyword_tweets.json'.



###### Output file:
1. GeoLocation - [Latitude,longitude,radius] equivalent of the location provided in input file
2. Id - TweetId in case of twitter, VideoId in case of youtube
3. KeyWord - The associated keyword
4. Language - Language of tweet / comment
5. Likes - Count of likes
6. Location - The raw location provided in the input file
7. Retweets - Retweets to a tweet in case of twitter, Invalid for youtube comment
8. Source - Social media feed used to fetch the resource (tweet/comment)
9. Text - Body of tweet/comment
10. TimeStamp - The time at which the resource is created. Youtube time stamp follows [RFC 3339](https://tools.ietf.org/html/rfc3339)



###### Notes:
1. When using twitterscraper to fetch tweets, please be aware of [Twitter terms of service](https://twitter.com/en/tos). It is intended to use it only for demo or experimentation purposes.
2. 'youtube-comment-replies', a branch in this repository, can be used if we are interested in fetching replies to each comment on a youtube video. The master branch doesn't support replies to each comment.
