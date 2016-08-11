import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.linalg as la

from scipy.sparse.linalg import eigs

def make_point_matrix(games, year):
    games = games[games.seas == year]    
    games = games[games.week <= 17]
    teams = sorted(games.h.unique())
    team_ids = {team: i for i, team in enumerate(teams)}

    games['winner'] = games.apply(lambda x: x.h if x.ptsh > x.ptsv
                                  else x.v, axis=1)
    games['loser'] = games.apply(lambda x: x.h if x.ptsh < x.ptsv
                                  else x.v, axis=1)
    
    games['pts_winner'] = games.apply(lambda x: x.ptsh if x.ptsh > x.ptsv
                                      else x.ptsv, axis=1)
    games['pts_loser'] = games.apply(lambda x: x.ptsh if x.ptsh < x.ptsv
                                      else x.ptsv, axis=1)

    num_teams = games.h.unique().shape[0]
    
    game_matrix = np.zeros((num_teams, num_teams))

    # Credit to Sean Taylor for an easy way to create this matrix
    
    for w, l in games[['winner', 'loser']].itertuples(index=False):
        sij =  games[(games.winner == w) & (games.loser == l)].pts_winner.values[0]
        sji = games[(games.winner == w) & (games.loser == l)].pts_loser.values[0]
        game_matrix[team_ids[w], team_ids[l]] += sij     
        game_matrix[team_ids[l], team_ids[w]] += sji
    
    for w, l in games[['winner', 'loser']].itertuples(index=False):
        sij = game_matrix[team_ids[w], team_ids[l]]
        sji = game_matrix[team_ids[l], team_ids[w]]
        game_matrix[team_ids[w], team_ids[l]] = (sij + 1) / (sij + sji + 2)
        game_matrix[team_ids[l], team_ids[w]] = (sji + 1) / (sij + sji + 2)

    return game_matrix

path = 'data/'

games = pd.read_csv('%s/GAMES.csv' % path)
games.columns = [c.lower() for c in games.columns.values]
teams = sorted(games.h.unique())
team_ids = {team: i for i, team in enumerate(teams)}

point_matrix = make_point_matrix(games, 2013)

mpl.rcParams['font.family'] = 'Open Sans'

plt.figure(figsize=(12, 9))
ax = plt.subplot(111)
ax.spines['top'].set_visible(False)
ax.spines['bottom'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.get_xaxis().tick_bottom()
ax.get_yaxis().tick_left()
plt.xlim((0, 1))
plt.xlabel("Strength score", fontsize=14)
plt.ylabel("Frequency", fontsize=14)
plt.title("Distribution of non-zero strength scores")
plt.hist(point_matrix[np.nonzero(point_matrix)], 10, color='SteelBlue')
plt.show()

def skew(x):
    return .5 + (np.sign(x - .5) * np.sqrt(np.abs(2 * x - 1)))/2 

x = np.linspace(0, 1, 50)
y = skew(x)
plt.figure(figsize=(12, 9))
ax = plt.subplot(111)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.get_xaxis().tick_bottom()
ax.get_yaxis().tick_left()
plt.xlim((0, 1))
plt.ylim((0, 1))
plt.xlabel('Non-adjusted strength score', fontsize=14)
plt.ylabel('Skewed strength score', fontsize=14)
plt.xticks([0, .25, .5, .75,  1], fontsize=14)
plt.yticks([0, .25, .5, .75, 1], fontsize=14)
plt.title('Skew-adjusted strength', fontsize=14)
plt.plot(np.linspace(0, 1), np.linspace(0, 1), 'k--', linewidth=0.5)
plt.plot(x, y, color='orange')
plt.show()

plt.figure(figsize=(12, 9))
ax = plt.subplot(111)
ax.spines['top'].set_visible(False)
ax.spines['bottom'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.get_xaxis().tick_bottom()
ax.get_yaxis().tick_left()
plt.xlim((0, 1))
plt.xlabel("Strength score", fontsize=14)
plt.ylabel("Frequency", fontsize=14)
plt.title("Distribution of skew-adjusted non-zero strength scores")
plt.hist(skew(point_matrix)[np.nonzero(skew(point_matrix))], 10, color='SteelBlue')
plt.show()

def eigens(point_matrix, skewed=False):
    if skewed:
        point_matrix = skew(point_matrix)
    eigenvalues = la.eigvals(point_matrix)
    real_eigenvalues = np.real(eigenvalues[-np.iscomplex(eigenvalues)])
    perron_value = np.max(real_eigenvalues)
    perron_vector = np.real(np.ravel(eigs(point_matrix, k=1, sigma=perron_value)[1]))
    return perron_value, perron_vector

# Initialize r
def power_method(point_matrix):
    r = np.repeat((1 / num_teams), num_teams)
    old_r = r.copy()
    tol = 0.0000000001
    mean_change = np.mean(old_r)
    iters = 1
    for i in range(100000):
        sigma = np.sum(r)
        r = np.dot(point_matrix, r) + sigma
        nu = np.sum(r)
        r = r / nu
        change = old_r - r
        mean_change = np.mean(change)
        iters += 1
        print(iters)
    return r

perron_value, perron_vector = eigens(point_matrix)
perron_value_skew, perron_vector_skew = eigens(point_matrix, skewed=True)
perron_vector = perron_vector / np.sum(perron_vector)
perron_vector_skew = perron_vector_skew / np.sum(perron_vector_skew)

power_ratings = power_method(point_matrix)

power_rating_order = np.argsort(power_ratings)[::-1]
perron_order = np.argsort(perron_vector)[::-1]
perron_skew_order = np.argsort(perron_vector_skew)[::-1]

print(np.array(teams)[power_rating_order])
print(np.array(teams)[perron_order])
print(np.array(teams)[perron_skew_order])

ratings_df = pd.DataFrame({'teams': teams, 'ratings': perron_vector})
ratings_df = ratings_df[['teams', 'ratings']]

skew_ratings_df = pd.DataFrame({'teams': teams, 'ratings': perron_vector_skew})
skew_ratings_df = skew_ratings_df[['teams', 'ratings']]