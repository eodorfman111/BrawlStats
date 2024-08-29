def calculate_brawler_score(wins, games_played, star_player_count, trophies):


    if games_played == 0:
        return 0.0

    win_rate = (wins / games_played) * 100
    star_player_rate = (star_player_count / games_played) * 100
    trophy_score = min((trophies / 1000) * 100, 100)  # Normalize to a max of 100%

    score = (
        (win_rate * 0.5) +  # Win rate contributes 50%
        (star_player_rate * 0.3) +  # Star player rate contributes 30%
        (trophy_score * 0.2)  # Trophy count contributes 20%
    )

    return score

def calculate_best_overall_brawler(battle_log, player_tag):

    brawler_stats = {}
    
    # Calculate stats for each brawler
    for battle in battle_log:
        players = battle['battle'].get('players', [])
        for player in players:
            if player['tag'] == f"#{player_tag}":
                brawler_name = player['brawler']['name']
                trophies = player['brawler'].get('trophies', 0)
                is_star_player = player.get('result', '') == 'victory' and player.get('isStarPlayer', False)
                
                if brawler_name not in brawler_stats:
                    brawler_stats[brawler_name] = {
                        'wins': 0,
                        'games_played': 0,
                        'star_player_count': 0,
                        'trophies': trophies
                    }

                brawler_stats[brawler_name]['games_played'] += 1
                if player.get('result', '') == 'victory':
                    brawler_stats[brawler_name]['wins'] += 1
                if is_star_player:
                    brawler_stats[brawler_name]['star_player_count'] += 1

    # Calculate scores
    best_brawler = None
    highest_score = 0

    for brawler_name, stats in brawler_stats.items():
        score = calculate_brawler_score(
            stats['wins'],
            stats['games_played'],
            stats['star_player_count'],
            stats['trophies']
        )

        if score > highest_score:
            highest_score = score
            best_brawler = brawler_name

    return best_brawler, highest_score

def convert_score_to_percentage(score):

    return f"{score:.2f}%"



def get_most_played_brawler(battle_log, player_tag):
    brawler_usage = {}
    
    for battle in battle_log:
        # Handle different battle types, including those without teams
        if 'teams' in battle['battle']:
            for team in battle['battle']['teams']:
                for player in team:
                    if player['tag'] == f"#{player_tag}":
                        brawler = player['brawler']['name']
                        brawler_usage[brawler] = brawler_usage.get(brawler, 0) + 1
        elif 'players' in battle['battle']:
            for player in battle['battle']['players']:
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
        if battle['battle'].get('result') == 'victory':
            # Handle different battle types, including those without teams
            if 'teams' in battle['battle']:
                for team in battle['battle']['teams']:
                    for player in team:
                        if player['tag'] == f"#{player_tag}":
                            brawler = player['brawler']['name']
                            brawler_wins[brawler] = brawler_wins.get(brawler, 0) + 1
            elif 'players' in battle['battle']:
                for player in battle['battle']['players']:
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
        if 'starPlayer' in battle['battle']:
            star_player_tag = battle['battle']['starPlayer']['tag']
            if star_player_tag == f"#{player_tag}":
                brawler = battle['battle']['starPlayer']['brawler']['name']
                star_player_count[brawler] = star_player_count.get(brawler, 0) + 1
    
    most_frequent_star_player_brawler = max(star_player_count, key=star_player_count.get, default=None)
    return most_frequent_star_player_brawler, star_player_count.get(most_frequent_star_player_brawler, 0)

def calculate_star_player_rate(battle_log, player_tag):
    # Get the most frequent star player brawler and their count
    most_frequent_star_player_brawler, star_player_count = get_most_frequent_star_player_brawler(battle_log, player_tag)
    
    if not most_frequent_star_player_brawler:
        return None, 0.0
    
    # Get the wins for the most frequent star player brawler
    brawler_wins = 0
    for battle in battle_log:
        if battle['battle'].get('result') == 'victory':
            if 'teams' in battle['battle']:
                for team in battle['battle']['teams']:
                    for player in team:
                        if player['tag'] == f"#{player_tag}" and player['brawler']['name'] == most_frequent_star_player_brawler:
                            brawler_wins += 1
            elif 'players' in battle['battle']:
                for player in battle['battle']['players']:
                    if player['tag'] == f"#{player_tag}" and player['brawler']['name'] == most_frequent_star_player_brawler:
                        brawler_wins += 1
    
    # Calculate the star player rate
    if brawler_wins > 0:
        star_player_rate = (star_player_count / brawler_wins) * 100
    else:
        star_player_rate = 0.0
    
    return most_frequent_star_player_brawler, star_player_rate

def get_most_played_mode(battle_log):
    mode_usage = {}
    for battle in battle_log:
        mode = battle['battle']['mode']
        mode_usage[mode] = mode_usage.get(mode, 0) + 1
    most_played_mode = max(mode_usage, key=mode_usage.get, default=None)
    return most_played_mode, mode_usage.get(most_played_mode, 0)

def get_team_composition_performance(battle_log, player_tag):
    team_compositions = {}
    for battle in battle_log:
        if 'teams' not in battle['battle']:
            continue  # Skip battles that don't have teams
        
        team = [player['brawler']['name'] for team in battle['battle']['teams'] for player in team if player['tag'] == f"#{player_tag}"]
        if not team:
            continue
        team_comp = tuple(sorted(team))
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
