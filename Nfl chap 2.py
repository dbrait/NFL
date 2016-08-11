import numpy as np
import pandas as pd

path = '/home/trey/Downloads/nfl'

games = pd.read_csv('%s/GAMES.csv' % path)
games.columns = [c.lower() for c in games.columns.values]
games = games[games.seas == 2013]
# games = games[games.ptsv != games.ptsh]
games = games[games.week <= 17]
games['winner'] = games.apply(lambda x: x.h if x.ptsh > x.ptsv
                              else x.v, axis=1)
games['loser'] = games.apply(lambda x: x.h if x.ptsh < x.ptsv
                              else x.v, axis=1)
num_games = games.week.max() - 1

# n teams (32)
# m games (256)

teams = sorted(games.h.unique())
team_ids = {team: i for i, team in enumerate(teams)}
game_matrix = np.eye(len(teams)) * num_games # M in Massey

# Credit to Sean Taylor for an easy way to create this matrix
for w, l in games[['winner', 'loser']].itertuples(index=False):
    game_matrix[team_ids[w], team_ids[l]] -= 1
    game_matrix[team_ids[l], team_ids[w]] -= 1

team_df = pd.DataFrame(index=teams, columns=teams, data=game_matrix)

# Will need this later
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
team_points['point_diff'] = team_points.points_for - team_points.points_against

point_diff = team_points.point_diff.values # p in Massey

massey_ratings = np.linalg.solve(game_matrix, point_diff)
team_points['massey_ratings'] = massey_ratings
team_points.sort('massey_ratings', ascending=False)

t_matrix = np.diag(np.repeat(num_games, len(teams)))

p_matrix = np.diag(np.repeat(0, len(teams)))
for i in range(len(teams)):
    for j in range(len(teams)):
        if i == j:
            continue
        p_matrix[i][j] = abs(game_matrix[i][j])

rhs = np.dot(t_matrix, massey_ratings) - team_points.points_for.values
team_points['defense_ratings'] = np.linalg.lstsq((t_matrix + p_matrix), rhs)[0]
team_points['offense_ratings'] = massey_ratings - defense_ratings

team_points.sort('massey_ratings', ascending=False)['massey_ratings']

team_points.sort('offense_ratings', ascending=False)['offense_ratings']

team_points.sort('defense_ratings', ascending=False)['defense_ratings']