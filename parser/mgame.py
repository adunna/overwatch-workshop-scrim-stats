from mconsts import *

class MatrixGame:
    """Track a single scrimmage game instance, including map and player info.

    A given section S refers to a KOTH map point, or an attack/defense side in
    another map type. Each section will have a number of items contained in it,
    done at each timestamp t. For example, map_tracking[0][46] would refer to
    the point progress at 47 seconds into the first KOTH point, or the first
    attack side of another map type.

    Attributes: language: Overwatch client language constant, default LANG_EN.
        map: string - Overwatch map name map_type: string - Overwatch map type (Hybrid, Control, Escort, Assault)
        map_score: [int, int] - Final map score for [Team 1, Team 2]
        player_order: [[MatrixPlayer, ...], [MatrixPlayer, ...]] - Player order to use in analyses and visualizations; can optionally be inferred
        map_tracking: [[MatrixMapInfo, ...], [MatrixMapInfo, ...], ...] - Map information at each timestamp T within each section S
    """

    def __init__(self):
        self.version = Version.PREV
        self.language = LANG_EN # TODO: make things into their own classes (ex. Map, Language, etc.)
        self.map = ""
        self.map_type = ""
        self.map_score = [0, 0]
        self.player_order = [] # [[player, player, ...], [player, player, ...]]
        self.map_tracking = [[]] # [[mapinfo, ...], ...]
        self.kill_tracking = [[]] # [[(timestamp, killer, victim), ...], ...]
        self.rez_tracking = [[]] # [[(timestamp, rezzed), ...], ...]
        self.dupe_tracking = [{}] # [{player: [[start_timestamp, end_timestamp, hero_duped], ...], ...}, ...]
        self.player_tracking = [[{}, {}]] # [[team1, team2], ...]
        self.overall_deaths = [{}] # [{player: [ts, ...], ...}, ...]
        self.section_lengths = [999999]  # [N, ...] one number for each section
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
        'number':
        set([
            'cooldown1',
            'cooldown2',
            'max_health',
            'charge_ability1',
            'charge_ability2',
            'resource_primary',
            'resource_secondary',
            'resource_ability1',
            'resource_ability2'
        ]),
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
            'offensive_assists',
            'defensive_assists',
            'weapon_accuracy'
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
            'offensive_assists': [],
            'defensive_assists': [],
            'charge_ability1': [],
            'charge_ability2': [],
            'resource_primary': [],
            'resource_secondary': [],
            'resource_ability1': [],
            'resource_ability2': [],
            'weapon_accuracy': []
        }
        self.dc_stats = {x: None for x in self.stats}
