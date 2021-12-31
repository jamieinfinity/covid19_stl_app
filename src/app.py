import datetime
import numpy as np
import pandas as pd
import altair as alt
import streamlit as st

nyt_county_url = 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv'
mo_counties = ['St. Louis city', 'St. Louis', 'Lincoln', 'Warren', 'Franklin', 'Jefferson', 'St. Charles']
il_counties = ['Monroe', 'St. Clair', 'Clinton', 'Madison', 'Jersey']


# functions
# @st.cache
def load_data():
    return pd.read_csv(nyt_county_url, parse_dates=['date'], dtype={'fips':'str'})

def stl_eda(df):
    mo = df[(df['county'].isin(mo_counties)) & (df['state']=='Missouri')]
    il = df[(df['county'].isin(il_counties)) & (df['state']=='Illinois')]
    stlmetro = pd.concat([mo,il]).copy().reset_index(drop=True)
    stlmetro_gb = stlmetro[['date', 'cases', 'deaths']].groupby('date').sum()
    stlmetro_gb['date'] = stlmetro_gb.index
    stlmetro_gb['new_cases_daily'] = stlmetro_gb.cases - stlmetro_gb.cases.shift(1)
    stlmetro_gb['new_cases_daily'] = stlmetro_gb.new_cases_daily.fillna(1)
    stlmetro_gb.loc[stlmetro_gb.new_cases_daily>5000, 'new_cases_daily'] = np.nan
    stlmetro_gb.loc[stlmetro_gb.date=='2021-03-08', 'new_cases_daily'] = np.nan
    stlmetro_gb.loc[stlmetro_gb.date=='2021-05-01', 'new_cases_daily'] = np.nan
    stlmetro_gb['new_cases_roll7d_mean'] = stlmetro_gb.rolling(window='7d', min_periods=4).new_cases_daily.mean().round(1)
    stlmetro_gb.loc[stlmetro_gb.new_cases_daily<0, 'new_cases_daily'] = np.nan
    return stlmetro_gb



# load data
nyt_full = load_data()
nyt_stl = stl_eda(nyt_full)


# create chart
date_domain = ["2020-03-01", "2022-3-1"]
date_domain = list(pd.to_datetime(date_domain))

c_pnt = alt.Chart(nyt_stl).mark_circle(point=True, color='#00C2E6', opacity=0.3, size=30).encode(
    x=alt.X('date', title='', scale=alt.Scale(domain=date_domain)),
    y=alt.Y('new_cases_daily', title='daily reported new cases'),
    tooltip=['date', alt.Tooltip('new_cases_daily', title='new cases')]
).properties(
    width=800,
    height=400
).interactive()

c_line = alt.Chart(nyt_stl).mark_line(color='#02A9C8', size=2).encode(
    x=alt.X('date'),
    y=alt.Y('new_cases_roll7d_mean'),
    tooltip=['date', alt.Tooltip('new_cases_roll7d_mean', title='rolling 7day avg')]
)

new_cases_chart = (c_pnt + c_line).configure_axis(
    labelFontSize=14,
    titleFontSize=14,
    titleColor='#555',
    labelColor='#555',
    titleFont='Verdana',
    labelFont='Verdana',
    titleFontWeight='normal'
)


# setup for the UI

title_text = 'COVID-19 Data for St. Louis Metro'
data_source_text = 'github.com/nytimes/covid-19-data'
metro_text = 'St. Louis Metro region comprises the following counties: '
mo_text = 'MO: {}'.format(', '.join(mo_counties)) 
il_text = 'IL: {}'.format(', '.join(il_counties))

title_html = "<div style='margin-left:0px; font-family:Avenir'> \
    <h2>{}</h2> \
    <br></div>".format(title_text)
footnote_html = "<div style='font-family:Avenir; font-size:small; color:#aaa'> \
<br> \
Data Source: <a href='https://{}' target='_blank'>{}</a> \
<br><br> \
{}{}; {} \
".format(data_source_text, data_source_text, metro_text, mo_text, il_text)

# render the UI

st.markdown(title_html, unsafe_allow_html=True)
#st.header(title_text)
st.text('')
st.write(new_cases_chart)
# st.text(data_source_text)
# st.text(metro_text)
# st.text(mo_text)
# st.text(il_text)
st.markdown(footnote_html, unsafe_allow_html=True)
