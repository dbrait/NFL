install.packages("devtools")

library(devtools)

devtools::install_github(repo="maksimhorowitz/nflscrapR")

library(nflscrapR)

season_2015 <- season_play_by_play(2015)
summary(season_2015)
head(season_2015)
season_2015$PlayType

#just have run or pass
nspec_season_2015 <- season_2015 %>% filter(PlayType == "Run" | PlayType == "Pass")

#chart teams offensive tendencies
pass_season_2015 <- nspec_season_2015 %>% filter(PlayType == "Pass") %>% count(posteam, PassLength, PassLocation, PassOutcome, Receiver)
write.csv(pass_season_2015, "pass distribution 2015.csv")

run_season_2015 <- nspec_season_2015 %>% filter(PlayType == "Run") %>% count(posteam, RunLocation, RunGap)
write.csv(run_season_2015, "run distribution 2015.csv")

#what teams tend to face defensively
def_pass_season_2015 <- nspec_season_2015 %>% filter(PlayType == "Pass") %>% count(DefensiveTeam, PassLength, PassLocation, PassOutcome, Receiver)
write.csv(def_pass_season_2015, "def pass distribution 2015.csv")

def_run_season_2015 <- nspec_season_2015 %>% filter(PlayType == "Run") %>% count(DefensiveTeam, RunLocation, RunGap)
write.csv(def_run_season_2015, "def run distribution 2015.csv")

#season 2014

season_2014 <- season_play_by_play(2014)

#just have run or pass
nspec_season_2014 <- season_2014 %>% filter(PlayType == "Run" | PlayType == "Pass")

pass_season_2014 <- nspec_season_2014 %>% filter(PlayType == "Pass") %>% count(posteam, PassLength, PassLocation, PassOutcome, Receiver)
write.csv(pass_season_2014, "pass distribution 2014.csv")

run_season_2014 <- nspec_season_2014 %>% filter(PlayType == "Pass") %>% count(posteam, RunLocation, RunGap)
write.csv(run_season_2014, "run distribution 2014.csv")

def_pass_season_2014 <- nspec_season_2014 %>% filter(PlayType == "Pass") %>% count(DefensiveTeam, PassLength, PassLocation, PassOutcome, Receiver)
write.csv(def_pass_season_2014, "def pass distribution 2014.csv")

def_run_reason_2014 <- nspec_season_2014 %>% filter(PlayType == "Run") %>% count(DefensiveTeam, RunLocation, RunGap)
write.csv(def_run_season_2014, "def run distribution 2014.csv")

season_2013 <- season_play_by_play(2013)

season_2012 <- season_play_by_play(2012)

season_2011 <- season_play_by_play(2011)

season_2010 <- season_play_by_play(2010)

season_2009 <- season_play_by_play(2009)

