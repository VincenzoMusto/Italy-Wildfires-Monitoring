## Gender Gap page
import geopandas as gpd
import leafmap
#importing the libraries
import dash
from dash import dcc, html, callback, Output, Input
import plotly.express as px
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
from PIL import Image
import os
import plotly.graph_objects as go
import calendar
import json
import matplotlib.pyplot as plt
from datetime import datetime




#setting the path to call datasets and images 
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
dname = dname.replace("\\", "/")
os.chdir(dname)

#Creating page Gender Gap and linking to the main app
dash.register_page(__name__, name='Wildfires exploration') 





EFFIS_fires = gpd.read_file("dataset/EFFIS_2023.json")
ground_fires = gpd.read_file("dataset/fires_ground_areas_detected.geojson")
catchment_outline = gpd.read_file('dataset/calabria.geojson')
# Filter for specific region
EFFIS_fires = EFFIS_fires[EFFIS_fires['admlvl2'].isin(['Calabria'])]

# Define map center
center = (float(catchment_outline.centroid.y), float(catchment_outline.centroid.x))









map_path = "static/map.html"


# PIE CHART
merged_data = pd.read_csv("dataset/merged_dataset.csv")
# Summing total areas for EFFIS fires, ground fires, and overlaps across all provinces
total_effis_area = merged_data['EFFIS_area'].sum()
total_ground_area = merged_data['ground_area'].sum()
total_overlap_area = merged_data['overlapped_area'].sum()

# Calculate total area affected
total_area = total_effis_area + total_ground_area + total_overlap_area

# Calculate percentages for the pie chart and round to 2 decimal places
effis_percent = round((total_effis_area / total_area) * 100, 2)
ground_percent = round((total_ground_area / total_area) * 100, 2)
overlap_percent = round((total_overlap_area / total_area) * 100, 2)


# Create the pie chart using Plotly
labels = ['EFFIS Fires (Exclusive)', 'Ground Fires (Exclusive)', 'Overlapping Area']
sizes = [effis_percent, ground_percent, overlap_percent]
colors = ['#FFA500','blue','green']

fig = go.Figure(data=[go.Pie(labels=labels, values=sizes, marker_colors=colors, textinfo='label+percent', insidetextorientation='radial', hole=.3)])

# Update layout for the pie chart
fig.update_layout(
    title_text='Total Percentage of Fire-Affected Areas',
    showlegend=True,
    #annotations=[dict(text='Fire Data', x=0.5, y=0.5, font_size=20, showarrow=False)]
)





# LAND TYPE
land_types = ['broadleaved_forest_percent', 'coniferous_forest_percent', 'mixed_forest_percent', 
              'sclerophillous_vegetation_percent', 'transitional_vegetation_percent', 'other_natural_percent', 
              'agriculture_percent', 'artificial_percent', 'other_percent', 'natura2k_percent']

# Create a new dataframe to hold the total area burned per land type
land_area_totals = pd.DataFrame(index=land_types, columns=['total_area_burned'])

for land_type in land_types:
    # Calculate total area burned for each land type
    land_area_totals.loc[land_type, 'total_area_burned'] = (EFFIS_fires['area_ha'] * (EFFIS_fires[land_type] / 100)).sum()

# Convert index to a more readable form
land_area_totals.index = [x.replace('_percent', '').replace('_', ' ').title() for x in land_area_totals.index]
land_area_totals.reset_index(inplace=True)
land_area_totals.columns = ['Land Type', 'Total Area Burned (ha)']
# I want to change natura2k to Natura 2000
land_area_totals['Land Type'] = land_area_totals['Land Type'].replace('natura2k', 'Natura 2000')
# I want them with first letter capital
land_area_totals['Land Type'] = land_area_totals['Land Type'].str.title()

# Plotting the total area burned by land type using Plotly
land_type = px.bar(land_area_totals, y='Land Type', x='Total Area Burned (ha)', orientation='h', 
             title='Total Area Burned by Land Type', labels={'Total Area Burned (ha)': 'Total Area Burned (ha)'})
land_type.update_layout(yaxis={'categoryorder':'total ascending'}, xaxis_title="Total Area Burned (ha)", yaxis_title="Land Type")




# BOXPLOT
# Create the box plots
def remove_outliers(df, column):
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    return df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]

