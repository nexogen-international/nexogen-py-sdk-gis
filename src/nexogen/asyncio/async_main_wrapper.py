#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
NEXOGEN AsyncIO Main Wrapper
"""

from __future__ import annotations
__version__ = '0.1.0'

from typing import Callable
import asyncio
import signal
import sys


class _GracefulExit(SystemExit):
    code = 1

    @staticmethod
    def throw():
        raise _GracefulExit()


def async_main_wrapper(main: Callable[[asyncio.AbstractEventLoop], None]):
    loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
    try:
        loop.add_signal_handler(signal.SIGINT, _GracefulExit.throw)
        loop.add_signal_handler(signal.SIGTERM, _GracefulExit.throw)
    except NotImplementedError:
        pass
    try:
        loop.run_until_complete(main(loop=loop))
        loop.close()
    except (_GracefulExit, KeyboardInterrupt, SystemExit):
        pass
