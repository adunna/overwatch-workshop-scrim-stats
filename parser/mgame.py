from mconsts import *

class MatrixGame:

    def __init__(self):
        self.language = LANG_EN
        self.map = ""
        self.map_type = ""
        self.map_score = [0, 0]
        self.map_tracking = [] # [[mapinfo, ...], ...]
        self.kill_tracking = [] # [[(timestamp, killer, victim), ...], ...]
        self.rez_tracking = [] # [[(timestamp, rezzed), ...], ...]
        self.dupe_tracking = [] # [{player: [[start_timestamp, end_timestamp, hero_duped], ...], ...}, ...]
        self.player_tracking = [] # [[team1, team2], ...]
        self.overall_deaths = [] # [{player: [ts, ...], ...}, ...]
        self.section_lengths = []  # [N, ...] one number for each section
        self.team_names = [] # [team 1, team 2]
        # team format = {playerName: player, ...}

class MatrixMapInfo:

    def __init__(self):
        self.point_number = 0 # TODO: use this for KOTH

        # KOTH
        self.team1Capture = 0
        self.team2Capture = 0

        # escort/hybrid/assault
        self.attacker = 0
        self.progress = 0

        # hybrid/assault
        self.pointCaptured = False

class MatrixPlayer:

    STAT_TYPES = {
        'number': set(['cooldown1', 'cooldown2', 'max_health']),
        'number_update':
        set([
            'hero_damage_dealt',
            'barrier_damage_dealt',
            'damage_blocked',
            'damage_taken',
            'deaths',
            'eliminations',
            'final_blows',
            'environmental_deaths',
            'environmental_kills',
            'healing_dealt',
            'objective_kills',
            'solo_kills',
            'ultimates_earned',
            'ultimates_used',
            'healing_received',
            'ultimate_charge',
            'hero_damage_dealt'
        ]),
        'string': set(['heroes', 'player_closest_reticle']),
        'vector': set(['position'])
    }

    def __init__(self):
        self.name = ""
        self.team = 0
        self.stats = {
            'heroes': [],
            'hero_damage_dealt': [],
            'barrier_damage_dealt': [],
            'damage_blocked': [],
            'damage_taken': [],
            'deaths': [],
            'eliminations': [],
            'final_blows': [],
            'environmental_deaths': [],
            'environmental_kills': [],
            'healing_dealt': [],
            'objective_kills': [],
            'solo_kills': [],
            'ultimates_earned': [],
            'ultimates_used': [],
            'healing_received': [],
            'ultimate_charge': [],
            'player_closest_reticle': [],
            'position': [],
            'cooldown1': [],
            'cooldown2': [],
            'max_health': [],
        }
        self.dc_stats = {x: None for x in self.stats}
