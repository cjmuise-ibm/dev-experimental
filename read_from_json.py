import json

def load_from_json_abm (filename):
    with open(filename) as json_file:
        data = json.load(json_file)
        # print (data['actions'])
        # print (data['fluents'])
        # print (data['traces'])

        print (len(data['traces']))

        return

load_from_json_abm('blocksworld-new/p1.json')
