# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

from __future__ import division, print_function

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import scale

#Need armchair analysis data

offense = pd.read_csv("OFFENSE.csv")
players = pd.read_csv("PLAYERS.csv")
offense = pd.merge(offense, players[["PLAYER", "PNAME", "POS1"]], on="PLAYER")
wrs = offense[(offense.POS1 == "WR") & (offense.YEAR == 2013)]
wrs = wrs[["PNAME", "TRG", "REC", "RECY", "TDRE", "FUML", "FPTS"]]

wr_games = wrs.groupby("PNAME")["TRG"].count()
wrs = wrs.groupby("PNAME").agg(np.mmean)
wrs["games"] = wr_games

k = list(range(3, 11))
scores = dict.fromkeys(k)

data = scale(wrs[["TRG", "REC", "RECY", "TDRE", "FUML", "FPTS"]].values)

for size in k:
    kmeans = KMeans(n_clusters=size)
    kmeans.fit(data)
    scores[size] = silhouette_score(data, kmeans.labels_)

plt.plot(k, scores.values())
plt.title("K-means clustering of WRs, 2013")
plt.xlabel("Number of clusters")
plt.ylabel("Silhouette score")

kmeans = KMeans(n_clusters=8)
kmeans.fit(data)

clusters = pd.DataFrame(kmeans.cluster_centers_,
                        columns=["TRG", "REC", "RECY", "TDRE", "FUML", "FPTS"])
wrs["cluster"] = kmeans.labels_

wrs[wrs.cluster == 2]

wrs[wrs.cluster == 7]