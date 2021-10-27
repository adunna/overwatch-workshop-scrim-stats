from mgame import MatrixPlayer
from mparser import MatrixParser
from manalyzer import MatrixAnalyzer
import argparse
from datetime import datetime
from influxdb_client import InfluxDBClient, Point, WritePrecision, WriteOptions
from influxdb_client.client.write_api import SYNCHRONOUS, ASYNCHRONOUS
import os

# Consts

token = "lkeQU_adQIBs5eh4XbyNI4D2Jy0eweHKCnB0yMQ7SkYn0CXalwtWNjm2KEZNPTbSJoR_rDLgEcXuKejFCRnkUA=="
org = "OverStat Malice"
bucket = "OverStat Malice Data"
client = InfluxDBClient(url="http://192.168.1.99:8086", token=token)
#token = "XiDu3FW7M4VrkVoG3Svt3omlmHBAcVthg0rFtRz2G3DxYNIHIOD9c463Q_611lJYpTHA5eL3R-_awRJ8slEJxw=="
#org = "OverStat Local Dev"
#bucket = "Malice Local"
#client = InfluxDBClient(url="http://localhost:8086", token=token)

write_api = client.write_api(write_options=SYNCHRONOUS)
roster_set = set(['akash', 'slugo', 'anghell1c', 'cyy'])
roster_aliases = {
    'akash': set(['MALPlayer1', 'BigBoy', 'Akash']),
    'Krawi': set(['MALPlayer2', 'krawi']),
    'foreshadow': set(['MALPlayer3', 'Hyohyun', 'Foreshadow']),
    'cyy': set(['MALPlayer4']),
    'Anghell1c': set(['MALPlayer5', 'anghell1c']),
    'Slugo': set(['MALPlayer6', 'slugo']),
    'TR33': set(['MALSub1', 'tr33', 'Tr33']),
    'mycrazycat': set(['MALSub2', 'MyCrazyCat']),
}
roster_name = 'Malice'
reference_start_time = 1621208532 # May 16, 2021, at 19:42:12 EST

# Get scrim information

arg_parser = argparse.ArgumentParser(description='Add map to InfluxDB.')
arg_parser.add_argument('logfile', type=str, help='log file (or folder of log files) from map')
arg_parser.add_argument('date', type=str, help='date of map, format MM-DD-YYYY')
arg_parser.add_argument('enemy', type=str, help='enemy team name')

args = arg_parser.parse_args()

# Read log(s)

logfiles = []
if args.logfile.endswith('.txt'):
    logfiles.append(args.logfile)
else:
    if not args.logfile.endswith('/'):
        args.logfile += '/'
    logfiles = [args.logfile + x for x in os.listdir(args.logfile)]

def ReplaceNames():
    for LOG in logfiles:
        filedata = None
        with open(LOG, 'r') as r:
            filedata = r.read()
        for player in roster_aliases:
            for name_to_replace in roster_aliases[player]:
                filedata = filedata.replace(name_to_replace, player)
        with open(LOG, 'w') as o:
            o.write(filedata)

