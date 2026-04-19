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
        disc.setScale(ROOMBA_SCALE * 0.1, ROOMBA_SCALE * 1.1, ROOMBA_SCALE * 0.25)
        disc.setColor(*COL_ROOMBA)
        disc.reparentTo(self.root)
        disc.setZ(ROOMBA_SCALE * 0.25)

        # -- eye
        eye = base.loader.loadModel("models/misc/sphere")
        eye.setScale(ROOMBA_SCALE * 0.18)
        eye.setColor(0.9, 0.1, 1)
        eye.reparentTo(self.root)
        eye.setPos(0, ROOMBA_SCALE * 0.9, ROOMBA_SCALE * 0.4)

        # -- collision
        cnode = CollisionNode("roomba_col")
        cnode.addSolid(CollisionSphere(0, 0, ROOMBA_SCALE * 0.25, ROOMBA_SCALE))
        cnode.setFromCollideMask(BitMask32.allOff())
        cnode.setIntoCollideMask(BitMask32.bit(1))
        self.col_np: NodePath = self.root.attachNewNode(cnode)

        # place at first waypoint
        if waypoints:
            self.root.setPos(waypoints[0][0], waypoints[0][1], 0)

    # -- update
    def update(self, dt: float, dog_pos: Vec3) -> bool:
        """Returns true if the roomba caught the dog this frame"""
        my_pos = self.root.getPos()
        dist = (dog_pos - my_pos).length()

        # state transitions
        if not self.chasing and dist < ROOMBA_SIGHT_RANGE:
            self.chasing = True
        elif self.chasing and dist < ROOMBA_LOSE_RANGE:
            self.chasing = False

        if self.chasing:
            return self._chase(dt, dog_pos, dist)
        else:
            self._patrol(dt)
            return False

    def _patrol(self, dt: float) -> None:
        if not self.waypoints:
            return

        target = Vec3(
            self.waypoints[self.wp_index][0], self.waypoints[self.wp_index][1], 0
        )
        self._move_toward(target, ROOMBA_PATROL_SPEED, dt)
        if (self.root.getPos() - target).length() < 0.3:
            self.wp_index = (self.wp_index + 1) % len(self.waypoints)

    def _chase(self, dt: float, dog_pos: Vec3, dist: float) -> bool:
        target = Vec3(dog_pos.x, dog_pos.y, 0)
        self._move_toward(target, ROOMBA_CHASE_SPEED, dt)
        return dist < ROOMBA_SCALE * 1.5

    def _move_toward(self, target: Vec3, speed: float, dt: float) -> None:
        my_pos = self.root.getPos()
        direction = target - my_pos
        direction.z = 0
        dist = direction.length()

        if dist < 0.01:
            return

        direction.normalize()
        self.root.setPos(my_pos + direction * speed * dt)

        angle = math.degrees(math.atan2(-direction.x, -direction.y))
        self.root.setH(angle)
