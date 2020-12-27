from mparser import MatrixParser
from manalyzer import MatrixAnalyzer
from mjsonifier import MatrixJSON
import pprint

MJ = MatrixJSON("../samples/Log-2020-12-24-14-14-13.txt")
MJ.DumpJSON()
#pprint.pprint(MJ.DumpJSON()['players_ordered'])

parseEngine = MatrixParser()
game = parseEngine.readLog("../samples/Log-2020-12-24-14-14-13.txt")
analyzer = MatrixAnalyzer(game)
#print(analyzer.GetAllTotalDamages())
#print(analyzer.game.section_lengths)
#print({player: analyzer.GetHeroesPlayed(player) for player in analyzer.GetPlayers()})
#parseEngine.write_csv(game, "../samples/TEST.csv")

#owssparser.write_csv(parsed_data, "../samples/workshop_output1.csv")

#player_stats, player_stats_summary = owssanalyzer.analyze("../samples/workshop_output1.csv")
