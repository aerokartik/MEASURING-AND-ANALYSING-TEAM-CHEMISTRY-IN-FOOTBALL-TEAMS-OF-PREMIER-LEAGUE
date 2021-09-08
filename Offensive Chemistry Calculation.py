# -*- coding: utf-8 -*-
"""
Created on Wed Aug  4 22:45:00 2021

@author: Kartik Gupta
"""

import warnings
from io import BytesIO
import pandas as pd
import numpy as np
import socceraction.vaep.features as features
import socceraction.vaep.labels as labels
from socceraction.spadl.wyscout import convert_to_spadl
from socceraction.vaep.formula import value
from tqdm.notebook import tqdm
from xgboost import XGBClassifier
import time

startTime = time.time()

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
df_missing_matches = df_matches[df_matches.isnull().any(axis=1)] # 0 matches with missing information

# appends compiled matches dataframe to the wyscout dataset 
df_matches.to_hdf('wyscout.h5', key='matches', mode='a')

# for loop to itereate over the competitions list to import the events file and store as dataframe
for competition in competitions:
    competition_name = competition.replace(' ', '_') # replaces the space with _ in the name of competitions to import the files
    file_events = f'events_{competition_name}'
    json_events = read_json_file(file_events)
    df_events = pd.read_json(json_events)
    df_events_matches = df_events.groupby('matchId', as_index=False) # groups all the events in the new events dataframe by the matchId
    
    # for loop to iterate within the df_events_matches dataframe 
    for match_id, df_events_match in df_events_matches:
        df_events_match.to_hdf('wyscout.h5', key=f'events/match_{match_id}', mode='a') # converts each match within the dataframe to a hdf format

#checking for missing values in events dataframe
df_missing_events = df_events[df_events.isnull().any(axis = 1)] # none missing values

# convert the entire data to SPADL format        
convert_to_spadl('wyscout.h5', 'spadl.h5')        


df_games = pd.read_hdf('spadl.h5', key='games')
# checking the players with missing information
df_missing_games = df_games[df_games.isnull().any(axis=1)] # none missing information

df_actiontypes = pd.read_hdf('spadl.h5', key='actiontypes')
# checking the players with missing information
df_missing_actiontypes = df_actiontypes[df_actiontypes.isnull().any(axis=1)] # none missing information

df_bodyparts = pd.read_hdf('spadl.h5', key='bodyparts')
# checking the bodypart dataframe for missing information
df_missing_bodyparts = df_bodyparts[df_bodyparts.isnull().any(axis=1)] # none missing information

df_results = pd.read_hdf('spadl.h5', key='results')
# checking the results dataframe for missing information
df_missing_results = df_results[df_results.isnull().any(axis=1)] # none missing information

# setting the gamestate of 3 actions
nb_prev_actions = 3

# functions within the features module of socceraction to create the features of the dataset from the spadl.h5 file
functions_features = [
    features.actiontype_onehot,
    features.bodypart_onehot,
    features.result_onehot,
    features.goalscore,
    features.startlocation,
    features.endlocation,
    features.movement,
    features.space_delta,
    features.startpolar,
    features.endpolar,
    features.team,
    features.time_delta
]

missing_actions = []
for _, game in tqdm(df_games.iterrows(), total=len(df_games)):
    game_id = game['game_id']
    df_actions = pd.read_hdf('spadl.h5', key=f'actions/game_{game_id}')
    df_actions = (df_actions
        .merge(df_actiontypes, how='left')
        .merge(df_results, how='left')
        .merge(df_bodyparts, how='left')
        .reset_index(drop=True)
    )
    # checking the results dataframe for missing information
    missing_actions.append(df_actions[df_actions.isnull().any(axis=1)])
    # creating gamestates of the actions
    dfs_gamestates = features.gamestates(df_actions, nb_prev_actions=nb_prev_actions)
    dfs_gamestates = features.play_left_to_right(dfs_gamestates, game['home_team_id'])
    # creating features for the games
    df_features = pd.concat([function(dfs_gamestates) for function in functions_features], axis=1)
    df_features.to_hdf('features.h5', key=f'game_{game_id}')

