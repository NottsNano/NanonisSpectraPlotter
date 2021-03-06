import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output, State
from dash_bootstrap_templates import load_figure_template
from plotly import graph_objects as go

import data
import plotting
import utils

dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@V1.0.4/dbc.min.css"
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY, dbc_css])
app._favicon = "favicon.ico"
app.title = "Spectra Explorer"
load_figure_template(["darkly"])

image_fig = plotting.make_empty_image_plot()
spectra_fig = plotting.make_empty_spectra_fig()
data.del_tmpfile_dir()


@app.callback(Output('uploaded-data', 'data'),
              Output('image-channel-dropdown', 'options'),
              Output('spectra-x-channel-dropdown', 'options'),
              Output('spectra-y-channel-dropdown', 'options'),
              Input('uploaded-data', 'data'),
              Input('upload-data-box', 'contents'),
              State('upload-data-box', 'filename'),
              prevent_initial_call=True)
def load_files(resource_data_store, list_of_contents, list_of_names):
    if resource_data_store is None:
        resource_data_store = data.make_empty_data_store()

    # Load in the data from each file into a unified, jsonable dictionary to be stored
    for contents, fname in zip(list_of_contents, list_of_names):
        resource_data_store = data.add_file_to_datastore(contents, fname, resource_data_store)

    # Populate the dropdown menu options
    image_channels = utils.makedropdownopts(resource_data_store, "signal_metadata", "img_channels")
    spectra_x_channels = utils.makedropdownopts(resource_data_store, "signal_metadata", "spectra_x_channels")
    spectra_y_channels = utils.makedropdownopts(resource_data_store, "signal_metadata", "spectra_y_channels")

    return resource_data_store, image_channels, spectra_x_channels, spectra_y_channels


@app.callback(Output('fig-image', 'figure'),
              Input('uploaded-data', 'data'),
              Input('image-channel-dropdown', 'value'),
              prevent_initial_call=True)
def update_image_spec_pos_figure(uploaded_data, image_channel):
    img_fig = plotting.make_image_spec_position_plot(uploaded_data, image_channel)
    return img_fig


# @app.callback(Output("download-spec", "data"),
#               Input("btn-download-spec", "n_clicks"),
#               State('fig-spectra', 'figure'),
#               prevent_initial_call=True)
# def download_spectra_as_json(_, fig_spectra):
#     return dict(content=fig_spectra, filename="spectra_data.json")


@app.callback(Output('fig-spectra', 'figure'),
              Output('data-clear-spec-btn', 'data'),
              Output('data-tabs-btn', 'data'),
              State('uploaded-data', 'data'),
              Input('spectra-x-channel-dropdown', 'value'),
              Input('spectra-y-channel-dropdown', 'value'),
              Input('fig-image', 'clickData'),
              Input('fig-image', 'selectedData'),
              Input('fig-spectra', 'figure'),
              Input('btn-clear-spec', 'n_clicks'),
              State('data-clear-spec-btn', 'data'),
              Input('background-data', 'data'),
              Input('tabs-spectra', 'value'),
              State('data-tabs-btn', 'data'),
              prevent_initial_call=True)
def update_spec_figure(uploaded_data, spectra_x_channel, spectra_y_channels, select_spectra, multi_select_spectra,
                       old_fig, reset_presses, reset_presses_old, background_spec_data, tab, old_tab):
    # Reset if clear spectra button pressed
    if utils.is_button_pressed(reset_presses, reset_presses_old):
        return plotting.make_empty_spectra_fig(), reset_presses, tab

    if (old_fig is None) or (utils.is_button_pressed(tab, old_tab)):
        spec_figure = plotting.make_empty_spectra_fig()
    else:
        spec_figure = go.Figure(old_fig)

    # Prevent execution if not enough options selected
    all_selections = utils.combine_selection_events((select_spectra, multi_select_spectra))
    if not all([all_selections, uploaded_data, spectra_x_channel, spectra_y_channels]):
        raise dash.exceptions.PreventUpdate

    # Draw the main figure
    spec_figure = plotting.make_spectra_fig(uploaded_data, spectra_x_channel, spectra_y_channels,
                                            all_selections, background_spec_data, spec_figure, tab)

    return spec_figure, reset_presses, tab


@app.callback(Output('background-data', 'data'),
              Output('data-background-spec-btn', 'data'),
              State('fig-spectra', 'figure'),
              State('spectra-y-channel-dropdown', 'value'),
              Input('btn-background-spec', 'n_clicks'),
              State('data-background-spec-btn', 'data'),
              prevent_initial_call=True)
def set_spectra_as_background(spec_figure, y_channels, reset_presses, reset_presses_old):
    if len(spec_figure["data"]) == 0:
        raise dash.exceptions.PreventUpdate

    if utils.is_button_pressed(reset_presses, reset_presses_old):
        out = {}
        spec_figure = go.Figure(spec_figure)
        out["x"] = spec_figure.data[0]["x"]

        for y_channel in y_channels:
            for trace in spec_figure.data:
                if trace.name == f"Mean ({y_channel})":
                    out[y_channel] = trace["y"]
        return out, reset_presses
    else:
        return None, reset_presses


