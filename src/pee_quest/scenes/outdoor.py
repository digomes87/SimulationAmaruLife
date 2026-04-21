"""Outdoor scene — street + praça with the hydrant goal."""

from __future__ import annotations

from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    AmbientLight,
    BitMask32,
    CollisionBox,
    CollisionNode,
    CollisionSphere,
    DirectionalLight,
    NodePath,
    Point3,
    Vec4,
)

from src.pee_quest.constants import (
    COL_FLOOR_OUTDOOR,
    COL_GRASS,
    COL_HYDRANT,
)


class OutdoorScene:
    def __init__(self, base: ShowBase) -> None:
        self.base = base
        self.root: NodePath = base.render.attachNewNode("outdoor_scene")
        self.root.hide()

        self._build_street()
        self._build_praca()
        self._setup_lighting()

        # The win-condition object: fire hydrant in the praça
        self.hydrant_pos = (30, 0)
        self._build_hydrant(*self.hydrant_pos)

    # ── Street ────────────────────────────────────────────────────────────────
    def _build_street(self) -> None:
        ldr = self.base.loader

        # Pavement (grey-ish)
        pave = ldr.loadModel("models/box")
        pave.setScale(8, 40, 0.1)
        pave.setColor(0.55, 0.55, 0.55, 1)
        pave.reparentTo(self.root)
        pave.setPos(0, 20, -0.1)

        # Grass strips either side
        for side_x in (-12, 12):
            g = ldr.loadModel("models/box")
            g.setScale(5, 40, 0.1)
            g.setColor(*COL_GRASS)
            g.reparentTo(self.root)
            g.setPos(side_x, 20, -0.1)

        # Pavement obstacles (trash cans, lampposts)
        obstacles = [
            # (x, y, r, g, b, sx, sy, sz)
            (-4, 20, 0.3, 0.3, 0.3, 0.4, 0.4, 0.9),
            (4, 28, 0.3, 0.3, 0.3, 0.4, 0.4, 0.9),
            (-3, 35, 0.55, 0.40, 0.25, 0.5, 0.5, 0.8),
            (5, 15, 0.55, 0.40, 0.25, 0.5, 0.5, 0.8),
        ]
        for x, y, r, g, b, sx, sy, sz in obstacles:
            obs = ldr.loadModel("models/box")
            obs.setScale(sx, sy, sz)
            obs.setColor(r, g, b, 1)
            obs.reparentTo(self.root)
            obs.setPos(x, y, sz)

    # ── Praça ─────────────────────────────────────────────────────────────────
    def _build_praca(self) -> None:
        ldr = self.base.loader

        # Grass square
        praca = ldr.loadModel("models/box")
        praca.setScale(15, 15, 0.12)
        praca.setColor(*COL_FLOOR_OUTDOOR)
        praca.reparentTo(self.root)
        praca.setPos(30, 30, -0.1)

        # Trees (simple green blobs)
        tree_spots = [
            (22, 22),
            (38, 22),
            (22, 38),
            (38, 38),
        ]
        for tx, ty in tree_spots:
            trunk = ldr.loadModel("models/box")
            trunk.setScale(0.3, 0.3, 1.5)
            trunk.setColor(0.40, 0.25, 0.08, 1)
            trunk.reparentTo(self.root)
            trunk.setPos(tx, ty, 1.5)

            crown = ldr.loadModel("models/misc/sphere")
            crown.setScale(1.2, 1.2, 1.0)
            crown.setColor(0.20, 0.60, 0.15, 1)
            crown.reparentTo(self.root)
            crown.setPos(tx, ty, 3.2)

    def _build_hydrant(self, x: float, y: float) -> None:
        ldr = self.base.loader

        body = ldr.loadModel("models/box")
        body.setScale(0.25, 0.25, 0.6)
        body.setColor(*COL_HYDRANT)
        body.reparentTo(self.root)
        body.setPos(x, y, 0.6)

        cap = ldr.loadModel("models/misc/sphere")
        cap.setScale(0.3, 0.3, 0.2)
        cap.setColor(*COL_HYDRANT)
        cap.reparentTo(self.root)
        cap.setPos(x, y, 1.3)

        # Win trigger collision
        cn = CollisionNode("hydrant_col")
        cn.addSolid(CollisionSphere(0, 0, 0, 1.5))
        cn.setFromCollideMask(BitMask32.allOff())
        cn.setIntoCollideMask(BitMask32.bit(4))
        body.attachNewNode(cn)

    # ── Lighting ──────────────────────────────────────────────────────────────
    def _setup_lighting(self) -> None:
        alight = AmbientLight("out_amb")
        alight.setColor(Vec4(0.65, 0.65, 0.60, 1))
        self.root.setLight(self.root.attachNewNode(alight))

        sun = DirectionalLight("sun")
        sun.setColor(Vec4(1.0, 0.95, 0.80, 1))
        sunp = self.root.attachNewNode(sun)
        sunp.setHpr(60, -70, 0)
        self.root.setLight(sunp)

    # ── Helpers ───────────────────────────────────────────────────────────────
    def hide(self) -> None:
        self.root.hide()

    def show(self) -> None:
        self.root.show()
