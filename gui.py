# Importing necessary packages
import shutil
import tkinter as tk
from tkinter import *
from tkinter import messagebox, filedialog
import pathlib
import subprocess 
import os
from video import convert_video_to_audio
import speech_recognition as sr
from pydub import AudioSegment
from pydub.silence import split_on_silence
from lsa_summarizer import lsa_summarize
import time

r = sr.Recognizer();

text_file_name = "final_text.txt";
summarized_text = "summary.txt";

destination_path = pathlib.Path(__file__).parent.absolute()
	
def CreateWidgets():
	link_Label = Label(root, text ="Select file to summarize: ",
					bg = "#E8D579")
	link_Label.grid(row = 1, column = 0,
					pady = 5, padx = 5)
	
	root.sourceText = Entry(root, width = 50,
							textvariable = sourceLocation)
	root.sourceText.grid(row = 1, column = 1,
						pady = 5, padx = 5,
						columnspan = 2)
	
	source_browseButton = Button(root, text ="Browse",
								command = source_browse, width = 15)
	source_browseButton.grid(row = 1, column = 3,
							pady = 5, padx = 5)
	
	root.info_box = Text(root, height=10, width=50);
	root.info_box.grid(row=5, column=2, padx=2, pady=2);

	moveButton = Button(root, text ="Start summarization",
						command = start_summarization, width = 15)
	moveButton.grid(row = 3, column = 2,
					pady = 5, padx = 5)

	

def source_browse():
	root.files_list = list(filedialog.askopenfilenames())
	root.sourceText.insert('1', root.files_list)
	
	
def start_summarization():
	files_list = root.files_list
	destination_location = destination_path
	for f in files_list:
		shutil.copy(f, destination_location)
	split_file = files_list[0].split('/');
	file_type = split_file[-1].split('.');
	if(file_type[-1] == 'txt'):
		text = "";
		with open(split_file[len(split_file) - 1], 'r', encoding="utf-8") as file:
			text = file.read();
		summary = lsa_summarize(text);
		summary = '\n'.join(summary);
		with open(summarized_text, 'w', encoding="utf-8") as out:
			out.writelines(summary);
		root.info_box.insert(tk.END, 'Summarization completed. Summarized content can be found in summary.txt');
		os.startfile(summarized_text);
		time.sleep(5);
		# root.destroy();
		return

	video_file = split_file[-1];
	audio_file = "audio.wav";
	root.info_box.insert(tk.END, 'Converting Video file to Audio file...\n');
	time.sleep(1);
	convert_video_to_audio(video_file);
	root.info_box.insert(tk.END, 'Coverted to audio file. Transcribing file...\n');
	time.sleep(1);
	transcribe_audio_file(audio_file);
	root.info_box.insert(tk.END, 'Transcription completed. Summarizing text...\n');
	time.sleep(1);
	text = "";
	with open(text_file_name, 'r', encoding="utf-8") as file:
		text = file.read();
	summary = lsa_summarize(text);
	summary = '\n'.join(summary);
	with open(summarized_text, 'w', encoding="utf-8") as out:
		out.writelines(summary);
	root.info_box.insert(tk.END, 'Summarization completed. Summarized content can be found in summary.txt');
	os.startfile(summarized_text);
	time.sleep(5);
	root.destroy();


def transcribe_audio_file(filename):
	sound = AudioSegment.from_wav(filename);
	chunks = split_on_silence(sound, min_silence_len=700, silence_thresh=sound.dBFS-14,);
	folder_name="audio-chunks";
	if not os.path.isdir(folder_name):
		os.mkdir(folder_name);
	whole_text = "";

	for i, audio_chunk in enumerate(chunks, start=1):
		chunk_filename=os.path.join(folder_name, f"chunk{i}.wav");
		audio_chunk.export(chunk_filename, format="wav");

		with sr.AudioFile(chunk_filename) as source:
			audio_listened = r.record(source);
			try:
				text = r.recognize_google(audio_listened);
			except sr.UnknownValueError as e:
				print(str(e));
			else:
				text = f"{text.capitalize()}. ";
				whole_text += text;


	with open('final_text.txt', 'w') as out:
		out.writelines(whole_text);




root = tk.Tk()
root.geometry("720x320")
root.title("Text Summarizer");
root.config(background = "#c2c2c2");

sourceLocation = StringVar()
destinationLocation = StringVar()

CreateWidgets()

root.mainloop()
