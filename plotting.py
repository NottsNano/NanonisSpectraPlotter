import numpy as np
from nOmicron.utils.plotting import nanomap
from plotly import graph_objects as go, express as px
import json
import utils
from data import dot3ds_params2pd
from utils import build_spectra_hover, mpl_to_plotly


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
                                                 np.array(pos[i])[..., 0].max(),
                                                 res[i][0]),
                                   y=np.linspace(np.array(pos[i])[..., 1].min(),
                                                 np.array(pos[i])[..., 1].max(),
                                                 res[i][1]),
                                   color_continuous_scale=mpl_to_plotly(nanomap),
                                   origin="lower", aspect="equal")
                image_fig.add_trace(imshow.data[0])
                image_fig.update_layout(imshow.layout, hovermode="closest")

        # Add spectra
        image_fig.add_trace(go.Scatter(x=np.array(pos[i])[..., 0].ravel(), y=np.array(pos[i])[..., 1].ravel(),
                                       name=names[i],
                                       mode="markers",
                                       hoverinfo='text',
                                       customdata=np.repeat(i, np.array(pos[i]).size // 2)))

    return image_fig


def make_spectra_fig():
    spectra_fig = go.Figure()
    spectra_fig.update_layout(title="Spectra",
                              xaxis_title="Sweep",
                              width=1200,
                              height=600,
                              margin={'t': 100, 'b': 20, 'r': 20, 'l': 20})

    return spectra_fig


def plot_positions_vs_image(dot3ds_data_dict, img):
    dot3ds_pandas = dot3ds_params2pd(dot3ds_data_dict)

    x_axis = np.linspace(dot3ds_pandas["X (m)"].min(),
                         dot3ds_pandas["X (m)"].max(),
                         dot3ds_data_dict["dim_px"][0])
    y_axis = np.linspace(dot3ds_pandas["Y (m)"].min(),
                         dot3ds_pandas["Y (m)"].max(),
                         dot3ds_data_dict["dim_px"][1])

    # Plotting
    image_fig = px.imshow(img, color_continuous_scale=mpl_to_plotly(nanomap), x=x_axis, y=y_axis,
                          origin="lower", aspect="equal")
    image_fig.add_trace(go.Scatter(x=dot3ds_pandas["X (m)"], y=dot3ds_pandas["Y (m)"], mode="markers",
                                   hoverinfo='text',
                                   text=dot3ds_pandas.columns,
                                   customdata=dot3ds_pandas.values,
                                   hovertemplate=build_spectra_hover(dot3ds_pandas)))

    image_fig.update_layout(title="Spectra Position",
                            width=600,
                            height=600,
                            autosize=True,
                            xaxis_title="x (m)",
                            yaxis_title="y (m)",
                            margin={'t': 100, 'b': 20, 'r': 20, 'l': 20})

    return image_fig


def plot_spectra(useful_data, selected_y_channels, dot3dsdata_dict):
    spectra_fig = make_spectra_fig()
    spectra_fig.data = []
    spectra_fig.update_layout(yaxis_title=selected_y_channels[0])

    all_y = np.zeros((len(useful_data) * len(selected_y_channels), len(dot3dsdata_dict["sweep_signal"])))
    all_y[:] = np.nan
    i = 0
    for pointindex, metadata in useful_data.items():
        for y_channel in selected_y_channels:
            all_y[i, :] = dot3dsdata_dict[y_channel][pointindex]
            spectra_fig.add_trace(go.Scatter(x=dot3dsdata_dict["sweep_signal"],
                                             y=dot3dsdata_dict[y_channel][pointindex],
                                             name=y_channel +
                                                  f": ({useful_data[pointindex]['x']:.2g}, "
                                                  f"{useful_data[pointindex]['y']:.2g})"))
            i += 1

    if i > 1:
        spectra_fig.add_trace(go.Scatter(x=dot3dsdata_dict["sweep_signal"],
                                         y=np.nanmean(all_y, axis=0),
                                         line=dict(width=4, dash="dash"),
                                         name="Mean"))

    return spectra_fig
