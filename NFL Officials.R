library(rvest)
library(stringr)
library(readr)
library(ggplot2)
library(dplyr)
library(tidyr)
library(broom)
library(lubridate)

base.url <- "http://www.pro-football-reference.com/"
officials.url <- "http://www.pro-football-reference.com/officials"

officials_urls <- read_html(officials.url) %>%
  html_nodes("table a") %>%
  html_attr("href")

official_names <- read_html(officials.url) %>%
  html_nodes("table a") %>%
  html_text()

officials <- data_frame(name = officials_names, url = official_urls)

all.data <- officials %>%
  group_by(name, url) %>% do({
    url <- paste(base.url, .$url, sep = "")
    doc <- read_html(url)
    off.data <- doc %>%
      html_nodes("table#game_logs") %>%
      html_table %>%
      first %>%
      filter(VPen != "VPen") %>%
      group_by(Year, Game, Position) %>% do({
        vals <- str_split(.$Game, "@")[[1]]
        data_frame(home = str_replace(vals[2], "\\*", ""),
                   away = str_replace(vals[1], "\\*", ""),
                   hpts = as.numeric(.$HPts),
                   vpts = as.numeric(.$Vpts),
                   hpen = as.numeric(.$HPen),
                   vpen = as.numeric(.$VPen),
                   hpenyards = as.numeric(.$HPYds),
                   vpenyeards = as.numeric(.$VPYds))
      }) %>%
      ungroup
  }) %>%
  ungroup

all.data %>% write_csv("officials_data.csv")



#after scraping
all.data <- read_csv("officials_data.csv")

home <- all.data %>%
  mutate(win = as.numeric(hpts > vpts)) %>%
  select(data = Year, name, team=home, pens=hpen, yds=hpenyards, win) %>%
  mutate(home=1)

away <- all.data %>%
  mutate(win = as.numeric(vpts > hpts)) %>%
  select(data = Year, name, team =  away, pens = vpen, yds = vpenyards, win) %>%
  mutate(home=0)

long.data <- home %>% bind_rows(away)

#top officials
all.data %>% 
  group_by(name) %>%
  summarise(n = n()) %>%
  arrange(-n)

#how many games per team
long.data %>%
  group_by(team) %>%
  summarise(n = length(unique(date))) %>%
  arrange(-n)

#convert to wide format, one column per official
#make indicator variables
wide <- long.data %>%
  mutate(seas = year(date - 180), #gets season
         present = 1) %>%
  spread(name, present, 0)

#officials one row per game, one column per official
officials.mat <- as.matrix(wide[,8:ncol(wide)])

#team has one row per game, one column per (team, season)
team.mat <- model.matrix( ~0 + team:factor(seas), wide)

#regression with penalties ~ team + all oficials involved
m <- lm(wide$pens ~ wide$home + team.mat + officials.mat)

#count games per official so use filter in plot below
official.rollup <- long.data %>%
  group_by(name) %>%
  summarise(n.games = n()/2)

tidy(m) %>%
  mutate(official = str_match(term, "officials\\.mat(.*)")[,2]) %>%
  filter(!is.na(official)) %>%
  inner_join(official.rollup, by=c("official" = "name")) %>%
  filter(n.games >= 250) %>%
  ggplot(aes(x = reorder(official, estimate), y = estimate,
             ymin = estimate - 1.96 * std.error,
             ymax = estimate + 1.96 * std.error)) +
  geom_pointrange() +
  coord_flip() +
  ylab("Team-Adjusted Extra Penalties per Game") +
  xlab("Official Name") +
  geom_hline(yintercept = 0.0, linetype="dashed") +
  theme_bw()

#team plots
tidy(m) %>%
  mutate(team = str_match(term, "team\\.matteam(.*):factor\\(seas\\)(.*)")[,2],
         seas = str_match(term, "team\\.matteam(.*):factor\\(seas\\)(.*)")[,3]) %>%
  filter(!is.na(team), seas == 2015) %>%
  ggplot(aes(x = reorder(team, estimate), y = estimate,
             ymin = estimate - 1.96 * std.error,
             ymax = estimate + 1.96 * std.error)) +
  geom_pointrange() +
  coord_flip() +
  ylab("Official-Adjusted Net Penalties per Game") +
  xlab("Team") +
  geom_hline(yintercept = 0.0, linetype = "dashed") +
  theme_bw()