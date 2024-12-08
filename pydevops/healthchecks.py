import json

 

def load_healthchecks_config():
    # Opening JSON file
    f = open('/etc/healthchecks.json')

    # returns JSON object as 
    # a dictionary
    data = json.load(f)

    return data


ping_key = load_healthchecks_config()["ping_key"]
