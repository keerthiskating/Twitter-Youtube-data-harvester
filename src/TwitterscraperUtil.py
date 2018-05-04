import json
import sys
import os.path
import pandas as pd


class JsonCsvUtil:
    def __init__(self, json_file, csv_file, tweet_params):
        self.__json_file = json_file
        self.__csv_file = csv_file
        self.__tweet_params = tweet_params
        self.__json_as_dictionary = dict()
        self.__row_count = None

    def to_dictionary(self):
        try:
            os.path.isfile(self.__json_file)
            with open(self.__json_file) as j:
                self.__json_as_dictionary = json.load(j)
            j.close()
            self.__row_count = len(self.__json_as_dictionary)
        except IOError:
            print self.__json_file, "doesn't exist"
            sys.exit(1)

    @staticmethod
    def encode_string(x):
        return x.encode('utf-8')

    def to_csv(self):
        self.to_dictionary()
        tweets = []
        for i in self.__json_as_dictionary:
            tweet = {
                'Location': None if "location" not in self.__tweet_params else self.__tweet_params["location"]+","+self.__tweet_params["radius"],
                'GeoLocation': None if "geolocation" not in self.__tweet_params else self.__tweet_params["geolocation"],
                'Id': i["id"].encode("utf-8"),
                'KeyWord': self.__tweet_params["keyword"],
                'Language': self.__tweet_params["lang"],
                'Likes': i["likes"],
                'Retweets': i["retweets"],
                'Source': 'Twitter',
                'Text': i["text"].encode("utf-8"),
                'Timestamp': i["timestamp"].encode("utf-8")
            }
            tweets.append(tweet)
        tweets_df = pd.DataFrame.from_dict(tweets, orient='columns')
        JsonCsvUtil.write_df_to_file(self.__csv_file, tweets_df)

    @staticmethod
    def write_df_to_file(path_to_file, df):
        if not os.path.exists(path_to_file):
            df.to_csv(path_to_file, mode='a', header=True)
        else:
            out_file = pd.read_csv(path_to_file)
            if out_file.empty:
                df.to_csv(header=True, path_or_buf=path_to_file, mode='a')
            else:
                df.to_csv(path_to_file, mode='a', encoding='utf-8', header=False)
