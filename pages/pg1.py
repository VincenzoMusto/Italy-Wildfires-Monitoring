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


#setting the path to call datasets and images 
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
dname = dname.replace("\\", "/")
os.chdir(dname)

#Creating page Gender Gap and linking to the main app
dash.register_page(__name__, path='/', name='Home') 





EFFIS_fires = gpd.read_file("dataset/EFFIS_2023.json")
EFFIS_fires = EFFIS_fires[EFFIS_fires['admlvl2'].isin(['Calabria'])]
# Deleting the specified columns
columns_to_delete = ['id', 'iso2', 'iso3', 'country', 'admlvl1', 'admlvl2', 'eu_area', 'noneu', 'updated', 'area_code']
EFFIS_fires = EFFIS_fires.drop(columns=columns_to_delete)

# Renaming the specified columns
columns_rename = {
    'admlvl3': 'City',
    'admlvl5': 'Location'
}
EFFIS_fires.rename(columns=columns_rename, inplace=True)

# Modifying 'Initialdate' and 'Finaldate' to keep only the date part
EFFIS_fires['initialdate'] = EFFIS_fires['initialdate'].str[:10]
EFFIS_fires['finaldate'] = EFFIS_fires['finaldate'].str[:10]



ground_fires = gpd.read_file("dataset/fires_ground_areas_detected.geojson")
ground_fires = ground_fires.drop(columns=['coorutmn', 'fid', 'coorutme', 'fuso'])

# Renaming the remaining columns to English
columns_translation = {
    'data_event': 'Event Date',
    'localita': 'Location',
    'anno': 'Year',
    'sup bosc': 'Forest Area (sq km)',
    'sup n bosc': 'Non-Forest Area (sq km)',
    'provincia': 'Province',
    'regione': 'Region',
    'sup totale': 'Total Area (sq km)',
    'comune': 'Municipality'
}

ground_fires.rename(columns=columns_translation, inplace=True)



catchment_outline = gpd.read_file('dataset/calabria.geojson')
# Filter for specific region


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
labels = ['EFFIS (Exclusive)', 'Local detections (Exclusive)', 'Overlapping Area']
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
    # Calculate total area burned for each land type and round to 0 decimal places
    land_area_totals.loc[land_type, 'total_area_burned'] = (EFFIS_fires['area_ha'] * (EFFIS_fires[land_type] / 100)).sum().round(0)

# Convert index to a more readable form
land_area_totals.index = [x.replace('_percent', '').replace('_', ' ').title() for x in land_area_totals.index]
land_area_totals.reset_index(inplace=True)
land_area_totals.columns = ['Land Type', 'Total Area Burnt (ha)']
# I want to change natura2k to Natura 2000
land_area_totals['Land Type'] = land_area_totals['Land Type'].replace('natura2k', 'Natura 2000')
land_area_totals['Land Type'] = land_area_totals['Land Type'].str.replace('Natura2K', 'Natura 2000')
# I want them with first letter capital
land_area_totals['Land Type'] = land_area_totals['Land Type'].str.title()

# Plotting the total area burned by land type using Plotly
land_type = px.bar(land_area_totals, y='Land Type', x='Total Area Burnt (ha)', orientation='h', 
             title='Total Area Burnt by Land Type', labels={'Total Area Burnt (ha)': 'Total Area Burnt (ha)'})
land_type.update_layout(yaxis={'categoryorder':'total ascending'}, xaxis_title="Total Area Burnt (ha)", yaxis_title="Land Type")




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
boxplot.add_trace(go.Box(y=effis_clean['area_ha'], name='EFFIS', boxpoints=False, marker_color='#FFA500'))

# Add Ground Fires data
boxplot.add_trace(go.Box(y=ground_clean['sup_totale'], name='Local detections', boxpoints=False, marker_color='blue'))

# Update the layout to add titles and labels
boxplot.update_layout(
    title='Distribution of Burnt Area',
    yaxis_title='Area in Hectares',
    xaxis=dict(
        title='Source',
        tickmode='array',
        tickvals=[0, 1],
        ticktext=['EFFIS', 'Local detections']
    ),
    showlegend=False
)






