#!/usr/bin/python
# -*- coding: utf-8 -*-

from default import Janitor
from util.logging.kodi import notify, debug
from util import settings


def autostart():
    """
    Starts the cleaning service.
    """
    janitor = Janitor()

    service_sleep = (
        4  # Lower than 4 causes too much stress on resource limited systems such as RPi
    )
    ticker = 0
    delayed_completed = False

    while not janitor.monitor.abortRequested():
        if settings.get_value(settings.service_enabled):
            scan_interval_ticker = (
                settings.get_value(settings.scan_interval) * 60 / service_sleep
            )
            delayed_start_ticker = (
                settings.get_value(settings.delayed_start) * 60 / service_sleep
            )

            if delayed_completed and ticker >= scan_interval_ticker:
                results, _ = janitor.clean()
                notify(janitor.get_cleaning_results(results))
                ticker = 0
            elif not delayed_completed and ticker >= delayed_start_ticker:
                delayed_completed = True
                results, _ = janitor.clean()
                notify(janitor.get_cleaning_results(results))
                ticker = 0

            janitor.monitor.waitForAbort(service_sleep)
            ticker += 1
        else:
            janitor.monitor.waitForAbort(service_sleep)

    debug(u"Abort requested. Terminating.")
    return


if __name__ == "__main__":
    autostart()
