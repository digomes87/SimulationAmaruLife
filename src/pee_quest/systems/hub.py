"""hub bladder bar, door coutndown status, text"""

from __future__ import annotations

from direct.gui.DirectGui import (
    DirectFrame,
    DirectLabel,
    DirectWaitBar,
)
from direct.showbase.ShowBase import ShowBase
from panda3d.core import TextNode

from src.pee_quest.constants import DOG_BLADDER_MAX


class HUD:
    def __init__(self, base: ShowBase) -> None:
        self.base = base

        # -- bladder bar
        self._bladder_bar = DirectWaitBar(
            text="",
            value=0,
            range=DOG_BLADDER_MAX,
            pos=(-0.0, 0, 0.88),
            scale=(0.45, 1, 0.045),
            frameColor=(0.2, 0.2, 0.2, 0.7),
            barColor=(0.25, 0.55, 1.0, 1),
        )
        self._bladder_label = DirectLabel(
            text="@. bladder",
            pos=(-0.55, 0, 0.88),
            scale=0.055,
            text_fg=(1, 1, 1, 1),
            text_align=TextNode.ARight,
            frameColor=(0, 0, 0, 0),
        )

        # -- status door
        self._door_label = DirectLabel(
            text="",
            pos=(0, 0, 0.78),
            scale=0.058,
            text_fg=(1, 0.95, 0.3, 1),
            text_align=TextNode.ACenter,
            frameColor=(0, 0, 0, 0),
        )

        # -- End Game
        self._status_label = DirectLabel(
            text="",
            pos=(0, 0, 0.1),
            scale=0.13,
            text_fg=(1, 1, 1, 1),
            text_align=TextNode.ACenter,
            frameColor=(0, 0, 0, 0.6),
        )

        # hit
        self._hint = DirectLabel(
            text="WASD = andar/girar  R= reiniciar",
            pos=(0, 0, -0.93),
            scale=0.048,
            text_fg=(0.8, 0.8, 0.8, 1),
            text_align=TextNode.ACenter,
            frameColor=(0, 0, 0, 0),
        )

    def update(
        self,
        bladder: float,
        door_open: bool,
        time_until_open: float,
        time_remaining_open: float,
        indoor: bool,
    ) -> None:
        self._bladder_bar["value"] = bladder
        urgency = bladder / DOG_BLADDER_MAX

        if urgency < 0.5:
            self._bladder_bar["barColor"] = (0.25, 0.55, 1.0, 1)
        elif urgency < 0.75:
            self._bladder_bar["barColor"] = (1.0, 0.75, 0.0, 1)
        else:
            self._bladder_label["barColor"] = (1.0, 0.2, 0.2, 1)

        # door hit
        if indoor:
            if door_open:
                self._door_label["text"] = (
                    f"🚪 PORTA ABERTA! {time_remaining_open:.1f}s"
                )
                self._door_label["text_fg"] = (1.0, 0.75, 0.0, 1)
            else:
                self._door_label["text"] = f"🚪 POrta fechada em {time_until_open:.0f}s"
                self._door_label["text_fg"] = (1.0, 0.95, 0.3, 1)
        else:
            self._door_label["text"] = "🌳 chega na praça e faz xixi"

    def show_status(self, msg: str) -> None:
        self._status_label["text"] = msg

    def clear_status(self) -> None:
        self._status_label["text"] = ""
