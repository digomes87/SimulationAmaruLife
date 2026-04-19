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
    def update(self, dt: float) -> None:
        if not self.is_open:
            self._timer += dt
            if self._timer >= DOOR_OPEN_INTERVAL:
                self._open()
        else:
            self._open_timer -= dt
            if self._open_timer <= 0:
                self._close()

    def _open(self) -> None:
        self.is_open = True
        self._timer = 0.0
        self._open_timer = DOOR_OPEN_DURATION

        # slide the door
        self._door_vis.setX(2.2)
        self._door_vis.setColor(*COL_DOOR_OPEN)
        self._col_np.hide()
        self._col_np.node().setIntoCollideMask(BitMask32.allOff())

    def _close(self) -> None:
        self.is_open = False
        self._door_vis.setX(0)
        self._door_vis.setColor(*COL_DOOR_CLOSED)
        self._col_np.hide()
        self._col_np.node().setIntoCollideMask(BitMask32.bit(2))

    @property
    def timer_remaining_open(self) -> float:
        return max(0.0, self._open_timer)

    @property
    def time_until_open(self) -> float:
        if self.is_open:
            return 0.0
        return max(0.0, DOOR_OPEN_INTERVAL - self._timer)
