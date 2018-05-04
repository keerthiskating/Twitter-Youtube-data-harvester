import sys


def get_encoded_string(string):
    if isinstance(string, unicode):
        return string.encode('utf-8')
    else:
        # print ("Unicode expected. Found " + str(string))
        print("Error in string encoder")
        sys.exit()
