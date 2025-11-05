from tkinter import *
from tkinter import filedialog, ttk
import pygame
import pygame.mixer as mixer
import os
from mutagen.mp3 import MP3
import time

# Inicijalizacija pygame mixer-a
pygame.init()
mixer.init()

# Globalne varijable
current_song_index = 0
auto_play_next = True  # Kontrola za automatsko preskakanje

root = Tk()
root.geometry("1000x450")
root.title("Music Player")
root.resizable(0, 0)

# GUI
# frames
song_frame = LabelFrame(root, text='Current Song', bg='lightblue', width=600, height=150)
song_frame.place(x=0, y=0)

button_frame = LabelFrame(root, text='Control Buttons', bg='turquoise', width=600, height=180)  # Povećana visina
button_frame.place(y=150)

time_frame = LabelFrame(root, text='Progress', bg='lightgreen', width=600, height=100)
time_frame.place(y=330)  # Pomaknuto prema dolje

listbox_frame = LabelFrame(root, text='Playlist', bg='blue', font=('Times', 15))
listbox_frame.place(x=600, y=0, height=500, width=400)

# variables
current_song = StringVar(root, value='<not selected>')
song_status = StringVar(root, value='<not available>')
current_time = StringVar(root, value='00:00 / 00:00')

# playlist
playlist = Listbox(listbox_frame, font=('helvetica', 10), selectbackground='orange')
scroll_bar = Scrollbar(listbox_frame, orient=VERTICAL)
scroll_bar.pack(side=RIGHT, fill=BOTH)
playlist.config(yscrollcommand=scroll_bar.set)
scroll_bar.config(command=playlist.yview)
playlist.pack(fill=BOTH, padx=5, pady=5)


# Music control functions
def get_song_length(file_path):
    try:
        audio = MP3(file_path)
        return audio.info.length
    except:
        return 0

def format_time(seconds):
    minutes, seconds = divmod(int(seconds), 60)
    return f"{minutes:02d}:{seconds:02d}"

def update_time_display():
    if mixer.music.get_busy():
        current_pos = mixer.music.get_pos() / 1000  # Vrijeme u sekundama
        song_path = playlist.get(ACTIVE)
        if song_path:
            song_length = get_song_length(song_path)
            
            if song_length > 0:
                current_time.set(f"{format_time(current_pos)} / {format_time(song_length)}")
                progress['value'] = (current_pos / song_length) * 100
    
    root.after(1000, update_time_display)  # Ažuriraj svaku sekundu

def play_song(song_name: StringVar, songs_list: Listbox, status: StringVar):
    global current_song_index
    try:
        selected_song = songs_list.get(ACTIVE)
        if not selected_song:
            return
            
        current_song_index = songs_list.curselection()[0]  # Ažuriraj trenutni indeks
        song_name.set(selected_song)
        mixer.music.load(selected_song)
        mixer.music.play()
        status.set("Playing")
        progress['value'] = 0
        update_time_display()
    except Exception as e:
        status.set(f"Error: {str(e)}")

def stop_song(status: StringVar):
    mixer.music.stop()
    status.set("Stopped")
    current_time.set("00:00 / 00:00")
    progress['value'] = 0

def load(listbox):
    music_dir = r'C:\Users\Krunoslav\OneDrive\Dokumenti\Python File\MP3 player\Muzika'
    os.chdir(music_dir)
    listbox.delete(0, END)  # Očisti postojeću listu
    tracks = os.listdir()
    for track in tracks:
        if track.endswith('.mp3'):  # Load only MP3 files
            listbox.insert(END, track)
    if tracks:
        listbox.selection_set(0)
        listbox.activate(0)

def pause_song(status: StringVar):
    mixer.music.pause()
    status.set("Paused")

def resume_song(status: StringVar):
    mixer.music.unpause()
    status.set("Resumed")

def play_next_song():
    global current_song_index
    if playlist.size() > 0:
        current_song_index = (current_song_index + 1) % playlist.size()
        playlist.selection_clear(0, END)
        playlist.selection_set(current_song_index)
        playlist.activate(current_song_index)
        play_song(current_song, playlist, song_status)

def play_previous_song():
    global current_song_index
    if playlist.size() > 0:
        current_song_index = (current_song_index - 1) % playlist.size()
        playlist.selection_clear(0, END)
        playlist.selection_set(current_song_index)
        playlist.activate(current_song_index)
        play_song(current_song, playlist, song_status)

def set_auto_play(value):
    global auto_play_next
    auto_play_next = bool(value)

def check_music_end():
    if not mixer.music.get_busy() and auto_play_next and playlist.size() > 0:
        play_next_song()
    root.after(1000, check_music_end)

def handle_events():
    for event in pygame.event.get():
        if event.type == pygame.USEREVENT:  # Kraj pjesme
            if auto_play_next:
                play_next_song()
    root.after(100, handle_events)

# labels
Label(song_frame, text='Now Playing:', bg='lightblue', font=('Times', 15, 'bold')).place(x=10, y=30)
song_lbl = Label(song_frame, textvariable=current_song, bg='orange', font=('Times', 15), width=40)
song_lbl.place(x=150, y=20)

# Progress bar
progress = ttk.Progressbar(time_frame, orient=HORIZONTAL, length=550, mode='determinate')
progress.place(x=20, y=20)

# Time display
time_label = Label(time_frame, textvariable=current_time, bg='lightgreen', 
                  font=('Times', 14, 'bold'))
time_label.place(x=250, y=50)

# buttons - prvi red
play_btn = Button(button_frame, text='Play', bg='aqua', font=('Georgia', 15), width=11,
                  command=lambda: play_song(current_song, playlist, song_status))
play_btn.place(x=15, y=15)

pause_btn = Button(button_frame, text='Pause', bg='aqua', font=('Georgia', 15), width=11,
                   command=lambda: pause_song(song_status))
pause_btn.place(x=160, y=15)

stop_btn = Button(button_frame, text='Stop', bg='aqua', font=('Georgia', 15), width=11,
                  command=lambda: stop_song(song_status))
stop_btn.place(x=305, y=15)

resume_btn = Button(button_frame, text='Resume', bg='aqua', font=('Georgia', 15), width=11,
                    command=lambda: resume_song(song_status))
resume_btn.place(x=450, y=15)

# buttons - drugi red
prev_btn = Button(button_frame, text='Previous', bg='aqua', font=('Georgia', 15), width=11,
                 command=play_previous_song)
prev_btn.place(x=15, y=60)

next_btn = Button(button_frame, text='Next', bg='aqua', font=('Georgia', 15), width=11,
                 command=play_next_song)
next_btn.place(x=160, y=60)

load_btn = Button(button_frame, text='Load Directory', bg='aqua', font=('Georgia', 15), width=23,
                  command=lambda: load(playlist))
load_btn.place(x=305, y=60)

auto_play_var = IntVar(value=1)
auto_play_check = Checkbutton(button_frame, text='Auto Play Next', variable=auto_play_var,
                             bg='turquoise', font=('Georgia', 12),
                             command=lambda: set_auto_play(auto_play_var.get()))
auto_play_check.place(x=15, y=110)

Label(root, textvariable=song_status, bg='Steelblue', font=('Times', 9), justify=LEFT).pack(side=BOTTOM, fill=X)


# Pokreni provjeru kraja pjesme
check_music_end()
handle_events()

root.mainloop()