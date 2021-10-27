from mgame import MatrixGame, MatrixPlayer, MatrixMapInfo
from mconsts import *

class MatrixParser:

    def __init__(self):
        pass

    def readLog(self, filename):

        INFO_LINES = []
        PARSED_LINES = []

        # Read log
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                if line[0] == '[':
                    line.replace('McCree', 'Cassidy')
                    if ',' in line:
                        PARSED_LINES.append(line.strip()[11:].split(','))
                    else:
                        INFO_LINES.append(line.strip()[11:])

        # Initialize game
        game = MatrixGame()
        KOTH_SECTION = ''
        TRACK_KILLER = None
        TRACK_VICTIM = None
        runningTS = 0
        prevRunningTS = 0

        # Determine version
        if len(INFO_LINES) != 0:
            if INFO_LINES[0] == 'Lobby Version: 0.6':
                game.version = Version.V0_6
        
        # Set game map (TODO: determine language first, and then convert accordingly)
        game.map = PARSED_LINES[0][0]
        if game.map in KR_REMAP_MAPS:
            game.map = KR_REMAP_MAPS[game.map]
            game.language = LANG_KR
        game.map_type = MAP_TYPES[game.map]

        # Set team names
        if len(PARSED_LINES[0]) == 3 or len(PARSED_LINES[0]) == 4:
            game.team_names = [PARSED_LINES[0][1], PARSED_LINES[0][2]]
            if len(PARSED_LINES[0]) == 4:
                KOTH_SECTION = PARSED_LINES[0][3]
        else:
            if game.language == LANG_EN:
                game.team_names = ["Team 1", "Team 2"]
            elif game.language == LANG_KR:
                game.team_names = ["1팀", "2팀"]
        
        # Parse rest of game data
        for lineNumber, line in enumerate(PARSED_LINES[1:]):

            if len(line) == 0: # empty line
                pass
            elif line[0] == '': # no content
                pass
            elif len(line) == 12: # player order
                game.player_order = [line[0:6], line[6:]]
            elif (game.language == LANG_EN and line[0] == game.map) or (game.language == LANG_KR and line[0] in KR_REMAP_MAPS and KR_REMAP_MAPS[line[0]] == game.map): # new part of map / next side
                for team in game.player_tracking[-1]:
                    for player in team:
                        game.section_lengths[-1] = min(game.section_lengths[-1], len(team[player].stats['heroes']))
                        #game.section_lengths[-1] = min([game.section_lengths[-1]] + [len(team[player].stats[stat]) for stat in team[player].stats if len(team[player].stats[stat]) != 0])
                game.map_tracking.append([])
                game.player_tracking.append([{}, {}])
                game.kill_tracking.append([])
                game.overall_deaths.append({})
                game.rez_tracking.append([])
                game.dupe_tracking.append({})
                game.section_lengths.append(999999)
                TRACK_KILLER = None
                TRACK_VICTIM = None
                runningTS = 0
                prevRunningTS = 0
                KOTH_SECTION = line[3]
            else:
                timestamp = float(line[0])
                if len(line) == 3:
                    if line[2] == "Death": # hero death
                        if ((PARSED_LINES[lineNumber-1][2] == "FinalBlow" and abs(float(PARSED_LINES[lineNumber-1][0]) - timestamp) <= 0.05) or (PARSED_LINES[lineNumber+1][2] == "FinalBlow" and abs(float(PARSED_LINES[lineNumber+1][0]) - timestamp) <= 0.05)): # murder
                            TRACK_VICTIM = line[1]
                        else: # suicide
                            TRACK_KILLER = line[1]
                            TRACK_VICTIM = line[1]
                    elif line[2] == "FinalBlow": # hero final blow
                        TRACK_KILLER = line[1]
                    elif line[1] == "Suicide": # hero suicide
                        game.kill_tracking[-1].append((runningTS, line[2], line[2], 'Suicide'))
                        if line[2] not in game.overall_deaths[-1]:
                            game.overall_deaths[-1][line[2]] = []
                        game.overall_deaths[-1][line[2]].append(runningTS)
                    elif line[1] == "Resurrected": # hero rezzed
                        if line[2] not in game.overall_deaths[-1]:
                            game.overall_deaths[-1][line[2]] = []
                        elif len(game.overall_deaths[-1][line[2]]) > 0 and runningTS - game.overall_deaths[-1][line[2]][-1] <= 10: # make sure player died recently
                            # check that player was not rezzed recently
                            not_rez = False
                            for rez_point in game.rez_tracking[-1]:
                                if rez_point[1] == line[2] and runningTS - rez_point[0] <= 10:
                                    not_rez = True
                            if not not_rez:
                                game.rez_tracking[-1].append((runningTS, line[2]))
                    elif line[1] == "DuplicatingEnd": # end dupe
                        if line[2] not in game.dupe_tracking[-1]: # dupe did not stop before match end
                            game.dupe_tracking[-2][line[2]][-1][1] = game.section_lengths[-2]
                        else: # dupe stopped normally
                            game.dupe_tracking[-1][line[2]][-1][1] = runningTS
                    else: # map info
                        game.map_tracking[-1].append(MatrixMapInfo())
                        game.map_tracking[-1][-1].point_number = KOTH_SECTION
                        if game.map_type == "Control":
                            game.map_tracking[-1][-1].team1Capture = float(line[1])
                            game.map_tracking[-1][-1].team2Capture = float(line[2])
                        else:
                            game.map_tracking[-1][-1].attacker = 0 if line[1] == "True" else 1
                            game.map_tracking[-1][-1].progress = float(line[2])
                        if (game.map_type == "Hybrid" or game.map_type == "Assault") and len(game.map_tracking[-1]) > 2:
                            game.map_tracking[-1][-1].pointCaptured = game.map_tracking[-1][-2].pointCaptured
                            if game.map_tracking[-1][-1].progress == 0 and game.map_tracking[-1][-2].progress >= 80:
                                game.map_tracking[-1][-1].pointCaptured = True

                    if TRACK_KILLER is not None and TRACK_VICTIM is not None:
                        game.kill_tracking[-1].append((runningTS, TRACK_KILLER, TRACK_VICTIM, 'Unknown'))
                        TRACK_KILLER = None
                        TRACK_VICTIM = None

                elif len(line) == 4:
                    if line[1] == "DuplicatingStart":
                        if line[2] not in game.dupe_tracking[-1]:
                            game.dupe_tracking[-1][line[2]] = []
                        if game.language == LANG_EN:
                            game.dupe_tracking[-1][line[2]].append([runningTS, 0, line[3]])
                        elif game.language == LANG_KR:
                            game.dupe_tracking[-1][line[2]].append([runningTS, 0, KR_REMAP_HEROES[line[3]]])

                elif len(line) == 5:
                    if line[1] == "FinalBlow":
                        game.kill_tracking[-1].append((runningTS, line[2], line[3], line[4])) # later will add what died to, which is line[4]
                        if line[3] not in game.overall_deaths[-1]:
                            game.overall_deaths[-1][line[3]] = []
                        game.overall_deaths[-1][line[3]].append(runningTS)

                else: # player info
                    if len(line) >= 24:
                        if "(" in line[20]:
                            playerTeam = line[23]
                        else:
                            playerTeam = line[21]
                    else:
                        playerTeam = "Team 1"
                    if playerTeam not in game.team_names: # outdated but still has team names
                        # need to infer new team names
                        if len(game.player_tracking[-1][0]) == 0:
                            game.team_names[0] = playerTeam
                        else:
                            game.team_names[1] = playerTeam
                    playerTeam = 0 if playerTeam == game.team_names[0] else 1
                    playerName = line[1]
                    if playerName not in game.player_tracking[-1][playerTeam]:
                        game.player_tracking[-1][playerTeam][playerName] = MatrixPlayer()
                        game.player_tracking[-1][playerTeam][playerName].name = playerName
                        game.player_tracking[-1][playerTeam][playerName].team = playerTeam
                    try:
                        game.player_tracking[-1][playerTeam][playerName].stats['position'].append((float(line[20][1:]), float(line[21]), float(line[22][:-1])))
                        if game.language == LANG_EN:
                            if line[2] in HERO_REMAPS:
                                game.player_tracking[-1][playerTeam][playerName].stats['heroes'].append(HERO_REMAPS[line[2]])
                            elif 'Torb' in line[2]:
                                game.player_tracking[-1][playerTeam][playerName].stats['heroes'].append('Torbjorn')
                            elif 'cio' in line[2]:
                                game.player_tracking[-1][playerTeam][playerName].stats['heroes'].append('Lucio')
                            else:
                                game.player_tracking[-1][playerTeam][playerName].stats['heroes'].append(line[2])
                        elif game.language == LANG_KR:
                            game.player_tracking[-1][playerTeam][playerName].stats['heroes'].append(KR_REMAP_HEROES[line[2]])
                        
                        # Patch numbers that are asterisks
                        for stat in STAT_NUMBER_MAPS:
                            if STAT_NUMBER_MAPS[stat] < len(line) and '*' in line[STAT_NUMBER_MAPS[stat]] and len(game.player_tracking[-1][playerTeam][playerName].stats['hero_damage_dealt']) != 0:
                                line[STAT_NUMBER_MAPS[stat]] = str(game.player_tracking[-1][playerTeam][playerName].stats[stat][-1])                                

                        game.player_tracking[-1][playerTeam][playerName].stats['hero_damage_dealt'].append(float(line[3]))
                        game.player_tracking[-1][playerTeam][playerName].stats['barrier_damage_dealt'].append(float(line[4]))
                        game.player_tracking[-1][playerTeam][playerName].stats['damage_blocked'].append(float(line[5]))
                        game.player_tracking[-1][playerTeam][playerName].stats['damage_taken'].append(float(line[6]))
                        game.player_tracking[-1][playerTeam][playerName].stats['deaths'].append(int(line[7]))
                        game.player_tracking[-1][playerTeam][playerName].stats['eliminations'].append(int(line[8]))
                        game.player_tracking[-1][playerTeam][playerName].stats['final_blows'].append(int(line[9]))
                        game.player_tracking[-1][playerTeam][playerName].stats['environmental_deaths'].append(int(line[10]))
                        game.player_tracking[-1][playerTeam][playerName].stats['environmental_kills'].append(int(line[11]))
                        game.player_tracking[-1][playerTeam][playerName].stats['healing_dealt'].append(float(line[12]))
                        game.player_tracking[-1][playerTeam][playerName].stats['objective_kills'].append(int(line[13]))
                        game.player_tracking[-1][playerTeam][playerName].stats['solo_kills'].append(int(line[14]))
                        game.player_tracking[-1][playerTeam][playerName].stats['ultimates_earned'].append(int(line[15]))
                        game.player_tracking[-1][playerTeam][playerName].stats['ultimates_used'].append(int(line[16]))
                        game.player_tracking[-1][playerTeam][playerName].stats['healing_received'].append(float(line[17]))
                        game.player_tracking[-1][playerTeam][playerName].stats['ultimate_charge'].append(float(line[18]))
                        game.player_tracking[-1][playerTeam][playerName].stats['player_closest_reticle'].append(line[19])
                        game.player_tracking[-1][playerTeam][playerName].stats['cooldown1'].append(float(line[24]))
                        game.player_tracking[-1][playerTeam][playerName].stats['cooldown2'].append(float(line[25]))
                        if len(line) > 26:
                            game.player_tracking[-1][playerTeam][playerName].stats['max_health'].append(float(line[26]))
                        else:
                            game.player_tracking[-1][playerTeam][playerName].stats['max_health'].append(0)
                        
                        if game.version >= Version.V0_6:
                            game.player_tracking[-1][playerTeam][playerName].stats['offensive_assists'].append(int(line[27]))
                            game.player_tracking[-1][playerTeam][playerName].stats['defensive_assists'].append(int(line[28]))
                            game.player_tracking[-1][playerTeam][playerName].stats['charge_ability1'].append(float(line[29]))
                            game.player_tracking[-1][playerTeam][playerName].stats['charge_ability2'].append(float(line[30]))
                            game.player_tracking[-1][playerTeam][playerName].stats['resource_primary'].append(float(line[31]))
                            game.player_tracking[-1][playerTeam][playerName].stats['resource_secondary'].append(float(line[32]))
                            game.player_tracking[-1][playerTeam][playerName].stats['resource_ability1'].append(float(line[33]))
                            game.player_tracking[-1][playerTeam][playerName].stats['resource_ability2'].append(float(line[34]))
                            game.player_tracking[-1][playerTeam][playerName].stats['weapon_accuracy'].append(float(line[35]))

                        if game.player_tracking[0][playerTeam][playerName].dc_stats['heroes'] is not None:
                            for stat in MatrixPlayer.STAT_TYPES['number_update']:
                                if len(game.player_tracking[-1][playerTeam][playerName].stats[stat]) > 0:
                                    game.player_tracking[-1][playerTeam][playerName].stats[stat][-1] += game.player_tracking[0][playerTeam][playerName].dc_stats[stat]
                        runningTS = max(len(game.player_tracking[-1][playerTeam][playerName].stats['heroes']), runningTS)
                        if runningTS > prevRunningTS: # check if missing any stats for a player, and if so, pad with previous stats
                            for team in game.player_tracking[-1]:
                                for player in team:
                                    timeDiff = runningTS - len(team[player].stats['heroes']) - 1
                                    while timeDiff > 0:
                                        for stat in team[player].stats:
                                            if len(team[player].stats[stat]) > 0:
                                                team[player].stats[stat].append(team[player].stats[stat][-1])
                                        timeDiff -= 1
                            prevRunningTS = runningTS
                    except Exception as e:
                        print(e)
                        for stat in game.player_tracking[0][playerTeam][playerName].dc_stats:
                            if len(game.player_tracking[-1][playerTeam][playerName].stats[stat]) > 0:
                                game.player_tracking[0][playerTeam][playerName].dc_stats[stat] = game.player_tracking[-1][playerTeam][playerName].stats[stat][-1]
                            else:
                                game.player_tracking[0][playerTeam][playerName].dc_stats[stat] = 0
                        if len(game.player_tracking[-1][playerTeam][playerName].stats['heroes']) == 0:
                            game.player_tracking[0][playerTeam][playerName].dc_stats['position'] = (0, 0, 0)
                            game.player_tracking[0][playerTeam][playerName].dc_stats['heroes'] = ''
                            game.player_tracking[0][playerTeam][playerName].dc_stats['player_closest_reticle'] = ''
                        if game.player_tracking[0][playerTeam][playerName].dc_stats['heroes'] == 'D.Va' and game.player_tracking[-1][playerTeam][playerName].dc_stats['max_health'] <= 200 and len([x[0] for x in game.kill_tracking[-1] if x[2] == playerName and runningTS - x[0] > 10]) == 0: # baby dva
                            game.player_tracking[0][playerTeam][playerName].dc_stats['damage_taken'] -= 600 # adjust for mech damage will take

        for section_num, section in enumerate(game.player_tracking):
            for team in section:
                for player in team:
                    game.section_lengths[section_num] = min(game.section_lengths[section_num], len(team[player].stats['heroes']))

        return game

    def write_csv(self, game, out_filename):

        # Make CSV header
        HEADER = 'Map,Section,Timestamp,Team,Player,Hero,Hero Damage Dealt,Barrier Damage Dealt,Damage Blocked,Damage Taken,Deaths,Eliminations,Final Blows,Environmental Deaths,Environmental Kills,Healing Dealt,Objective Kills,Solo Kills,Ultimates Earned,Ultimates Used,Healing Received,Ultimate Charge,Player Closest to Reticle,Cooldown 1,Cooldown 2,Position'
        if game.version >= Version.V0_6:
            HEADER += ',Offensive Assists,Defensive Assists,Ability 1 Charge,Ability 2 Charge,Primary Resource,Secondary Resource,Ability 1 Resource,Ability 2 Resource,Weapon Accuracy'
        
        # Write CSV
        with open(out_filename, 'w', encoding='utf-8') as o:
            o.write(HEADER + '\n')
            for section in range(0, len(game.player_tracking)):
                for ts in range(0, game.section_lengths[section]):
                    for team in range(0, len(game.player_tracking[section])):
                        for player in game.player_tracking[section][team]:
                            if ts < len(game.player_tracking[section][team][player].stats['hero_damage_dealt']):

                                o.write('%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s' % (
                                    game.map,
                                    section,
                                    ts,
                                    game.team_names[0] if team == 0 else game.team_names[1],
                                    player,
                                    game.player_tracking[section][team][player].stats['heroes'][ts],
                                    game.player_tracking[section][team][player].stats['hero_damage_dealt'][ts],
                                    game.player_tracking[section][team][player].stats['barrier_damage_dealt'][ts],
                                    game.player_tracking[section][team][player].stats['damage_blocked'][ts],
                                    game.player_tracking[section][team][player].stats['damage_taken'][ts],
                                    game.player_tracking[section][team][player].stats['deaths'][ts],
                                    game.player_tracking[section][team][player].stats['eliminations'][ts],
                                    game.player_tracking[section][team][player].stats['final_blows'][ts],
                                    game.player_tracking[section][team][player].stats['environmental_deaths'][ts],
                                    game.player_tracking[section][team][player].stats['environmental_kills'][ts],
                                    game.player_tracking[section][team][player].stats['healing_dealt'][ts],
                                    game.player_tracking[section][team][player].stats['objective_kills'][ts],
                                    game.player_tracking[section][team][player].stats['solo_kills'][ts],
                                    game.player_tracking[section][team][player].stats['ultimates_earned'][ts],
                                    game.player_tracking[section][team][player].stats['ultimates_used'][ts],
                                    game.player_tracking[section][team][player].stats['healing_received'][ts],
                                    game.player_tracking[section][team][player].stats['ultimate_charge'][ts],
                                    game.player_tracking[section][team][player].stats['player_closest_reticle'][ts],
                                    game.player_tracking[section][team][player].stats['cooldown1'][ts],
                                    game.player_tracking[section][team][player].stats['cooldown2'][ts],
                                    "(" + str(game.player_tracking[section][team][player].stats['position'][ts][0]) + "; " + str(game.player_tracking[section][team][player].stats['position'][ts][1]) + "; " + str(game.player_tracking[section][team][player].stats['position'][ts][2]) + ")",
                                ))

                                # Version-specific stats

                                if game.version >= Version.V0_6:
                                    o.write(',%s,%s,%s,%s,%s,%s,%s,%s,%s' % (
                                        game.player_tracking[section][team][player].stats['offensive_assists'][ts],
                                        game.player_tracking[section][team][player].stats['defensive_assists'][ts],
                                        game.player_tracking[section][team][player].stats['charge_ability1'][ts],
                                        game.player_tracking[section][team][player].stats['charge_ability2'][ts],
                                        game.player_tracking[section][team][player].stats['resource_primary'][ts],
                                        game.player_tracking[section][team][player].stats['resource_secondary'][ts],
                                        game.player_tracking[section][team][player].stats['resource_ability1'][ts],
                                        game.player_tracking[section][team][player].stats['resource_ability2'][ts],
                                        game.player_tracking[section][team][player].stats['weapon_accuracy'][ts],
                                    ))

                                o.write('\n')
