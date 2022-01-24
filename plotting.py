import json

import numpy as np
from nOmicron.utils.plotting import nanomap
from plotly import graph_objects as go, express as px

import utils
from utils import mpl_to_plotly


def make_empty_image_plot():
    image_fig = go.Figure()
    image_fig.update_layout(title="Spectra Position",
                            xaxis_title="x (m)",
                            yaxis_title="y (m)",
                            margin={'t': 100, 'b': 20, 'r': 20, 'l': 20})

    return image_fig


def make_image_spec_position_plot(data, img_channel):
    with open('tmp/data.json', 'w') as f:
        json.dump(data, f)

    # Extract needed data
    img_data = utils.extract_all_values(data, "signals", "img")
    pos = utils.extract_all_values(data, "signal_metadata", "pos_xy")
    sizes = utils.extract_all_values(data, "signal_metadata", "size_xy")
    names = utils.extract_all_values(data, "experiment_metadata", "experiment_name")
    res = utils.extract_all_values(data, "signal_metadata", "image_points_res")

    # Look through all uploaded files
    image_fig = make_empty_image_plot()
    for i in range(len(data)):
        # Add images
        if data[i]["signal_metadata"]["img_channels"] is not None:
            if img_channel in data[i]["signal_metadata"]["img_channels"]:
                imshow = px.imshow(np.array(img_data[i][img_channel]).reshape(res[i][::-1]),
                                   x=np.linspace(np.array(pos[i])[..., 0].min(),
                                                 np.array(pos[i])[..., 0].min() + sizes[i][0],
                                                 res[i][0]),
                                   y=np.linspace(np.array(pos[i])[..., 1].min(),
                                                 np.array(pos[i])[..., 1].min() + sizes[i][1],
                                                 res[i][1]),
                                   color_continuous_scale=mpl_to_plotly(nanomap),
                                   origin="lower", aspect="equal")
                image_fig.add_trace(imshow.data[0])
                image_fig.update_layout(imshow.layout)

        # Add spectra
        if data[i]["experiment_metadata"]["data_type"] == "spectra":
            image_fig.add_trace(go.Scatter(x=np.array(pos[i])[..., 0].ravel(), y=np.array(pos[i])[..., 1].ravel(),
                                           name=names[i],
                                           mode="markers",
                                           customdata=np.repeat(i, np.array(pos[i]).size // 2)))

    # image_fig.update_layout(hovermode="x unified")

    return image_fig


def make_empty_spectra_fig():
    spectra_fig = go.Figure()
    spectra_fig.update_layout(title="Spectra",
                              xaxis_title="Sweep",
                              width=1200,
                              height=600,
                              margin={'t': 100, 'b': 20, 'r': 20, 'l': 20})

    return spectra_fig


def make_spectra_fig(data, x_channel, y_channels, selectiondata, spectra_fig):
    for selected_point in selectiondata:  # Loop through all selected points and all channels
        for y_channel in y_channels:
            data_file_idx = selected_point["customdata"]

            # Check that we can actually plot our data!
            if x_channel in data[data_file_idx]["signals"]["spectra_x"].keys() and \
                    y_channel in data[data_file_idx]["signals"]["spectra_y"].keys():

                xdata = np.array(data[data_file_idx]["signals"]["spectra_x"][x_channel])
                ydata = np.array(data[data_file_idx]["signals"]["spectra_y"][y_channel]).reshape(-1, len(xdata))
                spectra_fig.add_trace(
                    go.Scatter(x=xdata,
                               y=ydata[selected_point["pointIndex"]],
                               name=data[data_file_idx]["experiment_metadata"]["experiment_name"]))

    return spectra_fig

#
# def plot_spectra(useful_data, selected_y_channels, dot3dsdata_dict):
#     spectra_fig = make_spectra_fig()
#     spectra_fig.data = []
#     spectra_fig.update_layout(yaxis_title=selected_y_channels[0])
#
#     all_y = np.zeros((len(useful_data) * len(selected_y_channels), len(dot3dsdata_dict["sweep_signal"])))
#     all_y[:] = np.nan
#     i = 0
#     for pointindex, metadata in useful_data.items():
#         for y_channel in selected_y_channels:
#             all_y[i, :] = dot3dsdata_dict[y_channel][pointindex]
#             spectra_fig.add_trace(go.Scatter(x=dot3dsdata_dict["sweep_signal"],
#                                              y=dot3dsdata_dict[y_channel][pointindex],
#                                              name=y_channel +
#                                                   f": ({useful_data[pointindex]['x']:.2g}, "
#                                                   f"{useful_data[pointindex]['y']:.2g})"))
#             i += 1
#
#     if i > 1:
#         spectra_fig.add_trace(go.Scatter(x=dot3dsdata_dict["sweep_signal"],
#                                          y=np.nanmean(all_y, axis=0),
#                                          line=dict(width=4, dash="dash"),
#                                          name="Mean"))
#
#     return spectra_fig