def Convert():

    for LOG in logfiles:
        parseEngine = MatrixParser()
        game = parseEngine.readLog(LOG)
        analyzer = MatrixAnalyzer(game)
        players = analyzer.GetPlayers()
        string_stat_types = MatrixPlayer.STAT_TYPES['string'].union(MatrixPlayer.STAT_TYPES['vector'])

        # Assign teams

        HOME_TEAM = 0
        ENEMY_TEAM = 1

        for team in players:
            for player in players[team]:
                if player.lower() in roster_set:
                    HOME_TEAM = team
                    ENEMY_TEAM = 1 - team

        # Store player data

        for team in players:
            for player in players[team]:
                for section_num, section in enumerate(game.player_tracking):
                    data_points = []
                    db_ts_modifier = 0 if section_num == 0 else sum(game.section_lengths[0:section_num])
                    for stat in section[team][player].stats:
                        for timestamp in range(0, len(section[team][player].stats[stat])):
                            curr_team = roster_name if team == HOME_TEAM else args.enemy
                            curr_enemy = roster_name if team == ENEMY_TEAM else args.enemy
                            value = '"' + str(section[team][player].stats[stat][timestamp]) + '"' if stat in string_stat_types else float(section[team][player].stats[stat][timestamp])
                            point = Point("playerstat_" + stat).tag('date', args.date).tag('team', curr_team).tag('enemy', curr_enemy).tag('map', game.map).tag('section', section_num).tag('player', player).tag('hero', section[team][player].stats['heroes'][timestamp]).field('value', value).time(reference_start_time + db_ts_modifier + timestamp, WritePrecision.S)
                            data_points.append(point)
                    write_api.write(bucket, org, data_points)
        
        # Store map data

        for section_num, section_length in enumerate(game.section_lengths):
            data_points = []
            db_ts_modifier = 0 if section_num == 0 else sum(game.section_lengths[0:section_num])
            for timestamp in range(0, len(game.map_tracking[section_num])):
                map_data = game.map_tracking[section_num][timestamp]
                data_points.append(Point('mapstat_point_number').tag('date', args.date).tag('map', game.map).tag('section', section_num).field('value', float(map_data.point_number)).time(reference_start_time + db_ts_modifier + timestamp, WritePrecision.S))
                data_points.append(Point('mapstat_koth_progress').tag('date', args.date).tag('team', roster_name).tag('map', game.map).tag('section', section_num).field('value', float(map_data.team1Capture if HOME_TEAM == 0 else map_data.team2Capture)).time(reference_start_time + db_ts_modifier + timestamp, WritePrecision.S))
                data_points.append(Point('mapstat_koth_progress').tag('date', args.date).tag('team', args.enemy).tag('map', game.map).tag('section', section_num).field('value', float(map_data.team1Capture if ENEMY_TEAM == 0 else map_data.team2Capture)).time(reference_start_time + db_ts_modifier + timestamp, WritePrecision.S))
                data_points.append(Point('mapstat_progress').tag('date', args.date).tag('team', roster_name if map_data.attacker == HOME_TEAM else args.enemy).tag('map', game.map).tag('section', section_num).field('value', float(map_data.progress)).time(reference_start_time + db_ts_modifier + timestamp, WritePrecision.S))
                data_points.append(Point('mapstat_point_captured').tag('date', args.date).tag('team', roster_name if map_data.attacker == HOME_TEAM else args.enemy).tag('map', game.map).tag('section', section_num).field('value', map_data.pointCaptured).time(reference_start_time + db_ts_modifier + timestamp, WritePrecision.S))
            write_api.write(bucket, org, data_points)
        
        # Store kill data

        for section_num, kills in enumerate(game.kill_tracking):
            data_points = []
            db_ts_modifier = 0 if section_num == 0 else sum(game.section_lengths[0:section_num])
            for kill_data in game.kill_tracking[section_num]:
                player_team = analyzer.GetTeam(kill_data[1])
                enemy_team = analyzer.GetTeam(kill_data[2])
                curr_team = roster_name if player_team == HOME_TEAM else args.enemy
                curr_enemy = roster_name if enemy_team == HOME_TEAM else args.enemy
                if kill_data[0] <= len(game.player_tracking[section_num][player_team][kill_data[1]].stats['heroes']) - 1 and kill_data[0] <= len(game.player_tracking[section_num][enemy_team][kill_data[2]].stats['heroes']) - 1:
                    data_points.append(Point('eventstat_kill').tag('date', args.date).tag('team', curr_team).tag('enemy', curr_enemy).tag('map', game.map).tag('section', section_num).tag('player', kill_data[1]).tag('hero', game.player_tracking[section_num][player_team][kill_data[1]].stats['heroes'][kill_data[0]]).tag('victim_hero', game.player_tracking[section_num][enemy_team][kill_data[2]].stats['heroes'][kill_data[0]]).tag('victim', kill_data[2]).field('killer', kill_data[1]).field('victim', kill_data[2]).field('death_cause', kill_data[3]).time(reference_start_time + db_ts_modifier + kill_data[0], WritePrecision.S))
                else:
                    data_points.append(Point('eventstat_kill').tag('date', args.date).tag('team', curr_team).tag('enemy', curr_enemy).tag('map', game.map).tag('section', section_num).tag('player', kill_data[1]).tag('victim', kill_data[2]).field('killer', kill_data[1]).field('victim', kill_data[2]).field('death_cause', kill_data[3]).time(reference_start_time + db_ts_modifier + kill_data[0], WritePrecision.S))
            write_api.write(bucket, org, data_points)
        
        # Store ultimate data

        for team in players:
            for player in players[team]:
                curr_team = roster_name if team == HOME_TEAM else args.enemy
                curr_enemy = roster_name if team == ENEMY_TEAM else args.enemy
                ult_timings = analyzer.GetUltTiming(player, team)
                data_points = []
                for section_num, section in enumerate(ult_timings):
                    db_ts_modifier = 0 if section_num == 0 else sum(game.section_lengths[0:section_num])
                    for ultinfo in section:
                        data_points.append(Point('eventstat_ult_earned').tag('date', args.date).tag('team', curr_team).tag('enemy', curr_enemy).tag('map', game.map).tag('section', section_num).tag('player', player).tag('hero', game.player_tracking[section_num][team][player].stats['heroes'][ultinfo[0]]).field('value', 1).time(reference_start_time + db_ts_modifier + ultinfo[0], WritePrecision.S))
                        if ultinfo[1] >= 0:
                            data_points.append(Point('eventstat_ult_used').tag('date', args.date).tag('team', curr_team).tag('enemy', curr_enemy).tag('map', game.map).tag('section', section_num).tag('player', player).tag('hero', game.player_tracking[section_num][team][player].stats['heroes'][ultinfo[1]]).field('value', 1).time(reference_start_time + db_ts_modifier + ultinfo[1], WritePrecision.S))
                write_api.write(bucket, org, data_points)

ReplaceNames()
Convert()
client.close()