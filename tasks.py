""" Invoke tasks for GreenPaths 2 CLI. """

# used to unify calling of green_paths_2_cli.py
# currently using monkeypatch to fix getargspec issue

# invoke seems not be too active so using green_paths_2_cli.py directly might be better?

import inspect
import os
import sys

if not hasattr(inspect, "getargspec"):
    inspect.getargspec = inspect.getfullargspec

from invoke import task


@task
def gp2(c, args=""):
    """
    Runs the GreenPaths 2 CLI with optional arguments.
    """
    command = f"poetry run python -u green_paths_2_cli.py {args}"
    # Check if the operating system is Windows
    if os.name == "nt":  # 'nt' means Windows
        c.run(
            command, echo=True, out_stream=sys.stdout, err_stream=sys.stderr, pty=False
        )
    else:
        c.run(
            command, echo=True, out_stream=sys.stdout, err_stream=sys.stderr, pty=True
        )
