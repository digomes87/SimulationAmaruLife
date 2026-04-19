"""Front door opens peridiocally, giving the dog its escape window"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from direct.showbase.ShowBase import ShowBase

from panda3d.core import BitMask32, CollisionBox, CollisionNode, NodePath, Point3

from src.pee_quest.constants import (
    COL_DOOR_CLOSED,
    COL_DOOR_OPEN,
    DOOR_OPEN_DURATION,
    DOOR_OPEN_INTERVAL,
)


class Door:
    def __init__(
        self,
        base: ShowBase,
        parent: NodePath,
        pos: tuple[float, float, float] = (
            0,
            0,
            0,
        ),
    ) -> None:
        self.base = base
        self.is_open = False
        self._timer = 0.0
        self._open_timer = 0.0

        # -- visual ---
        self.root: NodePath = parent.attachNewNode("door_root")
        self.root.setPos(*pos)

        self._door_vis = base.loader.loadModel("models/box")
        self._door_vis.setScale(0.25, 2.0, 2.5)
        self._door_vis.setColor(*COL_DOOR_CLOSED)
        self._door_vis.reparentTo(self.root)
        self._door_vis.setPos(0, 0, 1.25)

        # - collision --
        cnode = CollisionNode("door_col")
        cnode.addSolid(CollisionBox(Point3(-0.25, -1.0, 0), Point3(0.25, 1.0, 2.5)))
        cnode.setFromCollideMask(BitMask32.allOf())
        cnode.setIntoCollideMask(BitMask32.bit(2))
        self._col_np: NodePath = self.root.attachNewNode(cnode)

    # -- udpdate --
