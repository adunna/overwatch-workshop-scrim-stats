import owssparser
import owssanalyzer

parsed_data = owssparser.parse("../samples/workshop_output1.txt")
owssparser.write_csv(parsed_data, "../samples/workshop_output1.csv")

player_stats, player_stats_summary = owssanalyzer.analyze("../samples/workshop_output1.csv")
