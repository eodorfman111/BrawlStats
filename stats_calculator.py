def get_most_played_brawler(battle_log, player_tag):
    brawler_usage = {}

    for battle in battle_log:
        if 'rounds' in battle['battle']:
            used_brawlers = set()
            for round_data in battle['battle']['rounds']:
                players = round_data.get('players', [])
                for player in players:
                    if player['tag'] == f"#{player_tag}":
                        brawler = player['brawler']['name']
                        used_brawlers.add(brawler)
            for brawler in used_brawlers:
                brawler_usage[brawler] = brawler_usage.get(brawler, 0) + 1
        else:
            players = battle['battle'].get('players', [])
            for player in players:
                if player['tag'] == f"#{player_tag}":
                    brawler = player['brawler']['name']
                    brawler_usage[brawler] = brawler_usage.get(brawler, 0) + 1

    if not brawler_usage:
        return None, 0

    most_played_brawler = max(brawler_usage, key=brawler_usage.get)
    return most_played_brawler, brawler_usage.get(most_played_brawler, 0)

def get_most_wins_brawler(battle_log, player_tag):
    brawler_wins = {}

    for battle in battle_log:
        if 'rounds' in battle['battle']:
            match_won = False
            used_brawlers = set()
            for round_data in battle['battle']['rounds']:
                if round_data.get('result') == 'victory':
                    players = round_data.get('players', [])
                    for player in players:
                        if player['tag'] == f"#{player_tag}":
                            brawler = player['brawler']['name']
                            used_brawlers.add(brawler)
                    match_won = True
            if match_won:
                for brawler in used_brawlers:
                    brawler_wins[brawler] = brawler_wins.get(brawler, 0) + 1
        else:
            if battle['battle'].get('result') == 'victory':
                players = battle['battle'].get('players', [])
                for player in players:
                    if player['tag'] == f"#{player_tag}":
                        brawler = player['brawler']['name']
                        brawler_wins[brawler] = brawler_wins.get(brawler, 0) + 1

    if not brawler_wins:
        return None, 0

    most_wins_brawler = max(brawler_wins, key=brawler_wins.get)
    return most_wins_brawler, brawler_wins.get(most_wins_brawler, 0)

def get_most_frequent_star_player_brawler(battle_log, player_tag):
    star_player_count = {}

    for battle in battle_log:
        if 'rounds' in battle['battle']:
            star_player_awarded = False
            used_brawlers = set()
            for round_data in battle['battle']['rounds']:
                if 'starPlayer' in round_data:
                    star_player_tag = round_data['starPlayer']['tag']
                    if star_player_tag == f"#{player_tag}":
                        brawler = round_data['starPlayer']['brawler']['name']
                        used_brawlers.add(brawler)
                        star_player_awarded = True
            if star_player_awarded:
                for brawler in used_brawlers:
                    star_player_count[brawler] = star_player_count.get(brawler, 0) + 1
        else:
            if 'starPlayer' in battle['battle']:
                star_player_tag = battle['battle']['starPlayer']['tag']
                if star_player_tag == f"#{player_tag}":
                    brawler = battle['battle']['starPlayer']['brawler']['name']
                    star_player_count[brawler] = star_player_count.get(brawler, 0) + 1

    most_frequent_star_player_brawler = max(star_player_count, key=star_player_count.get, default=None)
    return most_frequent_star_player_brawler, star_player_count.get(most_frequent_star_player_brawler, 0)

