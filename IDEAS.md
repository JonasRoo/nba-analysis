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



