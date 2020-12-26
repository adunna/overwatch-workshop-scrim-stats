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
        final_stats = {player: {stat: self.Analyzer.GetFinalStat(player, stat, players[player]) for stat in STAT_TYPES} for player in players}
        stats_per_minute = {player: {stat: self.Analyzer.GetStatPerMinute(player, stat, players[player]) for stat in STAT_TYPES} for player in players}
        heroes_played = {player: self.Analyzer.GetHeroesPlayed(player) for player in players}
        avg_time_to_ult = {player: self.Analyzer.GetAverageTimeToUltimate(player) for player in players}
        avg_time_ult_held = {player: self.Analyzer.GetAverageTimeUltimateHeld(player) for player in players}
        team_damage_over_time = {
                "team1": self.Analyzer.GetAllTotalDamages(team=0),
                "team2": self.Analyzer.GetAllTotalDamages(team=1),
                }
        return {
                "players": players,
                "heroes_played": heroes_played,
                "final_stats": final_stats,
                "stats_per_minute": stats_per_minute,
                "team_damage_over_time": team_damage_over_time,
                "avg_time_to_ult": avg_time_to_ult,
                "avg_time_ult_held": avg_time_ult_held,
                }
