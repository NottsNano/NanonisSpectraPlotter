# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.
import base64
import io
import json
from io import StringIO

import dash
import dash_bootstrap_components as dbc
import numpy as np
from dash import dcc, html
from dash.dependencies import Input, Output, State
from dash_bootstrap_templates import load_figure_template
from nanonispy.read import Grid

import data
import plotting
import utils
from data import load_img, load_grid, dot3ds_2dict, sxm2dict, make_tmpfile
from dataloader.common import make_empty_data_dict
from utils import build_dropdown_options, combine_click_selects

dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@V1.0.4/dbc.min.css"
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY, dbc_css])
# app._favicon = ("path_to_folder/(your_icon).co")
app.title = "Spectra Explorer"
load_figure_template(["darkly"])

image_fig = plotting.make_image_plot()
spectra_fig = plotting.make_spectra_fig()


@app.callback(Output('ref-image', 'figure'),
              Output('spectra-data', 'data'),
              Output('image-dropdown', 'options'),
              Output('y-channel-dropdown', 'options'),
              Input("spectra-upload", 'value'),
              Input('sxm-upload', 'value'),
              Input('image-dropdown', 'value'))
def set_core_figs(spectra_path, sxm_path, image_channel):
    if spectra_path is (None or ""):
        return image_fig, json.dumps(""), [], []

    dot3ds_data = load_grid(spectra_path)
    dot3ds_data_dict = dot3ds_2dict(dot3ds_data)

    if sxm_path is not (None or ""):
        sxm_data = load_img(sxm_path)
        sxm_data_dict = sxm2dict(sxm_data)
    else:
        sxm_data = None

    dropdown_opts = build_dropdown_options(dot3ds_data, sxm_data)
    channel_dropdown_opts = [{"label": val, "value": val} for val in dot3ds_data_dict["channels"]]

    if image_channel is None:
        return image_fig, json.dumps(dot3ds_data_dict), dropdown_opts, channel_dropdown_opts
    elif image_channel in dot3ds_data_dict.keys():
        res = dot3ds_data.header["dim_px"][::-1]
        resizing = res + [-1]
        background_img = np.array(dot3ds_data_dict[image_channel]).reshape(resizing).mean(axis=-1)  # for now slice it, replace with slider in future
    else:
        background_img = sxm_data_dict[image_channel]

    # updated_top_fig = callbacks.set_title(updated_top_fig, dot3ds_data.basename)
    updated_top_fig = plotting.plot_positions_vs_image(dot3ds_data_dict, background_img)

    return updated_top_fig, json.dumps(dot3ds_data_dict), dropdown_opts, channel_dropdown_opts


@app.callback(Output('ref-spectra', 'figure'),
              Output('btn-clear-old-data', 'data'),
              Input('ref-image', 'clickData'),
              Input('ref-image', 'selectedData'),
              State('spectra-data', 'data'),
              Input('y-channel-dropdown', 'value'),
              Input('btn-clear-spec', 'n_clicks'),
              State('btn-clear-old-data', 'data'),
              prevent_initial_call=True)
def spectraplotter(clickdata, selectdata, dot3dsdata_dict, selected_y_channels, clearbutton_presses,
                   old_clearbutton_presses):
    if old_clearbutton_presses is None or clearbutton_presses is None:
        old_clearbutton_presses = clearbutton_presses = 0
    if clearbutton_presses > old_clearbutton_presses:
        return plotting.make_spectra_fig(), clearbutton_presses

    dot3dsdata_dict = json.loads(dot3dsdata_dict)
    useful_data = combine_click_selects([clickdata, selectdata])

    spectra_fig = plotting.plot_spectra(useful_data, selected_y_channels, dot3dsdata_dict)

    return spectra_fig, clearbutton_presses




@app.callback(Output('output-data-upload', 'data'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              prevent_initial_call=True)
def load_file(list_of_contents, list_of_names):
    # If reset button is clicked, recreate resource dict of images and spectra
    resource_data_dict = make_empty_data_dict()

    # Load in the data from each file into a unified, jsonable dictionary to be stored
    for contents, fname in zip(list_of_contents, list_of_names):
        resource_data_dict = data.loadfile(contents, fname,  resource_data_dict)

    return resource_data_dict








root_layout = html.Div([
    html.Hr(),
    html.Div([
        dcc.Markdown("** Spectra: **",
                     style={'width': '150px',
                            'margin': {'l': '10px'},
                            'display': 'inline-block'}),
        dcc.Input(
            id="spectra-upload",
            type="text",
            spellCheck=False,
            persistence=True,
            debounce=True,
            style={'width': '1640px'},
            placeholder=".3ds or .dat")]),
    html.Div([
        dcc.Markdown("** Image (opt.): **",
                     style={'width': '150px',
                            'margin': {'l': '10px'},
                            'display': 'inline-block'}),
        dcc.Input(
            id="sxm-upload",
            type="text",
            spellCheck=False,
            persistence=True,
            debounce=True,
            style={'width': '1640px'},
            placeholder=".sxm")]),
    html.Hr(),
    html.Div([
        dcc.Dropdown(id="image-dropdown",
                     placeholder="Image Channel",
                     style={'width': '600px',
                            'display': 'inline-block'}),
        dcc.Dropdown(id="y-channel-dropdown",
                     placeholder="Spectra Channel",
                     multi=True,
                     style={'width': '1000px',
                            'display': 'inline-block'}),
        dbc.Button("Clear Spectra", id="btn-clear-spec",
                   size="sm",
                   style={'width': '200px',
                          'height': "36px",
                          "position": "relative", "bottom": "14px",  # This is misaligned for some reason.
                          'display': 'inline-block'})]
    ),
    html.Hr(),
    html.Div([
        dcc.Graph(
            id='ref-image',
            figure=image_fig,
            style={'display': 'inline-block'}),
        dcc.Graph(
            id='ref-spectra',
            figure=spectra_fig,
            style={'display': 'inline-block'})
    ])
])

app.layout = dbc.Container(
    [root_layout,
     dcc.Store(id='spectra-data'),
     dcc.Store(id='btn-clear-old-data'),
dcc.Store(id='output-data-upload'),
dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=True
    )],
    fluid=True,
    className="dbc"
)


if __name__ == '__main__':
    app.run_server(debug=True)
