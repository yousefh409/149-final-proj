from playsound import playsound
import time

# for playing note.wav file
# playsound('sounds/cha-cha-slide.mp3', True)
from pygame import mixer

mixer.init()
mixer.music.load("sounds/cha-cha-slide.mp3")
mixer.music.play()

print("sliding to the left")

time.sleep(1.45)
print("sliding to the right")

time.sleep(1.35)
print("criss cross")

time.sleep(2.3)
print("criss cross")

time.sleep(1.95)
print("yeeeeee")

time.sleep(3)