# checking the df_features dataframe for missing information
df_missing_features = df_features[df_features.isnull().any(axis=1)] # none missing information
df_missing_actions = pd.concat(missing_actions)

 
# list consisting of functions to create the lables of the dataset
functions_labels = [
    labels.scores,
    labels.concedes
]

# creating labels
for _, game in tqdm(df_games.iterrows(), total=len(df_games)):
    game_id = game['game_id']
    df_actions = pd.read_hdf('spadl.h5', key=f'actions/game_{game_id}')
    df_actions = (df_actions
        .merge(df_actiontypes, how='left')
        .merge(df_results, how='left')
        .merge(df_bodyparts, how='left')
        .reset_index(drop=True)
    )
    
    df_labels = pd.concat([function(df_actions) for function in functions_labels], axis=1)
    df_labels.to_hdf('labels.h5', key=f'game_{game_id}')

# checking the df_labels dataframe for missing information
df_missing_labels = df_labels[df_labels.isnull().any(axis=1)] # none missing information


# creating dataset for XGBoost    
columns_features = features.feature_column_names(functions_features, nb_prev_actions=nb_prev_actions)

dfs_features = []
for _, game in tqdm(df_games.iterrows(), total=len(df_games)):
    game_id = game['game_id']
    df_features = pd.read_hdf('features.h5', key=f'game_{game_id}')
    dfs_features.append(df_features[columns_features])
df_features = pd.concat(dfs_features).reset_index(drop=True)

# checking the df_features dataframe for missing information
df_missing_features = df_features[df_features.isnull().any(axis=1)] # none missing information

columns_labels = [
    'scores',
    'concedes'
]

dfs_labels = []
for _, game in tqdm(df_games.iterrows(), total=len(df_games)):
    game_id = game['game_id']
    df_labels = pd.read_hdf('labels.h5', key=f'game_{game_id}')
    dfs_labels.append(df_labels[columns_labels])
df_labels = pd.concat(dfs_labels).reset_index(drop=True)

# checking the df_labels dataframe for missing information
df_missing_labels = df_labels[df_labels.isnull().any(axis=1)] # none missing information


# creating a dictionary of trained XGBoost models for scoring and conceding probability prediction
models = {}
for column_labels in columns_labels:
    model = XGBClassifier(
        eval_metric='logloss',
        use_label_encoder=False,
        nthread = -1
    )
    model.fit(df_features, df_labels[column_labels]) # fitting the model with features as inputs and labels [scores, concedes] as the output
    models[column_labels] = model # saves the model for predicting probability of scores and the model for concedes in the models dictionary
    
    
# predicting the probabilities using the trained model label by label first being scores followed by concedes
dfs_predictions = {}
for column_labels in columns_labels:
    model = models[column_labels]
    probabilities = model.predict_proba(df_features) # calculating probabilities of scoring or conceding
    predictions = probabilities[:, 1]
    dfs_predictions[column_labels] = pd.Series(predictions) # predictions stored in the dfs_predictions dictionary for each label
df_predictions = pd.concat(dfs_predictions, axis=1)   # all predictions for both labels converted to a dataframe

# checking the df_predictions dataframe for missing information
df_missing_predictions = df_predictions[df_predictions.isnull().any(axis=1)] # none missing information

dfs_game_ids = []
for _, game in tqdm(df_games.iterrows(), total=len(df_games)):
    game_id = game['game_id']
    df_actions = pd.read_hdf('spadl.h5', key=f'actions/game_{game_id}')
    dfs_game_ids.append(df_actions['game_id'])
df_game_ids = pd.concat(dfs_game_ids, axis=0).astype('int').reset_index(drop=True)

