import parser
import analyzer

parsed_data = parser.parse("../samples/workshop_output1.txt")
parser.write_csv(parsed_data, "../samples/workshop_output1.csv")

player_stats, player_stats_summary = analyzer.analyze("../samples/workshop_output1.csv")
