import flatbuffers
import zipfile
import io
import typing as T

import miner.buffers.tweets as Tweets
import miner.buffers.tweet as Tweet
from miner.extract import TweetData


def build_tweet_buffer(tweets: T.Iterable[TweetData]) -> bytes:
    builder = flatbuffers.Builder(1024)
    tweet_offsets = []
    for tweet in tweets:
        handle = builder.CreateString(tweet.handle)
        tweet_id = builder.CreateString(tweet.tweet_id)
        user_id = builder.CreateString(tweet.user_id)
        text = builder.CreateString(tweet.text)
        sub_tweet_id = (
            builder.CreateString(tweet.subtweet_id) if tweet.subtweet_id else None
        )
        Tweet.Start(builder)
        Tweet.AddHandle(builder, handle)
        Tweet.AddUserId(builder, user_id)
        Tweet.AddTweetId(builder, tweet_id)
        Tweet.AddText(builder, text)
        Tweet.AddLikes(builder, tweet.likes)
        Tweet.AddRetweets(builder, tweet.retweets)
        Tweet.AddReplies(builder, tweet.replies)
        Tweet.AddQuotes(builder, tweet.quotes)
        Tweet.AddCreatedAt(builder, tweet.created_at)
        if sub_tweet_id:
            Tweet.AddSubtweetId(builder, sub_tweet_id)
        tweet_offsets.append(Tweet.End(builder))
    Tweets.StartTweetsVector(builder, len(tweet_offsets))
    for tweet_offset in tweet_offsets:
        builder.PrependUOffsetTRelative(tweet_offset)
    tweet_vec = builder.EndVector()
    Tweets.Start(builder)
    Tweets.AddTweets(builder, tweet_vec)
    tweets = Tweets.End(builder)
    builder.Finish(tweets)
    buffer = builder.Output()
    return buffer


def build_zip_buffer(tweet_buffer: bytes) -> bytes:
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr("tweets.data", tweet_buffer)
    zip_buffer.seek(0)
    return zip_buffer.getvalue()
