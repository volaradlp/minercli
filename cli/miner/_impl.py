import subprocess
import os
import signal
import click

from constants import TMP_MINER_LOG, TMP_PID_FILE


def start_inline():
    import asyncio
    from miner.run import start_mining

    click.echo("Starting mining process in this shell...")
    asyncio.run(start_mining())


# Function to start the daemon
def start_daemon():
    try:
        with open(TMP_PID_FILE, "r") as file:
            pid = file.read()
        if pid:
            click.echo(f"Mining daemon already running with PID {pid}")
            return
    except FileNotFoundError:
        pass

    absolute_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "../../bin/volara_miner"
    )
    process = subprocess.Popen(
        [absolute_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setpgrp,
    )
    # Save the PID to a file to use it later in the stop command
    os.makedirs(os.path.dirname(TMP_PID_FILE), exist_ok=True)
    with open(TMP_PID_FILE, "w") as file:
        file.write(str(process.pid))
    click.echo(f"Mining daemon started with PID {process.pid}")


# Function to stop the daemon
def stop_daemon():
    # Read the PID from the file
    try:
        with open(TMP_PID_FILE, "r") as file:
            pid = int(file.read())
    except FileNotFoundError:
        click.echo("Mining daemon not running")
        return
    # Send SIGTERM signal to the process
    try:
        os.kill(pid, signal.SIGTERM)
    except ProcessLookupError:
        click.echo("Mining daemon not found... removing state")
        pass
    # Remove the pid file and log file
    os.remove(TMP_PID_FILE)
    os.remove(TMP_MINER_LOG)
    click.echo(f"Mining daemon stopped with PID {pid}")


def echo_logs():
    click.echo(_get_logs())


def _get_logs():
    try:
        with open(TMP_MINER_LOG, "r") as file:
            return file.read()
    except FileNotFoundError:
        return "No logs found. Start the mining daemon to get logs."
