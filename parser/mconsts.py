# random consts

HAS_ULT_CUTOFF = 90 # cutoff to determine if player has ultimate going into fight or not

# language remapping

LANG_EN = 0
LANG_KR = 1
KR_REMAP_MAPS = {
    '66번 국도': 'Route 66',
    '볼스카야 인더스트리': 'Volskaya Industries',
    '부산': 'Busan',
    '블리자드 월드': 'Blizzard World',
    '감시 기지: 지브롤터': 'Watchpoint: Gibraltar',
    '네팔': 'Nepal',
    '눔바니': 'Numbani',
    '파리': 'Paris',
    '쓰레기촌': 'Junkertown',
    '도라도': 'Dorado',
    '리알토': 'Rialto',
    '리장 타워': 'Lijiang Tower',
    '아누비스 신전': 'Temple of Anubis',
    '아이헨발데': 'Eichenwalde',
    '오아시스': 'Oasis',
    '왕의 길': "King's Row",
    '일리오스': 'Ilios',
    '하나무라': 'Hanamura',
    '하바나': 'Havana',
    '할리우드': 'Hollywood',
    '호라이즌 달 기지': 'Horizon Lunar Colony'
}
KR_REMAP_HEROES = {
    'D.Va': 'D.Va',
    '바스티온': 'Bastion',
    '바티스트': 'Baptiste',
    '브리기테': 'Brigitte',
    '토르비욘': 'Torbjorn',
    '트레이서': 'Tracer',
    '겐지': 'Genji',
    '솔저: 76': 'Soldier76',
    '솜브라': 'Sombra',
    '시그마': 'Sigma',
    '시메트라': 'Symmetra',
    '파라': 'Pharah',
    '한조': 'Hanzo',
    '둠피스트': 'Doomfist',
    '라인하르트': 'Reinhardt',
    '레킹볼': 'WreckingBall',
    '로드호그': 'Roadhog',
    '루시우': 'Lucio',
    '리퍼': 'Reaper',
    '아나': 'Ana',
    '애쉬': 'Ashe',
    '에코': 'Echo',
    '오리사': 'Orisa',
    '위도우메이커': 'Widowmaker',
    '윈스턴': 'Winston',
    '맥크리': 'McCree',
    '메르시': 'Mercy',
    '메이': 'Mei',
    '모이라': 'Moira',
    '자리야': 'Zarya',
    '정크랫': 'Junkrat',
    '젠야타': 'Zenyatta'
}

# stat data

STAT_TYPES = ['all_damage_dealt', 'barrier_damage_dealt', 'hero_damage_dealt', 'damage_blocked', 'damage_taken', 'eliminations', 'deaths', 'environmental_deaths', 'environmental_kills', 'final_blows', 'healing_dealt', 'healing_received', 'objective_kills', 'solo_kills', 'ultimate_charge', 'ultimates_earned', 'ultimates_used', 'cooldown1', 'cooldown2']

# map data

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

# hero data

HERO_REMAPS = {'LÃºcio': 'Lucio', 'Torbjörn': 'Torbjorn', 'Wrecking Ball': 'WreckingBall', 'Soldier: 76': 'Soldier76'}

# herotype & role data

ROLE_LIST = ['Main Tank', 'Off Tank', 'Hitscan DPS', 'Flex DPS', 'Main Support', 'Flex Support']
ROLE_LIST_SHORT = ['MT', 'OT', 'HSDPS', 'FDPS', 'MS', 'FS']
HEROTYPE_ROLE_MAPS = {
    'tank': ['main_tank', 'off_tank'],
    'dps': ['hitscan_dps', 'flex_dps'],
    'support': ['main_support', 'flex_support']
}
HEROTYPE_MAPS = {
    'tank': set(['D.Va', 'Orisa', 'Reinhardt', 'Roadhog', 'Sigma', 'Winston', 'WreckingBall', 'Zarya']),
    'dps': set(['Ashe', 'Bastion', 'Doomfist', 'Echo', 'Genji', 'Hanzo', 'Junkrat', 'McCree', 'Mei', 'Pharah', 'Reaper', 'Soldier76', 'Sombra', 'Symmetra', 'Torbjorn', 'Tracer', 'Widowmaker']),
    'support': set(['Ana', 'Baptiste', 'Brigitte', 'Lucio', 'Mercy', 'Moira', 'Zenyatta'])
}
ROLE_MAPS = {
    'main_tank': ['Reinhardt', 'Orisa', 'Winston', 'WreckingBall', 'Sigma', 'Roadhog', 'Zarya', 'D.Va'],
    'hitscan_dps': ['Widowmaker', 'McCree', 'Ashe', 'Tracer', 'Soldier76', 'Reaper', 'Sombra', 'Bastion', 'Hanzo', 'Symmetra', 'Mei', 'Echo', 'Torbjorn', 'Pharah', 'Doomfist', 'Genji', 'Junkrat'],
    'main_support': ['Lucio', 'Mercy', 'Brigitte', 'Baptiste', 'Moira', 'Ana', 'Zenyatta']
}
ROLE_MAPS['off_tank'] = ROLE_MAPS['main_tank'][::-1]
ROLE_MAPS['flex_dps'] = ROLE_MAPS['hitscan_dps'][::-1]
ROLE_MAPS['flex_support'] = ROLE_MAPS['main_support'][::-1]
