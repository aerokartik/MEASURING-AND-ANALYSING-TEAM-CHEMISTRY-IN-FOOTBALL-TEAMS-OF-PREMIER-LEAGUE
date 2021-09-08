# -*- coding: utf-8 -*-
"""
Created on Tue Sep  7 15:19:22 2021

@author: Kartik's Omen
"""

import warnings
from io import BytesIO
import pandas as pd
import itertools
import matplotlib.pyplot as plt
from mplsoccer import Pitch

warnings.filterwarnings('ignore', category=pd.io.pytables.PerformanceWarning)

# defining a function to the read the JSON files
def read_json_file(filename):
    with open(filename+'.json', 'rb') as json_file:
        return BytesIO(json_file.read()).getvalue().decode('unicode_escape')
    
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
competitions = ['England']

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

match_id = 2500045
match_events = df_events.loc[df_events['matchId'] == match_id]

match_events.drop(['eventId','subEventName','tags','subEventId'], axis = 1, inplace = True)
manc_events = match_events.loc[match_events['teamId'] == 1625]

# creating empty lists to store values of coordinates
positions = manc_events['positions']
start_X = []
start_Y = []
end_X = []
end_Y = []

# loop for iterating over the series:
for i in positions:
    # loop for iterating over the list within each element of the series
    for j in range(len(i)):
        d = i[j]
        # if condition for identifying the starting coordinate dictionary
        if j == 0:
            # loop for iterating over the starting coordinate dictionary within the list
            for key, value in d.items():
                if key == 'x':
                    start_X.append(value)
                if key == 'y':
                    start_Y.append(value)
        # if condition for identifying the end coordinate dictionary
        else:
            # loop for iterating over the end coordinate dictionary within the list
            for key, value in d.items():
                if key == 'x':
                    end_X.append(value)
                if key == 'y':
                    end_Y.append(value)
# creating a dataframe for manchester city with start and end cordinates of actions
manc_events.insert(3, 'start_X', start_X)
manc_events.insert(4, 'start_Y', start_Y)
manc_events.insert(5, 'end_X', end_X)
manc_events.insert(6, 'end_Y', end_Y)  

manc_events.drop('positions', axis = 1, inplace = True)

# calculating the average starting 11 players of manchester city players in that match
average_positions = manc_events.groupby('playerId').agg(average_sx=('start_X','mean'), average_sy=('start_Y', 'mean')).reset_index()
average_positions = average_positions.loc[average_positions['playerId'] != 0]
average_positions = average_positions.merge(df_players[['wyId','shortName']], how = 'left', left_on = 'playerId', right_on = 'wyId')
average_positions.drop('wyId', axis = 1, inplace = True)
average_positions = average_positions.iloc[0:11,:]

# creating combination of players
player_combination =  list(itertools.combinations(average_positions['playerId'], 2))        
player1_column = []
player2_column = []
    
for tuples in player_combination:
    player1_column.append(tuples[0])
    player2_column.append(tuples[1])
    
    player_pair = pd.DataFrame({'player1Id': player1_column, 'player2Id': player2_column})

player_pair = player_pair.merge(average_positions[['playerId','shortName']], how = 'left', left_on = 'player1Id', right_on = 'playerId')
player_pair.drop('playerId', axis = 1, inplace = True)    
player_pair = player_pair.merge(average_positions[['playerId','shortName']], how = 'left', left_on = 'player2Id', right_on = 'playerId')
player_pair.drop('playerId', axis = 1, inplace = True)

player_pair.rename(columns = {'shortName_x': 'Player1',
                              'shortName_y': 'Player2'},inplace = True) 

# importing offensive chemistry values and adding to the dataframe
joi90_df = pd.read_excel('team_Joint_Offensive_Impact.xlsx')
player_pair = player_pair.merge(joi90_df[['player1Id','player2Id','joi_90']], how = 'left', left_on = ['player1Id','player2Id'], right_on = ['player1Id','player2Id'])
player_pair.sort_values(by = 'joi_90', inplace = True, ascending = False)

# adding average positions of players to the new dataframe with player combinations
top_joi_pairs = player_pair.copy()
top_joi_pairs = top_joi_pairs.merge(average_positions[['playerId','average_sx','average_sy']], how = 'left', left_on = 'player1Id', right_on = 'playerId')
top_joi_pairs.drop('playerId', axis = 1, inplace = True)
top_joi_pairs.rename(columns = {'average_sx': 'player1_x',
                                'average_sy': 'player1_y'}, inplace = True)
top_joi_pairs = top_joi_pairs.merge(average_positions[['playerId','average_sx','average_sy']], how = 'left', left_on = 'player2Id', right_on = 'playerId')
top_joi_pairs.drop('playerId', axis = 1, inplace = True)
top_joi_pairs.rename(columns = {'average_sx': 'player2_x',
                                'average_sy': 'player2_y'}, inplace = True)

# calculating line width for the plot based on offensive chemistry values
top_joi_pairs['line_width'] = (top_joi_pairs.joi_90/top_joi_pairs.joi_90.max()) * 10

# plotting the football pitch
pitch = Pitch(pitch_type='wyscout', pitch_color='grass', line_color='white', stripe = True, constrained_layout=False, tight_layout=False)
fig, ax = pitch.draw(figsize=(20, 15))

# plotting the lines
lines = pitch.lines(top_joi_pairs.player1_x, top_joi_pairs.player1_y, top_joi_pairs.player2_x, top_joi_pairs.player2_y, ax=ax, lw = top_joi_pairs.line_width, zorder = 1, color='red')
# plotting nodes to identify player positions
player1_nodes = pitch.scatter(top_joi_pairs.player1_x, top_joi_pairs.player1_y, linewidth = 1, color = 'blue', 
                           edgecolors = 'black', zorder = 1, alpha = 1, s=500, ax = ax)
player2_nodes = pitch.scatter(top_joi_pairs.player2_x, top_joi_pairs.player2_y, linewidth = 1, color = 'blue', 
                           edgecolors = 'black', zorder = 1, alpha = 1, s=500,  ax = ax)
# annotating player names on the plot
for index, row in top_joi_pairs.iterrows():
    pitch.annotate(row.Player1, xy=(row.player1_x, row.player1_y), c='white', va='bottom',
                   ha='center', size=15, weight='bold', ax=ax)
pitch.annotate('Fernandinho', xy = (48.9182, 46.2818), c = 'white', va = 'bottom', ha='center', size = 15, weight = 'bold', ax=ax)
plt.show()