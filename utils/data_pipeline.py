"""
This file serves as a preprocessing pipeline for the raw data returned from the `balldontlie` API (serves as a buffer for the official NBA stats API.)
"""

# imports
from typing import List, Dict, Any

import pandas as pd

# endpoint URIs
BASE_URL = r"https://www.balldontlie.io/api/v1"
TEAMS_ENDPOINT = "/".join([BASE_URL, "teams"])
PLAYERS_ENDPOINT = "/".join([BASE_URL, "players"])
STATS_ENDPOINT = "/".join([BASE_URL, "stats"])

# column renaming mapping
COLS_DICT = {
    "ast": "assists",
    "blk": "blocks",
    "dreb": "defensive_rebounds",
    "fg3_pct": "three_pt_percentage",
    "fg3a": "three_pt_attempts",
    "fg3m": "three_pt_made",
    "fg_pct": "two_pt_percentage",
    "fga": "two_pt_attempts",
    "fgm": "two_pt_made",
    "ft_pct": "one_pt_percentage",
    "fta": "one_pt_attempts",
    "ftm": "one_pt_made",
    "game": "game_object",
    "oreb": "offensive_rebounds",
    "pf": "personal_fouls",
    "player": "player_object",
    "pts": "points",
    "reb": "rebounds",
    "stl": "steals",
    "team": "own_team",
    "turnover": "turnovers",
}

LOWEST_MINS_PLAYED_TO_CONSIDER = 1

# performance grading constants
PERF_GRADING_NUMERIC_COLS = ["assists", "blocks", "rebounds", "points", "steals",
                             "turnovers", "personal_fouls", "one_pt_attempts", "two_pt_attempts", "three_pt_attempts"]
PERF_GRADING_DEF_WEIGHT = 1
PERF_GRADING_ATTR_WEIGHTS = {
    "points": 1,
    "turnovers": -2,
    "personal_fouls": -.25,
    "assists": 1.5,
    "steals": 3,
    "blocks": 2,
    "rebounds": 1.25,
    # new(DAVID)
    "one_pt_attempts": -.25,
    "two_pt_attempts": -.25,
    "three_pt_attempts": -.25,
}
PERF_LOWEST_POSSIBLE_SCORE = 0.001


def stats_endpoint_data_pipeline(data: List[Dict[str, Any]], min_mins_played: int = None, min_games_played: int = None) -> pd.DataFrame:
    """Serves as the main entry point for the data pipeline.
    Converts a list of raw Dictionary's (.json-like format) to a preprocessed pandas DataFrame.

    Steps taken:
        1. Renames columns after loading List of Dicts to DataFrame
        2. extract meta data for players and teams to proper columns
        3. Applies a minutes_played threshold to filter out low-minute ("noisy") entries
        4. Optionally removes low sample-size players from the dataset
        5. Applies a custom-made, scaled performance-grading (on player-in-game levek) function to entries 

    Args:
        data (List[Dict[str, Any]]): One list-object := stats for one player in one game
        min_mins_played (int, optional): If set, removes stats entries that are below that amount of mins_played in single game. If this is negative, nothing will be filtered. Defaults to an internally set value.
        min_games_played (int, optional): If not None, removes all of a player's entries from the dataset if he has less than n games played in the entire dataset. Defaults to None.

    Raises:
        AttributeError: If the list of Dicts is empty or None.

    Returns:
        pd.DataFrame: A fully preprocessed DataFrame, where one row is a single player's stats for a single game.
    """
    if not data:
        raise AttributeError("data can't be `None`!")
    df = pd.DataFrame.from_dict(data)

    # renaming columns
    df.rename(columns=COLS_DICT, inplace=True)
    df.set_index("id", inplace=True)

    # V-------------------- extracting object field data --------------------V
    # TODO(jonas): make this cleaner (refactor into dict or smth)
    # reduces data redundancy (extract only ID)
    df["own_team_id"] = df["own_team"].apply(lambda d: d["id"])
    df["own_team_name"] = df["own_team"].apply(lambda d: d["full_name"])
    # extract relevant player data, then get rid of the object
    df["player_id"] = df["player_object"].apply(lambda d: d["id"])
    df["player_position"] = df["player_object"].apply(lambda d: d["position"])
    df["player_name"] = df["player_object"].apply(
        lambda d: " ".join([d["first_name"], d["last_name"]]))
    # game related stuff
    df["game_id"] = df["game_object"].apply(lambda d: d["id"])
    df["is_home_game"] = df.apply(
        lambda b: b["own_team_id"] == b["game_object"]["home_team_id"], axis=1)

    # now drop object columns
    # TODO(jonas): we also need to do this with the game_object (also adapt in functions)
    df.drop(columns=["own_team", "player_object"], inplace=True)

    # V-------------------- feature engineering --------------------V
    # time played
    df[["mins_played", "secs_played"]] = df["min"].str.split(":", expand=True)
    df["mins_played"] = pd.to_numeric(df["mins_played"])
    df["secs_played"] = pd.to_numeric(df["secs_played"])

    # data pre-selection
    mins_played_threshold = min_mins_played or LOWEST_MINS_PLAYED_TO_CONSIDER
    df = df.loc[df.mins_played >= mins_played_threshold]

    # filter all players out that played lower than `n` games in total to avoid noise
    if min_games_played:
        df = remove_all_players_with_lower_than_n_games_played(
            df=df, n_games_played=min_games_played)

    # performance related stuff
    df["performance_score"] = df.apply(weighted_grade_performance, axis=1)
    df["game_winning_team"] = df["game_object"].apply(get_winning_team_id)
    df["own_team_won"] = df.apply(
        lambda s: True if s["game_winning_team"] == s["own_team_id"] else False, axis=1)
    df["team_points_share"] = df.apply(get_share_of_team_points, axis=1)

    return df


