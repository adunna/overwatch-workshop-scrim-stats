from mparser import MatrixParser
from manalyzer import MatrixAnalyzer

parseEngine = MatrixParser()
game = parseEngine.readLog("../samples/map1.txt")
analyzer = MatrixAnalyzer(game)

#owssparser.write_csv(parsed_data, "../samples/workshop_output1.csv")

#player_stats, player_stats_summary = owssanalyzer.analyze("../samples/workshop_output1.csv")
