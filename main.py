from moviepy import VideoFileClip
from moviepy.config import check
import argparse
import os
import csv
import imageio_ffmpeg

def video_clipper(video_file_path, time_extraction_csv):
    try:
        clip = VideoFileClip(video_file_path, audio=False)
        csv_file = open(time_extraction_csv, newline='')
        print('Video and CSV Loaded Successfully')
    except Exception as e:
        print(e.with_traceback())
        
    #TODO: using moviepy clip scenes from video in reference to time logs
    time_logs = csv.DictReader(csv_file)
    
    for logs in time_logs:
        start = float(convert_time_to_seconds(logs.get('start_time')))
        end = float(convert_time_to_seconds(logs.get('end_time')))
        
        trimmed_clip = clip.subclipped(start, end)
        trimmed_clip.write_videofile(f'{logs.get('filename')}.mp4')
    
    clip.reader.close()
    clip.audio.reader.close() if clip.audio else None
    csv_file.close()


def convert_time_to_seconds(time:str):
    # TIME FORMAT: HH:MM:SS.MS
    hours, minutes, seconds = time.split(':')
    calculated_hours = convert_hours_to_seconds(hours)
    calculated_minutes = convert_minutes_to_seconds(minutes)
    return calculated_hours + calculated_minutes + int(seconds)
    

def convert_hours_to_seconds(hours):
    return int(hours) * 3600


def convert_minutes_to_seconds(minutes):
    return int(minutes) * 60
    
            
def verify_file_path(file_path):
    if (os.path.exists(file_path)):
        return file_path
    else:
        raise Exception (os.error.with_traceback())   


if __name__ == "__main__":
    # Set the correct ffmpeg path
    ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
    os.environ["IMAGEIO_FFMPEG_EXE"] = ffmpeg_path

    parser = argparse.ArgumentParser(description='Clip Extraction to Video')
    
    parser.add_argument('--video-path', required=False, type=str)
    parser.add_argument('--time-csv', required=True, type=str)
    
    args = parser.parse_args()
    
    video_path = verify_file_path(args.video_path)
    csv_path = verify_file_path(args.time_csv)

    video_clipper(video_path, csv_path)