import json
import datetime
from datetime import date, timedelta

try:
    path_to_input_json = 'C:\Users\/1022719\PycharmProjects\/feed-data-harvester\src\sample_input.json'
    with open(path_to_input_json) as i:
        input_dict = json.load(i)
    i.close()
    input_dict[0]['EndDate'] = str(datetime.datetime.today().strftime('%Y-%m-%d'))
    input_dict[0]['BeginDate'] = str(date.today() - timedelta(2))
    with open(path_to_input_json, 'w') as s:
        json.dump(input_dict, s)
    s.close()
except IOError as io:
    print(io)
    print('Invalid path to input file')
