# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

gb = spacex_df.groupby(['Launch Site', 'class']).size().to_frame(name='count').reset_index()
gb2 = spacex_df.groupby(['Launch Site']).size().to_frame(name='totalperLS').reset_index()
gb = gb.set_index('Launch Site').join(gb2.set_index('Launch Site'))
gb['success_rate'] = gb['count'] / gb['totalperLS']

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                dcc.Dropdown(
                                    id='site-dropdown',
                                    options=[
                                        {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                                        {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
                                        {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                                        {'label': 'VFAB SLC-4E', 'value': 'VFAB SLC-4E'},
                                        {'label': 'All Sites', 'value': 'ALL'},
                                    ],
                                    placeholder='Select a Launch Site here',
                                    searchable=True,
                                    value='ALL'
                                ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                    min=0, max=10000, step=1000,
                                    #marks={0: '0',
                                    #    100: '100'},
                                    value=[min_payload, max_payload]),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Function decorator to specify function input and output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))

def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        fig = px.pie(spacex_df, values='class', 
        names='Launch Site', 
        title='Total Success Launches By Site')
    else:
        fig = px.pie(gb.loc[entered_site], values='success_rate', 
        names='class', 
        title=f'Total Success Launches for site {entered_site}')
    return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback( Output(component_id='success-payload-scatter-chart', component_property='figure'),
               [Input(component_id='site-dropdown', component_property='value'),
               Input(component_id='payload-slider', component_property='value')])

# Add computation to callback function and return graph
def get_scatter(entered_site, payload):
    payload_min = payload[0]
    payload_max = payload[1]
    if entered_site == 'ALL':
        df_scatter = spacex_df[spacex_df['Payload Mass (kg)'].between(payload_min, payload_max, inclusive='both')]
        fig = px.scatter(df_scatter,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        title='Correlation between Payload and Success for all sites')
    else:
        df_scatter_site = spacex_df[spacex_df['Launch Site']==entered_site]
        df_scatter_site = df_scatter_site[df_scatter_site['Payload Mass (kg)'].between(payload_min, payload_max, inclusive='both')]
        fig = px.scatter(df_scatter_site,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        title=f'Correlation between Payload and Success for {entered_site}')
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server()
