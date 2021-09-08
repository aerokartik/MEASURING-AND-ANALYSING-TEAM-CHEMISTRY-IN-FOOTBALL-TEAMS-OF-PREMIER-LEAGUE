# -*- coding: utf-8 -*-
"""
Created on Wed Aug  4 22:45:00 2021

@author: Kartik Gupta
"""

import warnings
from io import BytesIO
import pandas as pd
import numpy as np
import itertools

warnings.filterwarnings('ignore', category=pd.io.pytables.PerformanceWarning)

# ----------------------------------------------------------------------- functions -----------------------------------------------------------------



# defining a function to the read the JSON files
def read_json_file(filename):
    with open(filename+'.json', 'rb') as json_file:
        return BytesIO(json_file.read()).getvalue().decode('unicode_escape')
    


# function to create combination of players from the same team
def create_player_combo(df):
    
    player_combination =  list(itertools.combinations(df['playerId'], 2))        
    player1_column = []
    player2_column = []
    
    for tuples in player_combination:
        player1_column.append(tuples[0])
        player2_column.append(tuples[1])
    
    df1 = pd.DataFrame({'player1Id': player1_column, 'player2Id': player2_column})
    df1['matchId'] = m
    return df1


# function to calculate the time between each pair 
def calculate_pair_time(df):
        
    playtime_list = []
        
    # iterating over the rows of team_1 dataframe
    for n, r in df.iterrows():
            
        # player1 = [start-game, subbed-out]; player2 = [start-game, subbed-out]
        if (r['starting_11_p1'] == 1 and r['subbedIn_p1'] == 0 and r['subbedOut_p1'] == 1 and r['starting_11_p2'] == 1 and r['subbedIn_p2'] == 0 and r['subbedOut_p2'] == 1):
            # if player1 subs-out before player2
            if r['minute_out_p1'] < r['minute_out_p2']:
                playtime = r['minute_out_p1']
            # if player1 subs-out after player2
            elif r['minute_out_p1'] > r['minute_out_p2']:
                playtime = r['minute_out_p2']
            else:
                playtime = 0
                    
        if (r['starting_11_p1'] == 1 and r['subbedIn_p1'] == 0 and r['subbedOut_p1'] == 1 and r['starting_11_p2'] == 1 and r['subbedIn_p2'] == 0 and r['subbedOut_p2'] == 0):
            playtime = r['minute_out_p1']
                 
        if (r['starting_11_p1'] == 1 and r['subbedIn_p1'] == 0 and r['subbedOut_p1'] == 1 and r['starting_11_p2'] == 0 and r['subbedIn_p2'] == 1 and r['subbedOut_p2'] == 0):
            if r['minute_out_p1'] < r['minute_in_p2']:
                playtime = 0
            elif r['minute_out_p1'] > r['minute_in_p2']:
                playtime = r['minute_out_p1'] - r['minute_in_p2']
            else:
                playtime = 0
            
        if (r['starting_11_p1'] == 1 and r['subbedIn_p1'] == 0 and r['subbedOut_p1'] == 0 and r['starting_11_p2'] == 1 and r['subbedIn_p2'] == 0 and r['subbedOut_p2'] == 0):
            playtime = r['matchDuration']
                
        if (r['starting_11_p1'] == 1 and r['subbedIn_p1'] == 0 and r['subbedOut_p1'] == 0 and r['starting_11_p2'] == 0 and r['subbedIn_p2'] == 1 and r['subbedOut_p2'] == 0):
            playtime = r['matchDuration'] - r['minute_in_p2']
            
        if (r['starting_11_p1'] == 0 and r['subbedIn_p1'] == 1 and r['subbedOut_p1'] == 0 and r['starting_11_p2'] == 0 and r['subbedIn_p2'] == 1 and r['subbedOut_p2'] == 0):
            if r['minute_in_p1'] < r['minute_in_p2']:
                playtime = r['matchDuration'] - r['minute_in_p2']
            elif r['minute_in_p1'] > r['minute_in_p2']:
                playtime = r['matchDuration'] - r['minute_in_p1']
            else:
                playtime = r['matchDuration'] - r['minute_in_p1']
                    
        if (r['starting_11_p1'] == 1 and r['subbedIn_p1'] == 0 and r['subbedOut_p1'] == 1 and r['starting_11_p2'] == 0 and r['subbedIn_p2'] == 1 and r['subbedOut_p2'] == 1):
            if r['minute_in_p2'] < r['minute_out_p1']:
                if r['minute_out_p2'] < r['minute_out_p1']:
                    playtime = r['minute_out_p2'] - r['minute_in_p2']
                elif r['minute_out_p2'] > r['minute_out_p1']:
                    playtime = r['minute_out_p1'] - r['minute_in_p2']
                else: 
                    pass
            elif r['minute_in_p2'] > r['minute_out_p1']:
                playtime = 0
            else:
                playtime = 0
        
                    
        if (r['starting_11_p1'] == 1 and r['subbedIn_p1'] == 0 and r['subbedOut_p1'] == 0 and r['starting_11_p2'] == 0 and r['subbedIn_p2'] == 1 and r['subbedOut_p2'] == 1):
            playtime = r['minute_out_p2'] - r['minute_in_p2']
                
        if (r['starting_11_p1'] == 0 and r['subbedIn_p1'] == 1 and r['subbedOut_p1'] == 1 and r['starting_11_p2'] == 0 and r['subbedIn_p2'] == 1 and r['subbedOut_p2'] == 0):
            if r['minute_in_p1'] < r['minute_in_p2']:
                if r['minute_out_p1'] < r['minute_in_p2']:
                    playtime = 0
                elif r['minute_out_p1'] > r['minute_in_p2']:
                    playtime = r['minute_out_p1'] - r['minute_in_p2'] 
                else:
                    playtime = 0
            elif r['minute_in_p1'] > r['minute_in_p2']:
                playtime = r['minute_out_p1'] - r['minute_out_p1']
            else:
                pass
            
        if (r['starting_11_p1'] == 1 and r['subbedIn_p1'] == 0 and r['subbedOut_p1'] == 0 and r['starting_11_p2'] == 1 and r['subbedIn_p2'] == 0 and r['subbedOut_p2'] == 1):
            playtime = r['minute_out_p2']
            
            
        # accumulating time into a single list
        playtime_list.append(playtime)
        
    # converting the list into a column of the dataframe    
    df['playtime'] = playtime_list
    return df


