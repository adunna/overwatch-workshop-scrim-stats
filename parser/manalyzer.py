from collections import defaultdict
from mgame import MatrixGame

class MatrixAnalyzer:

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
        'hitscan_dps': ['Ashe', 'Widowmaker', 'McCree', 'Soldier76', 'Reaper', 'Tracer', 'Sombra', 'Bastion', 'Hanzo', 'Symmetra', 'Echo', 'Mei', 'Torbjorn', 'Pharah', 'Doomfist', 'Genji', 'Junkrat'],
        'main_support': ['Lucio', 'Mercy', 'Brigitte', 'Zenyatta', 'Baptiste', 'Moira', 'Ana']
    }
    ROLE_MAPS['off_tank'] = ROLE_MAPS['main_tank'][::-1]
    ROLE_MAPS['flex_dps'] = ROLE_MAPS['hitscan_dps'][::-1]
    ROLE_MAPS['flex_support'] = ROLE_MAPS['main_support'][::-1]

    def __init__(self, game):
        self.game = game

    # Get names of all players, form of {team: [player, ...]}
    def GetPlayers(self):
        teams = {}
        for section in self.game.player_tracking:
            for team_num, team in enumerate(section):
                for player in team:
                    if team_num not in teams:
                        teams[team_num] = set()
                    teams[team_num].add(player)
        return {team: list(teams[team]) for team in teams}

    # Get team for given player
    def GetTeam(self, player):
        return 0 if player in self.game.player_tracking[0][0] else 1

    # Get heroes played for given player, with time on each, in form {hero: time, ...}
    def GetHeroesPlayed(self, player, team=None):
        if team is None:
            team = self.GetTeam(player)
        heroes_played = {}
        for section in range(0, len(self.game.player_tracking)):
            for timestamp in range(0, self.game.section_lengths[section]):
                if self.game.player_tracking[section][team][player].stats['heroes'][timestamp] not in heroes_played:
                    heroes_played[self.game.player_tracking[section][team][player].stats['heroes'][timestamp]] = 0
                heroes_played[self.game.player_tracking[section][team][player].stats['heroes'][timestamp]] += 1
        return heroes_played

    # Infer role groups for team from heroes played, format {player: role, ...}
    def GetInferRoleGroups(self, team):
        players = self.GetPlayers()[team]
        mostplayed = {} # player: hero
        for player in players:
            heroes_played = self.GetHeroesPlayed(player, team)
            mostplayed[player] = list(heroes_played.keys())[0]
            for hero in heroes_played:
                if heroes_played[hero] > heroes_played[mostplayed[player]]:
                    mostplayed[player] = hero
        player_roles = {}
        for player in mostplayed:
            for herotype in self.HEROTYPE_MAPS:
                if mostplayed[player] in self.HEROTYPE_MAPS[herotype]:
                    player_roles[player] = herotype
                    break
        return player_roles

    # Infer roles for team from heroes played, format {player: role, ...}
    def GetInferRoles(self, team):
        try:
            players = self.GetPlayers()[team]
            mostplayed = {} # player: hero
            for player in players:
                heroes_played = self.GetHeroesPlayed(player, team)
                mostplayed[player] = list(heroes_played.keys())[0]
                for hero in heroes_played:
                    if heroes_played[hero] > heroes_played[mostplayed[player]]:
                        mostplayed[player] = hero
            player_types = {x: [] for x in self.HEROTYPE_MAPS} # role: [player, player], ...
            for player in mostplayed:
                for herotype in self.HEROTYPE_MAPS:
                    if mostplayed[player] in self.HEROTYPE_MAPS[herotype]:
                        player_types[herotype].append(player)
                        break
            # now we can infer specific roles
            player_roles = {} # {player: role, ...}
            for herotype in player_types: # find main tank, main supp, and hitscan then assign other types
                firstoccs = [99, 99] # which player has lower number for role
                searching = self.HEROTYPE_ROLE_MAPS[herotype][0] # role we're searching
                for i in range(0, len(self.ROLE_MAPS[searching])):
                    if self.ROLE_MAPS[searching][i] == mostplayed[player_types[herotype][0]]:
                        firstoccs[0] = i
                    if self.ROLE_MAPS[searching][i] == mostplayed[player_types[herotype][1]]:
                        firstoccs[1] = i
                if firstoccs[0] < firstoccs[1]: # first player is this role
                    player_roles[player_types[herotype][0]] = searching
                    player_roles[player_types[herotype][1]] = self.HEROTYPE_ROLE_MAPS[herotype][1]
                else:
                    player_roles[player_types[herotype][1]] = searching
                    player_roles[player_types[herotype][0]] = self.HEROTYPE_ROLE_MAPS[herotype][1]
            return player_roles
        except: # not 2/2/2
            return self.GetInferRoleGroups(team)

    # Get death timestamps for given player for each section
    def GetDeaths(self, player, team=None):
        if team is None:
            team = self.GetTeam(player)
        death_times = []
        num_deaths = 0
        for section in range(0, len(self.game.player_tracking)):
            sec_death_times = []
            for timestamp in range(0, self.game.section_lengths[section]):
                if self.game.player_tracking[section][team][player].stats['deaths'][timestamp] > num_deaths:
                    num_deaths += 1
                    sec_death_times.append(timestamp)
            death_times.append(sec_death_times)
        return death_times

    # Get final stat for given player
    def GetFinalStat(self, player, stat, team=None):
        if team == None:
            team = self.GetTeam(player)
        if stat == 'all_damage_dealt':
            return self.game.player_tracking[-1][team][player].stats['hero_damage_dealt'][-1] + self.game.player_tracking[-1][team][player].stats['barrier_damage_dealt'][-1]
        else:
            return self.game.player_tracking[-1][team][player].stats[stat][-1]

    # Get stat per minute for given player
    def GetStatPerMinute(self, player, stat, team=None):
        if team == None:
            team = self.GetTeam(player)
        statSum = self.GetFinalStat(player, stat, team)
        statCount = sum(self.game.section_lengths)
        return (statSum / statCount) * 60

    # Get times ultimates used for given player, for each section
    def GetTimesUltimateUsed(self, player, team=None):
        if team is None:
            team = self.GetTeam(player)
        times_ult_used = []
        for section_num, section in enumerate(self.game.player_tracking):
            times_ult_used_section = []
            for i in range(1, self.game.section_lengths[section_num]):
                if section[team][player].stats['ultimates_used'][i] != section[team][player].stats['ultimates_used'][i-1]:
                    times_ult_used_section.append(i)
            times_ult_used.append(times_ult_used_section)
        return times_ult_used

    # Get time to ultimate (in seconds) for each ultimate for given player
    def GetTimesToUltimate(self, player, team=None):
        if team == None:
            team = self.GetTeam(player)
        times_to_ult = []
        prev_ults_earned = 0
        for section_num, section in enumerate(self.game.player_tracking):
            time_to_ult = 0
            for i in range(0, self.game.section_lengths[section_num]):
                if section[team][player].stats['ultimates_earned'][i] != prev_ults_earned:
                    times_to_ult.append(time_to_ult)
                    time_to_ult = 0
                else:
                    if section[team][player].stats['ultimates_earned'][i] == section[team][player].stats['ultimates_used'][i]:
                        time_to_ult += 1
                prev_ults_earned = section[team][player].stats['ultimates_earned'][i]
        return times_to_ult

    # Get time ultimate held (in seconds) for each ultimate for given player
    def GetTimesUltimateHeld(self, player, team=None):
        if team == None:
            team = self.GetTeam(player)
        times_ult_held = []
        for section_num, section in enumerate(self.game.player_tracking):
            time_ult_held = 0
            for i in range(0, self.game.section_lengths[section_num]):
                if section[team][player].stats['ultimates_earned'][i] != section[team][player].stats['ultimates_used'][i]:
                    time_ult_held += 1
                else:
                    if time_ult_held > 0:
                        times_ult_held.append(time_ult_held)
                        time_ult_held = 0
        if time_ult_held > 0:
            times_ult_held.append(time_ult_held)
        return times_ult_held

    # Get average time to ultimate (in seconds) for given player
    def GetAverageTimeToUltimate(self, player, team=None):
        times_to_ult = self.GetTimesToUltimate(player, team)
        if len(times_to_ult) > 0:
            return sum(times_to_ult) / len(times_to_ult)
        return 0

    # Get average time ultimate held (in seconds) for given player
    def GetAverageTimeUltimateHeld(self, player, team=None):
        times_ult_held = self.GetTimesUltimateHeld(player, team)
        if len(times_ult_held) > 0:
            return sum(times_ult_held) / len(times_ult_held)
        return 0

    # Segment game data into fights by sections [[(start, end), ...], ...]
    def GetFights(self):
        fights = []
        for section in range(0, len(self.game.player_tracking)):
            fight_starts = []
            fight_ends = []
            in_fight = 0
            for i in range(0, self.game.section_lengths[section]):
                damage = self.GetTotalDamage(section, i)
                if damage >= 250 and in_fight == 0:
                    in_fight = 1
                    fight_starts.append(i)
                elif damage >= 250 and in_fight > 1:
                    in_fight = 1
                elif damage < 250 and in_fight >= 1 and in_fight < 6:
                    in_fight += 1
                elif damage < 250 and in_fight >= 6:
                    in_fight = 0
                    fight_ends.append(i)
                if in_fight >= 1 and i == self.game.section_lengths[section] - 1:
                    in_fight = 0
                    fight_ends.append(i)
            fights.append([(fight_starts[x], fight_ends[x]) for x in range(0, len(fight_starts))])
        ret_fights = []
        for section_num, section in enumerate(fights):
            if len(section) > 0:
                filtered_fights = [section[0]]
                for i in range(1, len(section)):
                    if section[i][0] - 6 <= filtered_fights[-1][1]:
                        filtered_fights[-1] = (filtered_fights[-1][0], section[i][1])
                    else:
                        filtered_fights.append(section[i])
            else:
                filtered_fights = [(0, 0), (self.game.section_lengths[section_num], self.game.section_lengths[section_num])]
            ret_fights.append(filtered_fights)
        return ret_fights

    # Get first ult used in each fight, if any, in format [[(fight start, fight end, player, hero), ...], ...]
    def GetFirstUltUsedInFights(self):
        fights = self.GetFights()
        firstUlts = []
        for section in range(0, len(fights)):
            curr = 0
            sectionFirstUlts = []
            for ts in range(1, self.game.section_lengths[section]):
                if curr >= len(fights[section]):
                    break
                if ts > fights[section][curr][1]:
                    curr += 1
                if ts >= fights[section][curr][0] and ts <= fights[section][curr][1]:
                    for team in range(0, 2):
                        for player in self.game.player_tracking[section][team]:
                            if self.game.player_tracking[section][team][player].stats['ultimates_used'][ts] != self.game.player_tracking[section][team][player].stats['ultimates_used'][ts-1]:
                                sectionFirstUlts.append((fights[section][curr][0], fights[section][curr][1], player, self.game.player_tracking[section][team][player].stats['heroes'][ts]))
                                curr += 1
                                break
            firstUlts.append(sectionFirstUlts)
        return firstUlts

    # Get first death in each fight, if any, in format [[(fight start, fight end, player, hero), ...], ...]
    def GetFirstDeathInFights(self):
        fights = self.GetFights()
        firstDeaths = []
        for section in range(0, len(fights)):
            curr = 0
            sectionFirstDeaths = []
            for ts in range(1, self.game.section_lengths[section]):
                if curr >= len(fights[section]):
                    break
                if ts > fights[section][curr][1]:
                    curr += 1
                if ts >= fights[section][curr][0] and ts <= fights[section][curr][1]:
                    for team in range(0, 2):
                        for player in self.game.player_tracking[section][team]:
                            if self.game.player_tracking[section][team][player].stats['deaths'][ts] != self.game.player_tracking[section][team][player].stats['deaths'][ts-1]:
                                sectionFirstDeaths.append((fights[section][curr][0], fights[section][curr][1], player, self.game.player_tracking[section][team][player].stats['heroes'][ts]))
                                curr += 1
                                break
            firstDeaths.append(sectionFirstDeaths)
        return firstDeaths

    # Get stagger/feed deaths format (num_deaths, [[ts, ...], ...]) for a given player name
    def GetFeedDeaths(self, player, team=None):
        if team is None:
            team = self.GetTeam(player)
        fights = self.GetFights()
        death_times = self.GetDeaths(player, team)
        feed_deaths = []
        numFeedDeaths = 0
        for section in range(0, len(fights)):
            sec_feed_deaths = []
            for dtime in death_times[section]:
                foundDeath = False
                f = 0
                while not foundDeath and f < len(fights[section]):
                    if dtime >= fights[section][f][0] and dtime <= fights[section][f][1]:
                        foundDeath = True
                    f += 1
                if not foundDeath:
                    sec_feed_deaths.append(dtime)
                    numFeedDeaths += 1
            feed_deaths.append(sec_feed_deaths)
        return numFeedDeaths, feed_deaths

    # Get all poke damage taken for given player name
    def GetPokeDamage(self, player, team=None):
        if team is None:
            team = self.GetTeam(player)
        fights = self.GetFights()
        poke_dmg = 0
        prev_dmg_taken = 0
        for section in range(0, len(fights)):
            fight_ptr = 0
            for timestamp in range(0, self.game.section_lengths[section]):
                prev_dmg_taken = self.game.player_tracking[section][team][player].stats['damage_taken'][timestamp] if timestamp == 0 else self.game.player_tracking[section][team][player].stats['damage_taken'][timestamp - 1]
                if timestamp < fights[section][fight_ptr][0]:
                    poke_dmg += self.game.player_tracking[section][team][player].stats['damage_taken'][timestamp] - prev_dmg_taken
                elif timestamp >= fights[section][fight_ptr][1]:
                    fight_ptr += 1
        return poke_dmg

    # Get stagger/feed deaths for all players, form [{player: num, ...}, ...] for team 0 and 1
    def GetAllFeedDeaths(self):
        players = self.GetPlayers()
        feed_deaths = []
        for team in players:
            feed_deaths.append({})
            for player in players[team]:
                feed_deaths[team][player] = self.GetFeedDeaths(player, team)
        return feed_deaths

    # Get total damage at given section and timestamp; if team not specified, is over all teams
    def GetTotalDamage(self, section, timestamp, team=None):
        if timestamp == 0:
            if section == 0:
                damages = [sum([cteam[player].stats['hero_damage_dealt'][timestamp] + cteam[player].stats['barrier_damage_dealt'][timestamp] for player in cteam]) for cteam in self.game.player_tracking[section]]
                if team is not None:
                    damages = [damages[team]]
            else:
                return self.GetTotalDamage(section - 1, -1)
        else:
            damages = [sum([cteam[player].stats['hero_damage_dealt'][timestamp] - cteam[player].stats['hero_damage_dealt'][timestamp - 1] + cteam[player].stats['barrier_damage_dealt'][timestamp] - cteam[player].stats['barrier_damage_dealt'][timestamp - 1] for player in cteam if timestamp < len(cteam[player].stats['hero_damage_dealt'])]) for cteam in self.game.player_tracking[section]]
            if team is not None:
                damages = [damages[team]]
        return sum(damages)

    # Get total damages over all time; if team not specified, is over all teams
    def GetAllTotalDamages(self, team=None):
        damages = []
        for section in range(0, len(self.game.player_tracking)):
            for timestamp in range(0, self.game.section_lengths[section]):
                damages.append(self.GetTotalDamage(section, timestamp, team=team))
        return damages

    # Get hero damage dealt for given player
    def GetHeroDamageDealt(self, player, team=None):
        return self.GetFinalStat(player, 'hero_damage_dealt', team)

    # Get barrier damage dealt for given player
    def GetBarrierDamageDealt(self, player, team=None):
        return self.GetFinalStat(player, 'barrier_damage_dealt', team)

    # Get (avg distance, cumulative distance) in meters for given players at given timestamp in given section
    def GetGroupedness(self, players, section, timestamp, team=None):
        if team == None:
            team = self.GetTeam(players[0])
        positions = [self.game.player_tracking[section][team][player].stats['position'][timestamp] for player in players]
        x_pos = [position[0] for position in positions]
        y_pos = [position[1] for position in positions]
        z_pos = [position[2] for position in positions]
        center = (sum(x_pos)/len(x_pos), sum(y_pos)/len(y_pos), sum(z_pos)/len(z_pos))
        cumulative_dist_x = [abs(center[0] - x) for x in x_pos]
        cumulative_dist_y = [abs(center[1] - y) for y in y_pos]
        cumulative_dist_z = [abs(center[2] - z) for z in z_pos]
        cumulative_dist = sum(cumulative_dist_x) + sum(cumulative_dist_y) + sum(cumulative_dist_z)
        avg_dist = cumulative_dist / len(players)
        return (avg_dist, cumulative_dist)

    # Get average of (avg distance, cumulative distance) in meters for given players over all time
    def GetOverallGroupedness(self, players, team=None):
        if team == None:
            team = self.GetTeam(players[0])
        avg_dists = []
        cumulative_dists = []
        for section in range(0, len(self.game.player_tracking)):
            for timestamp in range(0, self.game.section_lengths[section]):
                avg_dist, cumulative_dist = self.GetGroupedness(players, section, timestamp, team)
                avg_dists.append(avg_dist)
                cumulative_dists.append(cumulative_dist)
        return (sum(avg_dists)/len(avg_dists), sum(cumulative_dists)/len(cumulative_dists))
