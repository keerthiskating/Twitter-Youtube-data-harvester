import os
import Geocoder
from os.path import join as pjoin
from TwitterscraperUtil import JsonCsvUtil


class FetchTweetsScraper:
    def __init__(self, input_entity_list):
        self.__input_entity_list = input_entity_list
        self.__command_string = ""
        self.__dir_path = os.path.dirname(os.path.realpath(__file__))
        self.__out_path = pjoin(self.__dir_path, 'out')
        self.__to_util = dict()
        self.__out_file_seq = 0
        self.__g = Geocoder.Geocoder()

    def reset(self):
        self.__out_file_seq = 0
        self.__command_string = "twitterscraper "

    def fork_scraper(self):
        for i in self.__input_entity_list:
            if "location" in i:
                if "radius" in i:
                    self.__to_util["location"] = i["location"]
                    self.__to_util["radius"] = i["radius"]
                    self.__to_util["geolocation"] = self.__g.get_location(i["location"])
            for keyword in i["keywordset"]:
                self.reset()
                self.__to_util["keyword"] = keyword.encode("utf-8")
                self.add_keyword(keyword.encode("utf-8"), i)
                if "location" in i:
                    if "radius" in i:
                        self.add_location(i["location"], i["radius"])
                if "begindate" in i:
                    self.add_start_date(i["begindate"])
                if "enddate" in i:
                    self.add_end_date(i["enddate"])
                if "limit" in i:
                    self.add_limit(i["limit"])
                if "language" in i:
                    self.__to_util["lang"] = i["language"]
                    self.add_lang(i["language"])
                else:
                    self.__to_util["lang"] = "en"

                joined_keyword = keyword.replace(' ', '_')
                check_path = pjoin(self.__out_path, joined_keyword+"_tweets_%s.json" % self.__out_file_seq)
                while os.path.exists(check_path):
                    self.__out_file_seq += 1
                    check_path = pjoin(self.__out_path, joined_keyword + "_tweets_%s.json" % self.__out_file_seq)
                path_to_json = pjoin(self.__out_path, joined_keyword + "_tweets_%s.json" % self.__out_file_seq)
                path_to_csv = pjoin(self.__out_path, "feed_data.csv")

                self.add_output_file(path_to_json)
                os.system(self.__command_string)
                if os.path.isfile(path_to_json):
                    scraper_util = JsonCsvUtil(path_to_json, path_to_csv, self.__to_util)
                    scraper_util.to_csv()
            self.__to_util.clear()

    def add_location(self, location, radius):
        self.__command_string = self.__command_string + 'near:' + location + " "
        self.add_radius(radius)

    def add_output_file(self, keyword):
        self.__command_string = self.__command_string + "-o " + keyword.replace(' ', '_') + " "

    def add_radius(self, radius):
        self.__command_string = self.__command_string + "within:" + radius + '"' + " "

    def add_keyword(self, keyword, i):
        if "location" in i:
            self.__command_string = self.__command_string + '"' + keyword + " "
        else:
            self.__command_string = self.__command_string + keyword + " "

    def add_start_date(self, begin_date):
        self.__command_string = self.__command_string + "-bd " + begin_date + " "

    def add_end_date(self, end_date):
        self.__command_string = self.__command_string + "-ed " + end_date + " "

    def add_limit(self, limit):
        self.__command_string = self.__command_string + "-l " + limit + " "

    def add_lang(self, lang):
        self.__command_string = self.__command_string + "--lang " + lang + " "
