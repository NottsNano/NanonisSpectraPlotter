import numpy as np


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


def combine_selection_events(events):
    out_dict = {}
    [out_dict.update(event) for event in events if event is not None]

    if len(out_dict):
        return out_dict["points"]
    else:
        return None


def is_button_pressed(new_n_clicks, old_n_clicks):
    if old_n_clicks is None:
        old_n_clicks = 0
    if new_n_clicks is None:
        new_n_clicks = 0
    return new_n_clicks > old_n_clicks


spectra_hovertemplate = '<br>(%{x:,.3g}, %{y:,.3g})'



