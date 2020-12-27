from mgame import MatrixPlayer
from mparser import MatrixParser
from manalyzer import MatrixAnalyzer

STAT_TYPES = ['all_damage_dealt', 'barrier_damage_dealt', 'hero_damage_dealt', 'damage_blocked', 'damage_taken', 'eliminations', 'deaths', 'environmental_deaths', 'environmental_kills', 'final_blows', 'healing_dealt', 'healing_received', 'objective_kills', 'solo_kills', 'ultimate_charge', 'ultimates_earned', 'ultimates_used', 'cooldown1', 'cooldown2']

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
        players_ordered = []
        desired_order = ['main_tank', 'off_tank', 'hitscan_dps', 'flex_dps', 'main_support', 'flex_support']
        desired_order_backup = ['tank', 'tank', 'dps', 'dps', 'support', 'support']
        for team in players:
            placed = 0
            prev_placed = placed
            ordering = desired_order
            if inferred_roles[team][players[team][0]] not in desired_order:
                ordering = desired_order_backup
            team_ordered = []
            while len(players[team]) > placed:
                prev_placed = placed
                for player in players[team]:
                    if inferred_roles[team][player] == ordering[placed]:
                        team_ordered.append(player)
                        placed += 1
                        if placed == len(players[team]):
                            break
                if prev_placed == placed: # encountered some error
                    placed = len(players[team])
                    team_ordered = players[team]
                    break
            players_ordered.append(team_ordered)

        team_damage_over_time = {
                "team1": self.Analyzer.GetAllTotalDamages(team=0),
                "team2": self.Analyzer.GetAllTotalDamages(team=1),
                }

        # match events info
        # format each player into one group, for each team
        # can do separately for each section
        match_events = {'kills': [], 'sections': [0]}
        match_event_id = 1
        last_time_end = 0
        all_players = []
        for team in list(players.keys()):
            all_players += players[team]
        match_events['groups'] = [{'id': player, 'content': player} for player in set(all_players)] # TODO: patch to support multiple instances of same player name
        for section in self.Analyzer.game.kill_tracking:
            for kill in section:
                match_events['kills'].append({'id': match_event_id, 'start': last_time_end + kill[0], 'className': 'event-elimination', 'type': 'point', 'group': kill[1], 'content': '', 'title': "Killed " + kill[2]})
                match_event_id += 1
                match_events['kills'].append({'id': match_event_id, 'start': last_time_end + kill[0], 'className': 'event-death', 'type': 'point', 'group': kill[2], 'content': '', 'title': "Died to " + kill[1]})
                match_event_id += 1
            last_time_end = match_events['kills'][-1]['start']
            match_events['sections'].append(last_time_end)

        return {
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
                }
