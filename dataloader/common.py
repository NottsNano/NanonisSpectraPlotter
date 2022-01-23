from collections import defaultdict

ALLOWED_HEADER_KEYS = {"data_type": "experiment_metadata",
                       "experiment_name": "experiment_metadata",
                       "time_start": "experiment_metadata",
                       "time_end": "experiment_metadata",
                       "comment": "experiment_metadata",

                       "pos_x": "signal_metadata",
                       "pos_y": "signal_metadata",
                       "size_x": "signal_metadata",
                       "size_y": "signal_metadata",
                       "image_points_res": "signal_metadata",
                       "spectra_res": "signal_metadata",
                       "spectra_x_channels": "signal_metadata",
                       "spectra_y_channels": "signal_metadata",
                       "img_channels": "signal_metadata",

                       "spectra_x": "signals",
                       "spectra_y": "signals",
                       "img": "signals"}


def make_empty_data_dict():
    empty_datadict = defaultdict(lambda: defaultdict(list))
    for needed_header, needed_section in ALLOWED_HEADER_KEYS.items():
        empty_datadict[needed_section][needed_header] = []

    return empty_datadict


def add_to_data_dict(resource_data_dict, mapping):
    for item_name, value in mapping.items():
        assert item_name in ALLOWED_HEADER_KEYS.keys()  # Because defaultdict would just make it otherwise!
        resource_data_dict[ALLOWED_HEADER_KEYS[item_name]][item_name].append(value)

    # Add empty entries if key is not present in the mapping
    for needed_header, needed_section in ALLOWED_HEADER_KEYS.items():
        if needed_header not in mapping.keys():
            resource_data_dict[needed_section][needed_header].append(None)

    return resource_data_dict
