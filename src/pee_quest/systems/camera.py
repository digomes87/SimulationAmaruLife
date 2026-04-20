"""third-person camera that smoothly follows the dog"""

from __future__ import annotations

from direct.showbase.ShowBase import ShowBase
from panda3d.core import NodePath, Vec3

from src.pee_quest.constants import (
    CAM_DISTANCE,
    CAM_HEIGHT,
    CAM_LERP,
)


class ThirdPersonCamera:
    def __init__(self, base: ShowBase, target: NodePath) -> None:
        self.base = base
        self.target = target
        base.disableMouse()

    def update(self, dt: float) -> None:
        target_pos = self.target.getPos()
        target_h = self.target.getH()

        import math

        rad = math.radians(target_h)

        desired_pos = Vec3(
            target_pos.x + math.sin(rad) * CAM_DISTANCE,
            target_pos.y - math.cos(rad) * CAM_DISTANCE,
            target_pos.z + CAM_HEIGHT,
        )

        cur = self.base.camera.getPos()
        lerp = min(1.0, CAM_LERP * dt)
        new_pos = cur + (desired_pos - cur) * lerp
        self.base.camera.setPos(new_pos)
        self.base.camera.lookAt(
            Vec3(
                target_pos.x,
                target_pos.y,
                target_pos.z + 0.8,
            ),
        )
