from mgame import MatrixPlayer
from mparser import MatrixParser
from manalyzer import MatrixAnalyzer

STAT_TYPES = ['all_damage_dealt', 'barrier_damage_dealt', 'hero_damage_dealt', 'damage_blocked', 'damage_taken', 'eliminations', 'deaths', 'environmental_deaths', 'environmental_kills', 'final_blows', 'healing_dealt', 'healing_received', 'objective_kills', 'solo_kills', 'ultimate_charge', 'ultimates_earned', 'ultimates_used']

class MatrixJSON:
    
    def __init__(self, logfile):
        self.ParseEngine = MatrixParser()
        self.game = self.ParseEngine.readLog(logfile)
        self.Analyzer = MatrixAnalyzer(self.game)

    def DumpJSON(self):
        players = self.Analyzer.GetPlayers()
        final_stats = {player: {stat: self.Analyzer.GetFinalStat(player, stat, players[player]) for stat in STAT_TYPES} for player in players}
        stats_per_minute = {player: {stat: self.Analyzer.GetStatPerMinute(player, stat, players[player]) for stat in STAT_TYPES} for player in players}
        return {
                "players": players,
                "final_stats": final_stats,
                "stats_per_minute": stats_per_minute,
                }
