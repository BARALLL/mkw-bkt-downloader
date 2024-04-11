import pathlib
import os
from random import randrange
import time
from rate_limiter import RateLimiter
from datetime import datetime, timedelta
import requests
import json
import config


def get_json(
    filename: str,
    ressource_path: str,
    SAVE_PATH: pathlib.Path | None = None,
    expiration_time_days: int | None = config.cache_expiration,
    proxies: dict[str, RateLimiter] | list[dict[str, RateLimiter]] | None = None,
):
    file_json = None
    SAVE_PATH, proxies = handle_inputs(SAVE_PATH, proxies)

    file_path = SAVE_PATH / filename
    file_json = retrieve_cached_json(file_path, expiration_time_days)

    if file_json is None:  # it not found or expired, download it
        resp = download_ressource(ressource_path, proxies)

        if resp and resp.status_code == 200:
            resp_text = resp.content.decode("utf-8-sig")
            file_json = json.loads(resp_text)

            if "recentRecords" in file_json:  # this shouldnt really be here..
                file_json.pop("recentRecords", None)

            with open(file_path, "w", encoding="utf8") as f:
                json.dump(file_json, f)
        else:
            config.logger.warning(
                f"Failed to retrieve {filename} from {ressource_path}. Status code: {resp.status_code}"
            )
            # print("abording...")
            # exit()
    return file_json


def handle_inputs(SAVE_PATH, proxies):
    if proxies and not isinstance(proxies, list):
        proxies = [proxies]

    if SAVE_PATH is None:
        SAVE_PATH = pathlib.Path(__file__).parent

    if not SAVE_PATH.exists():
        SAVE_PATH.mkdir(parents=True)
    return SAVE_PATH, proxies


def download_ressource(ressource_path, proxies):
    resp = None
    if proxies is None or not proxies:
        resp = requests.get(ressource_path)
    else:
        while proxies:
            if any(
                not (p := proxy)["rate_limiter"].lock.locked()
                and not (p := proxy)["rate_limiter"].request_lock.locked()
                for proxy in proxies
            ):
                next(p["rate_limiter"])
                with p["rate_limiter"].request_lock:
                    try:
                        resp = requests.get(
                            ressource_path,
                            proxies={"http": p["proxy"], "https": p["proxy"]},
                        )
                        break
                    except:
                        config.logger.warning(
                            f"connection with proxy {p['proxy']} failed"
                        )
                        if p in proxies:
                            proxies.remove(p)

                time.sleep(randrange(2, 5))
        if not proxies:
            config.logger.exception(f"no proxies left. could send request without proxy but prefer abording. Send a request without proxy")
            exit() #?
    return resp


def cache_hit(file_path: pathlib.Path, expiration_time_days: int | None = config.cache_expiration) -> bool:
    if file_path.is_file():
        file_stat = os.stat(file_path)  # (file_path).stat()
        modification_time = datetime.fromtimestamp(file_stat.st_mtime)
        return not expiration_time_days or (
            expiration_time_days
            and (datetime.now() - modification_time)
            < timedelta(days=expiration_time_days)
        )
    return False


def retrieve_cached_json(
    file_path: pathlib.Path, expiration_time_days: int | None = config.cache_expiration
) -> dict | None:
    file_json = None
    if file_path.is_file() and file_path.suffix == ".json":
        if cache_hit(file_path, expiration_time_days):
            with open(file_path) as f:
                try:
                    file_json = json.load(f)
                except Exception as e:
                    config.logger.warning(f"failed to load {file_path} with error {e}")
    return file_json


def download_ghost(
    filename: str,
    ressource_path: str,
    SAVE_PATH: pathlib.Path | None = None,
    expiration_time_days: int = config.cache_expiration,
    proxies: dict[str, RateLimiter] | list[dict[str, RateLimiter]] | None = None,
):
    file_json = None
    SAVE_PATH, proxies = handle_inputs(SAVE_PATH, proxies)
    file_path = (SAVE_PATH / filename).with_suffix(".rkg")
    if not cache_hit(
        file_path, expiration_time_days
    ):  # it not found or expired, download it
        resp = download_ressource(ressource_path, proxies)

        if resp and resp.status_code == 200:
            with open(file_path, "wb") as f:
                for chunk in resp.iter_content(1024):
                    f.write(chunk)
        else:
            config.logger.warning(
                f"Failed to retrieve {filename} from {ressource_path}. Status code: {resp.status_code}"
            )
            # print("abording...")
            # exit()
    return file_json