# grouped barchart province comparison
merged_data_long = merged_data.melt(id_vars='province', value_vars=['EFFIS_area', 'ground_area', 'overlapped_area'],
                                    var_name='Detection Method', value_name='Total Area Affected (ha)')

# Update the labels for clarity
merged_data_long['Detection Method'] = merged_data_long['Detection Method'].map({
    'EFFIS_area': 'EFFIS (Exclusive)',
    'ground_area': 'Local detections (Exclusive)',
    'overlapped_area': 'Both methods'
})
# Define the custom colors
custom_colors = {
    'EFFIS (Exclusive)': '#FFA500',
    'Local detections (Exclusive)': 'blue',
    'Both methods': 'green'
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
ground_fires['Event Date'] = pd.to_datetime(ground_fires['Event Date'], format='%m/%d/%Y')

# Extract the month from the dates
EFFIS_fires['month'] = EFFIS_fires['initialdate'].dt.month
ground_fires['month'] = ground_fires['Event Date'].dt.month
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
    pd.DataFrame({'Month': ground_fires_monthly['month'], 'Area': ground_fires_monthly['sup_totale'], 'Type': 'Local detections'})
])
# Define custom colors
custom_colors = {"EFFIS": "orange", "Local detections": "blue"}
# Create the bar plot using Plotly Express
monthly_sum = px.bar(combined_fires, x='Month', y='Area', color='Type', barmode='group',
             title='Area Burnt per Month', labels={'Area': 'Area in Hectares'}, color_discrete_map=custom_colors)

# Update layout for better visualization
monthly_sum.update_layout(
    xaxis_title='Month',
    yaxis_title='Area in Hectares',
    legend_title="Detection Method",
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
    pd.DataFrame({'Month': ground_fires_monthly_count['month'], 'Count': ground_fires_monthly_count['sup_totale'], 'Type': 'Local detections'})
])



# Create the bar plot using Plotly Express
monthly_count = px.bar(combined_fires_count, x='Month', y='Count', color='Type', barmode='group',
             title='Number of Wildfires per Month', labels={'Count': 'Number of Wildfires'},
             color_discrete_map=custom_colors)

# Update layout for better visualization
monthly_count.update_layout(
    xaxis_title='Month',
    yaxis_title='Number of Wildfires',
    legend_title="Detection Method",
    xaxis={'categoryorder': 'array', 'categoryarray': months}
)





















layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H4('Wildfires monitoring in Calabria region, Italy',
                    style={'textAlign': 'left', "color": "black", 'font-weight': 'bold'}),
            #html.H6("Data sources: EFFIS (European Forest Fire Information System) and geoportale.incendiboschivi.it provided by the italian police forces",)
        ], width=12)
    ], align="center"),




    dbc.Row([
        dbc.Col([
            html.Iframe(srcDoc=open(map_path, 'r').read(), width='100%', height='600')  # Adjust height and width as needed
        ], width=8),
        dbc.Col([
            html.H6("From this interactive map it is possible to see the areas affected by wildfires in the Calabria region, Italy. The map shows the areas affected by wildfires which have beendetected by the European Forest Fire Information System (EFFIS) and the local detections made by the Italian police forces. The EFFIS data are represented in orange, while the local detection in blue. These data regard the year 2023.",
                    style={'textAlign': 'center', "color": "black"})
        ], width=4)
    ], align="center"),
    html.Div(style={'height': '30px'}),  # Space


