from flatten_dict import flatten
from nanonispy.read import Grid, Spec, Scan

import utils
from dataloader.convert import convert_to_common

IMAGE_FILE_FORMATS = ["sxm"]
SPECTRA_FILE_FORMATS = ["dat", "3ds"]
ALL_FORMATS = [IMAGE_FILE_FORMATS + SPECTRA_FILE_FORMATS]


def convert_3ds(fname):
    data = Grid(fname)

    mapping = {"data_type": "spectra",
               "experiment_name": data.basename,
               "filetype": "3ds",
               "time_start": data.header["start_time"],
               "time_end": data.header["end_time"],
               "comment": data.header["comment"],

               "pos_xy": (data.signals["params"][...,
                          (len(data.header["fixed_parameters"]) + data.header["experimental_parameters"].index("X (m)"))
                          :(len(data.header["fixed_parameters"]) + data.header["experimental_parameters"].index("Y (m)")+1)].tolist()),
               "size_xy": list(data.header["size_xy"]),
               "image_points_res": list(data.header["dim_px"]),
               "spectra_res": data.header["num_sweep_signal"],
               "spectra_x_channels": utils.ensure_list(data.header["sweep_signal"]),
               "spectra_y_channels": utils.ensure_list(data.header["channels"]),
               "img_channels": ["topo"] + data.header["fixed_parameters"] + data.header["experimental_parameters"],
               "spectra_x": {data.header["sweep_signal"]: data.signals["sweep_signal"].tolist()},
               "spectra_y": {channel: data.signals[channel].ravel().tolist() for channel in data.header["channels"]},
               "img": {"topo": data.signals["topo"].ravel().tolist(),
                       **{channel: data.signals["params"][..., i].ravel().tolist() for i, channel in enumerate(
                           data.header["fixed_parameters"] + data.header["experimental_parameters"])}
                       }
               }

    resource_data = convert_to_common(mapping)

    return resource_data


def convert_dat(fname):
    data = Spec(fname)

    mapping = {"data_type": "spectra",
               "experiment_name": data.basename,
               "filetype": "dat",
               "time_start": data.header["Start time"],
               "time_end": data.header["Saved Date"],

               "pos_xy": [data.header["X (m)"], data.header["Y (m)"]],
               "spectra_res": len(list(data.signals.values())[0]),
               "spectra_x_channels": list(data.signals.keys()),
               "spectra_y_channels": list(data.signals.keys()),
               "spectra_x": {key: val.tolist() for key, val in data.signals.items()},
               "spectra_y": {key: val.tolist() for key, val in data.signals.items()}
               }

    resource_data = convert_to_common(mapping)

    return resource_data


def convert_sxm(fname):
    data = Scan(fname)

    def reducer(k1, k2):
        if k1 is None:
            return k2
        else:
            return f"{k1} ({k2})"

    flattened_signal_dict = flatten(data.signals, reducer=reducer)

    mapping = {"data_type": "image",
               "experiment_name": data.basename,
               "filetype": "sxm",
               "time_start": f"{data.header['rec_date']} {data.header['rec_time']}",
               "comment": data.header["comment"],

               "pos_xy": list(data.header["scan_offset"]),
               "size_xy": list(data.header["scan_range"]),
               "image_points_res": list(data.header["scan_pixels"]),
               "img_channels": list(flattened_signal_dict.keys()),
               "img": {key: val.tolist() for key, val in flattened_signal_dict.items()}
               }

    resource_data = convert_to_common(mapping)

    return resource_data
