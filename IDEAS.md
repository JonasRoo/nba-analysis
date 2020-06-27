# Features
    - Teams:
        - teams win%
        - home / away
        - "hot streak"
        - last match vs. that specific team
        - time passed since last game (exhaustion)
    - Players:
        - starting 5
        - individual player progression
            - "glow-up"
        - "hot streak" / performance trajectory
        - create an aggregating performance metric
            - sum of all numeric performance stats (e.g. pts, assts, steals, rebs etc.) divided by play_time
            - maybe need some sort of weighting in this function (e.g. weight 1 steal higher than 1 rebound, weight off. reb higher than def. rebounds)
                - could maybe do this as ML like: ax + by + cz = winloss, where [x, y, z] are numeric values

# References:
    - https://fantasydata.com/api/fantasy-scoring-system/nba
        > scoring function
            Three Point Field Goals: 3 points
            Two Point Field Goals: 2 points
            Free Throws Made: 1 point
            Rebounds: 1.2 points
            Assists: 1.5 points
            Blocked Shots: 2 points
            Steals: 2 points
            Turnovers: -1 points


# General:
    - Team chemistry
        - correlation between two player's scores?
        - how dependent is a team on an individual players score?

