from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from downloader import get_json, download_ghost
import config
from itertools import groupby


index_json = get_json(
    "chadsoft_index.json",
    config.chadsoft_subdomain + "/index.json",
    SAVE_PATH=config.CACHE_PATH,
)
index_links = index_json["_links"]
leaderboard_path = index_links[config.leaderboard_name]["href"]

track_json = get_json(
    f"chadsoft_leaderboards_{config.leaderboard_name}.json",
    config.chadsoft_subdomain + leaderboard_path,
    SAVE_PATH=config.CACHE_PATH,
)


# df_leaderboards = pd.DataFrame.from_dict(cts_json["leaderboards"])
def group_by(items, key):
    return {k: list(g) for k, g in groupby(items, key)}


tracks_links = []
tracks_by_id = group_by(track_json["leaderboards"], lambda x: x["trackId"])
for tracks in tracks_by_id.values():
    best_match = sorted(
        [
            (
                sum(
                    possibility.get(k, v)
                    == v  # if key is not present consider it valid
                    for k, v in config.track_filters.items()
                ),
                possibility,
            )
            for possibility in tracks
        ],
        key=lambda x: x[0],
        reverse=True,
    )
    for score, track in best_match:
        if score != len(config.track_filters):
            config.logger.warning(f"track {track['name']} does not match all filters")
        if (
            "name" in track
            and "_links" in track
            and "item" in track["_links"]
            and "href" in track["_links"]["item"]
        ):
            tracks_links.append((track["_links"]["item"]["href"], track["name"]))
            break
        else:
            config.logger.warning(f"no link to leaderboard for track {track['name']}")


def run(track):
    track_link, track_name = track
    track_leaderboard = get_json(
        track_name,
        config.chadsoft_subdomain + track_link,
        SAVE_PATH=config.CACHE_PATH / "tracks_leaderboards",
        proxies=config.proxy_list if config.proxy_list else None,
    )
    if "ghosts" in track_leaderboard and track_leaderboard["ghosts"]:
        download_ghost(track_leaderboard["ghosts"][0], track_name)
    else:
        config.logger.warning(f"no ghost in {track_name}")

if __name__ == "__main__":
    max_workers = max(config.max_workers, 1)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(run, track) for track in tracks_links]
        for future in tqdm(as_completed(futures)):
            pass