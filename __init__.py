# Grizzly Manager Copyright (c) 2022 big-vl
# GrizzlyManager plugin is released under the terms of the AGPLv3 or higher.

from . import GrizzlyManager


def getMetaData():
    return {}


def register(app):
    return {"extension": GrizzlyManager.GrizzlyManager()}
