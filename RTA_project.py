import time
from tweepy import API
from tweepy import Cursor
from tweepy import OAuthHandler
from tweepy import Stream
from textblob import TextBlob
import matplotlib.pyplot as plt

import numpy as np
import pandas as pd
import re


# # # # TWITTER CLIENT # # # #
class TwitterClient():
    def __init__(self, twitter_user=None):
        self.auth = TwitterAuthenticator().authenticate_twitter_app()
        self.twitter_client = API(self.auth)
        # f inicjalizujaca - autoryzacja do api
        # definiujemy parametry
        self.twitter_user = twitter_user

    def get_twitter_client_api(self):
        return self.twitter_client

    def get_user_timeline_tweets(self, num_tweets):
        tweets = []
        for tweet in Cursor(self.twitter_client.user_timeline, id=self.twitter_user).items(num_tweets):
            tweets.append(tweet)
        return tweets

    def get_friend_list(self, num_friends):
        friend_list = []
        for friend in Cursor(self.twitter_client.friends, id=self.twitter_user).items(num_friends):
            friend_list.append(friend)
        return friend_list

    def get_home_timeline_tweets(self, num_tweets):
        home_timeline_tweets = []
        for tweet in Cursor(self.twitter_client.home_timeline, id=self.twitter_user).items(num_tweets):
            home_timeline_tweets.append(tweet)
        return home_timeline_tweets


# # # # TWITTER AUTHENTICATER # # # #
class TwitterAuthenticator():

    def authenticate_twitter_app(self):
        auth = OAuthHandler("2puWiRsTR0BHGLkye1TtvuywO", "MrpICSwzEdBGX5EUlD9iImSyFp7dybY40diiyMPC2r1E6k9u9J")
        auth.set_access_token("1533422431431495685-SDGrmd4mqpyBtYyuPlMrIHV4e22Uix",
                              "beOxeLsF9ralrCxlI7CGnkf5X5VofPM7UcRhFArCYOM14")
        return auth

    # # # # TWITTER STREAMER # # # #


class TwitterStreamer():

    def __init__(self):
        self.twitter_autenticator = TwitterAuthenticator()

    def stream_tweets(self, fetched_tweets_filename, hash_tag_list):
        # This handles Twitter authetification and the connection to Twitter Streaming API
        listener = TwitterListener(fetched_tweets_filename)
        auth = self.twitter_autenticator.authenticate_twitter_app()
        stream = Stream(auth, listener)

        # This line filter Twitter Streams to capture data by the keywords:
        stream.filter(track=hash_tag_list)

    # # # # TWITTER STREAM LISTENER # # # #


class TwitterListener(Stream):

    def __init__(self, fetched_tweets_filename):
        self.fetched_tweets_filename = fetched_tweets_filename

    def on_data(self, data):
        try:
            print(data)
            with open(self.fetched_tweets_filename, 'a') as tf:
                tf.write(data)
            return True
        except BaseException as e:
            print("Error on_data %s" % str(e))
        return True

    def on_error(self, status):
        if status == 420:
            # Returning False on_data method in case rate limit occurs.
            return False
        print(status)


class TweetAnalyzer():

    def clean_tweet(self, tweet):
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

    def analyze_sentiment(self, tweet):
        analysis = TextBlob(self.clean_tweet(tweet))

        if analysis.sentiment.polarity > 0:
            return 1
        elif analysis.sentiment.polarity == 0:
            return 0
        else:
            return -1

    def tweets_to_data_frame(self, tweets):
        df = pd.DataFrame(data=[tweet.text for tweet in tweets], columns=['tweets'])

        df['id'] = np.array([tweet.id for tweet in tweets])
        df['len'] = np.array([len(tweet.text) for tweet in tweets])
        df['date'] = np.array([tweet.created_at for tweet in tweets])
        df['source'] = np.array([tweet.source for tweet in tweets])
        df['likes'] = np.array([tweet.favorite_count for tweet in tweets])
        df['retweets'] = np.array([tweet.retweet_count for tweet in tweets])

        return df


def main():
    if __name__ == '__main__':
        twitter_client = TwitterClient()
        tweet_analyzer = TweetAnalyzer()

        api = twitter_client.get_twitter_client_api()

        tweets = api.user_timeline(screen_name="POTUS", count=200)

        df = tweet_analyzer.tweets_to_data_frame(tweets)
        df['sentiment'] = np.array([tweet_analyzer.analyze_sentiment(tweet) for tweet in df['tweets']])
        pd.set_option('display.max_columns', None)
        print(df)

        # Sentiment visualization
        senti = pd.Series(data=df['sentiment'].value_counts(), index=df['sentiment'])
        fig = plt.figure(figsize=(16, 10))
        plt.bar(df['sentiment'], senti)

        plt.title('Analiza sentymentu tweetów użytkownika @POTUS', fontsize=16)
        plt.show()
        plt.pause(5)
        # Time Series
        ax1 = plt.subplot(4, 1, 1)
        time_likes = pd.Series(data=df['len'].values, index=df['date'])
        time_likes.plot(figsize=(16, 16), color='r')
        plt.title('Krzywa przedstawiająca ilości znaków w tweetach', fontsize=16)
        # plt.show()

        plt.subplot(4, 1, 2, sharex=ax1)
        time_favs = pd.Series(data=df['likes'].values, index=df['date'])
        time_favs.plot(figsize=(16, 16), color='r')
        plt.title('Zależność ilości polubień względem czasu', fontsize=16)
        # plt.show()

        plt.subplot(4, 1, 3, sharex=ax1)
        time_retweets = pd.Series(data=df['retweets'].values, index=df['date'])
        time_retweets.plot(figsize=(16, 16), color='r')
        plt.title('Zależność ilości retweetów względem czasu', fontsize=16)
        # plt.show()

        # Layered Time Series:
        plt.subplot(4, 1, 4, sharex=ax1)
        time_likes = pd.Series(data=df['likes'].values, index=df['date'])
        time_likes.plot(figsize=(16, 16), label="likes", legend=True)

        time_retweets = pd.Series(data=df['retweets'].values, index=df['date'])
        time_retweets.plot(figsize=(16, 16), label="retweets", legend=True)
        plt.title('Zależność ilości polubień i retweetów względem czasu', fontsize=16)
        plt.suptitle('Wizualizacja danych pobieranych z Tweetera użytkownika @POTUS ', fontsize=24)


while 1:
    main()
    plt.show()
    time.sleep(3)
    plt.pause(5)