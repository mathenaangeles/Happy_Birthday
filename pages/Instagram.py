import streamlit as st
import plotly.express as px
import pandas as pd
import json
import os
from collections import Counter
import matplotlib.pyplot as plt


st.set_page_config(
    page_title="Happy Birthday",
    page_icon=":birthday:",
)

st.write("# :speech_balloon: Instagram")

files = st.file_uploader("Upload your :red[Instagram messages] as JSON files.", type='json', accept_multiple_files=True)

for file in files:
 with open(os.path.join("./data/instagram",file.name),"wb") as instagram_file:
     instagram_file.write(file.getbuffer())
     instagram_file.close()

df = pd.DataFrame()
for file in os.listdir("./data/instagram"):
    if file.endswith(".json"):
        with open(f'./data/instagram/{file}',encoding="latin-1") as json_file:
            json_file = json_file
            messages_json = json.load(json_file)
            messages_df = pd.DataFrame(messages_json['messages'])
            df = pd.concat([df, messages_df])


if not df.empty:
    df.drop(["is_geoblocked_for_viewer"], axis=1, inplace=True)
    df['timestamp_ms'] = pd.to_datetime(df['timestamp_ms'], unit='ms')
    df['content'] = df['content'].str.encode('latin-1').str.decode('utf-8')
    if 'call_duration' in df:
        df['call_duration'] = df['call_duration'].fillna(0)
    df['length'] = df['content'].str.len()
    df = df.sort_values(by='timestamp_ms')

    min_date = "`" + str(df.iloc[0]['timestamp_ms'])[0:10] 
    max_date =  str(df.iloc[-1]['timestamp_ms'])[0:10] + "`"

    st.write("## :date:", min_date, "-", max_date)

    def highlight(sender_name, color):
        return ":"+color+"["+str(sender_name)+"]"

    st.write("## :pie: I only have pies for you...")

    length_pie = df.groupby(['sender_name'])['length'].mean()
    length_pie_df = pd.DataFrame({'sender_name': length_pie.index, 'length': length_pie.values}) 
    length_fig = px.pie(length_pie_df, values='length', names='sender_name')

    number_pie = df['sender_name'].value_counts()
    number_pie_df = pd.DataFrame({'sender_name': number_pie.index, 'number': number_pie.values}) 
    number_fig = px.pie(number_pie_df, values='number', names='sender_name')

    length_sender = length_pie_df.at[length_pie_df.length.idxmax(),'sender_name']
    number_sender = number_pie_df.at[number_pie_df.number.idxmax(),'sender_name']
    st.write(highlight(length_sender, "green"), "sends longer messages. ", highlight(number_sender,"green"), " sends more messages.")

    average_length = int(length_pie_df.loc[:, 'length'].mean())
    st.write("##### Our messages are about", highlight(average_length,"blue"), " characters long.")
    st.plotly_chart(length_fig)

    total_messages = number_pie_df['number'].sum()
    st.write("##### We sent each other", highlight(total_messages,"blue") +" messages in total.")
    st.plotly_chart(number_fig)

    st.write("## :heart_on_fire: Hey, hot stuff...")

    df['year'] = pd.DatetimeIndex(df.timestamp_ms).year
    df['month'] = pd.DatetimeIndex(df.timestamp_ms).month
    df['day'] = pd.DatetimeIndex(df.timestamp_ms).day
    df['hour'] = pd.DatetimeIndex(df.timestamp_ms).hour
    df['weekday'] = pd.DatetimeIndex(df.timestamp_ms).weekday

    calendar ={1:"January",2:"February",3:"March",4:"April",5:"May",6:"June",7:"July",8:"August",9:"September",10:"October",11:"November",12:"December"}

    time_heat = df.groupby(['hour','month'])['content'].size().reset_index().pivot(columns='hour',index='month',values='content')
    time_fig = px.imshow(time_heat, y=[value for key, value in calendar.items() if key in df['month'].unique().tolist()])
    time_hour = time_heat.max().idxmax()
    time_month = time_heat[time_hour].idxmax()
    time_activity = int(time_heat.max().max())

    week = ["Mondays","Tuesdays","Wednesdays","Thursdays","Fridays","Saturdays","Sundays"]
    weekday_heat = df.groupby(['hour','weekday'])['content'].size().reset_index().pivot(columns='hour',index='weekday',values='content')
    weekday_fig = px.imshow(weekday_heat, y=week)
    weekday_hour = weekday_heat.max().idxmax()
    weekday_day = weekday_heat[weekday_hour].idxmax()
    weekday_activity = int(weekday_heat.max().max())

    def seconds_to_hours(seconds):
        return int(seconds/60/60)

    if 'call_duration' in df:
        call_weekday_heat = df.groupby(['month','weekday'])['call_duration'].sum().reset_index().pivot(columns='month',index='weekday',values='call_duration')
        call_weekday_fig = px.imshow(call_weekday_heat, y=week, x=[value for key, value in calendar.items() if key in df['month'].unique().tolist()])
        call_weekday_month = call_weekday_heat.max().idxmax()
        call_weekday_day = call_weekday_heat[call_weekday_month].idxmax()
        call_weekday_activity = int(call_weekday_heat.max().max())

        total_call_duration = seconds_to_hours(df['call_duration'].sum())
        percent_call_duration = str(int(total_call_duration/(24*365) * 100))+"%"
        st.write("We spent a total of ", highlight(total_call_duration,"blue"), " :blue[hours] on the phone together. That's about", highlight(percent_call_duration,"blue"), " of a whole year.")

    st.write("##### We were most active at around", highlight(time_hour,"blue"),":blue[:00] on the month of",highlight(calendar[time_month],"blue")," when we sent a total of", highlight(time_activity,"blue"), "messages to each other.")
    st.write(time_fig)

    st.write("##### We were most active at around", highlight(weekday_hour,"blue"),":blue[:00] on",highlight(week[weekday_day],"blue")," when we sent a total of", highlight(weekday_activity,"blue"), "messages to each other.")
    st.write(weekday_fig)

    if 'call_duration' in df:
        st.write("##### We were most active on the ", highlight(week[call_weekday_day],"blue"), "of", highlight(calendar[call_weekday_month],"blue"), " when we spent about", highlight(seconds_to_hours(call_weekday_activity),"blue"), "hours on the phone with each other.")
        st.write(call_weekday_fig)

    st.write("## :bar_chart: You keep raising the bar...")

    def create_calendar_bar(calendar,df):
        calendar_bar = []
        for month in df['month'].unique().tolist():
            calendar_bar += [calendar[month]] * 2
        return calendar_bar

    sender_df = df.groupby(['month', 'sender_name']).count().reset_index()
    sender_df.drop(['year','timestamp_ms','day','hour','weekday','share','call_duration','sticker','length'], axis=1, inplace=True, errors='ignore')
    calendar_bar =create_calendar_bar(calendar, sender_df)

    sender_content = sender_df.copy()
    sender_content.drop(['reactions','photos','videos','audio_files'], axis=1, inplace=True, errors='ignore')
    sender_content_fig = px.bar(sender_content,x=calendar_bar,y='content',color='sender_name')
    sender_content_total = sender_content.groupby(['sender_name']).content.sum()

    if 'reactions' in df:
        sender_reactions= sender_df.copy()
        sender_reactions.drop(['content','photos','videos','audio_files'], axis=1, inplace=True, errors='ignore')
        sender_reactions_fig = px.bar(sender_reactions,x=calendar_bar,y='reactions',color='sender_name')
        sender_reactions_total = sender_reactions.groupby(['sender_name']).reactions.sum()

    if 'photos' in df:
        sender_photos= sender_df.copy()
        sender_photos.drop(['content','reactions','videos','audio_files'], axis=1, inplace=True, errors='ignore')
        sender_photos_fig = px.bar(sender_photos,x=calendar_bar,y='photos',color='sender_name')
        sender_photos_total = sender_photos.groupby(['sender_name']).photos.sum()

    if 'videos' in df:
        sender_videos= sender_df.copy()
        sender_videos.drop(['content','reactions','photos','audio_files'], axis=1, inplace=True, errors='ignore')
        sender_videos_fig = px.bar(sender_videos,x=calendar_bar,y='videos',color='sender_name')
        sender_videos_total = sender_videos.groupby(['sender_name']).videos.sum()

    if 'audio_files' in df:
        sender_audio_files= sender_df.copy()
        sender_audio_files.drop(['content','reactions','photos','videos'], axis=1, inplace=True, errors='ignore')
        sender_audio_files_fig = px.bar(sender_audio_files,x=calendar_bar,y='audio_files',color='sender_name')
        sender_audio_files_total = sender_audio_files.groupby(['sender_name']).audio_files.sum()

    st.write(highlight(sender_content_total.index[0],"green"), "sent a total of ", highlight(sender_content_total.iloc[0],"blue"), " text messages. ", 
            highlight(sender_content_total.index[1],"green"), "sent a total of ", highlight(sender_content_total.iloc[1],"blue"), " text messages. ")
    st.write(sender_content_fig)
    if 'reactions' in df:
        st.write(highlight(sender_reactions_total.index[0],"green"), "sent a total of ", highlight(sender_reactions_total.iloc[0],"blue"), " reactions. ", 
                highlight(sender_reactions_total.index[1],"green"), "sent a total of ", highlight(sender_reactions_total.iloc[1],"blue"), " reactions. ")
        st.write(sender_reactions_fig)
    if 'photos' in df:
        st.write(highlight(sender_photos_total.index[0],"green"), "sent a total of ", highlight(sender_photos_total.iloc[0],"blue"), " photos. ", 
                highlight(sender_photos_total.index[1],"green"), "sent a total of ", highlight(sender_photos_total.iloc[1],"blue"), " photos. ")
        st.write(sender_photos_fig)
    if 'videos' in df:
        st.write(highlight(sender_videos_total.index[0],"green"), "sent a total of ", highlight(sender_videos_total.iloc[0],"blue"), " photos. ", 
                highlight(sender_videos_total.index[1],"green"), "sent a total of ", highlight(sender_videos_total.iloc[1],"blue"), " photos. ")
        st.write(sender_videos_fig)
    if 'audio_files' in df:
        st.write(highlight(sender_audio_files_total.index[0],"green"), "sent a total of ", highlight(sender_audio_files_total.iloc[0],"blue"), " voice notes. ", 
                highlight(sender_audio_files_total.index[1],"green"), "sent a total of ", highlight(sender_audio_files_total.iloc[1],"blue"), " voice notes. ")
        st.write(sender_audio_files_fig)
else:
    st.write("## `404 - No Data Found`")