from mgame import MatrixGame, MatrixPlayer, MatrixMapInfo

class MatrixParser:

    def __init__(self):
        pass

    def readLog(self, filename):
        game = MatrixGame()
        with open(filename, 'r') as f:
            game.map = next(f).strip().split("]")[1][1:]
            game.map_type = MatrixGame.MAP_TYPES[game.map]
            game.player_tracking.append([{}, {}])

            for line in f:
                line = line.strip().split("]")[1][1:].split(",")

                if line[0] == game.map: # new part of map / next side
                    game.player_tracking.append([{}, {}])

                else:
                    timestamp = int(float(line[0]))
                    if len(line) == 3: # map info
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

                    else: # player info
                        playerTeam = line[23] if len(line) >= 24 else "Team 1"
                        playerTeam = 0 if playerTeam == "Team 1" else 1
                        playerName = line[1]
                        if playerName not in game.player_tracking[-1][playerTeam]:
                            game.player_tracking[-1][playerTeam][playerName] = MatrixPlayer()
                            game.player_tracking[-1][playerTeam][playerName].name = playerName
                            game.player_tracking[-1][playerTeam][playerName].team = playerTeam
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
                        try:
                            game.player_tracking[-1][playerTeam][playerName].stats['position'].append((float(line[20][1:]), float(line[21]), float(line[22][:-1])))
                        except:
                            game.player_tracking[-1][playerTeam][playerName].stats['position'].append((0, 0, 0))

        return game

    def write_csv(self, game, out_filename):
        with open(out_filename, 'w') as o:
            o.write('Section,Timestamp,Team,Player,Hero,Hero Damage Dealt,Barrier Damage Dealt,Damage Blocked,Damage Taken,Deaths,Eliminations,Final Blows,Environmental Deaths,Environmental Kills,Healing Dealt,Objective Kills,Solo Kills,Ultimates Earned,Ultimates Used,Healing Received,Ultimate Charge,Player Closest to Reticle,Position\n')
            for section in range(0, len(game.player_tracking)):
                for ts in range(0, len(game.player_tracking[section][0][list(game.player_tracking[section][0].keys())[0]].stats['hero_damage_dealt'])):
                    for team in range(0, len(game.player_tracking[section])):
                        for player in game.player_tracking[section][team]:
                            if ts < len(game.player_tracking[section][team][player].stats['hero_damage_dealt']):
                                o.write('%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n' % (
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
                                    str(game.player_tracking[section][team][player].stats['position'][ts])
                                ))