# ----------------------------------------------------------------- importing datasets --------------------------------------------------------------


# importing the teams.json file    
json_teams = read_json_file('teams')
# converting the json file into a DataFrame
df_teams = pd.read_json(json_teams)
# creating a hdf format dataset called Wyscout, with the 'teams' dataframe as the 1st element
df_teams.to_hdf('wyscout.h5', key='teams', mode='w')

# checking the teams with missing information
df_missing_teams = df_teams[df_teams.isnull().any(axis=1)] # 0 teams with missing information

# importing the teams.json file    
json_players = read_json_file('players')
# converting the json file into a DataFrame
df_players = pd.read_json(json_players)
# appending the player dataframe to the Wyscout dataset
df_players.to_hdf('wyscout.h5', key='players', mode='a') 

# checking the players with missing information
df_missing_players = df_players[df_players.isnull().any(axis=1)] # 91 players with missing information


# name of all the competitions we have data for, to import the files
competitions = [
     'England',
#     'France',
#     'Germany',
#     'Italy',
#    'Spain',
#    'European Championship',
#    'World Cup'
    ]

# creating a list to store all the DataFrames of the imported matches
dfs_matches = []

# for loop to itereate over the competitions list to import the matches file and store as dataframes
for competition in competitions:
    competition_name = competition.replace(' ', '_') # replaces the space with _ in the name of competitions to import the files
    file_matches = f'matches_{competition_name}' # it is a formatted string 
    json_matches = read_json_file(file_matches) 
    df_matches = pd.read_json(json_matches)
    dfs_matches.append(df_matches) # appends each new dataframe to the dfs_matches list to be later concatenated into a single dataframe

