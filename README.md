# Volara Miner

Miner for the Volara X DLP

# About

Volara is a decentralized data marketplace for X data, built on the robust Vana network. We empower users by giving them ownership of their data and enabling them to earn from it.

The Volara Miner is a software package which allows users to contribute X data to the network for rewards.

# Credentials

Volara uses two credentials to perform mining on Vana:

1. X username and password, for access to the Twitter API
2. Google OAUTH, for storing your mined X data in Google Drive.

# Mine With Docker

The easiest way to run the Volara miner is with Docker - a containerization solution that manages the miner dependencies.

## Quickstart

Paste this into your terminal to start mining:

```shell
[ -f "volara.sh" ] && rm volara.sh; curl -s -o volara.sh https://raw.githubusercontent.com/volaradlp/minercli/refs/heads/main/run_docker.sh && chmod +x volara.sh && ./volara.sh
```

## Prerequisites

You must have docker installed on your system.

### Install Docker

#### Mac / Linux / Windows

Docker desktop can be installed [here](https://www.docker.com/products/docker-desktop/)

The public installation documentation can be found [here](https://docs.docker.com/engine/install/)

### Create and Fund Your Wallet

Any Ethereum-compatible wallets will work with Vana/Volara. We recommend getting started with metamask.

#### Create Metamask Wallet

Create a Metamask wallet [here](https://support.metamask.io/getting-started/getting-started-with-metamask/#how-to-install-metamask)

Get <your_private_key> [here](https://support.metamask.io/managing-my-wallet/secret-recovery-phrase-and-private-keys/how-to-export-an-accounts-private-key/)

#### Fund Wallet

The Vana faucet can fund your address [here](https://faucet.vana.org)

#### Add Vana Network to Wallet

You can add the Vana network to your wallet to see Vana and Volara tokens [here](https://docs.vana.org/vana/for-builders/network-setup/network-information#setting-up-the-network)

## Start Mining

Once docker is installed, run the below commands in your terminal to run the miner.

Replace <your_private_key> with any Ethereum compatible private key.

```shell
docker pull volara/miner
export VANA_PRIVATE_KEY=<your_private_key>
docker run -it -e VANA_PRIVATE_KEY=${VANA_PRIVATE_KEY} volara/miner
```

# Mine With Native Installation

## Prerequisites

Volara uses several dependencies to operate.

- Python 3.12
- Poetry

```shell
brew install python
curl -sSL https://install.python-poetry.org | python3 -
```

## Quick Start

```shell
git clone https://github.com/volaradlp/minercli.git
cd minercli
source setup.sh
```

You should now have access to the `volara` cli command.

# Interface

The interface can be accessed via the CLI at `./bin/volara`

## Mining

By default, miner runs as a background daemon.

#### Start Mining

```shell
volara mine start
```

| Flag | Description                           |
| ---- | ------------------------------------- |
| -b   | Run the miner in a background process |

#### Stop Mining

```shell
volara mine stop
```

#### See Mining Logs

```shell
volara mine logs
```

## Account

### Rewards

#### View your hotkey's rewards

```shell
volara account rewards
```

## Auth

### Google Drive

#### Login to Drive

```shell
volara auth drive login
```

#### Logout to Drive

```shell
volara auth drive logout
```

### X

#### Login to X

```shell
volara auth twitter login
```

#### Logout to X

```shell
volara auth drive logout
```

## Misc

#### Update the Volara CLI

```shell
volara update
```

#### Check the Volara CLI version

```shell
volara --version
```
