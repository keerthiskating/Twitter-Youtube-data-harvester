import os
import pandas as pd
from os.path import join as pjoin
import tweepy
from nltk.corpus import stopwords
from tweepy import OAuthHandler
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


class FetchTweetsAPI:
    def __init__(self, authcontainer, input_entity_list):
        self.__credential_dictionary = authcontainer
        self.__input_entity_list = input_entity_list
        self.__analyzer = SentimentIntensityAnalyzer()
        self.__stopWords = set(stopwords.words('english'))
        self.__authentication = None
        self.__apiObj = None
        self.__dir_path = os.path.dirname(os.path.realpath(__file__))
        self.__out_path = pjoin(self.__dir_path, 'out')

    def authenticate(self):
            self.__authentication = OAuthHandler(self.__credential_dictionary["consumerkey"],
                                                 self.__credential_dictionary["consumersecret"])
            self.__authentication.set_access_token(self.__credential_dictionary["accesstoken"],
                                                   self.__credential_dictionary["accesstokensecret"])
            self.__apiObj = tweepy.API(self.__authentication)

    def fetch_tweets(self):
        self.authenticate()
        filename = "feed_data.csv"
        path_to_file = pjoin(self.__out_path, filename)
        tweet_df = pd.DataFrame()
        error_occured = False
        try:
            for i in self.__input_entity_list:
                for keyword in i["keywordset"]:
                    tweets = []
                    for fetched_tweet in tweepy.Cursor(self.__apiObj.search,
                                                       q=keyword,
                                                       lang=i["language"],
                                                       geocode=i["location_string"],
                                                       resultType=i["resulttype"],
                                                       until=i["until"]
                                                       ).items():
                        if i["location"] and i["radius"]:
                            tweets.append(FetchTweetsAPI.getTweet(fetched_tweet, keyword, i["location"]+","+i["radius"], i["location_string"]))
                        else:
                            tweets.append(FetchTweetsAPI.getTweet(fetched_tweet, keyword))
                    if len(tweets) == 0:
                        print("No tweets found for " + keyword)
                    else:
                        tweet_df = pd.DataFrame.from_dict(tweets, orient='columns')
        except tweepy.TweepError as tweep_error:
            if tweep_error.response.json()['errors'][0]['code'] == 32:
                print('Incorrect authentication credentials found for twitter API')
            elif tweep_error.response.json()['errors'][0]['code'] == 88:
                error_occured = True
                print 'Twitter API limit reached.', len(tweet_df), 'tweets fetched'
            else:
                print 'Unhandled twitter API exception', tweep_error
        finally:
            if not error_occured:
                print len(tweet_df), 'tweets found'
            FetchTweetsAPI.write_df_to_file(path_to_file, tweet_df)

    @staticmethod
    def write_df_to_file(path_to_file, df):
        if not os.path.exists(path_to_file):
            df.to_csv(path_to_file, mode='a', header=True)
        else:
            out_file = pd.read_csv(path_to_file)
            if out_file.empty:
                df.to_csv(path_to_file, mode='a', header=True)
            else:
                df.to_csv(path_to_file, mode='a', encoding='utf-8', header=False)

    @staticmethod
    def getTweet(fetched_tweet, keyword, location=None, location_string=None):
        tweet = {'Id': fetched_tweet.id,
                 'TimeStamp': fetched_tweet.created_at,
                 'Location': location,
                 'GeoLocation': location_string,
                 'KeyWord': keyword,
                 'Text': fetched_tweet.text.encode("utf-8"),
                 'Language': fetched_tweet.lang.encode("utf-8"),
                 'Likes': fetched_tweet.favorite_count,
                 'Retweets': fetched_tweet.retweet_count,
                 'Source': "Twitter"}
        return tweet
