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
        body.setZ(DOG_SCALE * 0.8)

        # head
        head = base.loader.loadModel("models/misc/sphere")
        head.setScale(DOG_SCALE * 0.55)
        head.setColor(*COL_DOG)
        head.reparentTo(self.root)
        head.setPos(0, DOG_SCALE * 0.9, DOG_SCALE * 1.6)

        # tail stub
        tail = base.loader.loadModel("models/box")
        tail.setScale(DOG_SCALE * 0.12, DOG_SCALE * 0.5, DOG_SCALE * 0.12)
        tail.setColor(*COL_DOG)
        tail.reparentTo(self.root)
        tail.setPos(0, -DOG_SCALE * 1.1, DOG_SCALE * 1.3)

        # -- colision
        cnode = CollisionNode("dog_col")
        cnode.addSolid(CollisionSphere(0, 0, DOG_SCALE * 0.8, DOG_SCALE * 0.9))
        cnode.setFromCollideMask(BitMask32.bit(1))
        cnode.setIntoCollideMask(BitMask32.allOff())
        self.col_np: NodePath = self.root.attachNewNode(cnode)

    # update
    def update(self, dt: float, keys: dict[str, bool], indoor: bool) -> None:
        """called every frame"""
        if self.caught or self.peed:
            return

        # rotation
        if keys["left"]:
            self.root.setH(self.root, self.turn_speed * dt)

        if keys["right"]:
            self.root.setH(self.root, -self.turn_speed * dt)

        # moviments
        move = Vec3(0, 0, 0)
        if keys["forward"]:
            move.y -= self.speed * dt

        if keys["backward"]:
            move.y += self.speed * dt

        if move.length() > 0:
            self.root.setFluidPos(
                self.root,
                move.x,
                move.y,
                move.z,
            )

        # blender
        if indoor:
            self.bladder += DOG_BLADDER_DRAIN * dt
            self.bladder = min(self.bladder, DOG_BLADDER_MAX)

    def get_pos(self) -> Vec3:
        return self.root.getPos()

    def set_pos(self, x: float, y: float, z: float = 0.0) -> None:
        self.root.setPos(x, y, z)