# checking the df_game_ids dataframe for missing information
df_missing_game_ids = df_game_ids[df_game_ids.isnull()] # none missing information

df_predictions = pd.concat([df_predictions, df_game_ids], axis=1)
df_predictions_per_game = df_predictions.groupby('game_id')

# checking the df_predictions dataframe for missing information
df_missing_predictions = df_predictions[df_predictions.isnull().any(axis=1)] # none missing information

for game_id, df_predictions in tqdm(df_predictions_per_game):
    df_predictions = df_predictions.reset_index(drop=True)
    df_predictions[columns_labels].to_hdf('predictions.h5', key=f'game_{game_id}')

# checking the df_predictions dataframe for missing information
df_missing_predictions = df_predictions[df_predictions.isnull().any(axis=1)] # none missing information
    
df_players = pd.read_hdf('spadl.h5', key='players')
# checking the df_players dataframe for missing information
df_missing_players_2 = df_players[df_players.isnull().any(axis=1)] # none missing information

df_teams = pd.read_hdf('spadl.h5', key='teams')
# checking the df_teams dataframe for missing information
df_missing_teams_2 = df_teams[df_teams.isnull().any(axis=1)] # none missing information

dfs_values = []
missing_actions_2 = []
for _, game in tqdm(df_games.iterrows(), total=len(df_games)):
    game_id = game['game_id']
    df_actions = pd.read_hdf('spadl.h5', key=f'actions/game_{game_id}')
    df_actions = (df_actions
        .merge(df_actiontypes, how='left')
        .merge(df_results, how='left')
        .merge(df_bodyparts, how='left')
        .merge(df_players, how='left')
        .merge(df_teams, how='left')
        .reset_index(drop=True)
    )
    
    # checking the results dataframe for missing information
    missing_actions_2.append(df_actions[df_actions.isnull().any(axis=1)])
    
    df_predictions = pd.read_hdf('predictions.h5', key=f'game_{game_id}')
    df_values = value(df_actions, df_predictions['scores'], df_predictions['concedes'])
    
    df_all = pd.concat([df_actions, df_predictions, df_values], axis=1)
    dfs_values.append(df_all)

# checking the results dataframe for missing information    
df_missing_actions_2 = pd.concat(missing_actions_2) # 3090 values with player names missing, NOTICE THAT ALL PLAYER IDS ARE 0
df_missing_actions_2['game_id'] = df_missing_actions_2['game_id'].astype(int)
df_missing_actions_2['type_name'].value_counts()


df_values = (pd.concat(dfs_values)
    .sort_values(['game_id', 'period_id', 'time_seconds'])
    .reset_index(drop=True)
)

df_values['game_id'] = df_values['game_id'].astype(int)

# checking the df_teams dataframe for missing information
df_missing_values = df_values[df_values.isnull().any(axis=1)] # none missing information
df_missing_values['game_id'] = df_missing_values['game_id'].astype(int)

df_values.dropna(axis = 0, inplace = True)

