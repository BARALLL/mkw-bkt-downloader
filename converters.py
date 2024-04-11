from math import floor
from typing_extensions import deprecated


def convert_ms_to_formatted(ms):
    if ms:
        minutes, seconds = divmod(ms, 60000)
        seconds, milliseconds = divmod(seconds, 1000)
        return "{:02d}:{:02d}.{:03d}".format(
            floor(minutes), floor(seconds), floor(milliseconds)
        )
    return ms


def convert_formatted_to_ms(t):
    return (
        int(t.split(":")[0]) * 60000
        + int(t.split(":")[1].split(".")[0]) * 1000
        + int(t.split(":")[1].split(".")[1])
    )


@deprecated
def get_name_by_trackId(df, trackId):
    return df.loc[df["trackId"] == trackId, "name"].values[0]
