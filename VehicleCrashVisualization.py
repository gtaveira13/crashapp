"""
Name: Gabriel Taveira
CS230: Section 6
Data: Vehicle Crashes in MA 2017
Description: This program is an interactive web application built with Streamlit,
designed to visualize and analyze motor vehicle crash data in Massachusetts for the year 2017.
It provides users with a variety of visualization options, including line graphs,
bar plots, pie charts, and maps.
"""

import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pydeck as pdk


monthsList = ['January', 'February', 'March', 'April',
              'May', 'June', 'July', 'August', 'September',
              'October', 'November', 'December']


def loading_data(filepath):
    dfCrashes = pd.read_csv(filepath, low_memory=False)
    dfCrashes['CRASH_DATE'] = pd.to_datetime(dfCrashes['CRASH_DATE'])
    dfCrashes['Month'] = dfCrashes['CRASH_DATE'].dt.month
    dfCrashes = dfCrashes.dropna(subset=['LAT', 'LON'])
    return dfCrashes


def lineplot(dfCrashes, show_grid=True):
    MonthlyCrashes = dfCrashes.groupby('Month').size().reset_index(name='Crashes')
    selectedMonth = st.slider('Select a month', 1, 12, 1)
    selectedMonthName = monthsList[selectedMonth - 1]
    selectedMonthCrashes = MonthlyCrashes[MonthlyCrashes['Month'] == selectedMonth]['Crashes'].iloc[0]
    st.write(f"Total crashes in {selectedMonthName}: {selectedMonthCrashes}")
    plt.figure(figsize=(8, 6))
    plt.plot(MonthlyCrashes['Month'], MonthlyCrashes['Crashes'], marker='x')
    plt.scatter(selectedMonth, selectedMonthCrashes, color='red')
    plt.title('Crash Volume throughout 2017')
    plt.xlabel('Months')
    plt.ylabel('Number of Crashes')
    plt.xticks(ticks=range(1, 13), labels=monthsList, rotation=45)
    plt.grid(show_grid)
    st.pyplot(plt)


def barplot(dfCrashes):
    monthlyData = dfCrashes.groupby('Month').size().reset_index(name='Crashes')
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = plt.cm.plasma(np.linspace(0, 1, 12))
    bars = ax.bar(monthlyData['Month'], monthlyData['Crashes'], color=colors)
    ax.set_title('Monthly Distribution of Vehicle Crashes', fontsize=16)
    ax.set_xticks(monthlyData['Month'])
    ax.set_xticklabels(monthsList, rotation=45, ha="right", fontsize=10)
    ax.set_xlabel('Month', fontsize=12)
    ax.set_ylabel('Number of Crashes', fontsize=12)
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, yval + 5, int(yval), ha='center', va='bottom', fontsize=10)
    st.pyplot(fig)


def piechart(data, column, title):
    countData = data[column].value_counts()
    percentData = (countData / countData.sum()) * 100
    threshold = 2.5
    smallCategories = percentData[percentData < threshold].index
    countData['Other'] = countData.loc[smallCategories].sum()
    countData = countData.drop(smallCategories)
    fig, ax = plt.subplots()
    # Explode the smallest pie pieces to improve label visibility
    explode = [0.1 if value < threshold else 0 for value in countData]
    texts, wedges, autotexts = ax.pie(countData, labels=countData.index, autopct='%1.1f%%', startangle=90, explode=explode,  pctdistance=0.85)
    plt.setp(autotexts, size=7, weight="bold")
    ax.axis('equal')
    plt.legend(title='Categories', loc='center left', bbox_to_anchor=(1.2, 0.5))
    plt.title(title)
    st.pyplot(fig)


def map_display(dfCrashes):
    # Defining the layer for the geo-map
    layer = pdk.Layer(
        'ScatterplotLayer',     # Scatter plot layer
        dfCrashes,              # DataFrame containing data
        get_position=['LON', 'LAT'],  # Longitude and Latitude columns
        get_color='[160, 30, 0, 160]',  # Color of markers
        get_radius=75,          # Radius of markers
    )
    # Set the view for the geo-map
    view_state = pdk.ViewState(
        latitude=dfCrashes['LAT'].mean(),
        longitude=dfCrashes['LON'].mean(),
        zoom=11,
        pitch=50,)

    # Render the geo-map
    st.pydeck_chart(pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip={"text": "{CRASH_DATE}\n{CRASH_SEVERITY_DESCR}"},
    ))




def crashStats(dfCrashes):
    monthlyData = dfCrashes.groupby('Month').size().reset_index(name='Crashes')
    totalCrashes = monthlyData['Crashes'].sum()
    maxCrashes = monthlyData['Crashes'].max()
    minCrashes = monthlyData['Crashes'].min()
    return totalCrashes, maxCrashes, minCrashes


# Streamlit Layout
st.title('Vehicle Crash Data in MA throughout 2017')
dfCrashes = loading_data('2017_Crashes_10000_sample.csv')
st.button('Press if you obtained any insight into vehicle crashes in MA during 2017!')

st.image("C:\\Users\\tavei\\OneDrive - Bentley University\\Spring 2024\\CS 230\\FictionalCarCrash.webp")
st.video('https://www.youtube.com/watch?v=2BS_pas7EwM')
st.subheader('This serves as a reminder to be alert and drive carefully. '
             'These tests are not too convincing')


view_options = st.selectbox('Choose the data view', ['Bar Plot', 'Pie Chart', 'Line Graph', 'Accident Map'])
if view_options == 'Bar Plot':
    barplot(dfCrashes)
    st.write('The distribution is relatively uniform but we can see that '
             'December and October contained the highest crash totals.'
             ' We also see that in the beginning of summer,'
             ' the crash total were elevated compared to the Spring months.')
elif view_options == 'Pie Chart':
    piechart_option = st.selectbox('Select detail view', ['By County', 'By Collision Type'])
    if piechart_option == 'By County':
        piechart(dfCrashes, 'CNTY_NAME', 'Accidents by County')
        st.write('The Middlesex county (where I am from) is leading with 22.4% of total crashes in 2017.')
    else:
        piechart(dfCrashes, 'MANR_COLL_DESCR', 'Accidents by Collision Type')
        st.write('Rear-end, angle, and single vehicle crashes were the most common'
                 ' collisions from this dataset in 2017.')
elif view_options == 'Line Graph':
    lineplot(dfCrashes)
    st.write('As we can see, October and December had the sharpest increases in crashes in 2017.')
elif view_options == 'Accident Map':
    map_display(dfCrashes)
    st.write('The 3-D map shows an interesting but obvious trend, the number of red dots, '
             'which are depicted as crash data points, increases. ')
