from itertools import chain

import numpy as np
import pandas as pd


def get_ext(fpath):
    return fpath.split(".")[-1]


def ensure_list(var):
    return [var] if not isinstance(var, list) else var


def extract_all_values(data, data_type, name):
    out = np.empty(len(data), dtype="object")
    for i, entry in enumerate(data):
        out[i] = entry[data_type][name]

    return out


def makedropdownopts(data, signal_type, channel):
    opts = []
    for entry in data:
        potential_entry = entry[signal_type][channel]
        if potential_entry is not None:
            opts += potential_entry

    return [{"label": val, "value": val} for val in list(set(opts))]


def mpl_to_plotly(cmap, pl_entries=30, rdigits=6):
    scale = np.linspace(0, 1, pl_entries)
    colors = (cmap(scale)[:, :3] * 255).astype(np.uint8)
    pl_colorscale = [[round(s, rdigits), f'rgb{tuple(color)}'] for s, color in zip(scale, colors)]
    return pl_colorscale


def build_spectra_hover(params_pandas: pd.DataFrame):
    hovertemplate = ""
    for i, col in enumerate(params_pandas.columns):
        hovertemplate += f"<b>{col}: </b>" + \
                         "%{customdata[" + f"{i}" + "]:,.3g}<br>"
    hovertemplate += '<extra></extra>'
    return hovertemplate


def combine_click_selects(events: list):
    all_outs = {}
    for interactiontype in events:
        if interactiontype is None:
            continue
        for event in interactiontype["points"]:
            all_outs[event["pointIndex"]] = {"customdata": event["customdata"],
                                             "x": event["x"],
                                             "y": event["y"]}

    return all_outs
