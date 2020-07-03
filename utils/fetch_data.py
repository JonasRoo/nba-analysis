import file_utils
from typing import List, Tuple, Dict, Union
import requests
import time
from requests.models import Response
import os
from pprint import pprint

ALL_STATS_ENDPOINT = "https://www.balldontlie.io/api/v1/stats"
JSON_DIR_FOLDER_NAME = "raw_data"
SEASONS_QUERY_PARAM_NAME = "seasons[]"
DELAY_BETWEEN_REQUESTS = 60 // 60

def fetch_stats_for_seasons(seasons: List[Union[str, int]]):
    curr_dir_name = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    json_dir_full_path = os.path.join(curr_dir_name, JSON_DIR_FOLDER_NAME)
    subfolder_name = f"seasons_{'_'.join([str(s) for s in seasons])}"
    subfolder_full_path = os.path.join(json_dir_full_path, subfolder_name)
    os.mkdir(subfolder_full_path, mode=0o777)

    curr_page, last_page = 1, 10e10

    seasons_param = [str(s) for s in seasons]
    query_params = {
        "page": curr_page,
        SEASONS_QUERY_PARAM_NAME: seasons_param,
        "per_page": 100,
    }

    while curr_page <= last_page:
        time_before_request = time.time()
        query_params["page"] = curr_page
        r = requests.get(url=ALL_STATS_ENDPOINT, params=query_params)
        print(r.request.url)
        data, meta_data, next_page = extract_data_from_response(r)
        last_page = meta_data.get("total_pages")
        file_name = f"data_page_{curr_page}.json"
        print(f"Writing file {file_name}...")
        file_utils.dump_json_to_file(
            data=data, folder_name=subfolder_full_path, file_name=file_name
            )
        curr_page = next_page
        time_after_request = time.time()
        time_taken_since = time_after_request - time_before_request
        if time_taken_since < DELAY_BETWEEN_REQUESTS:
            time.sleep(time_taken_since)


def extract_data_from_response(response: Response) -> Tuple[Dict[any, any]]:
    response.raise_for_status()
    raw_data = response.json()

    data, meta_data = raw_data.get("data"), raw_data.get("meta")
    if data is None or meta_data is None:
        print("Error parsing requests response. Encountered with params:\n")
        pprint(query_params)
        print("\nResponse:")
        pprint(raw_json_data)
        raise ValueError("Encountered error parsing request (see above).")
    else:
        next_page = meta_data.get("next_page")
        return data, meta_data, next_page

if __name__ == "__main__":
    fetch_stats_for_seasons([2019])
