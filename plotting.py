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


def make_spectra_fig(data, x_channel, y_channels, selectiondata, background, spectra_fig):
    if background is not None:
        spec_figure = make_empty_spectra_fig()
        spec_figure.update_layout(title="Spectra (Background Removed)")

    for selected_point in selectiondata:  # Loop through all selected points and all channels
        for y_channel in y_channels:
            data_file_idx = selected_point["customdata"]

            # Check that we can actually plot our data!
            if x_channel in data[data_file_idx]["signals"]["spectra_x"].keys() and \
                    y_channel in data[data_file_idx]["signals"]["spectra_y"].keys():
                xdata = np.array(data[data_file_idx]["signals"]["spectra_x"][x_channel])
                ydata = np.array(data[data_file_idx]["signals"]["spectra_y"][y_channel]).reshape(-1, len(xdata))

                if background is not None:
                    ydata -= background[y_channel]

                spectra_fig.add_trace(
                    go.Scatter(x=xdata,
                               y=ydata[selected_point["pointIndex"]],
                               name=data[data_file_idx]["experiment_metadata"]["experiment_name"],
                               customdata=[y_channel]))

    # Plot mean of all visible traces in this y channel
    for y_channel in y_channels:
        # Remove old mean trace
        tmp_data = list(spectra_fig.data)
        for i, entry in enumerate(tmp_data):
            if entry.name == f"Mean ({y_channel})":
                tmp_data.pop(i)
        spectra_fig.data = tuple(tmp_data)

        # Add new mean trace
        all_y = np.array([trace.y for trace in spectra_fig.data if trace.customdata[0] == y_channel])

        spectra_fig.add_trace(go.Scatter(x=spectra_fig.data[0].x, y=all_y.mean(axis=0),
                                         name=f"Mean ({y_channel})",
                                         customdata=[None],  # Otherwise no entry to compare to when building y
                                         line=dict(width=5, dash="dash"),
                                         visible=all_y.shape[0] > 1))

    spectra_fig.update_layout(xaxis_title=x_channel, yaxis_title=y_channel)

    return spectra_fig


def make_derivative_fig(spectra_fig):
    return spectra_fig
