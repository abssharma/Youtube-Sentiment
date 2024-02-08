#1 import required libraries
import json
from csv import writer
from apiclient.discovery import build
import streamlit as st
from urllib.parse import urlparse, parse_qs
import pandas as pd
import numpy as np
import nltk
from nltk.corpus import stopwords
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import matplotlib.pyplot as plt
from wordcloud import WordCloud
try:
    from bs4 import BeautifulSoup
except :
    from BeautifulSoup import BeautifulSoup 
import requests
nltk.download('stopwords')
nltk.download('vader_lexicon')
def build_service():
    key="AIzaSyBqXBT8NagvV97tOA3sDq2vkj3JiVmGz_k"
    YOUTUBE_API_SERVICE_NAME = "youtube"
    YOUTUBE_API_VERSION = "v3"
    return build(YOUTUBE_API_SERVICE_NAME,
                 YOUTUBE_API_VERSION,
                 developerKey=key)

#2 configure function parameters for required variables to pass to service
def get_comments(videoId,part='snippet', 
                 maxResults=100, 
                 textFormat='plainText',
                 order='time'):

    #3 create empty lists to store desired information
    comments=[]
       
    # build our service from path/to/apikey
    service = build_service()
    
    #4 make an API call using our service
    response = service.commentThreads().list(
        part=part,
        maxResults=maxResults,
        textFormat=textFormat,
        order=order,
        videoId=videoId
    ).execute()
                 

    while response: # this loop will continue to run until you max out your quota
                 
        for item in response['items']:
            #5 index item for desired data features
            comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
            #6 append to lists
            comments.append(comment)
            # #7 write line by line
            # with open(f'{csv_filename}.csv', 'a+') as f:
            #     # https://thispointer.com/python-how-to-append-a-new-row-to-an-existing-csv-file/#:~:text=Open%20our%20csv%20file%20in,in%20the%20associated%20csv%20file
            #     csv_writer = writer(f)
            #     csv_writer.writerow([comment, comment_id, reply_count, like_count])
        
        #8 check for nextPageToken, and if it exists, set response equal to the JSON response
        if 'nextPageToken' in response:
            response = service.commentThreads().list(
                part=part,
                maxResults=maxResults,
                textFormat=textFormat,
                order=order,
                videoId=videoId,
                pageToken=response['nextPageToken']
            ).execute()
        else:
            break

    #9 return our data of interest
    return comments


def get_id(url):
    u_pars = urlparse(url)
    quer_v = parse_qs(u_pars.query).get('v')
    if quer_v:
        return quer_v[0]
    pth = u_pars.path.split('/')
    if pth:
        return pth[-1]


def _get_polarity_score(analyzer: SentimentIntensityAnalyzer, text: str) -> float:
    """Calculate polarity score for the given text
    :type analyzer: SentimentIntensityAnalyzer
    :param analyzer: Sentiment analyzer for Vader model
    :type text: str
    :param text: Cleaned comment text
    :rtype: float
    :returns: Polarity score
    """

    scores = analyzer.polarity_scores(text)

    # logger.debug(f"Text: {text}, Scores: {scores}")

    return scores["compound"]


def _convert_score_to_sentiment(score) -> str:
    """Convert score to sentiment
    :type score: float
    :param score: Polarity score
    :rtype: str
    :returns: Sentiment as Positive, Negative, or Neutral
    """

    sentiment = ""

    if score <-0.2:
        sentiment = "Negative"
    elif -0.2 <= score <= 0.0:
        sentiment = "Neutral"
    else:
        sentiment = "Positive"

    return sentiment
def get_video_info(video_id):
    try:
        youtube=build_service()
        video_response = youtube.videos().list(
            part='snippet',
            id=video_id
        ).execute()

        video_item = video_response['items'][0]
        video_title = video_item['snippet']['title']
        channel_id = video_item['snippet']['channelId']

        channel_response = youtube.channels().list(
            part='snippet',
            id=channel_id
        ).execute()

        channel_item = channel_response['items'][0]
        channel_name = channel_item['snippet']['title']

        return video_title, channel_name
    except Exception as e:
        print(f"Error: {e}")
        return None, None