# Clean the data by removing outliers
effis_clean = remove_outliers(EFFIS_fires, 'area_ha')
ground_clean = remove_outliers(ground_fires, 'sup_totale')

# Create the box plots
boxplot = go.Figure()

# Add EFFIS Fires data
boxplot.add_trace(go.Box(y=effis_clean['area_ha'], name='EFFIS Fires', boxpoints=False, marker_color='#FFA500'))

# Add Ground Fires data
boxplot.add_trace(go.Box(y=ground_clean['sup_totale'], name='Ground Fires', boxpoints=False, marker_color='blue'))

# Update the layout to add titles and labels
boxplot.update_layout(
    title='Distribution of Burned Area',
    yaxis_title='Area in Hectares',
    xaxis=dict(
        title='Source',
        tickmode='array',
        tickvals=[0, 1],
        ticktext=['EFFIS Fires', 'Ground Fires']
    ),
    showlegend=False
)






# grouped barchart province comparison
merged_data_long = merged_data.melt(id_vars='province', value_vars=['EFFIS_area', 'ground_area', 'overlapped_area'],
                                    var_name='Detection Method', value_name='Total Area Affected (ha)')

# Update the labels for clarity
merged_data_long['Detection Method'] = merged_data_long['Detection Method'].map({
    'EFFIS_area': 'EFFIS Fires (Excluding Overlaps)',
    'ground_area': 'Ground Fires (Excluding Overlaps)',
    'overlapped_area': 'Overlapped Area'
})
# Define the custom colors
custom_colors = {
    'EFFIS Fires (Excluding Overlaps)': '#FFA500',
    'Ground Fires (Excluding Overlaps)': 'blue',
    'Overlapped Area': 'green'
}
# round the values to 0 decimal places
merged_data_long['Total Area Affected (ha)'] = merged_data_long['Total Area Affected (ha)'].round(0)
# Create the bar plot using Plotly Express
barchart_provinces = px.bar(merged_data_long, x='province', y='Total Area Affected (ha)', color='Detection Method',
             barmode='group', title='Comparison of Fire-Affected Area by Province and Detection Method', color_discrete_map=custom_colors)

# Update layout for a better visualization
barchart_provinces.update_layout(
    xaxis_title='Province',
    yaxis_title='Total Area Affected (ha)',
    legend_title="Detection Method",
    xaxis={'categoryorder':'total descending'}
)

# Update x-axis tick angle for better label visibility
barchart_provinces.update_xaxes(tickangle=45)



# MONTHLY GROUPED SUM
# Convert the dates to a suitable format
EFFIS_fires['initialdate'] = EFFIS_fires['initialdate'].str.slice(0, 10)
EFFIS_fires['initialdate'] = pd.to_datetime(EFFIS_fires['initialdate'])
ground_fires['data_event'] = pd.to_datetime(ground_fires['data_event'], format='%m/%d/%Y')

# Extract the month from the dates
EFFIS_fires['month'] = EFFIS_fires['initialdate'].dt.month
ground_fires['month'] = ground_fires['data_event'].dt.month
# Grouping data and summing areas
EFFIS_fires_monthly = EFFIS_fires.groupby('month')['area_ha'].sum().reset_index()
ground_fires_monthly = ground_fires.groupby('month')['sup_totale'].sum().reset_index()

# Convert month numbers to month names
months = [calendar.month_abbr[i] for i in range(1, 13)]
EFFIS_fires_monthly['month'] = EFFIS_fires_monthly['month'].map(lambda x: calendar.month_abbr[x])
ground_fires_monthly['month'] = ground_fires_monthly['month'].map(lambda x: calendar.month_abbr[x])

# Combine the data into a single DataFrame
combined_fires = pd.concat([
    pd.DataFrame({'Month': EFFIS_fires_monthly['month'], 'Area': EFFIS_fires_monthly['area_ha'], 'Type': 'EFFIS'}),
    pd.DataFrame({'Month': ground_fires_monthly['month'], 'Area': ground_fires_monthly['sup_totale'], 'Type': 'Ground'})
])

# Create the bar plot using Plotly Express
monthly_sum = px.bar(combined_fires, x='Month', y='Area', color='Type', barmode='group',
             title='Area Burned per Month', labels={'Area': 'Area in Hectares'})

