from collections import defaultdict
from mgame import MatrixGame
from mconsts import *

class MatrixAnalyzer:

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
                if player in self.game.player_tracking[section][team]:
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
            for herotype in HEROTYPE_MAPS:
                if mostplayed[player] in HEROTYPE_MAPS[herotype]:
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
            player_types = {x: [] for x in HEROTYPE_MAPS} # role: [player, player], ...
            for player in mostplayed:
                for herotype in HEROTYPE_MAPS:
                    if mostplayed[player] in HEROTYPE_MAPS[herotype]:
                        player_types[herotype].append(player)
                        break
            # now we can infer specific roles
            player_roles = {} # {player: role, ...}
            for herotype in player_types: # find main tank, main supp, and hitscan then assign other types
                firstoccs = [99, 99] # which player has lower number for role
                searching = HEROTYPE_ROLE_MAPS[herotype][0] # role we're searching
                for i in range(0, len(ROLE_MAPS[searching])):
                    if ROLE_MAPS[searching][i] == mostplayed[player_types[herotype][0]]:
                        firstoccs[0] = i
                    if ROLE_MAPS[searching][i] == mostplayed[player_types[herotype][1]]:
                        firstoccs[1] = i
                if firstoccs[0] < firstoccs[1]: # first player is this role
                    player_roles[player_types[herotype][0]] = searching
                    player_roles[player_types[herotype][1]] = HEROTYPE_ROLE_MAPS[herotype][1]
                else:
                    player_roles[player_types[herotype][1]] = searching
                    player_roles[player_types[herotype][0]] = HEROTYPE_ROLE_MAPS[herotype][1]
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
        try:
            if team == None:
                team = self.GetTeam(player)
            if stat == 'all_damage_dealt':
                return self.game.player_tracking[-1][team][player].stats['hero_damage_dealt'][-1] + self.game.player_tracking[-1][team][player].stats['barrier_damage_dealt'][-1]
            elif stat == 'ultimates_earned':
                return self.GetNumberUltsEarnedUsed(player, team)[0]
            elif stat == 'ultimates_used':
                return self.GetNumberUltsEarnedUsed(player, team)[1]
            else:
                return self.game.player_tracking[-1][team][player].stats[stat][-1]
        except:
            return 0

    # Get stat per minute for given player
    def GetStatPerMinute(self, player, stat, team=None):
        if team == None:
            team = self.GetTeam(player)
        statSum = self.GetFinalStat(player, stat, team)
        statCount = sum(self.game.section_lengths)
        return (statSum / statCount) * 60

    # Get number of ults earned and used by given player on given team
    def GetNumberUltsEarnedUsed(self, player, team=None): # returns (num earned, num used)
        if team is None:
            team = self.GetTeam(player)
        ult_times = self.GetUltTiming(player, team)
        num_earned = 0
        num_used = 0
        for section in ult_times:
            for ult_pair in section:
                num_earned += 1
                if ult_pair[1] >= 0:
                    num_used += 1
        return (num_earned, num_used)

    # Get time ultimate available at, and time ultimate used, for given player for each section
    ## Excludes Echo duplicate ultimates
    def GetUltTiming(self, player, team=None):
        if team is None:
            team = self.GetTeam(player)
        ult_times = [] # [[(tsgotten, tsused), ...], ...] if tsused is -timestamp then ult wasn't used and person swapped at timestamp or map ended
        for section_num, section in enumerate(self.game.player_tracking):
            earned_ults = []
            used_ults = []
            has_ult = False
            for i in range(1, self.game.section_lengths[section_num]):
                should_do = True
                if player in self.game.dupe_tracking[section_num]:
                    for dupe in self.game.dupe_tracking[section_num][player]:
                        if i >= dupe[0] + 1 and i <= dupe[1]:
                            should_do = False

                if should_do:
                    if not has_ult and section[team][player].stats['ultimates_earned'][i] != section[team][player].stats['ultimates_earned'][i-1]: # got ultimate
                        if section[team][player].stats['heroes'][i] != 'D.Va' or (section[team][player].stats['max_health'][i] >= 250 and section[team][player].stats['max_health'][i-1] >= 250): # baby D.Va
                            earned_ults.append(i)
                            has_ult = True
                    if has_ult and (section[team][player].stats['ultimates_used'][i] != section[team][player].stats['ultimates_used'][i-1] or (section[team][player].stats['ultimate_charge'][i] < section[team][player].stats['ultimate_charge'][i-1] and section[team][player].stats['heroes'][i] != 'D.Va')): # either swapped or used ult, or got demeched
                        if section[team][player].stats['heroes'][i] != 'D.Va' or section[team][player].stats['max_health'][i-1] >= 250:
                            if section[team][player].stats['heroes'][i] != section[team][player].stats['heroes'][i-1]: # swapped
                                if has_ult == True: # had ult and swapped, so did not use
                                    used_ults.append(-i)
                            else: # same hero
                                used_ults.append(i)

                            has_ult = False

            if has_ult:
                used_ults.append(-1)
            ult_times_sec = []
            for i in range(0, len(earned_ults)):
                ult_times_sec.append((earned_ults[i], used_ults[i]))
            ult_times.append(ult_times_sec)
        return ult_times

    # Get times ultimates used for given player, for each section
    ## Excludes Echo duplicate ultimates
    def GetTimesUltimateUsed(self, player, team=None):
        if team is None:
            team = self.GetTeam(player)
        times_ult_used = []
        for section_num, section in enumerate(self.game.player_tracking):
            times_ult_used_section = []
            for i in range(1, self.game.section_lengths[section_num]):
                should_do = True
                if player in self.game.dupe_tracking[section_num]:
                    for dupe in self.game.dupe_tracking[section_num][player]:
                        if i >= dupe[0] + 1 and i <= dupe[1]:
                            should_do = False
                if should_do:
                    if section[team][player].stats['ultimate_charge'][i] < section[team][player].stats['ultimate_charge'][i-1]:
                        if section[team][player].stats['heroes'][i] == section[team][player].stats['heroes'][i-1]:
                            times_ult_used_section.append(i)
            times_ult_used.append(times_ult_used_section)
        return times_ult_used

    # Get time to ultimate (in seconds) for each ultimate for given player
    ## Excludes Echo duplicate ultimates
    def GetTimesToUltimate(self, player, team=None):
        if team == None:
            team = self.GetTeam(player)
        ult_timing = self.GetUltTiming(player, team)
        times_to_ult = []
        for section in ult_timing:
            if len(section) > 0:
                times_to_ult.append(section[0][0])
                for i in range(1, len(section)):
                    times_to_ult.append(section[i][0] - abs(section[i-1][1]))
        return times_to_ult

    # Get time ultimate held (in seconds) for each ultimate for given player
    ## Excludes Echo duplicate ultimates
    def GetTimesUltimateHeld(self, player, team=None):
        if team == None:
            team = self.GetTeam(player)
        ult_timing = self.GetUltTiming(player, team)
        times_ult_held = []
        for section in ult_timing:
            for i in range(0, len(section)):
                if section[i][1] >= 0:
                    times_ult_held.append(section[i][1] - section[i][0])
        return times_ult_held

    # Get average time to ultimate (in seconds) for given player
    ## Excludes Echo duplicate ultimates
    def GetAverageTimeToUltimate(self, player, team=None):
        times_to_ult = self.GetTimesToUltimate(player, team)
        if len(times_to_ult) > 0:
            return sum(times_to_ult) / len(times_to_ult)
        return 0

    # Get average time ultimate held (in seconds) for given player
    ## Excludes Echo duplicate ultimates
    def GetAverageTimeUltimateHeld(self, player, team=None):
        times_ult_held = self.GetTimesUltimateHeld(player, team)
        if len(times_ult_held) > 0:
            return sum(times_ult_held) / len(times_ult_held)
        return 0

    # Get ultimates available at given timestamp for each team, in format ([player, player, ...], [player, player, ...], [hero, hero, ...], [hero, hero, ...])
    def GetUltimatesAvailable(self, section, timestamp):
        team1players = []
        team2players = []
        team1heroes = []
        team2heroes = []
        for team in range(0, 2):
            for player in self.game.player_tracking[section][team]:
                if self.game.player_tracking[section][team][player].stats['ultimate_charge'][timestamp] >= HAS_ULT_CUTOFF:
                    if team == 0:
                        team1players.append(player)
                        team1heroes.append(self.game.player_tracking[section][team][player].stats['heroes'][timestamp])
                    else:
                        team2players.append(player)
                        team2heroes.append(self.game.player_tracking[section][team][player].stats['heroes'][timestamp])
        return (team1players, team2players, team1heroes, team2heroes)

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

    # Get first ult used between given timestamps (inclusive), in format (player, hero)
    def GetFirstUltUsed(self, section, start, end):
        for ts in range(start, end + 1):
            for team in range(0, 2):
                for player in self.game.player_tracking[section][team]:
                    if self.game.player_tracking[section][team][player].stats['ultimates_used'][ts] != self.game.player_tracking[section][team][player].stats['ultimates_used'][ts-1]:
                        return (player, self.game.player_tracking[section][team][player].stats['heroes'][ts])
        return ('', '')

    # Get first death between given timestamps (inclusive), in format (player, hero)
    def GetFirstDeath(self, section, start, end):
        for ts in range(start, end + 1):
            for team in range(0, 2):
                for player in self.game.player_tracking[section][team]:
                    if self.game.player_tracking[section][team][player].stats['deaths'][ts] != self.game.player_tracking[section][team][player].stats['deaths'][ts-1]:
                        return (player, self.game.player_tracking[section][team][player].stats['heroes'][ts])
        return ('', '')

    # Get first final blow between given timestamps (inclusive), in format (player, hero)
    def GetFirstFinalBlow(self, section, start, end):
        for ts in range(start, end + 1):
            for team in range(0, 2):
                for player in self.game.player_tracking[section][team]:
                    if self.game.player_tracking[section][team][player].stats['final_blows'][ts] != self.game.player_tracking[section][team][player].stats['final_blows'][ts-1]:
                        return (player, self.game.player_tracking[section][team][player].stats['heroes'][ts])
        return ('', '')

    # Get ults used between given timestamps (inclusive) for each team, in format ([player, player, ...], [player, player, ...], [hero, hero, ...], [hero, hero, ...])
    def GetTeamUltsUsed(self, section, start, end):
        team1count = []
        team2count = []
        team1ults = []
        team2ults = []
        for ts in range(start, end + 1):
            for team in range(0, 2):
                for player in self.game.player_tracking[section][team]:
                    if self.game.player_tracking[section][team][player].stats['ultimates_used'][ts] != self.game.player_tracking[section][team][player].stats['ultimates_used'][ts-1]:
                        if team == 0:
                            team1count.append(player)
                            team1ults.append(self.game.player_tracking[section][team][player].stats['heroes'][ts])
                        else:
                            team2count.append(player)
                            team2ults.append(self.game.player_tracking[section][team][player].stats['heroes'][ts])
        return (team1count, team2count, team1ults, team2ults)

    # Get deaths between given timestamps (inclusive) for each team, in format ([player, player, ...], [player, player, ...], [hero, hero, ...], [hero, hero, ...])
    def GetTeamDeaths(self, section, start, end):
        team1count = []
        team2count = []
        team1deaths = []
        team2deaths = []
        for ts in range(start, end + 1):
            for team in range(0, 2):
                for player in self.game.player_tracking[section][team]:
                    if self.game.player_tracking[section][team][player].stats['deaths'][ts] != self.game.player_tracking[section][team][player].stats['deaths'][ts-1]:
                        if team == 0:
                            team1count.append(player)
                            team1deaths.append(self.game.player_tracking[section][team][player].stats['heroes'][ts])
                        else:
                            team2count.append(player)
                            team2deaths.append(self.game.player_tracking[section][team][player].stats['heroes'][ts])
        return (team1count, team2count, team1deaths, team2deaths)

    # Get final blows between given timestamps (inclusive) for each team, in format ([player, player, ...], [player, player, ...], [hero, hero, ...], [hero, hero, ...])
    def GetTeamFinalBlows(self, section, start, end):
        team1count = []
        team2count = []
        team1fbs = []
        team2fbs = []
        for ts in range(start, end + 1):
            for team in range(0, 2):
                for player in self.game.player_tracking[section][team]:
                    for c in range(0, self.game.player_tracking[section][team][player].stats['final_blows'][ts] - self.game.player_tracking[section][team][player].stats['final_blows'][ts-1]):
                        if team == 0:
                            team1count.append(player)
                            team1fbs.append(self.game.player_tracking[section][team][player].stats['heroes'][ts])
                        else:
                            team2count.append(player)
                            team2fbs.append(self.game.player_tracking[section][team][player].stats['heroes'][ts])
        return (team1count, team2count, team1fbs, team2fbs)

    # Get first ult used in each fight, if any, in format [[(fight start, fight end, player, hero), ...], ...]
    def GetFirstUltUsedInFights(self, fights=None):
        if fights is None:
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
    def GetFirstDeathInFights(self, fights=None):
        if fights is None:
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

    # Get ordered players based on role inferencing
    def GetPlayerOrder(self, inferred_roles, players):
        players_ordered = []
        desired_order = ['main_tank', 'off_tank', 'hitscan_dps', 'flex_dps', 'main_support', 'flex_support']
        desired_order_backup = ['tank', 'tank', 'dps', 'dps', 'support', 'support']
        for team in players:
            placed = 0
            prev_placed = placed
            ordering = desired_order
            if inferred_roles[team][players[team][0]] not in desired_order:
                ordering = desired_order_backup
            team_ordered = []
            while len(players[team]) > placed:
                prev_placed = placed
                for player in players[team]:
                    if inferred_roles[team][player] == ordering[placed]:
                        team_ordered.append(player)
                        placed += 1
                        if placed == len(players[team]):
                            break
                if prev_placed == placed: # encountered some error
                    placed = len(players[team])
                    team_ordered = players[team]
                    break
            players_ordered.append(team_ordered)
        return players_ordered

    # Get number of FBs for given player in given section, between given timestamps (inclusive)
    def GetNumFBsBtwn(self, player, section, start, end, team=None): # returns integer
        if team is None:
            team = self.GetTeam(player)
        fbcount = 0
        for ts in range(start, end + 1):
            for c in range(0, self.game.player_tracking[section][team][player].stats['final_blows'][ts] - self.game.player_tracking[section][team][player].stats['final_blows'][ts-1]):
                fbcount += 1
        return fbcount

    # Get number of eliminations for given player in given section, between given timestamps (inclusive)
    def GetNumElimsBtwn(self, player, section, start, end, team=None): # returns integer
        if team is None:
            team = self.GetTeam(player)
        elimcount = 0
        for ts in range(start, end + 1):
            for c in range(0, self.game.player_tracking[section][team][player].stats['eliminations'][ts] - self.game.player_tracking[section][team][player].stats['eliminations'][ts-1]):
                elimcount += 1
        return elimcount

    # Check if player used ultimate for given player in given section, between given timestamps (inclusive)
    def GetPlayerUsedUlt(self, player, section, start, end, team=None): # returns boolean
        if team is None:
            team = self.GetTeam(player)
        for ts in range(start, end + 1):
            if self.game.player_tracking[section][team][player].stats['ultimates_used'][ts] != self.game.player_tracking[section][team][player].stats['ultimates_used'][ts-1]:
                return True
        return False

    # Get first death of player in given section, between given timestamps (inclusive)
    def GetFirstDeathBtwn(self, player, section, start, end, team=None): # returns None if no death, (ts, killer) if died
        if team is None:
            team = self.GetTeam(player)
        for kill_event in self.game.kill_tracking[section]: # (timestamp, killer, victim)
            if kill_event[2] == player and kill_event[0] >= start and kill_event[0] <= end:
                return (kill_event[0], kill_event[1])
        return None

    # Get fight winner between given timestamps in given section (inclusive)
    def GetFightWinner(self, section, start, end): # returns 0, 1, or -1 if unknown
        fbs = self.GetTeamFinalBlows(section, start, end)
        fight_winner = -1
        if len(fbs[0]) > len(fbs[1]):
            fight_winner = 0
        elif len(fbs[1]) > len(fbs[0]):
            fight_winner = 1
        if fight_winner == -1: # if tie, team with point capture has won fight
            if self.game.map_type == 'Control':
                if self.game.map_tracking[section][end].team1Capture > self.game.map_tracking[section][end].team2Capture:
                    fight_winner = 0
                elif self.game.map_tracking[section][end].team1Capture < self.game.map_tracking[section][end].team2Capture:
                    fight_winner = 1
                else:
                    fight_winner = -1
            else:
                if self.game.map_tracking[section][end].progress > self.game.map_tracking[section][end-1].progress:
                    fight_winner = self.game.map_tracking[section][end].attacker
                else:
                    fight_winner = 1 - self.game.map_tracking[section][end].attacker
        return fight_winner

    # Write auxillary CSVs
    def WriteAuxillaryCSVs(self, out_base_filename):
        # get data
        fights = self.GetFights()
        fight_csv_types = ['fights', 'fights_roleorder']
        for fight_csv_type in fight_csv_types:
            with open(out_base_filename + '_' + fight_csv_type + '.csv', 'w', encoding='utf-8') as o:
                mapTypeSection = 'Section' if self.game.map_type == 'Control' else 'Attacker'
                o.write(
                    'Map,' + mapTypeSection + ',Fight,Start Timestamp,End Timestamp,Winner,First FB,First FB Hero,First Death,First Death Hero,First Ult Used,First Ult Used Hero'
                )
                colCount = 12
                for teamnum in self.game.team_names:
                    for role_num, role in enumerate(ROLE_LIST):
                        o.write(',' + teamnum + ' ' + role)
                        colCount += 1
                    for role_num, role in enumerate(ROLE_LIST):
                        o.write(',' + teamnum + ' ' + ROLE_LIST_SHORT[role_num] + ' Hero')
                        colCount += 1
                for teamnum in self.game.team_names:
                    for role_num, role in enumerate(ROLE_LIST):
                        for data_name in [' FBs', ' Elims', ' Had Ult', ' Used Ult', ' Died To', ' Timestamp Died']:
                            o.write(',' + teamnum + ' ' + ROLE_LIST_SHORT[role_num] + data_name)
                            colCount += 1
                o.write('\n')

                players = self.GetPlayers()
                inferred_roles = [self.GetInferRoles(team) for team in players]
                if fight_csv_type == 'fights' or self.game.player_order == []:
                    players_ordered = self.GetPlayerOrder(inferred_roles, players)
                elif fight_csv_type == 'fights_roleorder':
                    players_ordered = self.game.player_order

                fightNum = 0
                for section_num, section in enumerate(fights):
                    for fight in section:
                        section_info = section_num if self.game.map_type == 'Control' else self.game.team_names[self.game.map_tracking[section_num][fight[0]].attacker]
                        map_info = [self.game.map, section_info, fightNum, fight[0], fight[1]]

                        fight_winner_num = self.GetFightWinner(section_num, fight[0], fight[1])
                        if fight_winner_num == -1:
                            fight_winner = 'Unknown'
                        else:
                            fight_winner = self.game.team_names[fight_winner_num]

                        first_fb = self.GetFirstFinalBlow(section_num, fight[0], fight[1])
                        first_death = self.GetFirstDeath(section_num, fight[0], fight[1])
                        first_ult_used = self.GetFirstUltUsed(section_num, fight[0], fight[1])
                        fight_info = [fight_winner, first_fb[0], first_fb[1], first_death[0], first_death[1], first_ult_used[0], first_ult_used[1]]

                        player_info = []
                        player_fight_info = []
                        for team_num in [0, 1]:
                            for player_num, player in enumerate(players_ordered[team_num]):
                                player_info.append(player)

                                player_death = self.GetFirstDeathBtwn(player, section_num, fight[0], fight[1], team_num)

                                player_fight_info += [
                                    self.GetNumFBsBtwn(player, section_num, fight[0], fight[1], team_num),
                                    self.GetNumElimsBtwn(player, section_num, fight[0], fight[1], team_num),
                                    1 if self.game.player_tracking[section_num][team_num][player].stats['ultimate_charge'][fight[0]] >= HAS_ULT_CUTOFF else 0,
                                    int(self.GetPlayerUsedUlt(player, section_num, fight[0], fight[1], team_num)),
                                    player_death[1] if player_death is not None else '',
                                    player_death[0] if player_death is not None else ''
                                ]

                            for player_num, player in enumerate(players_ordered[team_num]):
                                player_info.append(self.game.player_tracking[section_num][team_num][player].stats['heroes'][fight[0]])

                        merged_info = [map_info, fight_info, player_info, player_fight_info]
                        merged_info_dense = [y for x in merged_info for y in x]

                        o.write((('%s,' * min(colCount, len(merged_info_dense)))[:-1] + '\n') % tuple(merged_info_dense))

                        fightNum += 1