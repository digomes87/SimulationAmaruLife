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
    (5, 4, 1.0, 1.1, 0.3, 0.18, 0.10),
    # tv
    (-5, -4, 2.0, 0.6, 0.7, 0.22, 0.22, 0.22),
]


class IndoorScene:
    def __init__(self, base: ShowBase) -> None:
        self.base = base
        self.root: NodePath = base.render.attachNewNode("indoor_scene")

        self._build_room()
        self._build_futniture()
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
        walls = []
