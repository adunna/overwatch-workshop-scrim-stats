from mparser import MatrixParser
from manalyzer import MatrixAnalyzer

class MatrixJSON:
    
    def __init__(self, logfile):
        self.ParseEngine = MatrixParser()
        self.game = self.ParseEngine.readLog(logfile)
        self.Analyzer = MatrixAnalyzer(self.game)

    def DumpJSON(self):
        players = self.Analyzer.GetPlayers()
        return {"players": players}
