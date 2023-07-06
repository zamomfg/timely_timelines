from datetime import datetime
import time
from dateutil import parser as datetimeparser
import numpy as np
import pandas as pd
import os
import argparse
import drawsvg as draw


x_size = 400
y_size = 150

x_max = x_size / 2
x_min = -x_max
y_min = -y_size / 2
y_max = -y_min

def calculate_times(time_str):
    time_obj = datetimeparser.parse(time_str)
    # time_obj = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
    unix_time = time.mktime(time_obj.timetuple())

    return {"time": time_obj, "unix_time" : unix_time}

def create_canvas(x_size, y_size):
    d = draw.Drawing(x_size, y_size, origin="center")

    d.append(draw.Rectangle(x_min, y_min, x_size, y_size, fill="#ffff"))

    print("canvas x min:", x_min,"x max:", x_max, "y min:", y_min, "y max:", y_max)

    return d

class Timeline:

    def __init__(self, canvas, x_pos_start, x_pos_end, y_pos, start_time=None, end_time=None, timeline_padding = 0.8, dot_endning=False):
        if start_time != None:
            start_time = calculate_times(start_time)
            self.start_time = start_time["time"]
            self.unix_start_time = start_time["unix_time"]
        else:
            self.start_time = None
            self.unix_start_time = None

        if end_time != None:
            end_time = calculate_times(end_time)
            self.end_time = end_time["time"]
            self.unix_end_time = end_time["unix_time"]
        else:
            self.end_time = None
            self.unix_end_time = None

        self.timeline_start = x_pos_start
        self.timeline_end = x_pos_end
        self.y_pos = y_pos
        self.canvas = canvas
        self.entry_list = []
        self.timeline_padding = timeline_padding
        self.dot_endning = dot_endning




    def add_entry(self, datetime_str, text, position="alternating"):

        if position != "alternating" and position != "up" and position != "down":
            raise ValueError("position can only have the values: \"up\", \"down\" or \"alternating\" ")

        entry = {"datetime" : datetime_str, "text" : text, "position" : position}
        self.entry_list.append(entry)


    # TODO create entry class
    def render_timeline_entry(self, str_datetime, text, position, index):

        time_calc = calculate_times(str_datetime)
        unix_entry_time = time_calc["unix_time"]
        entry_datetime = time_calc["time"]
        date_x_pos = (unix_entry_time - self.unix_start_time)/(self.unix_end_time - self.unix_start_time) * ((self.timeline_end * self.timeline_padding) - (self.timeline_start * self.timeline_padding)) + (self.timeline_start * self.timeline_padding)

        print(str_datetime, entry_datetime, text, date_x_pos)
        print("self.unix_start_time", self.unix_start_time, "self.unix_end_time", self.unix_end_time)

        text_y_offset = 7

        date_y_hight = 14
        start_line_y = self.y_pos + 4
        end_line_y = start_line_y + date_y_hight
        text_y_pos =  end_line_y + text_y_offset

        if position == "alternating" and index % 2 == 0:
            position = "up"

        if position == "up":
            date_y_hight = -date_y_hight
            start_line_y = -start_line_y
            end_line_y = -end_line_y
            text_y_pos = end_line_y  - text_y_offset

        line = draw.Lines(date_x_pos, start_line_y ,date_x_pos, end_line_y + date_y_hight, close=False, fill="#eeee00", stroke="black", stroke_width=1, stroke_linecap="round")
        self.canvas.append(line)


        fontSize = 6
        text_lines = [text, str_datetime]
        self.canvas.append(draw.Text(text_lines, font_size=fontSize, font_family="Georgia", x=date_x_pos+2, y=text_y_pos,
        text_anchor="auto", dominant_baseline="auto"))

    def render(self):

        if len(self.entry_list) > 1 and self.start_time == None:
            start_time = calculate_times(self.entry_list[0]["datetime"])
            self.start_time = start_time["time"]
            self.unix_start_time = start_time["unix_time"]
        if len(self.entry_list) > 2 and self.end_time == None:
            end_time = calculate_times(self.entry_list[-1]["datetime"])
            self.end_time = end_time["time"]
            self.unix_end_time = end_time["unix_time"]

            print("new start and end times!", self.start_time, self.end_time)

        end = self.timeline_end
        if self.dot_endning:
            dot_size = 10
            dot_start = self.timeline_end - dot_size
            self.render_dotted_line(dot_start, self.timeline_end)
            end = dot_start

        line = draw.Lines(self.timeline_start, self.y_pos, end, self.y_pos, close=False, fill="#eeee00", stroke="black", stroke_width=1, stroke_linecap="round")
        self.canvas.append(line)




        # print("render", len(self.entry_list))
        for index, entry in enumerate(self.entry_list):
            self.render_timeline_entry(entry["datetime"], entry["text"], entry["position"], index)

        self.canvas.set_pixel_scale(2)
        self.canvas.save_svg("example.svg")

    def render_dotted_line(self, start_x_pos, end_x_pos, nr_dotts=4):
        
        len = end_x_pos - start_x_pos
        base_line_length = 0.5
        base_break_length = 1.5
        line_length = (len/(nr_dotts*2)) * base_line_length
        break_length = (len/(nr_dotts*2)) * base_break_length

        for i in range(0, nr_dotts):
            start = start_x_pos + break_length + (break_length + line_length) * i
            end = start + line_length

            line = draw.Lines(start, self.y_pos, end, self.y_pos, close=False, fill="#eeee00", stroke="black", stroke_width=1, stroke_linecap="round")
            self.canvas.append(line)



if __name__ == "__main__":

    canvas = create_canvas(x_size, y_size)

    timeline_len = 0.8
    cap_len = ((x_size / 2) * timeline_len)
    timeline_x_start = -cap_len
    timeline_x_end = cap_len

    timeline = Timeline(canvas, timeline_x_start, timeline_x_end, 0, timeline_padding=0.95, end_time="2023-06-14", dot_endning=True)
    timeline.add_entry("2023-06-06 13:44:33", "text start")
    timeline.add_entry("2023-06-06 18:44:33", "text near start")
    timeline.add_entry("2023-06-08 14:36", "text midddddddddle")
    timeline.add_entry("2023-06-09", "text midddddddddle 22222222")
    timeline.add_entry("2023-06-11", "text end")

    timeline.render()