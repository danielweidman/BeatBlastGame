class ScoreKeeper():

    def __init__(self, beats_df):
        self.beats_df = beats_df
        self.beats_df["hit_yet"] = beats_df.apply(lambda row: False, axis = 1)


    def hit(self, time_in_song, which_drum):
        if which_drum == 1:
            acceptable_range = self.beats_df.query("@time_in_song-0.10 < time_sec and @time_in_song+0.10 > time_sec and hit_yet == False and (1 == which_drum or 3 == which_drum)")
        if which_drum == 0:
            acceptable_range = self.beats_df.query("@time_in_song-0.10 < time_sec and @time_in_song+0.10 > time_sec and hit_yet == False and (0 == which_drum or 2 == which_drum)")

        if len(acceptable_range) >= 1:
            for index, beat_row in acceptable_range.iterrows():
                if abs(time_in_song - beat_row["time_sec"]) < 0.03:
                    print("Perfect!")
                elif abs(time_in_song - beat_row["time_sec"]) < 0.06:
                    print("Great!")
                elif abs(time_in_song - beat_row["time_sec"]) < 0.08:
                    print("Good!")
                else:
                    print("Okay.")




            for ind in acceptable_range:
                self.beats_df["hit_yet"].loc[ind] = True

        else:
            print("Missed")









