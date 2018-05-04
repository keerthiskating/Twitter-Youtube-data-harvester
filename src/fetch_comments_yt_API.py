import sys
from googleapiclient.discovery import build
import os
from os.path import join as pjoin
import pandas as pd
import json
from googleapiclient.errors import HttpError


class FetchCommentsYtAPI:
    def __init__(self, auth_list, input_entity_list):
        self.__developer_key = auth_list['developerkey']
        self.__youtube_api_service_name = auth_list['youtubeapiname']
        self.__youtube_api_version = auth_list['youtubeapiversion']
        self.__videoid_list = list()
        self.__youtube_service_obj = None
        self.__dir_path = os.path.dirname(os.path.realpath(__file__))
        self.__out_path = pjoin(self.__dir_path, 'out')
        self.__input_entity_list = input_entity_list
        self.__comment_df = pd.DataFrame()
        self.__df_list = list()
        self.__dump_list = list()

    def build_service_obj(self):
        self.__youtube_service_obj = build(self.__youtube_api_service_name,
                                           self.__youtube_api_version,
                                           developerKey=self.__developer_key)

    def get_videos(self, keyword, input_list, token):
        try:
            search_response = self.__youtube_service_obj.search().list(
                q=keyword,
                type="video",
                pageToken=token,
                part="snippet",
                maxResults=50,
                publishedAfter=input_list['publishedafter'],
                publishedBefore=input_list['publishedbefore'],
                order='viewCount',  # This parameter can be changed if required
                location=input_list['locationstring'],
                locationRadius=input_list['radius'],
                relevanceLanguage=input_list['language']
            ).execute()
        except HttpError as h:
            print('Error occured when fetching videos. Reason: ' + h._get_reason())
            sys.exit()

        for search_result in search_response.get("items"):
            if search_result["id"]["kind"] == "youtube#video":
                self.__videoid_list.append(search_result['id']['videoId'])
        if 'nextPageToken' in search_response:
            return search_response['nextPageToken'].encode('utf-8')
        else:
            return 'last_page'

    def get_all_videos(self):
        for input_list in self.__input_entity_list:
            for keyword in input_list['keywordset']:
                self.__videoid_list = []
                token = None
                while True:
                    if token != 'last_page' or token is None:
                        token = self.get_videos(keyword, input_list, token)
                    else:
                        break
                print ('Found ' + str(len(self.__videoid_list)) + ' videos that match the input query')
                missed_video_count = 0
                for video_id in self.__videoid_list:
                    try:
                        print('Working on videoId: ' + video_id)
                        self.get_all_comment_threads(video_id, input_list, keyword)
                    except HttpError as h:
                        try:
                            print(h)
                            if not video_id.encode('utf-8').startswith("-"):
                                modified_video_id = "-"+video_id.encode('utf-8')
                                self.get_all_comment_threads(modified_video_id, input_list, keyword)
                            else:
                                modified_video_id = video_id.encode("utf-8")[1:]
                                self.get_all_comment_threads(modified_video_id, input_list, keyword)
                        except HttpError:
                            missed_video_count += 1
                            print 'Failed to fetch comments for:', video_id.encode('utf-8')
                            continue
        self.__comment_df = pd.DataFrame(self.__df_list)
        path_to_csv = pjoin(self.__out_path, "feed_data.csv")
        if os.path.exists(path_to_csv):
            out_file = pd.read_csv(path_to_csv)
            if out_file.empty:
                self.__comment_df.to_csv(header=True, path_or_buf=path_to_csv, mode='a')
            else:
                self.__comment_df.to_csv(header=False, path_or_buf=path_to_csv, mode='a')
        else:
            self.__comment_df.to_csv(header=True, path_or_buf=path_to_csv, mode='a')

    def get_all_comment_threads(self, video_id, input_list, keyword):
        next_page_token = None
        while True:
            if next_page_token is None or next_page_token != 'last_page':
                next_page_token = self.get_comment_threads(video_id, next_page_token, input_list, keyword)
            else:
                break

    def get_comment_threads(self, video_id, token, input_list, keyword):
        results = self.__youtube_service_obj.commentThreads().list(
            part="snippet,replies",
            videoId=video_id,
            textFormat="plainText",
            pageToken=token
        ).execute()

        if 'dump' in input_list:
            if input_list['dump'] == '1':
                if len(results["items"]) > 0:
                    for item in results["items"]:
                        self.__dump_list.append(item)
                    with open('out/youtube_dump', 'a') as y:
                        json.dump(self.__dump_list, y)
                        y.write(os.linesep)
                    y.close()

        try:
            if "items" in results:
                for item in results["items"]:
                    comment = item["snippet"]["topLevelComment"]
                    text = comment["snippet"]["textDisplay"].encode('utf-8')
                    timestamp = comment["snippet"]["publishedAt"].encode('utf-8')
                    like_count = comment["snippet"]["likeCount"]
                    temp1 = {
                        'Location': None if input_list['location'] is None else (input_list['location']+","+input_list['radius']),
                        'GeoLocation': None if input_list['locationstring'] is None else input_list['locationstring'],
                        'Id': video_id,
                        'KeyWord': keyword,
                        'Language': None if input_list['language'] is None else input_list['language'],
                        'Likes': like_count,
                        'Retweets': None,
                        'Source': 'Youtube',
                        'Text': text,
                        'Timestamp': timestamp,
                    }
                    self.__df_list.append(temp1)
                    if (len(self.__df_list) % 1000 == 0) and (len(self.__df_list) > 1000):
                        print('Fetched ' + str(len(self.__df_list)) + ' comments')
        except KeyError:
            pass

        if 'nextPageToken' in results:
            return results['nextPageToken'].encode('utf-8')
        else:
            return 'last_page'