# created a function to create interactions from actions(only continous actions are converted to actions)
def create_interactions(df,team_name):
    
    team_actions = df.loc[df['team_name'] == team_name]
    team_actions = team_actions.sort_values(by=['game_id','period_id','time_seconds'])
    team_offensive_actions = team_actions.loc[(team_actions['type_name'] == 'pass') | 
                                                    (team_actions['type_name'] =='cross' ) |
                                                    (team_actions['type_name'] == 'dribble') |
                                                    (team_actions['type_name'] == 'take-on') |
                                                    (team_actions['type_name'] == 'shot')]

    player_1 = []
    player_1_id = []
    player_2 = []
    player_2_id = []
    vaep_1 = []
    vaep_2 = []
    action_1 = []
    action_2 = []
    action_1_type = []
    action_2_type = []
    match_1_id = []
    match_2_id = []
    team_name =[]

    team_offensive_actions['action_id'] = team_offensive_actions.index
    team_offensive_actions['next_action_id'] = team_offensive_actions["action_id"].shift(-1)
    team_offensive_actions['next_action_id'] = team_offensive_actions['next_action_id'].fillna(0)
    for i, row in team_offensive_actions.iterrows():
        a = int(row['action_id'])
        b = int(row['next_action_id'])
        if (a+1 == b):
            player_1.append(team_offensive_actions.loc[a]['short_name'])
            player_2.append(team_offensive_actions.loc[b]['short_name'])
            player_1_id.append(team_offensive_actions.loc[a]['player_id'])
            player_2_id.append(team_offensive_actions.loc[b]['player_id'])
            vaep_1.append(team_offensive_actions.loc[a]['vaep_value'])
            vaep_2.append(team_offensive_actions.loc[b]['vaep_value'])
            action_1.append(team_offensive_actions.loc[a]['action_id'])
            action_2.append(team_offensive_actions.loc[b]['action_id'])
            action_1_type.append(team_offensive_actions.loc[a]['type_name'])
            action_2_type.append(team_offensive_actions.loc[b]['type_name'])
            match_1_id.append(team_offensive_actions.loc[a]['game_id'])
            match_2_id.append(team_offensive_actions.loc[b]['game_id'])
            team_name.append(team_offensive_actions.loc[a]['team_name'])

    joi = []
    for i in range(len(player_1)):
        joi.append(vaep_1[i] + vaep_2[i])
    
    interaction_df = pd.DataFrame({
        'player_1': player_1,
        'player_2': player_2,
        'player_1_id': player_1_id,
        'player_2_id': player_2_id,
        'team_name': team_name,
        'action_1': action_1,
        'action_2': action_2,
        'game_1_id': match_1_id,
        'game_2_id': match_2_id,
        'action_type_1': action_1_type,
        'action_type_2': action_2_type,
        'vaep_action_1': vaep_1,
        'vaep_action_2': vaep_2,
        'joi': joi
        }) 

    return interaction_df


compiled_interactions = []
teams = df_values['team_name'].unique()

# creating a single dataset of interactions for all the teams of that league
for team in teams:
    compiled_interactions.append(create_interactions(df_values, str(team)))

df_interactions = pd.concat(compiled_interactions)
# checking for missing values in df_interactions dataframe
df_missing_interaction =  df_interactions[df_interactions.isnull().any(axis=1)] #none missing information

# ranking players pairs based on their joi sum
df_ranking = (df_interactions.groupby(['player_1','player_2']).agg(joi_count=('joi', 'count'), joi_sum=('joi', 'sum'))).reset_index()
df_ranking.sort_values('joi_sum', ascending=False)

# checking the df_teams dataframe for missing information
df_missing_ranking = df_ranking[df_ranking.isnull().any(axis=1)] # none missing information
              
for n, row in df_ranking.iterrows():
    if row['player_1'] == row['player_2']:
        df_ranking.drop(n, inplace = True)              

# importing player pair times from the excel file formulated by the time calculation programme               
pair_time = pd.read_excel('new_pair_time_calculation.xlsx')

# adding player names to the data frame
df_ranking = df_ranking.merge(df_players[['player_id','short_name']],how = 'left',left_on=['player_1'],right_on=['short_name'])
df_ranking = df_ranking.merge(df_players[['player_id','short_name']],how = 'left',left_on=['player_2'],right_on=['short_name'])
df_ranking.drop(['short_name_x','short_name_y'], axis=1, inplace = True)
df_ranking.rename(columns = {'player_id_x': 'player1Id',
                            'player_id_y': 'player2Id'}, inplace = True)

