from mparser import MatrixParser
from manalyzer import MatrixAnalyzer
from mjsonifier import MatrixJSON
import pprint

# MJ = MatrixJSON("../samples/Log-2021-01-14-23-26-20.txt")
# json_dump = MJ.DumpJSON()
# pprint.pprint(json_dump['final_stats'][0]['scoob'])

# new
parseEngine = MatrixParser()
game = parseEngine.readLog("../samples/Ur3v5kDzC89XykDU.txt")

analyzer = MatrixAnalyzer(game)
players = analyzer.GetPlayers()
for team in players:
    for player in players[team]:
        print(
            player,
            analyzer.GetTimesToUltimate(player),
            analyzer.GetAverageTimeToUltimate(player),
            analyzer.GetTimesUltimateHeld(player),
            analyzer.GetAverageTimeUltimateHeld(player),
        )
parseEngine.write_csv(game, "../samples/TEST.csv")
analyzer.WriteAuxillaryCSVs("../samples/TEST")


# old
# parseEngine = MatrixParser()
# game = parseEngine.readLog("../samples/Log-2020-12-29-21-37-44.txt")
# analyzer = MatrixAnalyzer(game)
# print(game.kill_tracking)

# print(analyzer.GetUltTiming('Matrix'))
# analyzer.WriteAuxillaryCSVs("../samples/out/f3asdf2sz")
# print(analyzer.GetAllTotalDamages())
# print(analyzer.game.section_lengths)
# print({player: analyzer.GetHeroesPlayed(player) for player in analyzer.GetPlayers()})
# parseEngine.write_csv(game, "../samples/TEST.csv")

# owssparser.write_csv(parsed_data, "../samples/workshop_output1.csv")

# player_stats, player_stats_summary = owssanalyzer.analyze("../samples/workshop_output1.csv")
