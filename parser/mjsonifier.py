from mgame import MatrixPlayer
from mparser import MatrixParser
from manalyzer import MatrixAnalyzer
from mconsts import *

class MatrixJSON:

    def __init__(self, logfile):
        self.ParseEngine = MatrixParser()
        self.game = self.ParseEngine.readLog(logfile)
        self.Analyzer = MatrixAnalyzer(self.game)

    def DumpJSON(self):
        players = self.Analyzer.GetPlayers()
        if len(players) < 2:
            return {}
        final_stats = [{player: {stat: self.Analyzer.GetFinalStat(player, stat, team) for stat in STAT_TYPES} for player in players[team]} for team in players]
        stats_per_minute = [{player: {stat: self.Analyzer.GetStatPerMinute(player, stat, team) for stat in STAT_TYPES} for player in players[team]} for team in players]
        heroes_played = [{player: self.Analyzer.GetHeroesPlayed(player, team) for player in players[team]} for team in players]
        avg_time_to_ult = [{player: self.Analyzer.GetAverageTimeToUltimate(player, team) for player in players[team]} for team in players]
        avg_time_ult_held = [{player: self.Analyzer.GetAverageTimeUltimateHeld(player, team) for player in players[team]} for team in players]
        inferred_roles = [self.Analyzer.GetInferRoles(team) for team in players]
        players_ordered = self.Analyzer.GetPlayerOrder(inferred_roles, players)
        ult_timings_all = [{}, {}] # [team 0, team 1]

        team_damage_over_time = {
            "team1": self.Analyzer.GetAllTotalDamages(team=0),
            "team2": self.Analyzer.GetAllTotalDamages(team=1),
        }

        # match events info
        # format each player into one group, for each team
        # can do separately for each section
        match_events = {'kills': [], 'sections': [0], 'fights': [], 'heroes': [], 'sections_viz': [], 'ultimates': [], 'resurrections': []}
        match_event_id = 1
        last_time_end = 0
        all_players = []
        for team in list(players.keys()):
            all_players += players[team]
        match_events['groups'] = [{'id': player, 'content': player, 'className': 'team-' + str(team_number) + '-row ' + player + '-row'} for team_number, team in enumerate(players_ordered) for player in team] # TODO: patch to support multiple instances of same player name
        for section_num, section in enumerate(self.game.kill_tracking):
            for kill in section:
                match_events['kills'].append({'id': match_event_id, 'start': (last_time_end + kill[0])*1000, 'className': 'event-elimination', 'type': 'point', 'group': kill[1], 'content': '', 'title': "Killed " + kill[2]})
                match_event_id += 1
                match_events['kills'].append({'id': match_event_id, 'start': (last_time_end + kill[0])*1000, 'className': 'event-death', 'type': 'point', 'group': kill[2], 'content': '', 'title': "Died to " + kill[1]})
                match_event_id += 1
            last_time_end += self.game.section_lengths[section_num]
            match_events['sections'].append(last_time_end)
        fights = self.Analyzer.GetFights()
        for section_num, section in enumerate(fights):
            for fight in section:
                fight_winner = self.Analyzer.GetFightWinner(section_num, fight[0], fight[1])
                for team_num, team in enumerate(players_ordered):
                    for player in team:
                        fightclass = 'fight-tie-bg'
                        if team_num == fight_winner:
                            fightclass = 'fight-win-bg'
                        elif fight_winner != -1:
                            fightclass = 'fight-loss-bg'
                        match_events['fights'].append({'id': match_event_id, 'start': (fight[0] + match_events['sections'][section_num])*1000, 'end': (fight[1] + match_events['sections'][section_num])*1000, 'type': 'background', 'className': fightclass, 'group': player})
                        match_event_id += 1
        for team_num, team in enumerate(players_ordered):
            for player in team:
                prev_hero = None
                for section_num in range(0, len(self.game.player_tracking)):
                    for timestamp in range(1, self.game.section_lengths[section_num]):
                        if self.game.player_tracking[section_num][team_num][player].stats['heroes'][timestamp] != prev_hero:
                            match_events['heroes'].append({'id': match_event_id, 'group': player, 'type': 'point', 'start': (timestamp + match_events['sections'][section_num])*1000, 'className': 'event-heroswap', 'style': 'background: url(/static/assets/img/hero_icons/Icon-' + self.game.player_tracking[section_num][team_num][player].stats['heroes'][timestamp] + '.png);'})
                            match_event_id += 1
                        prev_hero = self.game.player_tracking[section_num][team_num][player].stats['heroes'][timestamp]
        for section in match_events['sections'][1:-1]:
            for team in players_ordered:
                for player in team:
                    match_events['sections_viz'].append({'id': match_event_id, 'group': player, 'type': 'background', 'start': section*1000, 'end': (section+1)*1000, 'className': 'section-bg'})
                    match_event_id += 1
        for section_num, section in enumerate(self.game.rez_tracking):
            for rez_point in section:
                match_events['resurrections'].append({'id': match_event_id, 'group': rez_point[1], 'type': 'point', 'start': (rez_point[0] + match_events['sections'][section_num])*1000, 'className': 'event-resurrection'})
                match_event_id += 1
        for team_num, team in enumerate(players_ordered):
            for player in team:
                ult_timings = self.Analyzer.GetUltTiming(player, team_num)
                ult_timings_all[team_num][player] = ult_timings
                for section_num, section in enumerate(ult_timings):
                    for ultinfo in section:
                        # (ult_earned_ts, ult_used_ts)
                        match_events['ultimates'].append({'id': match_event_id, 'group': player, 'type': 'point', 'start': (ultinfo[0] + match_events['sections'][section_num])*1000, 'className': 'event-ultearned'})
                        match_event_id += 1
                        if ultinfo[1] >= 0:
                            match_events['ultimates'].append({'id': match_event_id, 'group': player, 'type': 'point', 'start': (ultinfo[1] + match_events['sections'][section_num])*1000, 'className': 'event-ultused'})
                            match_event_id += 1
                            if ultinfo[0] != ultinfo[1]:
                                match_events['ultimates'].append({'id': match_event_id, 'group': player, 'type': 'background', 'start': (ultinfo[0] + match_events['sections'][section_num])*1000, 'end': (ultinfo[1] + match_events['sections'][section_num])*1000, 'className': 'event-ultheld'})
                                match_event_id += 1

        return {
                "game_map": self.game.map,
                "game_map_type": self.game.map_type,
                "game_map_score": self.game.map_score,
                "players": players,
                "heroes_played": heroes_played,
                "final_stats": final_stats,
                "stats_per_minute": stats_per_minute,
                "team_damage_over_time": team_damage_over_time,
                "avg_time_to_ult": avg_time_to_ult,
                "avg_time_ult_held": avg_time_ult_held,
                "inferred_roles": inferred_roles,
                "players_ordered": players_ordered,
                "match_events": match_events,
                "ult_timings": ult_timings_all,
                }
