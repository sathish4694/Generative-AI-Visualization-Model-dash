import pandas as pd
import plotly.express as px
import dash
import base64
import io
from dash import dcc, html
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
import dash_table
import dash_bootstrap_components as dbc

# Initialize Dash app with a Bootstrap theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Color options for different visualizations
color_scales = [
    'Viridis', 'Cividis', 'Inferno', 'Plasma', 'Magma', 'Jet', 'Rainbow', 'Blues', 'Greens', 'Reds', 'Purples'
]

# Helper function to read the file
def parse_file(contents, content_type):
    """Parse uploaded file."""
    content_string = contents.split(',')[1]
    decoded = base64.b64decode(content_string)
    
    if content_type.endswith('csv'):
        return pd.read_csv(io.StringIO(decoded.decode('utf-8')))
    elif content_type.endswith('xlsx'):
        return pd.read_excel(io.BytesIO(decoded))
    else:
        return None

# Layout of the app
app.layout = html.Div([
    dbc.Container([
        html.H1("Generative Visualization Model", style={'textAlign': 'center', 'marginTop': '20px'}),

        dbc.Row([
            dbc.Col([
                dcc.Upload(
                    id='upload-data',
                    children=html.Button('Upload File', className='btn btn-primary'),
                    multiple=False
                ),
                html.Div(id='file-upload-status', style={'marginTop': '10px'})
            ], width=4)
        ], style={'marginTop': '30px'}),

        # Data Preview Section
        dbc.Row([
            dbc.Col([
                html.Div(id='data-preview')
            ], width=12)
        ], style={'marginTop': '20px'}),

        # Visualization Selection
        dbc.Row([
            dbc.Col([
                dcc.Dropdown(
                    id='viz-type-dropdown',
                    options=[
                        {'label': 'Gantt Chart', 'value': 'Gantt Chart'},
                        {'label': 'Bar Chart', 'value': 'Bar Chart'},
                        {'label': 'Scatter Plot', 'value': 'Scatter Plot'},
                        {'label': 'Line Chart', 'value': 'Line Chart'},
                        {'label': 'Heatmap', 'value': 'Heatmap'},
                        {'label': 'Histogram', 'value': 'Histogram'},
                        {'label': 'Pie Chart', 'value': 'Pie Chart'},
                        {'label': 'Box Plot', 'value': 'Box Plot'}
                    ],
                    value='Bar Chart',
                    style={'width': '100%'}
                ),
            ], width=12)
        ], style={'marginTop': '20px'}),

        # Color scale selection
        dbc.Row([
            dbc.Col([
                dcc.Dropdown(
                    id='color-scale-dropdown',
                    options=[{'label': scale, 'value': scale} for scale in color_scales],
                    value='Viridis',
                    style={'width': '100%'}
                ),
            ], width=12)
        ], style={'marginTop': '20px'}),

        # Column Selection (Dynamic)
        dbc.Row([
            dbc.Col([
                html.Div(id='column-selection-container')
            ], width=12)
        ], style={'marginTop': '20px'}),

        # Graph display area
        dbc.Row([
            dbc.Col([
                dcc.Graph(id='visualization-graph', style={'height': '600px'})
            ], width=12)
        ], style={'marginTop': '30px'})
    ])
])

# Callback function to handle file upload
@app.callback(
    [Output('file-upload-status', 'children'),
     Output('data-preview', 'children')],
    Input('upload-data', 'contents'),
    Input('upload-data', 'filename')
)
def upload_file(contents, filename):
    if contents is None:
        return "No file uploaded.", ""

    # Parse the uploaded content based on file type (CSV or Excel)
    try:
        file_type = filename.split('.')[-1]
        df = parse_file(contents, file_type)

        if df is not None:
            # Show the first few rows of the dataset
            preview = dbc.Table.from_dataframe(df.head(), striped=True, bordered=True, hover=True)
            return f"File successfully uploaded: {filename} ({df.shape[0]} rows, {df.shape[1]} columns).", preview
        else:
            return "Error parsing the file. Ensure the file is a valid CSV or Excel.", ""
    except Exception as e:
        return f"Error processing file: {e}", ""