def grade_performance(row: pd.Series) -> float:
    """Computes a performance score for a single game entry.
    Multiplies every to-be-graded stat with its weight, and divide that sum by total amount of minutes played. 

    Args:
        row (pd.Series): A single (player, game) entry within a (preprocessed) DataFrame.

    Returns:
        float: The performance score for that (player, game).
    """
    score = 0
    # For each column we want to grade: multiply with its weight and add it to the running sum
    for col in PERF_GRADING_NUMERIC_COLS:
        score += row[col] * \
            PERF_GRADING_ATTR_WEIGHTS.get(col, PERF_GRADING_DEF_WEIGHT)

    # Finally, weight it by the minutes played in that game
    # since a player will naturally have a higher score if he has more minutes.
    return score / row["mins_played"]


def weighted_grade_performance(row: pd.Series) -> float:
    """Weights `grade_performance`s computed score with the total points scored for that game.

    Args:
        row (pd.Series): A single (player, game) entry within a (preprocessed) DataFrame.

    Returns:
        float: The performance score for that (player, game), weighted with the entire game.
    """
    unweighted_score = grade_performance(row)
    game_obj = row["game_object"]
    total_game_points = game_obj["home_team_score"] + \
        game_obj["visitor_team_score"]
    # TODO(jonas): should we scale this | try to minimize min-cases?
    return max(unweighted_score / total_game_points * 10e3, PERF_LOWEST_POSSIBLE_SCORE)


def get_winning_team_id(game: Dict[str, Any]) -> int:
    """Gets and returns the `team_id` of the winning team.

    Args:
        game (Dict[str, Any]): The `game_object`.

    Returns:
        int: The winning team's id.
    """
    return game["home_team_id"] if game["home_team_score"] > game["visitor_team_score"] \
        else game["visitor_team_id"]


def get_share_of_team_points(row: pd.Series) -> float:
    """Computes the player's share of his team's total scored points for that game.

    Args:
        row (pd.Series): A single (player, game) entry within a (preprocessed) DataFrame.

    Returns:
        float: Player's share of its team's points for that game. Between [0, 1].
    """
    game_obj = row["game_object"]
    team = "home_team" if row["own_team_id"] == game_obj.get(
        "home_team_id") else "visitor_team"
    return row["points"] / game_obj["_".join([team, "score"])]


def remove_all_players_with_lower_than_n_games_played(df: pd.DataFrame, n_games_played: int) -> pd.DataFrame:
    """Removes all entries for players that have less than `n_games_played` entries in the df.

    Args:
        df (pd.DataFrame): The DataFrame to trim.
        n_games_played (int): The threshold of unique games played under which a player will be eliminated from the DataFrame.

    Returns:
        pd.DataFrame: The trimmed DataFrame.
    """
    assert "player_name" in df.columns, "`player_name` needs to be in DataFrame columns!"
    counts = df.groupby("player_name").agg({"game_id": "nunique"})
    counts = counts.loc[counts.game_id > n_games_played]
    return df.loc[df.player_name.isin(counts.index)]
