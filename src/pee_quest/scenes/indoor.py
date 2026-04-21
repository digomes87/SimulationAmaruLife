"""Indoor scene - the house the dog must espace"""

from __future__ import annotations

from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    AmbientLight,
    BitMask32,
    CollisionBox,
    CollisionNode,
    DirectionalLight,
    NodePath,
    Point3,
    Vec4,
)

from src.pee_quest.constants import COL_FLOOR_INDOOR, COL_WALL
from src.pee_quest.entities.door import Door
from src.pee_quest.entities.roomba import Roomba

_PATROL_ROUTES: list[list[tuple[float, float]]] = [
    [(-4, 2), (4, 2), (4, -2), (-4, -2)],
    [(0, 5), (0, -5)],
]


# furniture pos
_FURNITURE = [
    # sofa
    (-5, 3, 3.5, 1.0, 1.0, 0.4, 0.25, 0.15),
    # table
    (2, -3, 1.2, 1.2, 0.9, 0.60, 0.45, 0.28),
    # armchair
    (5, 4, 1.0, 1.0, 1.1, 0.3, 0.18, 0.10),
    # TV stand
    (-5, -4, 2.0, 0.6, 0.7, 0.22, 0.22, 0.22),
]


class IndoorScene:
    def __init__(self, base: ShowBase) -> None:
        self.base = base
        self.root: NodePath = base.render.attachNewNode("indoor_scene")

        self._build_room()
        self._build_furniture()
        self._setup_lighting()

        # door
        self.door = Door(base, self.root, pos=(0, 10, 0))

        # roombas
        self.roombas: list[Roomba] = [
            Roomba(base, self.root, route) for route in _PATROL_ROUTES
        ]

    # --- draw the room
    def _build_room(self) -> None:
        ldr = self.base.loader

        # floor
        floor = ldr.loadModel("models/box")
        floor.setScale(10, 10, 0.1)
        floor.setColor(*COL_FLOOR_INDOOR)
        floor.reparentTo(self.root)
        floor.setPos(0, 0, -0.1)

        # walls
        walls = [
            (0, 10, 1.5, 10.0, 0.25, 1.5),  # north
            (0, -10, 1.5, 10.0, 0.25, 1.5),  # south
            (10, 0, 1.5, 0.25, 10.0, 1.5),  # East
            (-10, 0, 1.5, 0.25, 10.0, 1.5),  # west
        ]

        for px, py, pz, sx, sy, sz in walls:
            w = ldr.loadModel("models/box")
            w.setScale(sx, sy, sz)
            w.setColor(*COL_WALL)
            w.reparentTo(self.root)
            w.setPos(px, py, pz)

            # collision
            cn = CollisionNode("wall_col")
            cn.addSolid(CollisionBox(Point3(-sx, -sy, 0), Point3(sx, sy, sz)))
            cn.setFromCollideMask(BitMask32.allOff())
            cn.setIntoCollideMask(BitMask32.bit(3))
            w.attachNewNode(cn)

    def _build_furniture(self) -> None:
        ldr = self.base.loader

        for x, y, sx, sy, sz, r, g, b in _FURNITURE:
            piece = ldr.loadModel("models/box")
            piece.setScale(sx, sy, sz)
            piece.setColor(r, g, b, 1)
            piece.reparentTo(self.root)
            piece.setPos(x, y, sz)

            cn = CollisionNode("furniture_col")
            cn.addSolid(CollisionBox(Point3(-sx, -sy, -sy), Point3(sx, sy, sz)))
            cn.setFromCollideMask(BitMask32.allOff())
            cn.setFromCollideMask(BitMask32.bit(3))
            piece.attachNewNode(cn)

    def _setup_lighting(self) -> None:
        alight = AmbientLight("indoor_amb")
        alight.setColor(Vec4(0.55, 0.50, 0.45, 1))
        self.root.setLight(self.root.attachNewNode(alight))

        dlight = DirectionalLight("indoor_dir")
        dlight.setColor(Vec4(0.9, 0.85, 0.75, 1))
        dlnp = self.root.attachNewNode(dlight)
        dlnp.setHpr(45, -50, 0)
        self.root.setLight(dlnp)

    def update(self, dt: float, dog_pos) -> bool:
        self.door.update(dt)
        for roomba in self.roombas:
            if roomba.update(dt, dog_pos):
                return True
        return False

    def hide(self) -> None:
        self.root.hide()

    def show(self) -> None:
        self.root.show()
