from mgame import MatrixGame, MatrixPlayer, MatrixMapInfo

class MatrixParser:

    HERO_REMAPS = {'LÃºcio': 'Lucio', 'Torbjörn': 'Torbjorn', 'Wrecking Ball': 'WreckingBall', 'Soldier: 76': 'Soldier76'}

    def __init__(self):
        pass

    def readLog(self, filename):
        game = MatrixGame()
        with open(filename, 'r') as f:
            game.map = next(f).strip().split("]")[1][1:]
            game.map_type = MatrixGame.MAP_TYPES[game.map]
            game.player_tracking.append([{}, {}])
            game.kill_tracking.append([])
            game.section_lengths.append(999999)
            KD_track = [None, None] # [killer, victim]
            runningTS = 0
            prevRunningTS = 0
            PARSEDFILE = [line.strip().split("]")[1][1:].split(",") for line in f]

            for lineNumber, line in enumerate(PARSEDFILE):

                if line[0] == game.map: # new part of map / next side
                    game.player_tracking.append([{}, {}])
                    game.kill_tracking.append([])
                    for team in game.player_tracking[-1]:
                        for player in team:
                            game.section_lengths[-1] = min(game.section_lengths[-1], len(team[player].stats['heroes']))
                    game.section_lengths.append(999999)
                    KD_track = [None, None]
                    runningTS = 0
                    prevRunningTS = 0
                else:
                    timestamp = float(line[0])
                    if len(line) == 3:
                        if line[2] == "Death": # hero death
                            if ((PARSEDFILE[lineNumber-1][2] == "FinalBlow" and abs(float(PARSEDFILE[lineNumber-1][0]) - timestamp) <= 0.05) or (PARSEDFILE[lineNumber+1][2] == "FinalBlow" and abs(float(PARSEDFILE[lineNumber+1][0]) - timestamp) <= 0.05)): # murder
                                KD_track[1] = line[1]
                            else: # suicide
                                KD_track = [line[1], line[1]]
                        elif line[2] == "FinalBlow": # hero final blow
                            KD_track[0] = line[1]
                        else: # map info
                            game.map_tracking.append(MatrixMapInfo())
                            if game.map_type == "Control":
                                game.map_tracking[-1].team1Capture = float(line[1])
                                game.map_tracking[-1].team2Capture = float(line[2])
                            else:
                                game.map_tracking[-1].attacker = 1 if line[1] == "True" else 0
                                game.map_tracking[-1].progress = float(line[2])
                            if (game.map_type == "Hybrid" or game.map_type == "Assault") and len(game.map_tracking) > 2:
                                game.map_tracking[-1].pointCaptured = game.map_tracking[-2].pointCaptured
                                if game.map_tracking[-1].progress == 0 and game.map_tracking[-2].progress >= 80:
                                    game.map_tracking[-1].pointCaptured = True

                        if KD_track[0] is not None and KD_track[1] is not None:
                            game.kill_tracking[-1].append((runningTS, KD_track[0], KD_track[1]))
                            KD_track = [None, None]

                    else: # player info
                        if len(line) >= 24:
                            if "(" in line[20]:
                                playerTeam = line[23]
                            else:
                                playerTeam = line[21]
                        else:
                            playerTeam = "Team 1"
                        playerTeam = 0 if playerTeam == "Team 1" else 1
                        playerName = line[1]
                        if playerName not in game.player_tracking[-1][playerTeam]:
                            game.player_tracking[-1][playerTeam][playerName] = MatrixPlayer()
                            game.player_tracking[-1][playerTeam][playerName].name = playerName
                            game.player_tracking[-1][playerTeam][playerName].team = playerTeam
                        try:
                            game.player_tracking[-1][playerTeam][playerName].stats['position'].append((float(line[20][1:]), float(line[21]), float(line[22][:-1])))
                            if line[2] in self.HERO_REMAPS:
                                game.player_tracking[-1][playerTeam][playerName].stats['heroes'].append(self.HERO_REMAPS[line[2]])
                            else:
                                game.player_tracking[-1][playerTeam][playerName].stats['heroes'].append(line[2])
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
                            if game.player_tracking[-1][playerTeam][playerName].dc_stats['heroes'] is not None:
                                for stat in MatrixPlayer.STAT_TYPES['number_update']:
                                    game.player_tracking[-1][playerTeam][playerName].stats[stat][-1] += game.player_tracking[-1][playerTeam][playerName].dc_stats[stat]
                            runningTS = max(len(game.player_tracking[-1][playerTeam][playerName].stats['heroes']), runningTS)
                            if runningTS > prevRunningTS: # check if missing any stats for a player, and if so, pad with previous stats
                                for team in game.player_tracking[-1]:
                                    for player in team:
                                        timeDiff = runningTS - len(team[player].stats['heroes']) - 1
                                        while timeDiff > 0:
                                            for stat in team[player].stats:
                                                team[player].stats[stat].append(team[player].stats[stat][-1])
                                            timeDiff -= 1
                                prevRunningTS = runningTS
                        except:
                            for stat in game.player_tracking[-1][playerTeam][playerName].dc_stats:
                                game.player_tracking[-1][playerTeam][playerName].dc_stats[stat] = game.player_tracking[-1][playerTeam][playerName].stats[stat][-1]
                            if game.player_tracking[-1][playerTeam][playerName].dc_stats['heroes'] == 'D.Va' and game.player_tracking[-1][playerTeam][playerName].dc_stats['max_health'] <= 200 and len([x[0] for x in game.kill_tracking[-1] if x[2] == playerName and runningTS - x[0] > 10]) == 0: # baby dva
                                game.player_tracking[-1][playerTeam][playerName].dc_stats[stat] -= 600 # adjust for mech damage will take

        for section_num, section in enumerate(game.player_tracking):
            for team in section:
                for player in team:
                    game.section_lengths[section_num] = min(game.section_lengths[section_num], len(team[player].stats['heroes']))

        return game

    def write_csv(self, game, out_filename):
        with open(out_filename, 'w') as o:
            o.write('Section,Timestamp,Team,Player,Hero,Hero Damage Dealt,Barrier Damage Dealt,Damage Blocked,Damage Taken,Deaths,Eliminations,Final Blows,Environmental Deaths,Environmental Kills,Healing Dealt,Objective Kills,Solo Kills,Ultimates Earned,Ultimates Used,Healing Received,Ultimate Charge,Player Closest to Reticle,Cooldown 1,Cooldown 2,Position\n')
            for section in range(0, len(game.player_tracking)):
                for ts in range(0, len(game.player_tracking[section][0][list(game.player_tracking[section][0].keys())[0]].stats['hero_damage_dealt'])):
                    for team in range(0, len(game.player_tracking[section])):
                        for player in game.player_tracking[section][team]:
                            if ts < len(game.player_tracking[section][team][player].stats['hero_damage_dealt']):
                                o.write('%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n' % (
                                    section,
                                    ts,
                                    "Team 1" if team == 0 else "Team 2",
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
