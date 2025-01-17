from flask import Flask, render_template, request, url_for
import os
import requests
from dotenv import load_dotenv
from stats_calculator import calculate_all_stats, get_brawler_stats, get_player_trophies

load_dotenv()

app = Flask(__name__)

API_KEY = os.getenv("API_KEY")
BASE_URL = "https://api.brawlstars.com/v1"

QUOTAGUARDSTATIC_URL = "http://xcazcsmwecie4j:zy3yx9malpjyv8gafppxj0c4pmwd9@us-east-static-04.quotaguard.com:9293"
proxies = {
    "http": QUOTAGUARDSTATIC_URL,
    "https": QUOTAGUARDSTATIC_URL,
}

def get_player_data(player_tag):
    url = f"{BASE_URL}/players/%23{player_tag}"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = requests.get(url, headers=headers, proxies=proxies)
    if response.status_code == 200:
        player_data = response.json()
        print(f"API Response for {player_tag}: {player_data}")
        if not player_data or not isinstance(player_data, dict):
            raise Exception("Player data not found or invalid format.")
        return player_data
    else:
        raise Exception(f"Error fetching player data: {response.status_code} - {response.text}")

def get_player_battle_log(player_tag):
    url = f"{BASE_URL}/players/%23{player_tag}/battlelog"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = requests.get(url, headers=headers, proxies=proxies)
    if response.status_code == 200:
        battle_log = response.json().get('items', [])
        for battle in battle_log:
            print(f"Mode: {battle['battle'].get('mode', 'Unknown')}")
            print(f"Battle Data: {battle}")
            print("-" * 50)
        return battle_log
    else:
        raise Exception(f"Error fetching battle log: {response.status_code} - {response.text}")

@app.route('/')
def index():
    brawl_icon_url = url_for('static', filename='images/brawll.png.png')
    return render_template('index.html', brawl_icon_url=brawl_icon_url)

@app.route('/stats', methods=['POST'])
def stats():
    player_tag = request.form['playerTag'].strip().upper()
    try:
        player_data = get_player_data(player_tag)
        required_keys = ['name', 'trophies', 'highestTrophies']
        for key in required_keys:
            if key not in player_data or player_data[key] is None:
                raise Exception(f"Missing or None key in player data: {key}")
        battle_log = get_player_battle_log(player_tag)
        if not battle_log:
            return "No battle log data found."
        player_stats = {
            "name": player_data.get('name', 'Unknown Player'),
            "current_trophies": player_data.get('trophies', 0),
            "highest_trophies": player_data.get('highestTrophies', 0),
            "three_v_three_victories": player_data.get('3vs3Victories', 'N/A'),
            "solo_victories": player_data.get('soloVictories', 'N/A'),
            "duo_victories": player_data.get('duoVictories', 'N/A'),
            "most_challenge_wins": player_data.get('bestRoboRumbleTime', 'N/A'),
            "profile_picture_url": url_for('static', filename='images/shelly.png.png')
        }
        stats = calculate_all_stats(battle_log, player_tag)
        return render_template('stats.html', stats=stats, player_stats=player_stats)
    except Exception as e:
        return f"An error occurred: {e}"

@app.route('/brawler_stats', methods=['POST'])
def brawler_stats():
    player_tag = request.form['playerTag']
    brawler_name = request.form['brawlerName'].strip().upper()
    try:
        player_data = get_player_data(player_tag)
        brawler_stats = get_brawler_stats(player_data, brawler_name)
        if brawler_stats:
            return render_template('brawler_stats.html', brawler_name=brawler_name, brawler_stats=brawler_stats)
        else:
            return f"No stats found for brawler: {brawler_name}"
    except Exception as e:
        return f"An error occurred: {e}"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
