import moviepy.editor as mp

def convert_video_to_audio(file):
	clip = mp.VideoFileClip(file);
	clip.audio.write_audiofile("audio.wav");