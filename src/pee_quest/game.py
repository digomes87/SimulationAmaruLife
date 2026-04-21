"""PeeQuest — main application class."""

from __future__ import annotations

from direct.gui.DirectGui import DirectLabel
from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    BitMask32,
    ClockObject,
    CollisionHandlerEvent,
    CollisionNode,
    CollisionSphere,
    CollisionTraverser,
    TextNode,
    Vec3,
    WindowProperties,
)

globalClock = ClockObject.getGlobalClock()

from src.pee_quest.constants import (
    DOG_BLADDER_MAX,
    WINDOW_HEIGHT,
    WINDOW_TITLE,
    WINDOW_WIDTH,
)
from src.pee_quest.entities.dog import Dog
from src.pee_quest.scenes.indoor import IndoorScene
from src.pee_quest.scenes.outdoor import OutdoorScene
from src.pee_quest.systems.camera import ThirdPersonCamera
from src.pee_quest.systems.hub import HUD

# Game states
STATE_INDOOR = "indoor"
STATE_OUTDOOR = "outdoor"
STATE_WIN = "win"
STATE_LOSE = "lose"


class PeeQuest(ShowBase):
    def __init__(self) -> None:
        super().__init__()

        self._setup_window()
        self._setup_input()

        # ── Scenes ────────────────────────────────────────────────────────────
        self.indoor_scene = IndoorScene(self)
        self.outdoor_scene = OutdoorScene(self)

        # ── Dog ───────────────────────────────────────────────────────────────
        self.dog = Dog(self, self.render)
        self.dog.set_pos(0, -6, 0)

        # ── Camera ────────────────────────────────────────────────────────────
        self.cam_system = ThirdPersonCamera(self, self.dog.root)
        self.camera.setPos(0, 10, 8)

        # ── HUD ───────────────────────────────────────────────────────────────
        self.hud = HUD(self)

        # ── Collision ─────────────────────────────────────────────────────────
        self._setup_collision()

        # ── State ─────────────────────────────────────────────────────────────
        self.state = STATE_INDOOR

        # ── Main task ─────────────────────────────────────────────────────────
        self.taskMgr.add(self._update, "main_update")

    # ── Window ────────────────────────────────────────────────────────────────
    def _setup_window(self) -> None:
        props = WindowProperties()
        props.setTitle(WINDOW_TITLE)
        props.setSize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.win.requestProperties(props)
        self.setBackgroundColor(0.53, 0.81, 0.92, 1)  # sky blue

    # ── Input ─────────────────────────────────────────────────────────────────
    def _setup_input(self) -> None:
        self.keys: dict[str, bool] = {
            "forward": False,
            "backward": False,
            "left": False,
            "right": False,
        }
        mapping = {
            "w": "forward",
            "arrow_up": "forward",
            "s": "backward",
            "arrow_down": "backward",
            "a": "left",
            "arrow_left": "left",
            "d": "right",
            "arrow_right": "right",
        }
        for key, action in mapping.items():
            self.accept(key, self._key_down, [action])
            self.accept(f"{key}-up", self._key_up, [action])

        self.accept("r", self._restart)
        self.accept("escape", self.userExit)

    def _key_down(self, action: str) -> None:
        self.keys[action] = True

    def _key_up(self, action: str) -> None:
        self.keys[action] = False

    # ── Collision setup ───────────────────────────────────────────────────────
    def _setup_collision(self) -> None:
        self.cTrav = CollisionTraverser("main_trav")
        self.cTrav.setRespectPrevTransform(True)

        handler = CollisionHandlerEvent()
        handler.addInPattern("%fn-into-%in")

        # Dog's FROM node
        self.cTrav.addCollider(self.dog.col_np, handler)

        # Hydrant win trigger (bit 4) — add a separate FROM on dog for win check
        win_cnode = CollisionNode("dog_win_col")
        win_cnode.addSolid(CollisionSphere(0, 0, 0.5, 0.95))
        win_cnode.setFromCollideMask(BitMask32.bit(4))
        win_cnode.setIntoCollideMask(BitMask32.allOff())
        self._win_col_np = self.dog.root.attachNewNode(win_cnode)
        self.cTrav.addCollider(self._win_col_np, handler)

        self.accept("dog_win_col-into-hydrant_col", self._on_win)

    # ── Main update ───────────────────────────────────────────────────────────
    def _update(self, task):
        dt = min(globalClock.getDt(), 0.05)

        if self.state in (STATE_WIN, STATE_LOSE):
            return task.cont

        dog_pos = self.dog.get_pos()
        indoor = self.state == STATE_INDOOR

        # Dog movement
        self.dog.update(dt, self.keys, indoor)

        # Camera
        self.cam_system.update(dt)

        if self.state == STATE_INDOOR:
            self._update_indoor(dt, dog_pos)
        elif self.state == STATE_OUTDOOR:
            self._update_outdoor(dt)

        # Collision traversal
        self.cTrav.traverse(self.render)

        # HUD
        door = self.indoor_scene.door
        self.hud.update(
            bladder=self.dog.bladder,
            door_open=door.is_open,
            time_until_open=door.time_until_open,
            time_remaining_open=door.timer_remaining_open,
            indoor=indoor,
        )

        return task.cont

    def _update_indoor(self, dt: float, dog_pos: Vec3) -> None:
        # Roomba catch check
        caught = self.indoor_scene.update(dt, dog_pos)
        if caught:
            self._on_caught()
            return

        # Bladder accident indoors
        if self.dog.bladder >= DOG_BLADDER_MAX:
            self._on_accident()
            return

        # Check if dog reached the door while open
        door = self.indoor_scene.door
        door_world_pos = self.indoor_scene.door.root.getPos()
        dist_to_door = (dog_pos - door_world_pos).length()
        if door.is_open and dist_to_door < 2.5:
            self._enter_outdoor()

    def _update_outdoor(self, dt: float) -> None:
        # Nothing special yet — win is handled by collision event
        pass

    # ── State transitions ─────────────────────────────────────────────────────
    def _enter_outdoor(self) -> None:
        self.state = STATE_OUTDOOR
        self.indoor_scene.hide()
        self.outdoor_scene.show()

        # Place dog just outside the door
        self.dog.set_pos(0, 12, 0)
        self.dog.root.setH(180)
        self.setBackgroundColor(0.53, 0.81, 0.50, 1)  # outdoor sky
        self.hud.show_status("Liberdade! 🐾  Chega na praça!")
        self.taskMgr.doMethodLater(
            2.5, lambda t: self.hud.clear_status() or t.cont, "clear_msg"
        )

    def _on_win(self, entry=None) -> None:
        if self.state != STATE_OUTDOOR:
            return
        self.state = STATE_WIN
        self.dog.peed = True
        self.hud.show_status("🎉 XIXI FEITO! Missão cumprida! 🎉\n\nR = jogar de novo")
        self.setBackgroundColor(1.0, 0.95, 0.40, 1)

    def _on_caught(self) -> None:
        if self.state == STATE_LOSE:
            return
        self.state = STATE_LOSE
        self.dog.caught = True
        self.hud.show_status("😱 O Roomba te pegou!\n\nR = tentar de novo")

    def _on_accident(self) -> None:
        if self.state == STATE_LOSE:
            return
        self.state = STATE_LOSE
        self.hud.show_status("💦 Fez xixi dentro de casa!\n\nR = tentar de novo")

    # ── Restart ───────────────────────────────────────────────────────────────
    def _restart(self) -> None:
        # Reset dog
        self.dog.bladder = 0.0
        self.dog.caught = False
        self.dog.peed = False
        self.dog.set_pos(0, -6, 0)
        self.dog.root.setH(0)

        # Reset scenes
        self.outdoor_scene.hide()
        self.indoor_scene.show()
        self.indoor_scene.door._timer = 0.0
        self.indoor_scene.door._open_timer = 0.0
        self.indoor_scene.door._close()

        # Reset roombas to first waypoint
        for roomba in self.indoor_scene.roombas:
            roomba.chasing = False
            roomba.wp_index = 0
            wp = roomba.waypoints[0]
            roomba.root.setPos(wp[0], wp[1], 0)

        self.setBackgroundColor(0.53, 0.81, 0.92, 1)
        self.state = STATE_INDOOR
        self.hud.clear_status()
