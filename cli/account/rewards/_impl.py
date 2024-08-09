import requests
import click
from dataclasses import dataclass

import cli.auth.volara as volara_auth
from constants import VOLARA_API


@dataclass
class IndexStats:
    totalFiles: int
    totalIndexedTweets: int


@dataclass
class RewardStats:
    ownershipScore: float
    miningScore: float
    validatorScore: float


@dataclass
class RankStats:
    rank: str
    ownershipRank: str
    miningRank: str
    validatorRank: str


@dataclass
class Stats:
    indexStats: IndexStats
    rewardStats: RewardStats
    rankStats: RankStats


def _fetch_rewards() -> Stats:
    jwt = volara_auth.get_volara_jwt()
    resp = requests.get(
        f"{VOLARA_API}/v1/user/stats",
        headers={"Authorization": f"Bearer {jwt}"},
    )
    data = resp.json()["data"]
    return Stats(
        indexStats=IndexStats(**data["indexStats"]),
        rewardStats=RewardStats(**data["rewardStats"]),
        rankStats=RankStats(**data["rankStats"]),
    )


def print_rewards():
    rewards = _fetch_rewards()

    click.echo("=" * 40)
    click.echo(click.style("Volara Rewards Stats", fg="green", bold=True))
    click.echo("=" * 40)

    sections = [
        (
            "Index Stats:",
            [
                ("Total Files", rewards.indexStats.totalFiles),
                ("Total Indexed Tweets", rewards.indexStats.totalIndexedTweets),
            ],
        ),
        (
            "Reward Stats:",
            [
                ("Ownership Score", f"{rewards.rewardStats.ownershipScore:.2f}"),
                ("Mining Score", f"{rewards.rewardStats.miningScore:.2f}"),
                ("Validator Score", f"{rewards.rewardStats.validatorScore:.2f}"),
            ],
        ),
        (
            "Rank Stats:",
            [
                ("Overall Rank", rewards.rankStats.rank),
                ("Ownership Rank", rewards.rankStats.ownershipRank),
                ("Mining Rank", rewards.rankStats.miningRank),
                ("Validator Rank", rewards.rankStats.validatorRank),
            ],
        ),
    ]

    for section_title, items in sections:
        click.echo(click.style(section_title, fg="yellow", bold=True))
        for label, value in items:
            click.echo(f"{label}: {value}")
        click.echo()