# Callback function to dynamically update column selections based on the chosen visualization
@app.callback(
    Output('column-selection-container', 'children'),
    [Input('viz-type-dropdown', 'value'),
     Input('upload-data', 'contents'),
     Input('upload-data', 'filename')]
)
def update_column_selection(viz_type, contents, filename):
    if contents is None:
        raise PreventUpdate

    try:
        file_type = filename.split('.')[-1]
        df = parse_file(contents, file_type)

        if df is not None:
            column_options = [{'label': col, 'value': col} for col in df.columns]

            # Dynamically render the appropriate column selectors based on the selected chart type
            if viz_type == 'Gantt Chart':
                return html.Div([
                    dcc.Dropdown(id='gantt-start-col', options=column_options, placeholder='Select Start Date'),
                    dcc.Dropdown(id='gantt-end-col', options=column_options, placeholder='Select End Date'),
                    dcc.Dropdown(id='gantt-task-col', options=column_options, placeholder='Select Task Column')
                ])
            elif viz_type == 'Bar Chart':
                return html.Div([
                    dcc.Dropdown(id='bar-x-col', options=column_options, placeholder='Select X-axis Column'),
                    dcc.Dropdown(id='bar-y-col', options=column_options, placeholder='Select Y-axis Column')
                ])
            elif viz_type == 'Scatter Plot':
                return html.Div([
                    dcc.Dropdown(id='scatter-x-col', options=column_options, placeholder='Select X-axis Column'),
                    dcc.Dropdown(id='scatter-y-col', options=column_options, placeholder='Select Y-axis Column'),
                    dcc.Dropdown(id='scatter-color-col', options=column_options, placeholder='Select Color Column')
                ])
            elif viz_type == 'Line Chart':
                return html.Div([
                    dcc.Dropdown(id='line-x-col', options=column_options, placeholder='Select X-axis Column'),
                    dcc.Dropdown(id='line-y-col', options=column_options, placeholder='Select Y-axis Column')
                ])
            elif viz_type == 'Heatmap':
                return html.Div([
                    dcc.Dropdown(id='heatmap-x-col', options=column_options, placeholder='Select X-axis Column'),
                    dcc.Dropdown(id='heatmap-y-col', options=column_options, placeholder='Select Y-axis Column'),
                    dcc.Dropdown(id='heatmap-value-col', options=column_options, placeholder='Select Value Column')
                ])
            elif viz_type == 'Histogram':
                return html.Div([
                    dcc.Dropdown(id='histogram-col', options=column_options, placeholder='Select Column')
                ])
            elif viz_type == 'Pie Chart':
                return html.Div([
                    dcc.Dropdown(id='pie-col', options=column_options, placeholder='Select Column for Pie')
                ])
            elif viz_type == 'Box Plot':
                return html.Div([
                    dcc.Dropdown(id='box-col', options=column_options, placeholder='Select Column')
                ])
    except Exception as e:
        print(f"Error generating column selections: {e}")
        return ""

# Callback function to generate visualization based on user inputs
@app.callback(
    Output('visualization-graph', 'figure'),
    [Input('viz-type-dropdown', 'value'),
     Input('color-scale-dropdown', 'value'),
     Input('upload-data', 'contents'),
     Input('upload-data', 'filename'),
     Input('gantt-start-col', 'value'),
     Input('gantt-end-col', 'value'),
     Input('gantt-task-col', 'value'),
     Input('bar-x-col', 'value'),
     Input('bar-y-col', 'value'),
     Input('scatter-x-col', 'value'),
     Input('scatter-y-col', 'value'),
     Input('scatter-color-col', 'value'),
     Input('line-x-col', 'value'),
     Input('line-y-col', 'value'),
     Input('heatmap-x-col', 'value'),
     Input('heatmap-y-col', 'value'),
     Input('heatmap-value-col', 'value'),
     Input('histogram-col', 'value'),
     Input('pie-col', 'value'),
     Input('box-col', 'value')]
)
def generate_visualization(viz_type, color_scale, contents, filename, *args):
    if contents is None:
        raise PreventUpdate

    try:
        file_type = filename.split('.')[-1]
        df = parse_file(contents, file_type)

        if viz_type == 'Gantt Chart':
            start_col, end_col, task_col = args
            fig = generate_gantt_chart(df, start_col, end_col, task_col, color_scale)
        elif viz_type == 'Bar Chart':
            x_col, y_col = args
            fig = generate_bar_chart(df, x_col, y_col, color_scale)
        elif viz_type == 'Scatter Plot':
            x_col, y_col, color_col = args
            fig = generate_scatter_plot(df, x_col, y_col, color_col, color_scale)
        elif viz_type == 'Line Chart':
            x_col, y_col = args
            fig = generate_line_chart(df, x_col, y_col, color_scale)
        elif viz_type == 'Heatmap':
            x_col, y_col, value_col = args
            fig = generate_heatmap(df, x_col, y_col, value_col, color_scale)
        elif viz_type == 'Histogram':
            col = args[0]
            fig = generate_histogram(df, col, color_scale)
        elif viz_type == 'Pie Chart':
            col = args[0]
            fig = generate_pie_chart(df, col, color_scale)
        elif viz_type == 'Box Plot':
            col = args[0]
            fig = generate_box_plot(df, col, color_scale)

        return fig
    except Exception as e:
        print(f"Error generating visualization: {e}")
        return {}

# Helper functions to generate each visualization
def generate_gantt_chart(df, start_col, end_col, task_col, color_scale):
    return px.timeline(df, x_start=start_col, x_end=end_col, y=task_col, color=task_col, color_continuous_scale=color_scale)

def generate_bar_chart(df, x_col, y_col, color_scale):
    return px.bar(df, x=x_col, y=y_col, color=color_scale)

def generate_scatter_plot(df, x_col, y_col, color_col, color_scale):
    return px.scatter(df, x=x_col, y=y_col, color=color_col, color_continuous_scale=color_scale)

def generate_line_chart(df, x_col, y_col, color_scale):
    return px.line(df, x=x_col, y=y_col, color=color_scale)

def generate_heatmap(df, x_col, y_col, value_col, color_scale):
    return px.density_heatmap(df, x=x_col, y=y_col, z=value_col, color_continuous_scale=color_scale)

def generate_histogram(df, col, color_scale):
    return px.histogram(df, x=col, color=color_scale)

def generate_pie_chart(df, col, color_scale):
    return px.pie(df, names=col)

def generate_box_plot(df, col, color_scale):
    return px.box(df, y=col, color=color_scale)

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
