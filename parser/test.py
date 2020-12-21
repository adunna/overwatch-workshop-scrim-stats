from mparser import MatrixParser
from manalyzer import MatrixAnalyzer
from mjsonifier import MatrixJSON
import pprint

MJ = MatrixJSON("../samples/Hollywood.txt")
pprint.pprint(MJ.DumpJSON())

#parseEngine = MatrixParser()
#game = parseEngine.readLog("../samples/Hollywood.txt")
#analyzer = MatrixAnalyzer(game)

#owssparser.write_csv(parsed_data, "../samples/workshop_output1.csv")

#player_stats, player_stats_summary = owssanalyzer.analyze("../samples/workshop_output1.csv")
