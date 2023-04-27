import requests
import time
import json

url = 'https://127.0.0.1:2999/liveclientdata/playerlist'
cert_file = './riotgames.pem'
usernames = [{"discordName": "ironpack#4338", "leagueName": "Ir0npack"},
             {"discordName": "GrassyTree#0503", "leagueName": "andyisbomb"},
             {"discordName": "Reginat#3424", "leagueName": "MILF Draven"},
             {"discordName": "rtorrez491#9591", "leagueName": "Kaisious"},
             {"discordName": "DraconianBirch#2672", "leagueName": "DraconianBirch"},
             {"discordName":"Whiitebread#8247", "leagueName":"Whiitebread"},
             {"discordName":"RumHam#9135", "leagueName":"hominy2597"}]

def get_live_data():
    response = requests.get(url, verify=cert_file)
    return response.json()

def update_players_data(data):
    current_players = [user for summoner in data for user in usernames if summoner['summonerName'] == user['leagueName']]
    return current_players

def update_json_file(current_players, data):
    json_file = [{"discordName": player["discordName"], "isDead": summoner["isDead"]}
                 for player in current_players for summoner in data
                 if summoner["summonerName"] == player["leagueName"]]
    
    with open('./data.json', 'w') as file:
        json.dump(json_file, file)

while True:
    try:
        live_data = get_live_data()
        current_players = update_players_data(live_data)

        while True:
            live_data = get_live_data()
            update_json_file(current_players, live_data)
            time.sleep(0.1)
    except Exception as e:
        with open('./data.json', 'w') as file:
            json.dump([], file)
    time.sleep(1)
