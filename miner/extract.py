import typing as T
import time
from dataclasses import dataclass


@dataclass
class TweetData:
    handle: str
    user_id: str
    tweet_id: str
    text: str
    likes: int
    retweets: int
    replies: int
    quotes: int
    created_at: int
    subtweet_id: T.Optional[str] = None

    def __hash__(self) -> int:
        return hash(self.tweet_id)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TweetData):
            return NotImplemented
        return self.tweet_id == other.tweet_id


def extract_tweets(tweet_data: list[dict[str, T.Any]]) -> list[TweetData]:
    tweets: list[TweetData] = []
    for tweet_bundle in tweet_data:
        for tweets_intructions in tweet_bundle["data"]["home"]["home_timeline_urt"][
            "instructions"
        ]:
            for tweets_entry in tweets_intructions["entries"]:
                for tweet_wrapper in _iterate_entries(tweets_entry["content"]):
                    tweet = tweet_wrapper["legacy"]
                    user_info = tweet_wrapper["core"]["user_results"]["result"][
                        "legacy"
                    ]
                    tweet = TweetData(
                        handle=user_info["screen_name"],
                        user_id=tweet["user_id_str"],
                        tweet_id=tweet["id_str"],
                        text=tweet["full_text"],
                        likes=tweet["favorite_count"],
                        retweets=tweet["retweet_count"],
                        replies=tweet["reply_count"],
                        quotes=tweet["quote_count"],
                        created_at=_parse_tweet_ts(tweet["created_at"]),
                        subtweet_id=tweet["quoted_status_id_str"]
                        if "quoted_status_id_str" in tweet
                        else None,
                    )
                    tweets.append(tweet)
    return tweets


def _iterate_entries(tweets_entry: dict[str, T.Any]):
    if "item" in tweets_entry:
        for entry in _iterate_entries(tweets_entry["item"]):
            yield entry
        return
    if "itemContent" in tweets_entry:
        for entry in _iterate_entries(tweets_entry["itemContent"]):
            yield entry
        return
    type = None
    if "entryType" in tweets_entry:
        type = tweets_entry["entryType"]
    if "itemType" in tweets_entry:
        type = tweets_entry["itemType"]
    match type:
        case "TimelineTimelineModule":
            for entry in tweets_entry["items"]:
                for sub_entry in _iterate_entries(entry):
                    yield sub_entry
        case "TimelineTimelineItem":
            for entry in _iterate_entries(tweets_entry["itemContent"]):
                yield entry
        case "TimelineTweet":
            if "tweet" in tweets_entry["tweet_results"]["result"]:
                yield tweets_entry["tweet_results"]["result"]["tweet"]
                return
            yield tweets_entry["tweet_results"]["result"]
        case "TimelineTimelineCursor":
            if "items" in tweets_entry:
                for entry in _iterate_entries(tweets_entry["items"]):
                    yield entry
        case "TimelineRecruitingOrganization":
            return
        case "TimelineUser":
            return
        case "TimelineCommunity":
            return
        case "TimelineMessagePrompt":
            return
        case _:
            raise Exception(f"Unknown entry type: {type}")


def _parse_tweet_ts(tweet_ts: str) -> int:
    return int(time.mktime(time.strptime(tweet_ts, "%a %b %d %H:%M:%S %z %Y")))