def calculate_star_player_rate(battle_log, player_tag):
    most_frequent_star_player_brawler, star_player_count = get_most_frequent_star_player_brawler(battle_log, player_tag)

    if not most_frequent_star_player_brawler:
        return None, 0.0

    brawler_wins = 0
    for battle in battle_log:
        if 'rounds' in battle['battle']:
            match_won = False
            for round_data in battle['battle']['rounds']:
                if round_data.get('result') == 'victory':
                    players = round_data.get('players', [])
                    for player in players:
                        if player['tag'] == f"#{player_tag}" and player['brawler']['name'] == most_frequent_star_player_brawler:
                            match_won = True
                            brawler_wins += 1
            if match_won:
                brawler_wins += 1
        else:
            if battle['battle'].get('result') == 'victory':
                players = battle['battle'].get('players', [])
                for player in players:
                    if player['tag'] == f"#{player_tag}" and player['brawler']['name'] == most_frequent_star_player_brawler:
                        brawler_wins += 1

    if brawler_wins > 0:
        star_player_rate = (star_player_count / brawler_wins) * 100
    else:
        star_player_rate = 0.0

    return most_frequent_star_player_brawler, star_player_rate

def get_most_played_mode(battle_log):
    mode_usage = {}

    for battle in battle_log:
        mode = battle['battle'].get('mode', None)
        if mode:
            mode_usage[mode] = mode_usage.get(mode, 0) + 1

    most_played_mode = max(mode_usage, key=mode_usage.get, default=None)
    return most_played_mode, mode_usage.get(most_played_mode, 0)

def get_team_composition_performance(battle_log, player_tag):
    team_compositions = {}

    for battle in battle_log:
        if 'rounds' in battle['battle']:
            used_teams = set()
            for round_data in battle['battle']['rounds']:
                if 'teams' not in round_data:
                    continue

                team = tuple(sorted([player['brawler']['name'] for team in round_data['teams'] for player in team if player['tag'] == f"#{player_tag}"]))
                if team:
                    used_teams.add(team)

            for team_comp in used_teams:
                result = round_data.get('result')  # Use .get() to avoid KeyError
                if team_comp not in team_compositions:
                    team_compositions[team_comp] = {'wins': 0, 'games': 0}
                team_compositions[team_comp]['games'] += 1
                if result == 'victory':
                    team_compositions[team_comp]['wins'] += 1
        else:
            if 'teams' not in battle['battle']:
                continue

            team_comp = tuple(sorted([player['brawler']['name'] for team in battle['battle']['teams'] for player in team if player['tag'] == f"#{player_tag}"]))
            if team_comp:
                result = battle['battle'].get('result')  # Use .get() to avoid KeyError
                if team_comp not in team_compositions:
                    team_compositions[team_comp] = {'wins': 0, 'games': 0}
                team_compositions[team_comp]['games'] += 1
                if result == 'victory':
                    team_compositions[team_comp]['wins'] += 1

    best_team_composition = None
    best_win_rate = 0

    for team_comp, stats in team_compositions.items():
        win_rate = stats['wins'] / stats['games']
        if win_rate > best_win_rate:
            best_win_rate = win_rate
            best_team_composition = team_comp

    return best_team_composition, team_compositions.get(best_team_composition, {}).get('wins', 0)

def get_player_trophies(player_data):
    """Extracts and returns the player's current and highest trophies."""
    return player_data['trophies'], player_data['highestTrophies']

def get_brawler_stats(player_data, brawler_name):
    """Returns detailed stats for a specific brawler."""
    for brawler in player_data['brawlers']:
        if brawler['name'].upper() == brawler_name.upper():
            return {
                "highest_trophies": brawler['highestTrophies'],
                "power_level": brawler['power'],
                "gears": [gear['name'] for gear in brawler.get('gears', [])],
                "gadgets": [gadget['name'] for gadget in brawler.get('gadgets', [])],
            }
    return None

def calculate_all_stats(battle_log, player_tag):
    stats = {
        "most_played_brawler": get_most_played_brawler(battle_log, player_tag),
        "most_wins_brawler": get_most_wins_brawler(battle_log, player_tag),
        "most_frequent_star_player_brawler": get_most_frequent_star_player_brawler(battle_log, player_tag),
        "highest_star_player_rate": calculate_star_player_rate(battle_log, player_tag),
        "most_played_mode": get_most_played_mode(battle_log),
        "best_team_composition": get_team_composition_performance(battle_log, player_tag),
    }
    return stats