# Update layout for better visualization
monthly_sum.update_layout(
    xaxis_title='Month',
    yaxis_title='Area in Hectares',
    legend_title="Fire Type",
    xaxis={'categoryorder': 'array', 'categoryarray': months}
)





# MONTHLY GROUPED COUNT
# Grouping data to count occurrences
EFFIS_fires_monthly_count = EFFIS_fires.groupby('month')['area_ha'].count().reset_index()
ground_fires_monthly_count = ground_fires.groupby('month')['sup_totale'].count().reset_index()

# Convert month numbers to month names
months = [calendar.month_abbr[i] for i in range(1, 13)]
EFFIS_fires_monthly_count['month'] = EFFIS_fires_monthly_count['month'].map(lambda x: calendar.month_abbr[x])
ground_fires_monthly_count['month'] = ground_fires_monthly_count['month'].map(lambda x: calendar.month_abbr[x])

# Combine the data into a single DataFrame
combined_fires_count = pd.concat([
    pd.DataFrame({'Month': EFFIS_fires_monthly_count['month'], 'Count': EFFIS_fires_monthly_count['area_ha'], 'Type': 'EFFIS'}),
    pd.DataFrame({'Month': ground_fires_monthly_count['month'], 'Count': ground_fires_monthly_count['sup_totale'], 'Type': 'Ground'})
])

# Define custom colors
custom_colors = {"EFFIS": "orange", "Ground": "blue"}

# Create the bar plot using Plotly Express
monthly_count = px.bar(combined_fires_count, x='Month', y='Count', color='Type', barmode='group',
             title='Number of Wildfires per Month', labels={'Count': 'Number of Wildfires'},
             color_discrete_map=custom_colors)

# Update layout for better visualization
monthly_count.update_layout(
    xaxis_title='Month',
    yaxis_title='Number of Wildfires',
    legend_title="Fire Type",
    xaxis={'categoryorder': 'array', 'categoryarray': months}
)








# Load your GeoDataFrame (assumed pre-processed as you described)
effis_only = gpd.read_file("dataset/only_EFFIS_detected.geojson")
effis_only = effis_only.sort_values(by='area_ha', ascending=False).head(5)
# round area_ha to 0 decimal places
effis_only['area_ha'] = effis_only['area_ha'].round(0)

# Create the 'fire_period' column
effis_only['fire_period'] = effis_only.apply(
    lambda row: row['admlvl5'] + ' ' + (row['initialdate'] + ', wildfire area of:' + str(row['area_ha']) + ' ha' if row['initialdate'] == row['finaldate'] else row['initialdate'] + ' - ' + row['finaldate'] + ', wildfire area of:' + str(row['area_ha']) + ' ha'),
    axis=1
)



map_paths = {
    'Motta San Giovanni 2023-07-19 - 2023-07-24, wildfire area of:1842.0 ha': "1",
    'Reggio di Calabria 2023-07-18 - 2023-07-21, wildfire area of:1101.0 ha': "2",
    'San Lorenzo 2023-07-20 - 2023-07-23, wildfire area of:589.0 ha': "3",
    'Reggio di Calabria 2023-07-22 - 2023-07-25, wildfire area of:522.0 ha': "4",
    'Santa Domenica Talao 2023-08-27 - 2023-08-28, wildfire area of:491.0 ha': "5",
    # Add more mappings as necessary
}


# I want a map_paths but with effis_only['fire_period'] as keys
#map_paths = effis_only.set_index('fire_period').to_dict(orient='index')























