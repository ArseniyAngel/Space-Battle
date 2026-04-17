import arcade
from config import SOUNDS_DIR


class SoundManager:
    def __init__(self):
        self.sounds = {}
        self.music_player = None
        self._load_sounds()

    def _load_sounds(self):
        sound_files = {
            "shoot": "cannon-shot.wav",
            "explosion": "single-explosion.mp3",
            "hit": "shield.wav",
            "music": "soundtrack.mp3",
        }

        for name, filename in sound_files.items():
            try:
                path = f"{SOUNDS_DIR}/{filename}"
                self.sounds[name] = arcade.load_sound(path)
            except FileNotFoundError:
                if name == "shoot":
                    self.sounds[name] = arcade.load_sound(":resources:/sounds/hit1.wav")
                elif name == "explosion":
                    self.sounds[name] = arcade.load_sound(":resources:/sounds/hit2.wav")
                else:
                    self.sounds[name] = None

    def play(self, name: str, volume: float = 1.0):
        if name in self.sounds and self.sounds[name]:
            arcade.play_sound(self.sounds[name], volume=volume)

    def play_music(self, loop: bool = True, volume: float = 0.5):
        if self.sounds.get("music"):
            if self.music_player:
                self.music_player.delete()
            self.music_player = arcade.play_sound(
                self.sounds["music"],
                volume=volume,
                loop=loop
            )

    def stop_music(self):
        if self.music_player:
            self.music_player.delete()
            self.music_player = None