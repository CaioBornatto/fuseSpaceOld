from pygame import mixer
import os

class Sound_Fx:
    def player_fire(self):
        laser = mixer.Sound(os.path.join("assets/sounds", "player_fire.wav"))
        laser.play()

    def game_over(self):
        game_over = mixer.Sound(os.path.join("assets/sounds", "game_over.wav"))
        game_over.play()


class Music:

    def play_track(self, play=True):
        if play == False:
            mixer.music.stop()
        else:
            mixer.music.load(os.path.join("assets/sounds", "Blazer_Rail_2.wav"))
            mixer.music.play(-1)