# aggregating values for actions inititated by different player or each pair
cols = ['player1Id','player2Id']
df_ranking[cols] = pd.DataFrame(np.sort(df_ranking[cols], axis=1))
updated_df_ranking = df_ranking.groupby(cols, as_index = False).agg(interaction_count = ('joi_count','sum'), joi_sum = ('joi_sum','sum')).reset_index()
updated_df_ranking.drop('index',axis = 1,inplace = True)
updated_df_ranking = updated_df_ranking.merge(df_players[['player_id','short_name']], how = 'left', left_on = 'player1Id', right_on = 'player_id')
updated_df_ranking = updated_df_ranking.merge(df_players[['player_id','short_name']], how = 'left', left_on = 'player2Id', right_on = 'player_id')
updated_df_ranking.drop(['player_id_x','player_id_y'], axis = 1, inplace = True)
updated_df_ranking.rename(columns = {'short_name_x':'player1_name',
                                     'short_name_y': 'player2_name'}, inplace = True)

# merging the pair_time dataframe with joi dataframe 
final_df = updated_df_ranking.merge(pair_time, how = 'left', left_on = ['player1Id', 'player2Id'], right_on = ['player1Id', 'player2Id'])
final_df.drop(['player1_name_y','player2_name_y'], axis = 1, inplace = True)
final_df.rename(columns = {'player1_name_x': 'player1_name',
                            'player2_name_x': 'player2_name'}, inplace = True)

# formulating the joint_offensive_impact for 90 mins   
final_df['joi_90'] = (final_df['joi_sum'] / final_df['playtime']) * 90

# only considering pair of players who have played over 500 mins together 
final_df = final_df.loc[final_df['playtime'] > 450]

# sorting of dataframe in descending order of joi_90
final_df.sort_values(['joi_90'], ascending = False, inplace = True)
#final_df.drop(['player1_name','player2_name'], axis = 1, inplace = True)
final_df.reset_index(inplace = True)
final_df.drop('index', axis = 1, inplace = True)
player_team_df = df_values[['player_id','short_team_name']].copy()
player_team_df.drop_duplicates(inplace = True)

# adding team name for the players
final_df = final_df.merge(player_team_df, how = 'left', left_on = 'player1Id', right_on = 'player_id' )
final_df.drop('player_id', axis = 1, inplace = True)
final_df = final_df.merge(player_team_df, how = 'left', left_on = 'player2Id', right_on = 'player_id')
final_df.drop('player_id', axis = 1, inplace = True)

# players with 2 team names due to mid season transfers
error = final_df.loc[final_df['short_team_name_x'] != final_df['short_team_name_y']]
# removig such players time as they were double
final_df = final_df.loc[final_df['short_team_name_x'] == final_df['short_team_name_y']]

# adding teams and roles to final_df
df_players_copy = pd.read_json(json_players)
df_players_copy = df_players_copy[['wyId','role']]

# adding player roles to the dataframe
role_list = []
for r, row in enumerate(df_players_copy['role']):
    for index, role in df_players_copy['role'][r].items():
        if index == 'name':
          role_list.append(role)  
        
df_players_copy['player_role'] = role_list
df_players_copy.drop('role', axis = 1, inplace = True)    

# adding player roles to the dataframe
final_df =  final_df.merge(df_players_copy, how = 'left', left_on = 'player1Id', right_on = 'wyId')
final_df.drop('wyId', axis = 1, inplace = True)
final_df =  final_df.merge(df_players_copy, how = 'left', left_on = 'player2Id', right_on = 'wyId')
final_df.drop('wyId', axis = 1, inplace = True)
final_df.rename(columns = {'player_role_x': 'player1_role',
                            'player_role_y': 'player2_role'}, inplace = True)

final_df.drop('short_team_name_y', axis=1, inplace=True)
final_df.rename(columns = {'short_team_name_x':'Team'},inplace = True)

final_df.to_excel('team_Joint_Offensive_Impact.xlsx', index= False)

executionTime = (time.time() - startTime)
print('\nExecution time in seconds: ' + str(executionTime))