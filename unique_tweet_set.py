import pandas as pd
import os.path


path_to_feed_file = 'C:\Users\/1022719\PycharmProjects\/feed-data-harvester\src\out\/feed_data.csv'
if os.path.isfile(path_to_feed_file):
    df = pd.read_csv(path_to_feed_file)
    df1 = df.drop_duplicates('Id')
    df1.to_csv('C:\Users\/1022719\PycharmProjects\/feed-data-harvester\src\out\/unique_feed_data.csv')
else:
    print('Found Invalid path to feed data')
