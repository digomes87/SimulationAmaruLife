"""Roomba -  the domestic nemesis"""

from __future__ import annotations

import math

from direct.showbase.ShowBase import ShowBase
from panda3d.core import BitMask32, CollisionNode, CollisionSphere, NodePath, Vec3

from src.pee_quest.constants import (
    COL_ROOMBA,
    ROOMBA_CHASE_SPEED,
    ROOMBA_LOSE_RANGE,
    ROOMBA_PATROL_SPEED,
    ROOMBA_SCALE,
    ROOMBA_SIGHT_RANGE,
)


class Roomba:
    """Patrols a route, chase the dog on sight"""

    def __init__(
        self,
        base: ShowBase,
        parent: NodePath,
        waypoints: list[tuple[float, float]],
    ) -> None:
        self.base = base
        self.waypoints = waypoints
        self.wp_index = 0
        self.chasing = False

        # visual
        self.root: NodePath = parent.attachNewNode("roomba_root")

        disc = base.loader.loadModel("models/misc/sphere")
