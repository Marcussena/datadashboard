import pandas as pd
import plotly.graph_objs as go

# Use this file to read in your data and prepare the plotly visualizations. The path to the data files are in
# `data/file_name.csv`

def clean_data(dataset, keepcols = []):
    """Clean Covid 19 vaccination data for a visualizaiton dashboard

    Keeps only the columns of interest from the dataset

    Args:
        dataset (str): name of the csv data file
        keepcols (list): list with the desired columns from the original dataset

    Returns:
        clean_df: cleaned dataframe

    """  
    df = pd.read_csv(dataset)
    
    world_vax = df.groupby(['iso_code'])[keepcols].max()
    world_vax = world_vax.reset_index(drop=True)
    world_vax['people_partly_vaccinated'] = world_vax['people_vaccinated'] - world_vax['people_fully_vaccinated']
    world_vax = world_vax.sort_values(by='people_vaccinated', ascending = False)
    world_vax = world_vax[world_vax['continent'].isna()==False]
                         
    return world_vax

def vax_per_continent(data, continent = 'South America'):
    '''
    Function to plot a map of the vaccination situation in a desired continent
    
    Inputs:
    data - pandas dataframe with covid 19 data
    continent - continent from which the data will be plotted
    
    Output:
    fig_map - plotly figure with the desired data 
    
    '''
    cols = ['iso_code','continent','location','people_vaccinated', 'people_fully_vaccinated','people_vaccinated_per_hundred','people_fully_vaccinated_per_hundred']
    world_vax = data.groupby(['iso_code'])[cols].max()
    world_vax = world_vax.reset_index(drop=True)
    world_vax['people_partly_vaccinated'] = world_vax['people_vaccinated'] - world_vax['people_fully_vaccinated']
    world_vax = world_vax.sort_values(by='people_vaccinated', ascending = False)
    world_vax = world_vax[world_vax['continent'].isna()==False]
    cont_vax = world_vax[world_vax['continent']==continent]
    
    
    map_data = dict(
    type = 'choropleth',
    colorscale = 'Greens',
    locations = cont_vax['location'],
    locationmode = "country names",
    z = cont_vax['people_fully_vaccinated_per_hundred'],
    text = cont_vax['location'],
    colorbar = {'title' : 'number of doses' }
    )
    
    layout = dict(title = 'People fully vaccinated per hundred in {}'.format(continent),
              geo = dict(projection = {'type':'mercator'})
                 )
    
    fig_map = go.Figure(data = [map_data], layout = layout)
    fig_map.update_geos(
    visible=False, resolution=50, scope=continent.lower(),
    showcountries=True, countrycolor="Black",
    showsubunits=True, subunitcolor="Blue"
    )
    
    
    return fig_map
def vax_time_series(countries = [],dataset= pd.DataFrame()):
    """
    Function that returns a graph of the evolution of vaccinations over time for a list of countries

    Inputs:
    countries (list): list of countries
    dataset (DataFrame): dataframe with vaccination data 

    Outputs:
    graph: list with the charts corresponding to each country
    layout: layout with the settings of the visualization

    """
    graph = []
    for country in countries:
        country_vax = dataset[dataset['location']==country][['iso_code','date','new_vaccinations_per_hundred']]
        country_vax = country_vax[country_vax['new_vaccinations_per_hundred'].isna() == False]
    
        x_data = list(country_vax.date)
        y_data = list(country_vax.new_vaccinations_per_hundred)
    
        graph.append(go.Scatter(
            x = x_data,
            y = y_data,
            mode = 'lines',
            line=dict(width=1.0),
            connectgaps = True,
            name = country_vax.iso_code.iloc[0]
            )
            )

    layout = go.Layout(title = 'vaccination evolution',
                            xaxis = dict(title = 'Date'),
                            yaxis = dict(title = 'number of vaccines applied'),
                            showlegend = True
                            )

    return graph, layout

def return_figures():
    """Creates four plotly visualizations

    Args:
        None

    Returns:
        list (dict): list containing the four plotly visualizations

    """

    # first chart plots arable land from 1990 to 2015 in top 10 economies 
    # as a line chart
    
    path = 'data/owid-covid-data.csv'
    cols = ['iso_code','continent','location','people_vaccinated', 'people_fully_vaccinated','people_vaccinated_per_hundred','people_fully_vaccinated_per_hundred']
    world_vax = clean_data(path, cols)
    graph_one = []    
    graph_one.append(
      dict(
          type = 'choropleth',
          colorscale = 'Greens',
          locations = world_vax['location'],
          locationmode = "country names",
          z = world_vax['people_vaccinated_per_hundred'],
          text = world_vax['location'],
          colorbar = {'title' : 'Doses'},
          reversescale=True
          )
    )

    layout_one = dict(title = 'People Vaccinated against COVID-19 in the world',
                      geo = dict(projection = {'type':'natural earth'})
                      )

# second chart plots ararble land for 2015 as a bar chart    
    graph_two = []
    trace1 = go.Bar(
    x = list(world_vax.head(10).location),
    y = list(world_vax.head(10)['people_partly_vaccinated']),
    name = 'partly'
    )
    
    trace2 = go.Bar(
    x = list(world_vax.head(10).location),
    y = list(world_vax.head(10)['people_fully_vaccinated']),
    name = 'fully'
    )
    
    graph_two.append(trace1)
    graph_two.append(trace2)
    
    layout_two = go.Layout(
    title = 'Number of people vaccinated against COVID-19', 
    xaxis = dict(title = 'Country'),
    yaxis = dict(title = 'number of doses'),
    barmode = 'stack'
    )
    
# third chart plots percent of population that is rural from 1990 to 2015
    owid = pd.read_csv(path)
    owid['new_vaccinations_per_hundred'] = (owid['new_vaccinations']/owid['population'])*100
    bra_vax = owid[owid['iso_code']=='BRA'][['date','new_vaccinations']]
    bra_vax = bra_vax[bra_vax['new_vaccinations'].isna() == False]
    
    x_data = list(bra_vax.date)
    y_data = list(bra_vax.new_vaccinations)
    
    graph_three = []
    graph_three.append(
      go.Bar(x = x_data,
             y = y_data
             )
      )

    layout_three = go.Layout(title = 'Vaccination in Brazil', 
                             xaxis = dict(title = 'Date'),
                             yaxis = dict(title = 'number of vaccines applied')
                             )
    
# fourth chart shows rural population vs arable land

    fig_four = vax_per_continent(owid,'South America')

# fifth chart shows the evolution of the vaccination per country
    countries = ['India', 'United States', 'Russia', 'Brazil', 'Mexico', 'Germany', 'Turkey']
    graph_five, layout_five = vax_time_series(countries, owid)

    # append all charts to the figures list
    figures = []
    figures.append(dict(data=graph_one, layout=layout_one))
    figures.append(dict(data=graph_two, layout=layout_two))
    figures.append(dict(data=graph_three, layout=layout_three))
    figures.append(fig_four)
    figures.append(dict(data = graph_five, layout = layout_five))

    return figures