#Second paragraph
    dbc.Row([
        dbc.Col([
            html.H4(children = 'Explorative data analysis', 
                    style={'textAlign': 'left', "color" : "black", 'font-weight': 'bold'}),
            #html.H6("Change the term and see how the percentage of women in the European Parliament changes across countries and through the different political orientations.")
            ], width=12)]),


    html.Div(style={'height':'20px'}),
    

    dbc.Row([
        dbc.Col([        
            
            #define the map 
            dcc.Graph(id = "land_type", figure=land_type),
            html.Div(style={'height':'30px'}),
            #commenting the map
            html.H6(children = "Burnt areas detected from the satellites on the EFFIS platform are also classified on the typology of land which has been damaged. The areas are classified on various types of vegetation and forests. Among all the categories, it can be seen that the “Agriculture” areas are by far the most sensible to wildfires, followed by the “Transitional Vegetation”. Another interesting aspect is that “Natura 2000” areas, even if they are areas of interest with particular protections, are heavily impacted by wildfires.",
                    style={'textAlign': 'justify'}),
        ],width=6),

        dbc.Col([
            #defining the stacked bar chart
            dcc.Graph(id = "boxplot", figure=boxplot),
            html.Div(style={'height':'30px'}),
            #commenting the insights ftom the bar chart
            html.H6(children = "By looking at the median, the quartiles and the maximum of the botplots, the satellites-detected wildfires present always a wider area, compared with the local detections. It can be therefore assumed that the local detections are underestimating the area of the wildfires. Without the use of satellites images, drones or other technologies, the local detections should be considered more as an estimation, rather than measurements.",
                    style={'textAlign': 'justify'}),
        ],width=6),
        
    ]),


    
    html.Div(style={'height':'50px'}),




dbc.Row([
        dbc.Col([        
            
            #define the map 
            dcc.Graph(id = "monthly_sum", figure=monthly_sum),
            html.Div(style={'height':'30px'}),
            #commenting the map
            html.H6(children = "As both datasets cover the entire year 2023, it can be useful to understand in which months there are more wildfires and more damaged areas. As it can be seen from the barplot above, it can be understood that the months between July and October are the ones with the highest number of detected wildfires, with an interesting detail about the fact that the month of June has almost no wildfires phenomena.",
                    style={'textAlign': 'justify'}),
        ],width=6),

        dbc.Col([
            #defining the stacked bar chart
            dcc.Graph(id = "barchart_provinces", figure=monthly_count),
            html.Div(style={'height':'30px'}),
            #commenting the insights ftom the bar chart
            html.H6(children = "In general, wildfires are damaging the environment almost only between July and September, with a huge spike in the month of July, especially in the case of burnt areas detected by the EFFIS systems.",
                    style={'textAlign': 'justify'}),
        ],width=6),
        
    ]),
    

    html.Div(style={'height':'60px'}), 







    
    dbc.Row([
        dbc.Col([        
            
            #define the map 
            dcc.Graph(id = "fig", figure=fig),
            html.Div(style={'height':'30px'}),
            #commenting the map
            html.H6(children = "Wildfire areas detected by the local measurements only cover about the 40% of the burnt areas. In particular, the 24.9% of the areas are detected by both the measurements, while the 15.7% is only detected by local measurements. In general, the smallest wildfires may be detected only from local detections as the satellites’ resolution is not able to catch small areas. The 59.4% of wildfire damaged areas detected only by satellites are an interesting starting point to understand which wildfires were not reported by local police forces and administrations.",
                    style={'textAlign': 'justify'}),
        ],width=6),

        dbc.Col([
            #defining the stacked bar chart
            dcc.Graph(id = "barchart_provinces", figure=barchart_provinces),
            html.Div(style={'height':'30px'}),
            #commenting the insights ftom the bar chart
            html.H6(children = "Wildfires phenomena are a prerogative of the “Reggio di Calabria” province. The fact that over 8.000 hectares of burnt areas are detected only from satellites implies that the local detections activities present some kind of issues. This huge difference may indicate that police forces may be understaffed in that area, or the reporting system is not efficiently implemented. Policy makers can adopt policies to improve this situation thanks to this insight. Moreover, these areas shoulb be taken in consideration during decision making processes about the reforest process or the recovery of the area in general.",
                    style={'textAlign': 'justify'}),
        ],width=6),
        
    ]),
    

    html.Div(style={'height':'60px'}), 








     dbc.Row([      
         dbc.Col([
             #Commenting the insights from the bar chart 
             html.H6(children="Data sources: EFFIS (https://forest-fire.emergency.copernicus.eu) and geoportale.incendiboschivi.it provided by the italian police forces",  
                 style={'textAlign': 'center'}),
             ])]
             ,className=' mb-4'),     
   
   
])

