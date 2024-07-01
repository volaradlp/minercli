import os

VOLARA_TMP_DIR = os.path.expanduser("~/.volara")

TMP_MINER_LOG = f"{VOLARA_TMP_DIR}/miner.log"
TMP_PID_FILE = f"{VOLARA_TMP_DIR}/miner.pid"
TMP_TWITTER_AUTH = f"{VOLARA_TMP_DIR}/twitter.cookies"
TMP_DRIVE_AUTH = f"{VOLARA_TMP_DIR}/drive.token"

TIMELINE_SLEEP_INTERVAL = 120
TARGET_TWEET_COUNT = 1000

VOLARA_API = "https://api.volara.xyz"

DLP_ADDRESS = "0xE3ED21cFc82708b62ffc4E3a0E3ffba0CdE4635D"