layout = dbc.Container([



    dbc.Row([
        dbc.Col([
            html.H4(children = 'Analysis of the 5 widest wildfires detected by EFFIS but not from the local detections in Calabria', 
                    style={'textAlign': 'left', "color" : "black", 'font-weight': 'bold'}),
            html.H6("The maps with the pre- and post-fire situations are displayed below (data from Sentinel-2), as well as the evolution of the selected polluting gas over time (data from Sentinel-5P).",
            )], width=12)]),

    html.Div(style={'height': '30px'}),  # Space


    dbc.Row([
        dbc.Col([
            html.H6("Use the slicer to select the wildfire event to analyse:",
            ),
            dcc.Dropdown(
        id='fire-period-dropdown',
        options=[{'label': period, 'value': period} for period in effis_only['fire_period']],
        value=effis_only['fire_period'].iloc[1]  # Default value set to first entry
    ),
    html.Div(id='display-selected-period'),
        ], width=12)
    ], align="center"),


    






    html.Div(style={'height':'10px'}),
    

    dbc.Row([
    dbc.Col([
        html.Iframe(id='map-iframe-pre', srcDoc=open('static/SENTINEL2/1/pre.html', 'r').read(), width='100%', height='600'),
    ], width=6),
    dbc.Col([
        html.Iframe(id='map-iframe-post', srcDoc=open('static/SENTINEL2/1/post.html', 'r').read(), width='100%', height='600'),
    ], width=6)
            ], align="center"),


    html.Div(style={'height':'30px'}),





    dbc.Row([
        dbc.Col([
            html.H5("Proof of Concept: This line plot shows the evolution of the selected polluting gas over time. The red dashed lines indicate the beginning and the end of the selected wildfire event. Missing data may be due to cloudy weather")
        ], width=12)
    ]),

    html.Div(style={'height':'10px'}),

    dbc.Row([
        dbc.Col([
            html.H6("Select the polluting gas to analyse:",
            ),
            dcc.Dropdown(
                id='gas-dropdown',
                options=[{'label': gas, 'value': gas} for gas in ['CO', 'NO2', 'O3', 'HCHO', 'SO2']],
                value='CO'  # Default value
            )    
        ], width=6),
        
    ]),


    
    html.Div(style={'height':'10px'}),



    dbc.Row([
        dbc.Col([
            dcc.Graph(id='line-plot')
        ], width=12)
    ]),
    
    




     
     html.Div(style={'height':'50px'}),

     dbc.Row([      
         dbc.Col([
             #Commenting the insights from the bar chart 
             html.H6(children="Data sources: EFFIS (https://forest-fire.emergency.copernicus.eu) and geoportale.incendiboschivi.it provided by the italian police forces",  
                 style={'textAlign': 'center'}),
             ])]
             ,className=' mb-4'),     
   
   
])

#Callback section

@callback(
    [Output('map-iframe-pre', 'srcDoc'), Output('map-iframe-post', 'srcDoc')],
    [Input('fire-period-dropdown', 'value')]
)
def update_maps(selected_period):
    map_path = map_paths[selected_period]
    with open(f"static/SENTINEL2/{map_path}/pre.html", 'r') as file:
        pre_map_html = file.read()
    with open(f"static/SENTINEL2/{map_path}/post.html", 'r') as file:
        post_map_html = file.read()
    return pre_map_html, post_map_html




@callback(
    Output('line-plot', 'figure'),
    [Input('gas-dropdown', 'value'),
     Input('fire-period-dropdown', 'value')]
)
def update_line_plot(selected_gas, selected_period):
    # Filter your data here based on the dropdowns
# Load the JSON file
    with open(f'static/SENTINEL5/{selected_gas}/{map_paths[selected_period]}.json') as f:
        data = json.load(f)

    # Prepare data for plotting
    dates = []
    values = []

    for date, value in data.items():
        dates.append(datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ'))
        values.append(value[0][0])

    # Create a DataFrame for plotting
    import pandas as pd
    df = pd.DataFrame({
        'Date': dates,
        'Value': values
    })

    # Fetch the initial and final dates from effis_only using map_paths
    index = int(map_paths[selected_period]) - 1  # Adjusting index as map_paths gives 1-based index

    # Assuming effis_only is indexed properly and contains the required columns
    initial_date = effis_only.iloc[index]['initialdate']
    final_date = effis_only.iloc[index]['finaldate']

    # Convert strings to datetime if they are not already datetime objects
    initial_date = pd.to_datetime(initial_date)
    final_date = pd.to_datetime(final_date)

    # Create the line plot using Plotly Express
    fig = px.line(df, x='Date', y='Value', title=f'{selected_gas} Levels Over Time',
                markers=True, line_shape='linear', labels={'Value': f'{selected_gas} Level'})

    # Add vertical lines for initial and final dates
    fig.add_vline(x=initial_date, line_width=3, line_dash="dash", line_color="red")
    fig.add_vline(x=final_date, line_width=3, line_dash="dash", line_color="red")
    # Formatting the plot
    fig.update_layout(
        xaxis_title='Date',
        yaxis_title=f'{selected_gas} Level in mol/m2',
        xaxis_tickformat='%Y-%m-%d',
        xaxis_tickangle=-45,
        template='plotly_white'
    )
    return fig