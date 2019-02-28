from playsound import playsound
import pyglet, threading, datetime, time
import pandas as pd
import subprocess, platform

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

BPM=beats["_beatsPerMinute"]
notes_df["time_sec"] = notes_df["_time"]*(60.0/BPM)
print(notes_df)

LED_ARRAY_0 = [' ']*LED_COUNT
LED_ARRAY_1 = [' ']*LED_COUNT
LED_ARRAY_2 = [' ']*LED_COUNT
LED_ARRAY_3 = [' ']*LED_COUNT
def add_beat_to_strip(led_index, which_drum):
    try:
        if which_drum == 0:
            LED_ARRAY_0[int(led_index)] = 'A'

        if which_drum == 1:
            LED_ARRAY_1[int(led_index)] = 'B'

        if which_drum == 2:
            LED_ARRAY_2[int(led_index)] = 'C'

        if which_drum == 3:
            LED_ARRAY_3[int(led_index)] = 'D'
    except:
        pass

def print_demo_array():
    global LED_ARRAY_1, LED_ARRAY_3, LED_ARRAY_2, LED_ARRAY_0
    upcoming_vis_string = ''
    for array in [LED_ARRAY_0,LED_ARRAY_1,LED_ARRAY_2, LED_ARRAY_3]:
        for val in array:
            upcoming_vis_string+=val
        upcoming_vis_string+="\n"

    print(upcoming_vis_string)


    LED_ARRAY_0 = [' '] * LED_COUNT
    LED_ARRAY_1 = [' '] * LED_COUNT
    LED_ARRAY_2 = [' '] * LED_COUNT
    LED_ARRAY_3 = [' '] * LED_COUNT


def show_upcoming_beats(upcoming_beats_df, time_in_song):
    #We'll add another column to the df called "led_pos" that is the time until
    #the beat with scaled to which LED should be on presently on the strip

    for index, beat in upcoming_beats_df.iterrows():
        which_drum = 2 * beat["_type"]
        if (beat["_cutDirection"] in [5,3,7] and beat["_type"] == 0) or (beat["_cutDirection"] in [0,8,1,5,3,7] and beat["_type"] == 1):
            which_drum+=1
        add_beat_to_strip(round(((beat["time_sec"]-time_in_song)*(LED_COUNT/1.98)))-1, which_drum)


while True:
    time_so_far = (datetime.datetime.now() - start_time).total_seconds()
    iteration_start_time = datetime.datetime.now()

    current_beats = notes_df.query("@time_so_far < time_sec and @time_so_far+0.02 >= time_sec")
    upcoming_beats = notes_df.query("@time_so_far + 0.02 < time_sec and @time_so_far+2.0 > time_sec")
    show_upcoming_beats(upcoming_beats, time_so_far)


    if len(current_beats) > 0:
        #print(current_beats)
        pass


    print_demo_array()

    try:
        adjustment_time = 0.001 + ((datetime.datetime.now() - iteration_start_time).total_seconds())
        time.sleep(0.02 - adjustment_time) #keep it in sync
    except:
        time.sleep(0.04 - (datetime.datetime.now() - iteration_start_time).total_seconds())  # skip one time if we took longer than 0.02 sec this iteration
        print("miss")


