from playsound import playsound
 
# for playing note.mp3 file
playsound('military-alarm-129017.mp3')
print('playing sound using  playsound')

is_playing = False

def play():
    global is_playing
    if not is_playing:
        # Code to play the sound
        playsound('military-alarm-129017.mp3')
        print("Sound is playing")
        is_playing = True
    else:
        print("Sound is already playing")

def pause():
    global is_playing
    if is_playing:
        # Code to pause the sound
        playsound('military-alarm-129017.mp3')
        print("Sound is paused")
        is_playing = False
    else:
        print("Sound is already paused")


play()
time.sleep(1)
pause()