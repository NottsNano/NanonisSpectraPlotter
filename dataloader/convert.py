from collections import defaultdict

ALLOWED_HEADER_KEYS = {"data_type": "experiment_metadata",
                       "filetype": "experiment_metadata",
                       "experiment_name": "experiment_metadata",
                       "time_start": "experiment_metadata",
                       "time_end": "experiment_metadata",
                       "comment": "experiment_metadata",

                       "pos_xy": "signal_metadata",
                       "size_xy": "signal_metadata",
                       "image_points_res": "signal_metadata",
                       "spectra_res": "signal_metadata",
                       "spectra_x_channels": "signal_metadata",
                       "spectra_y_channels": "signal_metadata",
                       "img_channels": "signal_metadata",

                       "spectra_x": "signals",
                       "spectra_y": "signals",
                       "img": "signals"}


def convert_to_common(mapping):
    new_entry = defaultdict(lambda: defaultdict(list))
    for needed_header, needed_section in ALLOWED_HEADER_KEYS.items():
        new_entry[needed_section][needed_header] = None

    for item_name, value in mapping.items():
        assert item_name in ALLOWED_HEADER_KEYS.keys()
        new_entry[ALLOWED_HEADER_KEYS[item_name]][item_name] = value

    return new_entry
