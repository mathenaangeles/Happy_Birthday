import streamlit as st
import plotly.express as px
import pandas as pd
import json
import os

st.set_page_config(
    page_title="Happy Birthday",
    page_icon=":birthday:",
)

st.write("# :speech_balloon: Instagram")
st.write("## :date: `June 14, 2023 - May 20, 2024`")

df = pd.DataFrame()
for file in os.listdir("./data/instagram"):
    if file.endswith(".json"):
        with open(f'./data/instagram/{file}') as json_file:
            messages_json = json.load(json_file)
            messages_df = pd.DataFrame(messages_json['messages'])
            df = pd.concat([df, messages_df])
df.drop(["is_geoblocked_for_viewer"], axis=1, inplace= True)
df['timestamp_ms'] = pd.to_datetime(df['timestamp_ms'], unit='ms')
df['length'] = df['content'].str.len()
df = df.sort_values(by='timestamp_ms')
st.write(df.head(5))

st.write("## :pie: I only have pies for you.")
st.write(":violet[Mathena] sends longer messages. :green[Lewis] send more messages.")

length_pie = df.groupby(['sender_name'])['length'].mean()
length_pie_df = pd.DataFrame({'sender_name': length_pie.index, 'length': length_pie.values}) 
st.write('##### Our messages are about :blue[34 characters] long on average.')
length_fig = px.pie(length_pie_df, values='length', names='sender_name')
st.plotly_chart(length_fig)
count_pie = df['sender_name'].value_counts()
count_pie_df = pd.DataFrame({'sender_name': count_pie.index, 'count': count_pie.values}) 
st.write('##### We sent each other :blue[96,047 messages].')
count_fig = px.pie(count_pie_df, values='count', names='sender_name')
st.plotly_chart(count_fig)
