from collections import defaultdict

formatting = {
    'ts': 0,
    'player': 1,
    'hero': 1,
    'dmg_done': 2,
    'dmg_taken': 3,
    'healing_done': 4,
    'ult_charge': 5,
    'eliminations': 6,
    'deaths': 7,
    'accuracy': 9
}

player_stats_format = [
    'dmg_done',
    'dmg_taken',
    'healing_done',
    'ult_charge',
    'eliminations',
    'deaths',
    'accuracy'
]

def analyze(csv):
    player_stats = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    player_stats_summary = defaultdict(dict)
    player_stats_hero_summary = defaultdict(lambda: defaultdict(dict))
    with open(csv, 'r') as f:
        next(f)
        for line in f:
            line = line.strip().split(",")

            player = line[formatting['player']]
            hero = line[formatting['hero']]

            # player stats populate
            player_stats[player][hero]['dmg_done'].append(int(float(line[formatting['dmg_done']])))
            player_stats[player][hero]['dmg_taken'].append(int(float(line[formatting['dmg_taken']])))
            player_stats[player][hero]['healing_done'].append(int(float(line[formatting['healing_done']])))
            player_stats[player][hero]['ult_charge'].append(int(float(line[formatting['ult_charge']])))
            player_stats[player][hero]['eliminations'].append(int(float(line[formatting['eliminations']])))
            player_stats[player][hero]['deaths'].append(int(float(line[formatting['deaths']])))
            #player_stats[player][hero]['accuracy'].append(int(float(line[formatting['accuracy']])))

    # summarize player stats
    for player in player_stats:
        player_stats_summary[player]['dmg_done'] = 0
        player_stats_summary[player]['dmg_taken'] = 0
        player_stats_summary[player]['healing_done'] = 0
        player_stats_summary[player]['ultimates'] = 0
        player_stats_summary[player]['eliminations'] = 0
        player_stats_summary[player]['deaths'] = 0
        player_stats_summary[player]['hero_time'] = defaultdict(int) # seconds played per hero
        for hero in player_stats[player]:
            # hero stats
            # TODO: player_stats_hero_summary fill

            # player stats
            player_stats_summary[player]['dmg_done'] = max(player_stats_summary[player]['dmg_done'], player_stats[player][hero]['dmg_done'][-1])
            player_stats_summary[player]['dmg_taken'] = max(player_stats_summary[player]['dmg_taken'], player_stats[player][hero]['dmg_taken'][-1])
            player_stats_summary[player]['healing_done'] = max(player_stats_summary[player]['healing_done'], player_stats[player][hero]['healing_done'][-1])
            player_stats_summary[player]['eliminations'] = max(player_stats_summary[player]['eliminations'], player_stats[player][hero]['eliminations'][-1])
            player_stats_summary[player]['deaths'] = max(player_stats_summary[player]['deaths'], player_stats[player][hero]['deaths'][-1])
            prev_max_ult_charge = 0
            for ult_charge in player_stats[player][hero]['ult_charge']:
                if ult_charge >= prev_max_ult_charge:
                    prev_max_ult_charge = ult_charge
                else:
                    prev_max_ult_charge = 0
                    player_stats_summary[player]['ultimates'] += 1
            player_stats_summary[player]['hero_time'][hero] += len(player_stats[player][hero]['dmg_done'])
    
    return (player_stats, player_stats_summary)
