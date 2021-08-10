import pandas as pd
import numpy as np
import plotly.graph_objs as go
import plotly.colors
from collections import OrderedDict
import requests


# default list of all countries of interest
country_default = OrderedDict(
    [
        ("Canada", "CAN"),
        ("United States", "USA"),
        ("Brazil", "BRA"),
        ("France", "FRA"),
        ("India", "IND"),
        ("Italy", "ITA"),
        ("Germany", "DEU"),
        ("United Kingdom", "GBR"),
        ("China", "CHN"),
        ("Japan", "JPN"),
    ]
)

# World Bank indicators of interest for pulling data
indicators_default = [
    "EG.USE.ELEC.KH.PC",  # Electric power consumption (kWh per capita)
    "EG.FEC.RNEW.ZS",  # Renewable energy consumption (% of total final energy consumption)
    "EG.USE.PCAP.KG.OE",  # Energy use (kg of oil equivalent per capita)
    "EN.ATM.GHGT.KT.CE",  # Total greenhouse gas emissions (kt of CO2 equivalent)
]


def return_figures(countries=country_default, indicators=indicators_default):
    """Creates four plotly visualizations using the World Bank API

    # Example of the World Bank API endpoint:
    # arable land for the United States and Brazil from 1990 to 2015
    # http://api.worldbank.org/v2/countries/usa;bra/indicators/AG.LND.ARBL.HA?date=1990:2015&per_page=1000&format=json

      Args:
          countries (OrderedDict): list of countries for filtering the data

      Returns:
          list (dict): list containing the four plotly visualizations

    """

    # prepare filter data for World Bank API
    # the API uses ISO-3 country codes separated by ;
    country_filter = ";".join([c.lower() for c in list(countries.values())])

    # stores the data frames with the indicator data of interest
    data_frames = []
    # url endpoints for the World Bank API
    urls = []

    # pull data from World Bank API and clean the resulting json
    # results stored in data_frames variable
    for indicator in indicators:
        url = (
            "http://api.worldbank.org/v2/country/"
            + country_filter
            + "/indicator/"
            + indicator
            + "?date=1990:2015&per_page=1000&format=json"
        )
        urls.append(url)

        try:
            resp = requests.get(url)
            data = resp.json()[1]
        except:
            print(f"could not load data for {indicator}")

        for value in data:
            value["indicator"] = value["indicator"]["value"]
            value["country"] = value["country"]["value"]

        data_frames.append(data)

    # first chart plots Electric power consumption (kWh per capita) from 1990 to 2015
    # in top 10 economies as a line chart
    graph_one = []
    df_one = pd.DataFrame(data_frames[0])

    # filter and sort values for the visualization
    # filtering plots the countries in decreasing order by their values
    df_one = df_one[
        df_one["date"].isin(["1990", "1995", "2000", "2005", "2010", "2014"])
    ]
    df_one.sort_values("date", inplace=True)

    # this  country list is re-used by all the charts to ensure legends have the same
    # order and color
    countrylist = df_one.country.unique().tolist()

    for country in countrylist:
        x_val = df_one[df_one["country"] == country].date.tolist()
        y_val = df_one[df_one["country"] == country].value.tolist()
        graph_one.append(
            go.Scatter(x=x_val, y=y_val, mode="lines+markers", name=country)
        )

    layout_one = dict(
        title="Electric power consumption 1990 to 2015<br>(kWh per capita)",
        xaxis=dict(title="Year"),
        yaxis=dict(title="KWh (Thousand)"),
    )

    # second chart plots Renewable energy consumption (% of total final energy consumption)
    # from 1990 to 2015 as a line chart
    graph_two = []
    df_two = pd.DataFrame(data_frames[1])
    df_two = df_two[
        df_two["date"].isin(["1990", "1995", "2000", "2005", "2010", "2015"])
    ]
    df_two.sort_values("date", inplace=True)

    for country in countrylist:
        x_val = df_two[df_two["country"] == country].date.tolist()
        y_val = df_two[df_two["country"] == country].value.tolist()
        graph_two.append(go.Bar(x=x_val, y=y_val, name=country))

    layout_two = dict(
        barmode="stack",
        title="% Renewable energy consumption 1990 to 2015",
        xaxis=dict(
            title="Year",
        ),
        yaxis=dict(title="% of total final energy"),
    )

    # third chart plots Energy use (kg of oil equivalent per capita) from 1990 to 2015
    graph_three = []
    df_three = pd.DataFrame(data_frames[1])
    df_three = df_three[
        df_three["date"].isin(["1990", "1995", "2000", "2005", "2010", "2015"])
    ]
    df_three.sort_values("date", inplace=True)

    for country in countrylist:
        x_val = df_three[df_three["country"] == country].date.tolist()
        y_val = df_three[df_three["country"] == country].value.tolist()
        graph_three.append(
            go.Scatter(x=x_val, y=y_val, mode="lines+markers", name=country)
        )

    layout_three = dict(
        title="Energy use <br> (kg of oil equivalent per capita)",
        xaxis=dict(title="Year"),
        yaxis=dict(title="Energy (Kg of oil)"),
    )

    # fourth chart shows Total greenhouse gas emissions (kt of CO2 equivalent)
    graph_four = []
    df_four = pd.DataFrame(data_frames[3])
    df_four = df_four[
        df_four["date"].isin(["1990", "1995", "2000", "2005", "2010", "2015"])
    ]
    df_four.sort_values("date", inplace=True)

    for country in countrylist:
        x_val = df_four[df_four["country"] == country].date.tolist()
        y_val = df_four[df_four["country"] == country].value.tolist()
        graph_four.append(go.Bar(x=x_val, y=y_val, name=country))

    layout_four = dict(
        barmode="stack",
        title="Total greenhouse gas emissions 1990-2015<br>(kt of CO2 equivalent)",
        xaxis=dict(
            title="Year",
        ),
        yaxis=dict(title="CO2 equivalents (kilo tonnes)"),
    )

    # append all charts
    figures = []
    figures.append(dict(data=graph_one, layout=layout_one))
    figures.append(dict(data=graph_two, layout=layout_two))
    figures.append(dict(data=graph_three, layout=layout_three))
    figures.append(dict(data=graph_four, layout=layout_four))

    return figures
