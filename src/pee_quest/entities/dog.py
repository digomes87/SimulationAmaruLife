"""Dog - player controlled"""

from __future__ import annotations

from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    BitMask32,
    CollisionNode,
    CollisionSphere,
    NodePath,
    Vec3,
)

from src.pee_quest.constants import (
    COL_DOG,
    DOG_BLADDER_DRAIN,
    DOG_BLADDER_MAX,
    DOG_SCALE,
    DOG_SPEED,
    DOG_TURN_SPEED,
)


class Dog:
    """The hero: a very desperate dog"""

    def __init__(self, base: ShowBase, parent: NodePath) -> None:
        self.base = base
        self.bladder: float = 0.0
        self.caught: bool = False
        self.peed: bool = False
        self.speed = DOG_SPEED
        self.turn_speed = DOG_TURN_SPEED

        # -- visual
        self.root: NodePath = parent.attachNewNode("dog_root")
        self.root.setPos(0, 0, 0)

        body = base.loader.loadModel("models/misc/sphere")
        body.setScale(DOG_SCALE * 0.9, DOG_SCALE * 1.3, DOG_SCALE * 0.8)
        body.setColor(*COL_DOG)
        body.reparentTo(self.root)
        body.setZ(0, DOG_SCALE * 0.9, DOG_SCALE * 1.6)

        # head
