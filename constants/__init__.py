import os

VOLARA_TMP_DIR = os.path.expanduser("~/.volara")

TMP_MINER_LOG = f"{VOLARA_TMP_DIR}/miner.log"
TMP_PID_FILE = f"{VOLARA_TMP_DIR}/miner.pid"
TMP_TWITTER_AUTH = f"{VOLARA_TMP_DIR}/twitter.cookies"
TMP_DRIVE_AUTH = f"{VOLARA_TMP_DIR}/drive.token"
TMP_VOLARA_TOKEN = f"{VOLARA_TMP_DIR}/volara.jwt"

TIMELINE_SLEEP_INTERVAL = 120
TARGET_TWEET_COUNT = 1000

VOLARA_API = "https://api.volara.xyz"

DLP_ADDRESS = "0x3f0c5b6E3525b302F5FDa5d93b47085999D472f8"
