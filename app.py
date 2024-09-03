from flask import Flask, render_template, request
import os
import requests
from dotenv import load_dotenv
from stats_calculator import calculate_all_stats, get_brawler_stats

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

SCRAPER_API_KEY = os.getenv("SCRAPER_API_KEY")
BRAWL_API_KEY = os.getenv("BRAWL_API_KEY")
BASE_URL = "https://api.brawlstars.com/v1"

def get_player_data(player_tag):
    scraperapi_url = 'https://api.scraperapi.com/'
    brawl_stars_url = f"{BASE_URL}/players/%23{player_tag}"

    payload = {
        'api_key': SCRAPER_API_KEY,
        'url': brawl_stars_url
    }

    response = requests.get(scraperapi_url, params=payload)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error fetching player data: {response.status_code} - {response.text}")

def get_player_battle_log(player_tag):
    scraperapi_url = 'https://api.scraperapi.com/'
    brawl_stars_url = f"{BASE_URL}/players/%23{player_tag}/battlelog"

    payload = {
        'api_key': SCRAPER_API_KEY,
        'url': brawl_stars_url
    }

    response = requests.get(scraperapi_url, params=payload)

    if response.status_code == 200:
        return response.json().get('items', [])
    else:
        raise Exception(f"Error fetching battle log: {response.status_code} - {response.text}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/stats', methods=['POST'])
def stats():
    player_tag = request.form['playerTag'].strip().upper()

    try:
        player_data = get_player_data(player_tag)
        battle_log = get_player_battle_log(player_tag)

        if not battle_log:
            return "No battle log data found."

        # Retrieve basic player stats
        player_stats = {
            "name": player_data['name'],
            "current_trophies": player_data['trophies'],
            "highest_trophies": player_data['highestTrophies'],
            "three_v_three_victories": player_data.get('3vs3Victories', 'N/A'),
            "solo_victories": player_data.get('soloVictories', 'N/A'),
            "duo_victories": player_data.get('duoVictories', 'N/A'),
            "most_challenge_wins": player_data.get('bestRoboRumbleTime', 'N/A'),
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
