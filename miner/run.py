import asyncio
import logging
import os

import miner.dlp.volara as volara
from constants import (
    ERROR_SLEEP_INTERVAL,
    TARGET_TWEET_COUNT,
    TIMELINE_SLEEP_INTERVAL,
    TMP_MINER_LOG,
)
from cli.auth.twitter import get_active_account
from miner.build import build_tweet_buffer, build_zip_buffer
from miner.extract import TweetData, extract_tweets
from miner.drive import write_uuid_file
from miner.miner.encrypt import encrypt_buffer


logger = logging.getLogger(__name__)


async def start_mining():
    logger.info("Starting mining...")
    account = get_active_account()
    if account is None:
        logger.error("No active account found.")
        return
    while True:
        tweets: set[TweetData] = set()
        while len(tweets) < TARGET_TWEET_COUNT:
            logger.info("Pulling tweets...")
            try:
                timeline = account.home_timeline(limit=TARGET_TWEET_COUNT)
            except Exception:
                logger.exception("Error pulling timeline")
                logger.info(f"Sleeping {ERROR_SLEEP_INTERVAL}s for timeline refresh...")
                await asyncio.sleep(ERROR_SLEEP_INTERVAL)
                continue
            try:
                new_tweets = extract_tweets(timeline)
            except Exception:
                logger.exception("Error extracting the fetched tweets...")
                logging.info(timeline)
                logger.info(f"Sleeping {ERROR_SLEEP_INTERVAL}s for timeline refresh...")
                await asyncio.sleep(ERROR_SLEEP_INTERVAL)
                continue
            tweets.update(new_tweets)
            logger.info(
                f"Pulled {len(new_tweets)} tweets... total buffer: {len(tweets)}"
            )
            if len(tweets) >= TARGET_TWEET_COUNT:
                break
            logger.info(f"Sleeping {TIMELINE_SLEEP_INTERVAL}s for timeline refresh...")
            await asyncio.sleep(TIMELINE_SLEEP_INTERVAL)
        tweet_buffer = build_tweet_buffer(tweets)
        logger.info("Uploading tweet buffer to drive...")
        zip_buffer = build_zip_buffer(tweet_buffer)
        encrypted_zip_buffer = encrypt_buffer(zip_buffer)
        file_url = await write_uuid_file(encrypted_zip_buffer)
        logger.info(f"Uploaded tweet buffer to {file_url}")
        logger.info("Submitting to volara...")
        await volara.submit(file_url)
        logger.info("Submitted to volara.")


if __name__ == "__main__":
    os.makedirs(os.path.dirname(TMP_MINER_LOG), exist_ok=True)
    try:
        os.remove(TMP_MINER_LOG)
    except FileNotFoundError:
        pass
    output_handler = logging.FileHandler(TMP_MINER_LOG)
    logger.setLevel(logging.INFO)
    logger.addHandler(output_handler)
    try:
        asyncio.run(start_mining())
    except Exception:
        logger.exception("Exception encountered")
        logger.info("Exiting...")
