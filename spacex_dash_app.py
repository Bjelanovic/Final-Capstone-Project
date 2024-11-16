# Import necessary libraries
import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# Load SpaceX dataset
spacex_df = pd.read_csv("spacex_launch_data.csv")

# Get the min and max values for Payload Mass
min_payload = spacex_df['Payload Mass (kg)'].min()
max_payload = spacex_df['Payload Mass (kg)'].max()

# List of launch sites for the dropdown
launch_sites = [{'label': 'All Sites', 'value': 'ALL'}] + \
    [{'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()]

# Initialize Dash app
app = dash.Dash(__name__)

# App layout
app.layout = html.Div([
    html.H1("SpaceX Launch Records Dashboard", style={'textAlign': 'center'}),

    # Dropdown for selecting launch sites
    dcc.Dropdown(
        id='site-dropdown',
        options=launch_sites,
        value='ALL',
        placeholder="Select a Launch Site",
        searchable=True
    ),
    
    # Range slider for payload mass
    html.Div([
        html.P("Payload Range (kg):"),
        dcc.RangeSlider(
            id='payload-slider',
            min=min_payload,
            max=max_payload,
            step=1000,
            marks={int(i): f'{int(i)} kg' for i in range(0, int(max_payload) + 1, 2000)},
            value=[min_payload, max_payload]
        )
    ]),
    
    # Pie chart for success counts
    html.Div(dcc.Graph(id='success-pie-chart')),

    # Scatter chart for payload success analysis
    html.Div(dcc.Graph(id='success-payload-scatter-chart'))
])

# Callback for updating the pie chart
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def update_pie_chart(selected_site):
    if selected_site == 'ALL':
        # Overall success count for all sites
        fig = px.pie(
            spacex_df,
            names='class',
            title='Total Success Launches for All Sites'
        )
    else:
        # Success count for the selected site
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]
        fig = px.pie(
            filtered_df,
            names='class',
            title=f'Total Success Launches for {selected_site}'
        )
    return fig

# Callback for updating the scatter chart
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [
        Input(component_id='site-dropdown', component_property='value'),
        Input(component_id='payload-slider', component_property='value')
    ]
)
def update_scatter_chart(selected_site, payload_range):
    # Filter data based on payload range
    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= payload_range[0]) &
        (spacex_df['Payload Mass (kg)'] <= payload_range[1])
    ]

    if selected_site == 'ALL':
        # If "ALL", include all launch sites
        fig = px.scatter(
            filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title=f'Success by Payload Mass for All Sites ({payload_range[0]}-{payload_range[1]} kg)',
            labels={'class': 'Launch Outcome'},
            symbol='Launch Site'
        )
    else:
        # Filter for a specific site
        filtered_site_df = filtered_df[filtered_df['Launch Site'] == selected_site]
        fig = px.scatter(
            filtered_site_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title=f'Success by Payload Mass for {selected_site} ({payload_range[0]}-{payload_range[1]} kg)',
            labels={'class': 'Launch Outcome'}
        )

    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
