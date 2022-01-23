import base64
import os

import nanonispy as napy
import numpy as np
import pandas as pd
from PIL import Image
from nOmicron.utils.plotting import nanomap

from dataloader.converters import nanonis, omicron
from utils import get_ext


def make_tmpfile(contents: str, orig_name: str):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)

    f = open(orig_name, "wb")
    f.write(decoded)
    f.close()


def del_tmpfile(orig_name: str):
    os.remove(orig_name)


def make_empty_data_store():
    return []


def add_file_to_datastore(data, filename: str, old_datastore):
    tmp_path = f"tmp/{filename}"
    make_tmpfile(data, tmp_path)

    if get_ext(tmp_path) == "3ds":  # Use some code to generate function automatically??
        new_entry = nanonis.convert_3ds(tmp_path)
    elif get_ext(tmp_path) == "dat":
        new_entry = nanonis.convert_dat(tmp_path)
    elif get_ext(tmp_path) == "sxm":
        new_entry = nanonis.convert_sxm(tmp_path)
    else:
        raise ValueError("File Format Not Supported!")

    del_tmpfile(tmp_path)

    return old_datastore.append(new_entry)


def load_img(filename: str):
    return napy.read.Scan(filename)


def load_grid(filename: str):
    return napy.read.Grid(filename)


def sxm2pil(img: np.ndarray, min_cutoff=None, max_cutoff=None, cmap=nanomap):
    img = img.copy()

    if min_cutoff is None:
        min_cutoff = np.min(img)
    if max_cutoff is None:
        max_cutoff = np.max(img)

    normed_img = (img - min_cutoff) / (max_cutoff - min_cutoff)
    pillow_img = Image.fromarray(np.uint8(cmap(np.flipud(normed_img)) * 255))

    return pillow_img


def sxm2dict(sxm: napy.read.Scan):
    flat_dict = {}
    for outterdict, outterval in sxm.signals.items():
        for innerdict, innerval in sxm.signals[outterdict].items():
            flat_dict[f"{outterdict} ({innerdict})"] = innerval

    return flat_dict


def dot3ds_2dict(grid: napy.read.Grid):
    out_dict = grid.header
    out_dict["basename"] = grid.basename
    for key, val in grid.signals.items():
        if val.ndim <= 2:
            out_dict[key] = val.ravel().tolist()
        else:
            out_dict[key] = val.reshape(-1, val.shape[-1]).tolist()

    for i, param in enumerate(grid.header["fixed_parameters"] + grid.header["experimental_parameters"]):
        out_dict[param] = grid.signals["params"][:, :, i].ravel().tolist()

    return out_dict


def dot3ds_params2pd(dot3ds_data_dict):
    all_params = dot3ds_data_dict["fixed_parameters"] + dot3ds_data_dict["experimental_parameters"]
    data = np.array(dot3ds_data_dict["params"])
    df = pd.DataFrame(columns=all_params, data=data).dropna(axis=1, how="all")
    return df