# creating a single dataframe of all the matches of all the competitions of interest to us
df_matches = pd.concat(dfs_matches)

# checking the matches with missing information
df_missing_matches = df_matches[df_matches.isnull().any(axis=1)] #


# for loop to itereate over the competitions list to import the events file and store as dataframe
for competition in competitions:
    competition_name = competition.replace(' ', '_') # replaces the space with _ in the name of competitions to import the files
    file_events = f'events_{competition_name}'
    json_events = read_json_file(file_events)
    df_events = pd.read_json(json_events)
   
# sorting the team_actions 
team_actions = df_events.sort_values(by=['matchId','matchPeriod','eventSec'])
# creating a new column for time measured in minutes
team_actions['eventmin'] = df_events['eventSec']/60


# ---------------------------------------- calculating the match duartion of each match in the season -----------------------------------------------



# creating a list of all Match Ids
match_ids = list(team_actions['matchId'].unique())
time = []

# creating a dataframe of matchsets 
for ids in match_ids:
    match_duration = team_actions.loc[team_actions['matchId'] == ids]
    # calculating the sum of max time for each half of a game to sum them up to get the overall match duration
    time_duration = match_duration.loc[match_duration['matchPeriod'] == '1H'].eventmin.max() + match_duration.loc[match_duration['matchPeriod'] == '2H'].eventmin.max()
    # saving the total match duration calculated in the time list
    time.append(time_duration)

# creating a dictionary of match_ids and their respective match duractions calculated 
match_duration_dict = {'matchId': match_ids, 'matchDuration': time}
# converting the dictionary into a dataframe
match_duration_df = pd.DataFrame(match_duration_dict)



# ------------------------------------------------- calculating time played by pair of players ------------------------------------------------------


# creating a sub dataframe from df_matches consisting of just match_ids and the teamsData
teams_data = df_matches[['wyId','teamsData']].copy()

# creating empty lists and dataframes to store the infromation after penetrating the teamsData column for each match
starting_list = []                # list to temporarily store the dataframe of starting 11 players
substitution_list = []            # list to temporarily store the dataframe of substitute players 
substitution_df = pd.DataFrame()  # empty dataset to store substitute players


# for loop to iterate over the teams_data dataframe 
for length in range(len(teams_data)):
    match = teams_data.iloc[length,:]

    # penetrating the dictionaries to retrieve the starting 11 players, the substitute coming in and player going over out
    for index, dict1 in match.iteritems(): 
        if index == 'wyId':
            matchId = dict1
        if index == 'teamsData':
            for team_key, dict2 in dict1.items():
                teamId = team_key
                for formation_key, dict3 in dict2.items():
                    if formation_key == 'formation':
                        for lineup_key, lineup_list in dict3.items():
                            # gathering information of the starting_ 11 players and storing them in starting_df temporary dataframe
                            if lineup_key == 'lineup':
                                starting_df = pd.DataFrame.from_dict(lineup_list)
                                starting_df['teamId'] = teamId
                                starting_df['matchId'] = matchId
                                # storing the starting_11 dataframe in the starting_list to be concatinated into starting_11_df dataframe
                                starting_list.append(starting_df)
    
                            
                            # gather information of the substitution players and storing it in the sub_df temporary dataframe
                            if lineup_key == 'substitutions':
                                if lineup_list != 'null':
                                    sub_df = pd.DataFrame.from_dict(lineup_list)
                                    sub_df['teamId'] = teamId
                                    sub_df['matchId'] = matchId
                                    # storing the sub_df dataframes into the substitution_list to be concatenated later into substitution_df dataframe
                                    substitution_list.append(sub_df)   

    
# creating a dataframe of starting 11 players
starting_11_df = pd.concat(starting_list)
# reseting the index of starting_11_df dataframe
starting_11_df = starting_11_df.reset_index()
# assigning 1 to the players that started the match in the column starting_11
starting_11_df['starting_11'] = 1

