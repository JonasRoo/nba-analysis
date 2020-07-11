# Last step
    - implemented share of team points, quadratic weighting function of points
    - weighting function for individual player performance

# Next steps
    - tweak weighting function (also incorporate new weighted points / share of team points) | remove regular points
    - maybe regression: [numeric attributes] -> team won


# Last step
    - weighted performance metric by overall points in the game
    - cross-evaluation between Butler and Nunn (Butler "performs better" than Nunn in 88% of all games)

# Next steps
    - refactoring needed URGENTLY
    - pipeline for json response > df with feature engineered columns
    - apply to entire 2018 / 2019 season
    - sum this by team, per game
    - some sort of consistent visualization


# Last step (07/03)
    - refactored pipeline into external module
        - implemented a minimum performance_score (0.01) to prevent negative scores
        - reorganized a couple of columns, removed unweighted scores
    - automated data retrieval from `stats` endpoint for any given list of seasons

# Next steps
    - min/max scale the performances in pipeline
    - consider removing people who've only played 1 / 2 games with very low game time (remove "one-hit wonders")
        > esp. important when averaging on team level
    - Performance indicator should consider the make% for each throw
        - "Punish" unsucessful attempts?
        - Sum of points per this category of points * make%
        - Every throw "costs" points, and making it redeems them + a bonus?
            > weight for attemps would be negative value?
                > should all attempt types be weighted equally?
    - consider factor: `team chemistry` > need starting five data for this one
        > should also take into consideration when a player makes his teammates perform better (than avg)
    - TODO's in `pipeline` file
