import numpy as np
import pandas as pd

def colley_rankings(games, year, massey=False):
    games = games[games.seas == year]    
    games = games[games.week <= 17]
    games['winner'] = games.apply(lambda x: x.h if x.ptsh > x.ptsv
                                  else x.v, axis=1)
    games['loser'] = games.apply(lambda x: x.h if x.ptsh < x.ptsv
                                  else x.v, axis=1)

    num_games = games.week.max() - 1

    wins = dict(games.groupby('winner')['winner'].count())
    losses =  dict(games.groupby('loser')['loser'].count())

    # Note use of dict.get() method here -- otherwise
    # New England's 2007 undefeated season causes an error
    b_vector = [(1 + .5 * (wins.get(team, 0) - losses.get(team, 0))) 
                for team in teams]

    game_matrix = np.eye(len(teams)) * (2 + num_games) # C in Colley

    # Credit to Sean Taylor for an easy way to create this matrix
    
    for w, l in games[['winner', 'loser']].itertuples(index=False):
        game_matrix[team_ids[w], team_ids[l]] -= 1
        game_matrix[team_ids[l], team_ids[w]] -= 1

    colley_ratings = np.linalg.solve(game_matrix, b_vector)

    team_ratings = pd.DataFrame(index=teams)
    team_ratings['colley_ratings'] = colley_ratings

    if massey:
        points_for = dict.fromkeys(teams, 0)
        points_against = dict.fromkeys(teams, 0)

        for team in teams:
            home_points = games[games.h == team]['ptsh'].sum()
            away_points = games[games.v == team]['ptsv'].sum()
            points_for[team] = home_points + away_points
            home_conceded = games[games.h == team]['ptsv'].sum()
            away_conceded = games[games.v == team]['ptsh'].sum()
            points_against[team] = home_conceded + away_conceded

        team_points = pd.DataFrame(index=teams)
        team_points['points_for'] = pd.Series(points_for)
        team_points['points_against'] = pd.Series(points_against)
        team_points['point_diff'] = (team_points.points_for - 
                                     team_points.points_against)

        colley_massey_ratings = np.linalg.solve(game_matrix, 
                                     team_points.point_diff.values)

        team_ratings['colley_massey_ratings'] = colley_massey_ratings 
    
    return team_ratings

path = '/home/trey/Downloads/nfl/'

games = pd.read_csv('%s/GAMES.csv' % path)
games.columns = [c.lower() for c in games.columns.values]
teams = sorted(games.h.unique())
team_ids = {team: i for i, team in enumerate(teams)}
seasons = [seas for seas in games.seas.unique()
           if seas >= 2002]

ranking_df = pd.DataFrame(index=teams,
                          columns=seasons)

for season in seasons:
    ranking_df[season] = colley_rankings(games, season)

def largest_change(s):
    diff = (s - s.shift())[1:]
    if abs(min(diff)) >= max(diff):
        return min(diff)
    else:
        return max(diff)

ranking_df['max_change'] = ranking_df.apply(largest_change, axis=1)
ranking_df['max_change'].describe()

ranking_df = ranking_df.applymap(lambda x: np.round(x, 2))

ranking_df[ranking_df.max_change == ranking_df.max_change.max()]

ranking_df[ranking_df.max_change == ranking_df.max_change.min()]

# Using Colley-Massey

mov_ranking_df = pd.DataFrame(index=teams,
                          columns=seasons)

for season in seasons:
    mov_ranking_df[season] = colley_rankings(games, 
                                             season, 
                                             massey=True)['colley_massey_ratings']

mov_ranking_df['max_change'] = mov_ranking_df.apply(largest_change, axis=1)
mov_ranking_df['max_change'].describe()

mov_ranking_df = mov_ranking_df.applymap(lambda x: np.round(x, 2))

mov_ranking_df[mov_ranking_df.max_change == mov_ranking_df.max_change.max()]

mov_ranking_df[mov_ranking_df.max_change == mov_ranking_df.max_change.min()]

# Stability

diffs = ranking_df.apply(lambda x: x[:-1] - x[:-1].shift(), axis=1)
diffs['sd'] = diffs.apply(np.std, axis=1)
diffs[['sd']].sort('sd', ascending=False)

mov_diffs = mov_ranking_df.apply(lambda x: x[:-1] - x[:-1].shift(), 
                                 axis=1)
mov_diffs['sd'] = mov_diffs.apply(np.std, axis=1)
mov_diffs[['sd']].sort('sd', ascending=False)

means = ranking_df.iloc[:, :-1].apply(np.mean, axis=1)
means.sort(ascending=False)

mov_means = mov_ranking_df.iloc[:, :-1].apply(np.mean, axis=1)
mov_means.sort(ascending=False)

diff_df = diffs.join(mov_diffs, lsuffix="_col", rsuffix="_cm")

diff_df[['sd_col', 'sd_cm']].sort('sd_col', ascending=False)

diff_df[['sd_col', 'sd_cm']].sort('sd_cm', ascending=False)