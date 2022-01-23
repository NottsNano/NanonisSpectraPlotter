# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output, State
from dash_bootstrap_templates import load_figure_template

import data
import plotting
import utils

dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@V1.0.4/dbc.min.css"
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY, dbc_css])
# app._favicon = ("path_to_folder/(your_icon).co")
app.title = "Spectra Explorer"
load_figure_template(["darkly"])

image_fig = plotting.make_empty_image_plot()
spectra_fig = plotting.make_spectra_fig()


@app.callback(Output('uploaded-data', 'data'),
              Output('image-channel-dropdown', 'options'),
              Output('spectra-x-channel-dropdown', 'options'),
              Output('spectra-y-channel-dropdown', 'options'),
              Input('uploaded-data', 'data'),
              Input('upload-data-box', 'contents'),
              State('upload-data-box', 'filename'),
              prevent_initial_call=True)
def load_files(resource_data_store, list_of_contents, list_of_names):
    # If full reset button is clicked, delete data store
    if resource_data_store is None: # or button is pressed
        resource_data_store = data.make_empty_data_store()

    # Load in the data from each file into a unified, jsonable dictionary to be stored
    for contents, fname in zip(list_of_contents, list_of_names):
        resource_data_store = data.add_file_to_datastore(contents, fname, resource_data_store)

    # Populate the dropdown menu options
    image_channels = utils.makedropdownopts(resource_data_store, "signal_metadata", "img_channels")
    spectra_x_channels = utils.makedropdownopts(resource_data_store, "spectra_x_channels", "img_channels")
    spectra_y_channels = utils.makedropdownopts(resource_data_store, "spectra_x_channels", "img_channels")

    return resource_data_store, image_channels, spectra_x_channels, spectra_y_channels


@app.callback(Output('ref-image', 'figure'),
              Input('uploaded-data', 'data'),
              Input('image-channel-dropdown', 'value'),
              prevent_initial_call=True)
def update_image_figure(uploaded_data, image_channel):
    return plotting.make_image_spec_position_plot(uploaded_data, image_channel)


#
#
# @app.callback(Output('ref-image', 'figure'),
#               Output('spectra-data', 'data'),
#               Output('image-dropdown', 'options'),
#               Output('y-channel-dropdown', 'options'),
#               Input("uploaded-data", 'data'))
# def set_image_fig(spectra_path, sxm_path, image_channel):
#     if spectra_path is (None or ""):
#         return image_fig, json.dumps(""), [], []
#
#     dot3ds_data = load_grid(spectra_path)
#     dot3ds_data_dict = dot3ds_2dict(dot3ds_data)
#
#     if sxm_path is not (None or ""):
#         sxm_data = load_img(sxm_path)
#         sxm_data_dict = sxm2dict(sxm_data)
#     else:
#         sxm_data = None
#
#     dropdown_opts = build_dropdown_options(dot3ds_data, sxm_data)
#     channel_dropdown_opts = [{"label": val, "value": val} for val in dot3ds_data_dict["channels"]]
#
#     if image_channel is None:
#         return image_fig, json.dumps(dot3ds_data_dict), dropdown_opts, channel_dropdown_opts
#     elif image_channel in dot3ds_data_dict.keys():
#         res = dot3ds_data.header["dim_px"][::-1]
#         resizing = res + [-1]
#         background_img = np.array(dot3ds_data_dict[image_channel]).reshape(resizing).mean(
#             axis=-1)  # for now slice it, replace with slider in future
#     else:
#         background_img = sxm_data_dict[image_channel]
#
#     # updated_top_fig = callbacks.set_title(updated_top_fig, dot3ds_data.basename)
#     updated_top_fig = plotting.plot_positions_vs_image(dot3ds_data_dict, background_img)
#
#     return updated_top_fig, json.dumps(dot3ds_data_dict), dropdown_opts, channel_dropdown_opts


#
# @app.callback(Output('ref-spectra', 'figure'),
#               Output('btn-clear-old-data', 'data'),
#               Input('ref-image', 'clickData'),
#               Input('ref-image', 'selectedData'),
#               State('spectra-data', 'data'),
#               Input('y-channel-dropdown', 'value'),
#               Input('btn-clear-spec', 'n_clicks'),
#               State('btn-clear-old-data', 'data'),
#               prevent_initial_call=True)
# def spectraplotter(clickdata, selectdata, dot3dsdata_dict, selected_y_channels, clearbutton_presses,
#                    old_clearbutton_presses):
#     if old_clearbutton_presses is None or clearbutton_presses is None:
#         old_clearbutton_presses = clearbutton_presses = 0
#     if clearbutton_presses > old_clearbutton_presses:
#         return plotting.make_spectra_fig(), clearbutton_presses
#
#     dot3dsdata_dict = json.loads(dot3dsdata_dict)
#     useful_data = combine_click_selects([clickdata, selectdata])
#
#     spectra_fig = plotting.plot_spectra(useful_data, selected_y_channels, dot3dsdata_dict)
#
#     return spectra_fig, clearbutton_presses


root_layout = html.Div([
    html.Hr(),
    html.Div(dcc.Upload(
        id='upload-data-box',
        multiple=True,
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')]),
        style={
            'width': '1800px',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center'
        })),
    html.Hr(),
    html.Div([
        dcc.Markdown("**Image Channel: **",
                     style={'width': '600px',
                            "text-align": "center",
                            'display': 'inline-block'}),
        dcc.Markdown("**Spectra Channels: **",
                     style={'width': '1200px',
                            "text-align": "center",
                            'display': 'inline-block'}),

        dcc.Dropdown(id="image-channel-dropdown",
                     placeholder="Image Channel",
                     style={'width': '600px',
                            'display': 'inline-block'}),

        dcc.Dropdown(id="spectra-x-channel-dropdown",
                     placeholder="Spectra Channel (x)",
                     multi=False,
                     style={'width': '300px',
                            'display': 'inline-block'}),
        dcc.Dropdown(id="spectra-y-channel-dropdown",
                     placeholder="Spectra Channel (y)",
                     multi=True,
                     style={'width': '300px',
                            'display': 'inline-block'}),
        dbc.Button("Clear Spectra", id="btn-clear-spec",
                   size="sm",
                   style={'width': '7%',
                          'height': "36px",
                          "position": "relative", "bottom": "14px",  # This is misaligned for some reason.
                          'display': 'inline-block'})]
    ),
    html.Hr(),
    html.Div([
        dcc.Graph(
            id='ref-image',
            figure=image_fig,
            style={'width': "600px",
                   'height': "600px",
                   'display': 'inline-block'}),
        dcc.Graph(
            id='ref-spectra',
            figure=spectra_fig,
            style={'width': "1200px",
                   'height': "600px",
                   'display': 'inline-block'})
    ])
])

app.layout = dbc.Container(
    [root_layout,
     dcc.Store(id='uploaded-data'),  # storage_type='session'
     dcc.Store(id='btn-clear-old-data')],
    fluid=True,
    className="dbc"
)

if __name__ == '__main__':
    app.run_server(debug=True)
