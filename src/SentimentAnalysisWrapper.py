import optparse
import os
import json
import sys
import Geocoder
from Encoder import get_encoded_string
from fetch_tweets_API import FetchTweetsAPI
from fetch_tweets_scraper import FetchTweetsScraper
from fetch_comments_yt_API import FetchCommentsYtAPI


class FetchFeedData:

    def __init__(self):
        self.__input_file = None
        self.__credential_file = None
        self.__twitter_auth_valid_key_set = {'consumerkey', 'consumersecret', 'accesstoken', 'accesstokensecret'}
        self.__youtube_auth_valid_key_set = {'developerkey', 'youtubeapiname', 'youtubeapiversion'}
        self.__twitterscraper_input_valid_key_set = {'keywordset', 'limit', 'language', 'begindate', 'enddate',
                                                     'poolsize', 'location', 'radius'}
        self.__youtube_input_valid_key_set = {'keywordset', 'location', 'radius', 'language', 'publishedafter',
                                              'publishedbefore', 'dump'}
        self.__twitter_credential_dictionary = dict()
        self.__youtube_credential_dictionary = dict()
        self.__twitterscraper_input_entity_list = list()
        self.__twitter_input_entity_list = list()
        self.__youtube_input_entity_list = list()
        self.__parser = optparse.OptionParser()

    @staticmethod
    def check_out_folder():
        if not os.path.exists('out'):
            os.makedirs('out')

    def read_args(self):
        self.__parser.add_option('-c', '--credential file', dest='cred', help='Path to Credential file (mandatory)')
        self.__parser.add_option('-i', '--input file', dest='inp', help='Path to Input file (mandatory)')
        (options, args) = self.__parser.parse_args()

        if not options.cred:
            self.__parser.error("Missing credential file")
        elif not options.inp:
            self.__parser.error("Missing input file")
        else:
            self.__credential_file = options.cred
            self.__input_file = options.inp

    def credential_parser(self):
        if os.path.isfile(self.__credential_file):

            try:
                with open(self.__credential_file) as c:
                    cred_dict = json.load(c)
                c.close()

            except ValueError:
                print(self.__credential_file, " is not a valid JSON")

            else:
                for key, value in cred_dict.iteritems():
                    encoded_lower_key = get_encoded_string(key.lower())

                    if encoded_lower_key == 'twitter':
                        for k, v in value.iteritems():
                            encoded_lower_k = get_encoded_string(k.lower())
                            if encoded_lower_k in self.__twitter_auth_valid_key_set:
                                self.__twitter_credential_dictionary[encoded_lower_k] = get_encoded_string(v)
                            else:
                                raise KeyError('Found invalid key ' + get_encoded_string(k) + ' in twitter credentials')
                        if len(self.__twitter_credential_dictionary) != 4:
                            print('Missing a parameter in twitter credentials')

                    elif encoded_lower_key == 'youtube':
                        for k, v in value.iteritems():
                            encoded_lower_k = get_encoded_string(k.lower())
                            if encoded_lower_k in self.__youtube_auth_valid_key_set:
                                self.__youtube_credential_dictionary[encoded_lower_k] = get_encoded_string(v)
                            else:
                                raise KeyError('Found invalid key ' + get_encoded_string(k) + ' in youtube credentials')
                        if len(self.__youtube_credential_dictionary) != 3:
                            print('Missing a parameter in youtube credentials')

        else:
            raise IOError("Credential file not found")

    def input_parser(self):
        if os.path.isfile(self.__input_file):

            try:
                with open(self.__input_file) as i:
                    inp_list = json.load(i)
                i.close()

            except ValueError:
                print self.__input_file, "is not a valid JSON"

            else:
                for dictionary in inp_list:
                    lower_dictionary = dict((get_encoded_string(k.lower()), dictionary[k]) for k in dictionary)
                    pass_set = {'keywordset', 'feedtype', 'fetch'}

                    if 'location' in lower_dictionary:
                        if lower_dictionary['location']:
                            if ('radius' not in lower_dictionary) or (lower_dictionary['radius'] == ""):
                                print('Radius is expected when Location is present')
                                sys.exit()

                    if 'radius' in lower_dictionary:
                        if lower_dictionary['radius']:
                            if ('location' not in lower_dictionary) or (lower_dictionary['location'] == ""):
                                print('Location is expected when Radius is present')
                                sys.exit()

                    if 'feedtype' in lower_dictionary:

                        if lower_dictionary['feedtype'].lower() == 'twitter':
                            if 'fetch' in lower_dictionary:
                                encoded_fetch = get_encoded_string(lower_dictionary['fetch'])
                            else:
                                print("Fetch parameter required for twitter in input")
                                sys.exit()

                            if encoded_fetch == '1':
                                if ('keywordset' in lower_dictionary) and (len(lower_dictionary['keywordset']) > 0):
                                    geocode_string = None
                                    if 'location' in lower_dictionary and 'radius' in lower_dictionary:
                                        if lower_dictionary['location'] and lower_dictionary['radius']:
                                            first_char = get_encoded_string(lower_dictionary['location'][0])
                                            if first_char.isalpha():
                                                g = Geocoder.Geocoder()
                                                geocode_string = g.get_location(get_encoded_string(lower_dictionary['location'])) + "," + str(get_encoded_string(lower_dictionary['radius']))
                                            elif first_char.isdigit() or first_char == '-':
                                                geocode_string = str(lower_dictionary['location']+","+str(get_encoded_string(lower_dictionary['radius'])))
                                    temp = {
                                        'location': None if 'location' not in lower_dictionary else get_encoded_string(
                                            lower_dictionary['location']),
                                        'radius': None if 'radius' not in lower_dictionary else get_encoded_string(
                                            lower_dictionary['radius']),
                                        'location_string': geocode_string,
                                        'keywordset': map(get_encoded_string, lower_dictionary['keywordset']),
                                        'language': 'en' if 'language' not in lower_dictionary else get_encoded_string(
                                            lower_dictionary['language']),
                                        'resulttype': None if 'resulttype' not in lower_dictionary else get_encoded_string(
                                            lower_dictionary['resulttype'].lower()),
                                        'until': None if 'until' not in lower_dictionary else get_encoded_string(
                                            lower_dictionary['until'])
                                    }
                                    self.__twitter_input_entity_list.append(temp)
                                else:
                                    print('KeyWordSet is either invalid or missing in the input')
                                    sys.exit()

                            elif encoded_fetch == '0':
                                if ('keywordset' in lower_dictionary) and (len(lower_dictionary['keywordset']) > 0):
                                    temp = {
                                        'keywordset': map(get_encoded_string, lower_dictionary['keywordset']),
                                        'limit': "100"
                                    }
                                    for k, v in lower_dictionary.iteritems():
                                        if k in pass_set:
                                            pass
                                        elif k in self.__twitterscraper_input_valid_key_set:
                                            temp[k] = get_encoded_string(v)
                                        else:
                                            print 'Invalid key', k, 'found in input'
                                            sys.exit()
                                    self.__twitterscraper_input_entity_list.append(temp)
                                else:
                                    print('KeyWordSet is either invalid or missing in the input')
                                    sys.exit()
                            else:
                                print('Expected 0(Scraper) or 1(API) for Fetch. Found ' + str(lower_dictionary['fetch']))
                                sys.exit()

                        elif lower_dictionary['feedtype'].lower() == 'youtube':
                            if ('keywordset' in lower_dictionary) and (len(lower_dictionary['keywordset']) > 0):
                                temp = {
                                    'keywordset': map(get_encoded_string, lower_dictionary['keywordset']),
                                    'location': None if 'location' not in lower_dictionary else lower_dictionary['location'],
                                    'radius': None,
                                    'locationstring': None,
                                    'language': 'en',
                                    'publishedafter': None,
                                    'publishedbefore': None
                                }
                                for k, v in lower_dictionary.iteritems():
                                    if k in pass_set:
                                        pass
                                    elif k in self.__youtube_input_valid_key_set:
                                        if k == "location":
                                            if v:
                                                first_char = get_encoded_string(v)[0]
                                                if first_char.isalpha():
                                                    temp['locationstring'] = Geocoder.Geocoder().get_location(get_encoded_string(v))
                                                elif first_char.isdigit() or first_char == "-":
                                                    temp['locationstring'] = temp['location']
                                        temp[k] = get_encoded_string(v)
                                    else:
                                        print 'Invalid key', k, 'found in input'
                                        sys.exit()
                                self.__youtube_input_entity_list.append(temp)
                            else:
                                print('KeyWordSet is either invalid or missing in the input')
                                sys.exit()
                    else:
                        print("Missing FeedType parameter")
                        sys.exit()
        else:
            raise IOError("Input file not found")

    def fork_fetch(self):
        if len(self.__twitter_input_entity_list) > 0:
            print('Fetching tweets using Twitter API')
            self.init_twitter_API()
        if len(self.__twitterscraper_input_entity_list) > 0:
            print('Fetching tweets using Scraper')
            self.init_twitter_scraper()
        if len(self.__youtube_input_entity_list) > 0:
            print('Fetching comments using Youtube API')
            self.init_youtube()

    def init_twitter_API(self):
        FetchFeedData.check_out_folder()
        FetchFeedData.fetch_tweets_API(self.__twitter_credential_dictionary, self.__twitter_input_entity_list)

    @staticmethod
    def fetch_tweets_API(auth_container, input_entity_list):
        fetch_tweet_obj = FetchTweetsAPI(auth_container, input_entity_list)
        fetch_tweet_obj.fetch_tweets()

    def init_twitter_scraper(self):
        FetchFeedData.check_out_folder()
        FetchFeedData.fetch_tweets_scrapper(self.__twitterscraper_input_entity_list)

    @staticmethod
    def fetch_tweets_scrapper(input_entity_list):
        fetch_obj = FetchTweetsScraper(input_entity_list)
        fetch_obj.fork_scraper()

    def init_youtube(self):
        FetchFeedData.check_out_folder()
        FetchFeedData.fetch_youtube_content(self.__youtube_credential_dictionary, self.__youtube_input_entity_list)

    @staticmethod
    def fetch_youtube_content(auth_dictionary, input_entity_list):
        yt_obj = FetchCommentsYtAPI(auth_dictionary, input_entity_list)
        yt_obj.build_service_obj()
        yt_obj.get_all_videos()


s = FetchFeedData()
s.read_args()
s.credential_parser()
s.input_parser()
s.fork_fetch()