fig_layout = html.Div([
    html.Hr(),
    html.Div(dcc.Upload(
        id='upload-data-box',
        multiple=True,
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files.'),
            ' (Formats Supported:  *.sxm,  *.dat,  *.3ds,  *.XX_mtrx)']),
        style={
            'width': '1888px',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center'
        })),
    html.Hr(),
    html.Div([
        dcc.Markdown("**Image Channel:**",
                     style={'width': '640px',
                            "text-align": "center",
                            'display': 'inline-block'}),
        dcc.Markdown("**Spectra Channels:**",
                     style={'width': '700px',
                            "text-align": "center",
                            'display': 'inline-block'}),
        dcc.Markdown("**Data Controls:**",
                     style={'width': '200px',
                            "margin-left": "210px",
                            "text-align": "center",
                            'display': 'inline-block'}),

        dcc.Dropdown(id="image-channel-dropdown",
                     placeholder="Image Channel",
                     style={'width': '640px',
                            "margin-right": "25px",
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
        dbc.Button("Set as Background", id="btn-background-spec",
                   size="sm",
                   color="secondary",
                   style={'width': "150px",
                          'height': "36px",
                          "position": "relative", "bottom": "14px",  # This is misaligned for some reason.
                          'display': 'inline-block'}),

        dbc.Button("Clear Spectra", id="btn-clear-spec",
                   size="sm",
                   style={'width': "150px",
                          'height': "36px",
                          "margin-left": "85px",
                          "position": "relative", "bottom": "14px",  # This is misaligned for some reason.
                          'display': 'inline-block'}),
        dbc.Button("Clear All", id="btn-clear-all",
                   href="/",
                   external_link=True,
                   size="sm",
                   style={'width': "150px",
                          'height': "36px",
                          "position": "relative", "bottom": "14px",  # This is misaligned for some reason.
                          'display': 'inline-block'}),
        # dbc.Button("Download Spectra", id="btn-download-spec",
        #            size="sm",
        #            style={'width': "150px",
        #                   'height': "36px",
        #                   "position": "relative", "bottom": "14px",  # This is misaligned for some reason.
        #                   'display': 'inline-block'}),
    ]
    ),
    html.Hr(),
    html.Div([
        dbc.Row([
            dbc.Col(
                children=[dcc.Graph(
                    id='fig-image',
                    figure=image_fig,
                    style={'height': '550px',
                           'width': '640px',
                           "margin-top": '50px',
                           'display': 'inline-block'},
                    config={"modeBarButtonsToRemove": ["toImage"]})],
                width=4),
            dbc.Col(children=[
                dcc.Tabs(id="tabs-spectra", value='orig', children=[
                    dcc.Tab(label='Integrate', value='integrate'),
                    dcc.Tab(label='Original', value='orig'),
                    dcc.Tab(label='Derivative', value='diff'),
                    dcc.Tab(label='Double Derivative', value='double-diff')],
                         style={'height': '50px',
                                'width': '1265px',
                                'text-align': 'center',
                                'vertical-align': 'middle',
                                'line-height': '25px'}),
                dcc.Graph(
                    id='fig-spectra',
                    figure=spectra_fig,
                    style={'height': '550px',
                           'width': '1265px',
                           'display': 'inline-block'},
                    config={"modeBarButtonsToRemove": ["toImage"],
                            'showEditInChartStudio': True,
                            'editable': False,
                            "plotlyServerURL": "https://chart-studio.plotly.com"})
            ],
                width=8

            )
        ], justify="evenly", className="g-0"),
    ])
])

datastore_layout = html.Div([dcc.Store(id='uploaded-data'),  # storage_type='session'
                             dcc.Store(id='background-data'),
                             dcc.Store(id='data-background-spec-btn'),
                             dcc.Store(id='data-clear-spec-btn'),
                             dcc.Store(id='data-clear-all-btn'),
                             dcc.Store(id='data-tabs-btn'),
                             dcc.Download(id="download-spec")])

attribution_layout = html.Div(children=[
    html.A('???? Made by Oliver Gordon for the University of Nottingham Nanoscience Group (2022). ',
           id="author-attribution",
           style={"color": "#AAAAAA"}
           ),
    html.A('Assess favicon created by Anggara - Flaticon',
           id="favicon-attribution",
           href="https://www.flaticon.com/free-icons/assess",
           style={"margin-left": "5px",
                  "color": "#AAAAAA"}
           )],
    style={"width": "1800px"})

app.layout = dbc.Container(
    [fig_layout,
     datastore_layout,
     html.Hr(),
     attribution_layout],
    fluid=True,
    className="dbc"
)

if __name__ == '__main__':
    app.run_server(debug=True)
