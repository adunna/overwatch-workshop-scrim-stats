class MatrixGame:

    MAP_TYPES = {
            "Blizzard World": "Hybrid",
            "Busan": "Control",
            "Dorado": "Escort",
            "Eichenwalde": "Hybrid",
            "Hanamura": "Assault",
            "Havana": "Escort",
            "Hollywood": "Hybrid",
            "Horizon Lunar Colony": "Assault",
            "Ilios": "Control",
            "Junkertown": "Escort",
            "King's Row": "Hybrid",
            "Lijiang Tower": "Control",
            "Nepal": "Control",
            "Numbani": "Hybrid",
            "Oasis": "Control",
            "Paris": "Assault",
            "Rialto": "Escort",
            "Route 66": "Escort",
            "Temple of Anubis": "Assault",
            "Volskaya Industries": "Assault",
            "Watchpoint: Gibraltar": "Escort"
    }

    def __init__(self):
        self.map = ""
        self.map_type = ""
        self.map_tracking = [] # [mapinfo, ...]
        self.kill_tracking = [] # [[(timestamp, killer, victim), ...], ...]
        self.player_tracking = [] # [[team1, team2], ...]
        self.section_lengths = []  # [N, ...] one number for each section
        # team format = {playerName: player, ...}

class MatrixMapInfo:

    def __init__(self):
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
