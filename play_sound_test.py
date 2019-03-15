from playsound import playsound
import pyglet, threading, datetime, time
import pandas as pd, numpy as np
import config_led as config
from inputs import get_gamepad
import led, colorsys
import subprocess, platform
updates_this_second = 0
STRING_TIME = 3.00
import ScoreKeeper
def track_updates_per_second():
    global updates_this_second

    while True:
        updates_this_second = 0
        time.sleep(1)
        print(updates_this_second)



updates_tracker = threading.Thread(target=track_updates_per_second)
updates_tracker.start()
shift = 0
song_path = r"Songs/Dura/Dura.ogg"
json_path =  r"Songs/Dura/Expert.json"
LED_COUNT = 100
def play_song(song_path):

    song = pyglet.media.load(song_path)
    song.play()
    pyglet.app.run()
#start playing the song
music_thread = threading.Thread(target=play_song, args=(song_path,))
music_thread.start()
start_time = datetime.datetime.now()

import json
beats = json.load(open(json_path,'rb'))

notes_df = pd.DataFrame(beats["_notes"])




def which_drum(beat_row):
    #determines which beat target of the four a particular beat goes to

    which_drum = 2 * beat_row["_type"]
    if (beat_row["_cutDirection"] in [5,3,7] and beat_row["_type"] == 0) or (beat_row["_cutDirection"] in [0,8,1,5,3,7] and beat_row["_type"] == 1):
        which_drum+=1
    return which_drum

notes_df["which_drum"] = notes_df.apply(lambda beat_row: which_drum(beat_row), axis = 1)

score_keeper = ScoreKeeper.ScoreKeeper(notes_df)

def detect_hits_input(score_keeper):
    while True:
        events = get_gamepad()
        for event in events:

            if event.state == 255 and event.code == "ABS_Z":
                print("hit left trigger")
                score_keeper.hit(time_so_far, 0)
            elif event.state == 255 and event.code == "ABS_RZ":
                print("hit right trigger")
                score_keeper.hit(time_so_far, 0)

detect_hits_thread = threading.Thread(target=detect_hits_input, args=(score_keeper,))
detect_hits_thread.start()



BPM=beats["_beatsPerMinute"]
notes_df["time_sec"] = notes_df["_time"]*(60.0/BPM)
print(notes_df)

LED_ARRAY_0 = [' ']*LED_COUNT
LED_ARRAY_1 = [' ']*LED_COUNT
LED_ARRAY_2 = [' ']*LED_COUNT
LED_ARRAY_3 = [' ']*LED_COUNT

strip_0_pixels = np.tile(0, (3, 100))
strip_1_pixels = np.tile(0, (3, 100))


def clear_leds():
    global strip_0_pixels, strip_1_pixels
    led.pixels = np.tile(0, (3, config.N_PIXELS))
    strip_0_pixels = np.tile(0, (3, 100))
    strip_1_pixels = np.tile(0, (3, 100))



def update_leds_now():
    global updates_this_second
    global strip_0_pixels, strip_1_pixels
    global shift
    shift=(shift+0.01) % 1.0
    updates_this_second +=1


    for pixel_array in [strip_0_pixels,strip_1_pixels]: #really inefficient
        for num in range(0,100):

            hsv = (colorsys.rgb_to_hsv(float(pixel_array[0][num])/255,float(pixel_array[1][num])/255,float(pixel_array[2][num])/255))
            pixel_array[0][num] = colorsys.hsv_to_rgb((hsv[0]+shift) % 1.0, hsv[1], hsv[2])[0]*255
            pixel_array[1][num] = colorsys.hsv_to_rgb((hsv[0] + shift) % 1.0, hsv[1], hsv[2])[1]*255
            pixel_array[2][num] = colorsys.hsv_to_rgb((hsv[0] + shift) % 1.0, hsv[1], hsv[2])[2]*255




    led.pixels[0][0:100] = np.flip(strip_0_pixels[0])
    led.pixels[1][0:100] = np.flip(strip_0_pixels[1])
    led.pixels[2][0:100] = np.flip(strip_0_pixels[2])
    led.pixels[0][100:200] = (strip_1_pixels[0])
    led.pixels[1][100:200] = (strip_1_pixels[1])
    led.pixels[2][100:200] = (strip_1_pixels[2])
    led.update()



def add_beat_to_strip(led_index, which_drum):
    try:
        if which_drum == 0:
            LED_ARRAY_0[int(led_index)] = 'A'
            strip_0_pixels[0][int(led_index)] = 255
            strip_0_pixels[1][int(led_index)] = 0
            strip_0_pixels[2][int(led_index)] = 200

        if which_drum == 1:
            LED_ARRAY_1[int(led_index)] = 'B'
            strip_1_pixels[0][int(led_index)] = 0
            strip_1_pixels[1][int(led_index)] = 255
            strip_1_pixels[2][int(led_index)] = 200

        if which_drum == 2:
            LED_ARRAY_2[int(led_index)] = 'C'
            strip_0_pixels[0][int(led_index)] = 0
            strip_0_pixels[1][int(led_index)] = 255
            strip_0_pixels[2][int(led_index)] = 200

        if which_drum == 3:
            LED_ARRAY_3[int(led_index)] = 'D'
            strip_1_pixels[0][int(led_index)] = 255
            strip_1_pixels[1][int(led_index)] = 0
            strip_1_pixels[2][int(led_index)] = 200

    except:
        pass

def show_on_leds():
    #update_leds_now()
    update_thread = threading.Thread(target=update_leds_now).start()
    clear_leds()
def print_demo_array():
    #update_leds_now()
    global LED_ARRAY_1, LED_ARRAY_3, LED_ARRAY_2, LED_ARRAY_0
    upcoming_vis_string = ''
    for array in [LED_ARRAY_0,LED_ARRAY_1,LED_ARRAY_2, LED_ARRAY_3]:
        for val in array:
            upcoming_vis_string+=val
        upcoming_vis_string+="\n"

    #print(upcoming_vis_string)

    clear_leds()

    LED_ARRAY_0 = [' '] * LED_COUNT
    LED_ARRAY_1 = [' '] * LED_COUNT
    LED_ARRAY_1 = [' '] * LED_COUNT
    LED_ARRAY_2 = [' '] * LED_COUNT
    LED_ARRAY_3 = [' '] * LED_COUNT


def show_upcoming_beats(upcoming_beats_df, time_in_song):
    #We'll add another column to the df called "led_pos" that is the time until
    #the beat with scaled to which LED should be on presently on the strip

    #score_keeper.update_upcoming(upcoming_beats_df)

    for index, beat in upcoming_beats_df.iterrows():

        add_beat_to_strip(round(((beat["time_sec"]-time_in_song)*(LED_COUNT/STRING_TIME)))-1, beat["which_drum"])


while True:
    time_so_far = (datetime.datetime.now() - start_time).total_seconds()
    iteration_start_time = datetime.datetime.now()

    upcoming_beats = notes_df.query("@time_so_far + 0.00 < time_sec and @time_so_far+@STRING_TIME+0.02 > time_sec")
    show_upcoming_beats(upcoming_beats, time_so_far)



    #print_demo_array()
    show_on_leds()





    try:
        adjustment_time = 0.001 + ((datetime.datetime.now() - iteration_start_time).total_seconds())
        time.sleep(0.02 - adjustment_time) #keep it in sync
    except:
        time.sleep(0.03 - (datetime.datetime.now() - iteration_start_time).total_seconds())  # skip one time if we took longer than 0.02 sec this iteration
        print("miss")