def main():
    st.set_option('deprecation.showPyplotGlobalUse', False)
    st.set_page_config(page_title="Youtube Comments Sentiment Analysis",page_icon="https://upload.wikimedia.org/wikipedia/commons/thumb/7/72/YouTube_social_white_square_%282017%29.svg/1200px-YouTube_social_white_square_%282017%29.svg.png",layout="centered")
    st.title("Youtube Comments Sentiment Analysis")
    
    with st.form("my_form"):
        url=st.text_input("Enter URL")
        videoId=get_id(url)
        submitted = st.form_submit_button("Submit")
    if submitted:
        # comments=get_comments(video_id)
        # st.write(comments)
        video_title, channel_name = get_video_info(videoId)
        st.subheader(video_title)
        st.write(channel_name)
        part='snippet'
        maxResults=100
        textFormat='plainText'
        order='time'
        comments=[]
        # build our service from path/to/apikey
        service = build_service()
        
        #4 make an API call using our service
        response = service.commentThreads().list(
            part=part,
            maxResults=maxResults,
            textFormat=textFormat,
            order=order,
            videoId=videoId
        ).execute()
                    

        while response: # this loop will continue to run until you max out your quota
                    
            for item in response['items']:
                #5 index item for desired data features
                comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
                #6 append to lists
                comments.append(comment)
                # #7 write line by line
                # with open(f'{csv_filename}.csv', 'a+') as f:
                #     # https://thispointer.com/python-how-to-append-a-new-row-to-an-existing-csv-file/#:~:text=Open%20our%20csv%20file%20in,in%20the%20associated%20csv%20file
                #     csv_writer = writer(f)
                #     csv_writer.writerow([comment, comment_id, reply_count, like_count])
            
            #8 check for nextPageToken, and if it exists, set response equal to the JSON response
            if 'nextPageToken' in response:
                response = service.commentThreads().list(
                    part=part,
                    maxResults=maxResults,
                    textFormat=textFormat,
                    order=order,
                    videoId=videoId,
                    pageToken=response['nextPageToken']
                ).execute()
            else:
                break
        
        df = pd.DataFrame(list(comments), columns=["comments"])
        df['comments'].replace("", np.nan, inplace=True)
        df.dropna(subset=['comments'], inplace=True)
        # st.write(df)
        # st.write("Cleaning the database")
        df["comments"] = (
            df["comments"]
            # remove whitespace
            .str.strip()
            # replace newlines with space
            .str.replace("\n", " ")
            # remove mentions and links
            .str.replace(r"(?:\@|http?\://|https?\://|www)\S+", "", regex=True)
            # remove punctuations, emojis, special characters
            .str.replace(r"[^\w\s]+", "", regex=True)
            # turn to lowercase
            .str.lower()
            # remove numbers
            .str.replace(r"\d+", "", regex=True)
            # remove hashtags
            .str.replace(r"#\S+", " ", regex=True)
        )
        # remove stop words
        stop_words = stopwords.words("english")
        df["comments"] = df["comments"].apply(
            lambda comment: " ".join([word for word in comment.split() if word not in stop_words])
        )
        # st.write(df)
        analyzer = SentimentIntensityAnalyzer()
        df['comments'].replace("", np.nan, inplace=True)
        df.dropna(subset=['comments'], inplace=True)
        df["Sentiment Score"] = df["comments"].apply(
            lambda comment: _get_polarity_score(analyzer, comment)
        )

        df["Sentiment"] = df["Sentiment Score"].apply(
            lambda score: _convert_score_to_sentiment(score)
        )
        pos=0
        neg=0
        neut=0
        # st.write(df['Sentiment'].value_counts())
        for i in df["Sentiment"]:
            if i=="Positive" :
                pos=pos+1
            elif i=="Negative":
                neg=neg+1
            else:
                neut=neut+1
        sizes=[pos,neg,neut]
        labels=["Postive","Negative","Neutral"]
        col1, col2= st.columns(2)
        with col1:
            st.write("Number of Neutral comments :",neut)
            st.write("Number of Positive comments :",pos)
            st.write("Number of Negative comments :",neg)
        with col2:
            fig1, ax1 = plt.subplots()
            ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
            ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
            st.pyplot(fig1)
        df_pos=df.loc[df["Sentiment"]=="Positive"]
        res_pos=df_pos.sort_values(by="Sentiment Score",ascending=False)
        # res_pos.reset_index(inplace = True)
        df_neg=df.loc[df["Sentiment"]=="Negative"]
        # df_neg.reset_index(inplace = True)
        res_neg=df_neg.sort_values(by="Sentiment Score",ascending=True)
        # res_neg.reset_index(inplace = True)
        st.subheader("Most Positive Comments")
        st.write(res_pos.head(100))
        st.subheader("Most Positive Words")
        pos_text=" ".join(word for word in df_pos['comments'])
        word_cloud2 = WordCloud( background_color = 'white').generate(pos_text)
        st.image(word_cloud2.to_array())
        st.subheader("Most Negative Comments")
        st.write(res_neg.head(100))
        st.subheader("Most Negative Words")
        neg_text=" ".join(word for word in df_neg['comments'])
        word_cloud1 = WordCloud( background_color = 'white').generate(neg_text)
        st.image(word_cloud1.to_array())
main()