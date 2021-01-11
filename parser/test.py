from mparser import MatrixParser
from manalyzer import MatrixAnalyzer
from mjsonifier import MatrixJSON
import pprint

MJ = MatrixJSON("../samples/Rialto.txt")
MJ.DumpJSON()
pprint.pprint(MJ.DumpJSON())

# new
parseEngine = MatrixParser()
game = parseEngine.readLog("../samples/Rialto.txt")
parseEngine.write_csv(game, '../samples/TEST.csv')

analyzer = MatrixAnalyzer(game)
print(game.dupe_tracking)
print(analyzer.GetUltTiming("bruhnuts", 1))
analyzer.WriteAuxillaryCSVs('../samples/TEST')

# old
#parseEngine = MatrixParser()
#game = parseEngine.readLog("../samples/Log-2020-12-29-21-37-44.txt")
#analyzer = MatrixAnalyzer(game)
#print(game.kill_tracking)

#print(analyzer.GetUltTiming('Matrix'))
#analyzer.WriteAuxillaryCSVs("../samples/out/f3asdf2sz")
#print(analyzer.GetAllTotalDamages())
#print(analyzer.game.section_lengths)
#print({player: analyzer.GetHeroesPlayed(player) for player in analyzer.GetPlayers()})
#parseEngine.write_csv(game, "../samples/TEST.csv")

#owssparser.write_csv(parsed_data, "../samples/workshop_output1.csv")

#player_stats, player_stats_summary = owssanalyzer.analyze("../samples/workshop_output1.csv")