# creating a dataframe of substitute players
substitution_df = pd.concat(substitution_list)
substitution_df = substitution_df.reset_index()
substitution_df['subbedIn'] = 1
substitution_df['subbedOut'] = 1
substitution_df.drop('index', axis = 1, inplace = True)

# creating a play_df dataframe consisting substitution and lineup information of players in all matches
play_df = pd.DataFrame()
play_df['matchId'] = starting_11_df['matchId'].append(substitution_df['matchId'])
play_df['teamId'] = starting_11_df['teamId'].append(substitution_df['teamId'])
play_df['playerId'] = starting_11_df['playerId'].append(substitution_df['playerIn'])

# merging 1 and 0 columns of starting_11 to play_df
starting_11_df.drop(['index','ownGoals','redCards','goals','yellowCards','teamId'], axis = 1, inplace = True)
play_df = play_df.merge(starting_11_df, how = 'left', left_on = ['playerId','matchId'], right_on = ['playerId','matchId'])

# merging 1 and 0 columns of subbedIn and subbedOut and minutes to play_df 
play_df = play_df.merge(substitution_df.drop(['teamId','playerOut','subbedOut'], axis = 1), how = 'left', left_on = ['playerId','matchId'], right_on = ['playerIn','matchId'])
play_df = play_df.merge(substitution_df.drop(['teamId','playerIn','subbedIn'], axis = 1), how = 'left', left_on = ['playerId','matchId'], right_on = ['playerOut','matchId'])
play_df.drop(['playerIn','playerOut'], axis =1, inplace = True)
play_df.fillna(0, inplace = True) # filling the blank non 1 cells (nan) with 0

play_df.rename(columns = {'minute_x': 'minute_in',
                          'minute_y': 'minute_out'
                          }, inplace = True)


pair_time_list = []
zero_one_list = []

# ruuning a loop over all matches to create player combinations and to calculate the player pair times
for m in match_ids:
    
    dataframe = play_df.loc[play_df['matchId'] == m]
    
    # creating combinations of teams for each match of the season
    teamId = dataframe['teamId'].unique()    
    team_1_df = dataframe.loc[dataframe['teamId'] == teamId[0]]
    team_2_df = dataframe.loc[dataframe['teamId'] == teamId[1]]

    # creating player combinations for both teams in a match
    team_1 = create_player_combo(team_1_df)
    team_2 = create_player_combo(team_2_df)

    
    team_1 = team_1.merge(team_1_df, how = 'left', left_on = ['matchId','player1Id'], right_on = ['matchId','playerId'])
    team_1 = team_1.merge(team_1_df, how = 'left', left_on = ['matchId','player2Id'], right_on = ['matchId','playerId'])

    team_1.drop(['playerId_x','playerId_y','teamId_y'], axis = 1, inplace = True)
        
    for i, row in match_duration_df.iterrows():
        if row['matchId'] == m:
            team_1['matchDuration'] = row['matchDuration']
        
    team_1.rename(columns = {'starting_11_x': 'starting_11_p1',
                             'minute_in_x': 'minute_in_p1',
                             'subbedIn_x': 'subbedIn_p1',
                             'minute_out_x': 'minute_out_p1',
                             'subbedOut_x': 'subbedOut_p1',
                             'teamId_x': 'teamId',
                             'starting_11_y': 'starting_11_p2',
                             'minute_in_y': 'minute_in_p2',
                             'subbedIn_y': 'subbedIn_p2',
                             'minute_out_y': 'minute_out_p2',
                             'subbedOut_y': 'subbedOut_p2',
                             }, inplace = True)
        

        
    team_2 = team_2.merge(team_2_df, how = 'left', left_on = ['matchId','player1Id'], right_on = ['matchId','playerId'])
    team_2 = team_2.merge(team_2_df, how = 'left', left_on = ['matchId','player2Id'], right_on = ['matchId','playerId'])
  
    team_2.drop(['playerId_x','playerId_y','teamId_y'], axis = 1, inplace = True)
      
    for i, row in match_duration_df.iterrows():
        if row['matchId'] == m:
            team_2['matchDuration'] = row['matchDuration']
                
    team_2.rename(columns = {'starting_11_x': 'starting_11_p1',
                             'minute_in_x': 'minute_in_p1',
                             'subbedIn_x': 'subbedIn_p1',
                             'minute_out_x': 'minute_out_p1',
                             'subbedOut_x': 'subbedOut_p1',
                             'teamId_x': 'teamId',
                             'starting_11_y': 'starting_11_p2',
                             'minute_in_y': 'minute_in_p2',
                             'subbedIn_y': 'subbedIn_p2',
                             'minute_out_y': 'minute_out_p2',
                             'subbedOut_y': 'subbedOut_p2',
                             }, inplace = True)       
    # calculatig the player pair time
    team_1 = calculate_pair_time(team_1)
    team_2 = calculate_pair_time(team_2)
    # combining the times of player pairs for both teams
    combined_time_df = pd.concat([team_1,team_2]).reset_index()
    combined_time_df.drop('index', axis = 1, inplace = True)
    pair_time_list.append(combined_time_df)

# commbining times of player pairs for all teams    
pair_time_df = pd.concat(pair_time_list).reset_index()
pair_time_df =  pair_time_df.drop('index', axis = 1)

# renaming columns and formatting the dataframe
p2 = pair_time_df.drop(['starting_11_p1','minute_in_p1','subbedIn_p1','minute_out_p1','subbedOut_p1', 'starting_11_p2','minute_in_p2','subbedIn_p2','minute_out_p2','subbedOut_p2'], axis = 1)
p2 = pair_time_df.groupby(['player1Id','player2Id']).agg(aggregated_playtime = ('playtime','sum')).reset_index()
p2 = p2.merge(df_players.drop(['role', 'passportArea','weight', 'firstName','middleName','lastName', 'currentTeamId', 'birthDate', 'height', 'birthArea', 'foot', 'currentNationalTeamId'], axis = 1), how = 'left', left_on = 'player1Id', right_on = 'wyId')
p2 = p2.merge(df_players.drop(['role','passportArea','weight', 'firstName','middleName','lastName', 'currentTeamId', 'birthDate', 'height', 'birthArea', 'foot', 'currentNationalTeamId'], axis = 1), how = 'left', left_on = 'player2Id', right_on = 'wyId')
p2.drop(['wyId_x','wyId_y'], axis = 1, inplace = True)
p2.rename(columns = {'shortName_x':'player1_name',
                     'shortName_y': 'player2_name'}, inplace = True)

# since it doesnt matter who inititated the interaction between the players, adding the times for player pairs with iteractions inititated by both players
cols = ['player1Id','player2Id']
p2[cols] = pd.DataFrame(np.sort(p2[cols], axis=1))
p3 = p2.groupby(cols, as_index = False).agg(playtime = ('aggregated_playtime','sum')).reset_index()
p3.drop('index',axis = 1,inplace = True)
p3 = p3.merge(df_players.drop(['role', 'passportArea','weight', 'firstName','middleName','lastName', 'currentTeamId', 'birthDate', 'height', 'birthArea', 'foot', 'currentNationalTeamId'], axis = 1), how = 'left', left_on = 'player1Id', right_on = 'wyId')
p3 = p3.merge(df_players.drop(['role', 'passportArea','weight', 'firstName','middleName','lastName', 'currentTeamId', 'birthDate', 'height', 'birthArea', 'foot', 'currentNationalTeamId'], axis = 1), how = 'left', left_on = 'player2Id', right_on = 'wyId')
p3.drop(['wyId_x','wyId_y'], axis = 1, inplace = True)
p3.rename(columns = {'shortName_x':'player1_name',
                     'shortName_y': 'player2_name'}, inplace = True)

# saving the file to excel
p3.to_excel('new_pair_time_calculation.xlsx', index = False)
