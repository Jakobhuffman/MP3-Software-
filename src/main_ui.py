import sqlite3
import json
import os
from PySide6.QtWidgets import QMainWindow, QFileDialog, QInputDialog, QListWidget, QVBoxLayout, QWidget, QHBoxLayout, QPushButton, QListWidgetItem, QSlider, QLabel, QCheckBox
from PySide6.QtCore import Qt, QTimer  # Added QTimer import
from PySide6.QtGui import QDropEvent, QDragEnterEvent
import pygame.mixer
from src.main_window import Ui_MainWindow
from src.dialog import AboutDialog
import resources.img_rc

class SoundSourceWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Enforce size
        self.resize(640, 480)
        self.setMinimumSize(640, 480)

        # Set up layout with two columns: playlists and songs, plus controls
        self.central_widget = QWidget(self)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.addWidget(self.ui.centralwidget)  # Original UI content

        # Horizontal layout for playlists and songs
        self.list_layout = QHBoxLayout()
        self.main_layout.addLayout(self.list_layout)

        # Playlist list
        self.playlist_list = QListWidget(self.central_widget)
        self.playlist_list.setMaximumWidth(200)
        self.list_layout.addWidget(self.playlist_list)
        self.playlist_list.itemClicked.connect(self.on_playlist_selected)

        # Songs list
        self.songs_list = QListWidget(self.central_widget)
        self.list_layout.addWidget(self.songs_list)
        self.songs_list.itemClicked.connect(self.select_song)  # Set current_song on single-click
        self.songs_list.itemDoubleClicked.connect(self.play_selected_song)

        # Playback controls
        self.control_layout = QHBoxLayout()
        self.play_button = QPushButton("Play")
        self.pause_button = QPushButton("Pause")
        self.stop_button = QPushButton("Stop")
        self.next_button = QPushButton("Next")
        self.play_all_checkbox = QCheckBox("Play All")  # Toggle for continuous playback
        self.volume_label = QLabel("Volume:")
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.control_layout.addWidget(self.play_button)
        self.control_layout.addWidget(self.pause_button)
        self.control_layout.addWidget(self.stop_button)
        self.control_layout.addWidget(self.next_button)
        self.control_layout.addWidget(self.play_all_checkbox)
        self.control_layout.addWidget(self.volume_label)
        self.control_layout.addWidget(self.volume_slider)
        self.main_layout.addLayout(self.control_layout)

        self.play_button.clicked.connect(self.play)
        self.pause_button.clicked.connect(self.pause)
        self.stop_button.clicked.connect(self.stop)
        self.next_button.clicked.connect(self.next_song)
        self.volume_slider.valueChanged.connect(self.set_volume)
        self.play_all_checkbox.stateChanged.connect(self.toggle_play_all)

        self.setCentralWidget(self.central_widget)

        # Define paths (moved to local temp folder)
        self.project_root = r"C:\temp"
        self.db_path = os.path.join(self.project_root, "playlists.db")
        self.json_path = os.path.join(self.project_root, "playlists.json")

        # Initialize pygame mixer with error handling
        try:
            pygame.mixer.init()
            print("Pygame mixer initialized")
        except Exception as e:
            print(f"Error initializing pygame mixer: {e}")

        self.current_song = None
        self.song_index = 0
        self.current_playlist_songs = []
        self.playlists = {}  # Hash map for playlists and songs
        self.play_all = False

        # Set initial volume
        pygame.mixer.music.set_volume(0.5)

        self.init_db()
        self.load_playlists()
        self.update_playlist_list()

        # Connect menu actions
        self.ui.actionadd_song.triggered.connect(self.add_song)
        print("Connected actionadd_song")
        self.ui.actionremove.triggered.connect(self.remove_song)
        print("Connected actionremove")
        self.ui.actionAdd_Playlist.triggered.connect(self.add_playlist)
        print("Connected actionAdd_Playlist")
        self.ui.action_About.triggered.connect(self.show_about)
        print("Connected action_About")

        self.setAcceptDrops(True)
        self.songs = []
        self.current_playlist = None

    def set_volume(self):
        volume = self.volume_slider.value() / 100.0
        pygame.mixer.music.set_volume(volume)
        print(f"Volume set to: {volume}")

    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS playlists
                         (id INTEGER PRIMARY KEY, name TEXT, created_at TIMESTAMP)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS songs
                         (id INTEGER PRIMARY KEY, path TEXT, playlist_id INTEGER,
                          FOREIGN KEY (playlist_id) REFERENCES playlists(id))''')
        conn.commit()
        conn.close()
        print(f"Database initialized at {self.db_path}")

    def load_playlists(self):
        self.playlists.clear()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM playlists")
        for playlist_id, name in cursor.fetchall():
            cursor.execute("SELECT path FROM songs WHERE playlist_id=?", (playlist_id,))
            songs = [row[0] for row in cursor.fetchall()]
            self.playlists[name] = {"id": playlist_id, "songs": songs}
        conn.close()
        print(f"Loaded playlists: {list(self.playlists.keys())}")

    def update_playlist_list(self):
        self.playlist_list.clear()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM playlists")
        for playlist_id, name in cursor.fetchall():
            item = QListWidgetItem(name)
            item.setData(Qt.UserRole, playlist_id)
            self.playlist_list.addItem(item)
        conn.close()

    def on_playlist_selected(self, item):
        playlist_id = item.data(Qt.UserRole)
        self.current_playlist = playlist_id
        playlist_name = item.text()
        self.statusBar().showMessage(f"Selected playlist: {playlist_name}", 5000)
        self.update_songs_list()
        self.update_song_list(playlist_name)

    def update_songs_list(self):
        self.songs_list.clear()
        if self.current_playlist:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT path FROM songs WHERE playlist_id=?", (self.current_playlist,))
            for row in cursor.fetchall():
                self.songs_list.addItem(os.path.basename(row[0]))
            conn.close()

    def update_song_list(self, playlist_name):
        self.current_playlist_songs = self.playlists.get(playlist_name, {}).get("songs", [])
        self.song_index = 0
        if not self.current_playlist_songs:
            self.current_song = None
        elif self.song_index < len(self.current_playlist_songs):
            self.current_song = self.current_playlist_songs[self.song_index]
        print(f"Updated song list for {playlist_name}: {self.current_playlist_songs}")

    def select_song(self, item):
        song_name = item.text()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT path FROM songs WHERE playlist_id=? AND path LIKE ?",
                      (self.current_playlist, f"%{song_name}"))
        song_path = cursor.fetchone()
        conn.close()
        if song_path:
            self.current_song = song_path[0]
            self.song_index = self.current_playlist_songs.index(self.current_song)
            print(f"Selected song: {self.current_song}")

    def play_selected_song(self, item):
        song_name = item.text()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT path FROM songs WHERE playlist_id=? AND path LIKE ?",
                      (self.current_playlist, f"%{song_name}"))
        song_path = cursor.fetchone()
        conn.close()
        if song_path:
            self.current_song = song_path[0]
            self.song_index = self.current_playlist_songs.index(self.current_song)
            print(f"Attempting to play: {self.current_song}")
            try:
                pygame.mixer.music.load(self.current_song)
                pygame.mixer.music.play()
                self.statusBar().showMessage(f"Playing: {song_name}", 5000)
                if self.play_all:
                    self.schedule_next()
            except Exception as e:
                print(f"Error playing song: {e}")
                self.statusBar().showMessage(f"Error playing {song_name}: {e}", 5000)

    def play(self):
        print("Play button clicked")
        if self.current_song:
            print(f"Playing: {self.current_song}")
            try:
                pygame.mixer.music.load(self.current_song)
                pygame.mixer.music.play()
                self.statusBar().showMessage(f"Playing: {os.path.basename(self.current_song)}", 5000)
                if self.play_all:
                    self.schedule_next()
            except Exception as e:
                print(f"Error playing song: {e}")
                self.statusBar().showMessage(f"Error playing {os.path.basename(self.current_song)}: {e}", 5000)
        else:
            print("No song selected")
            self.statusBar().showMessage("Select a song first!", 5000)

    def pause(self):
        pygame.mixer.music.pause()
        self.statusBar().showMessage("Paused", 5000)

    def stop(self):
        pygame.mixer.music.stop()
        self.statusBar().showMessage("Stopped", 5000)
        self.play_all = False  # Turn off Play All when stopped

    def next_song(self):
        print("Next button clicked")
        if self.current_playlist_songs:
            self.song_index = (self.song_index + 1) % len(self.current_playlist_songs)
            self.current_song = self.current_playlist_songs[self.song_index]
            print(f"Skipping to: {self.current_song}")
            try:
                pygame.mixer.music.load(self.current_song)
                pygame.mixer.music.play()
                song_name = os.path.basename(self.current_song)
                self.statusBar().showMessage(f"Playing: {song_name}", 5000)
                if self.play_all:
                    self.schedule_next()
            except Exception as e:
                print(f"Error playing song: {e}")
                self.statusBar().showMessage(f"Error playing {song_name}: {e}", 5000)
        else:
            print("No songs in playlist")
            self.statusBar().showMessage("No songs to skip!", 5000)

    def toggle_play_all(self, state):
        self.play_all = state == Qt.Checked
        print(f"Play All toggled to: {self.play_all}")
        if self.play_all and self.current_song:
            self.schedule_next()

    def schedule_next(self):
        if self.play_all and self.current_playlist_songs:
            pygame.mixer.music.set_endevent()  # Use pygame event for end detection
            QTimer.singleShot(1000, self.check_playback)  # Check every second

    def check_playback(self):
        if self.play_all and not pygame.mixer.music.get_busy() and self.current_playlist_songs:
            self.next_song()  # Move to next song when current one ends
        elif self.play_all:
            QTimer.singleShot(1000, self.check_playback)  # Keep checking

    def create_playlist(self, name):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO playlists (name, created_at) VALUES (?, datetime('now'))", (name,))
        playlist_id = cursor.lastrowid
        conn.commit()
        conn.close()
        self.current_playlist = playlist_id
        self.playlists[name] = {"id": playlist_id, "songs": []}
        self.save_to_json()
        self.update_playlist_list()
        self.update_songs_list()
        self.update_song_list(name)

    def add_song_to_playlist(self, file_path):
        if file_path.lower().endswith('.mp3'):
            self.songs.append(file_path)
            if self.current_playlist:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("INSERT INTO songs (path, playlist_id) VALUES (?, ?)",
                             (file_path, self.current_playlist))
                conn.commit()
                conn.close()
                playlist_name = self.playlist_list.currentItem().text()
                if playlist_name in self.playlists:
                    self.playlists[playlist_name]["songs"].append(file_path)
                self.save_to_json()
                self.update_songs_list()
                self.update_song_list(playlist_name)
            else:
                self.statusBar().showMessage("Select a playlist first!", 5000)

    def save_to_json(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM playlists")
        playlists = cursor.fetchall()
        data = {}
        for playlist_id, name in playlists:
            cursor.execute("SELECT path FROM songs WHERE playlist_id=?", (playlist_id,))
            songs = [row[0] for row in cursor.fetchall()]
            data[name] = {"id": playlist_id, "songs": songs}
        conn.close()
        with open(self.json_path, 'w') as f:
            json.dump(data, f, indent=4)

    def remove_song(self):
        selected = self.songs_list.currentItem()
        if selected and self.current_playlist:
            song_name = selected.text()
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT path FROM songs WHERE playlist_id=? AND path LIKE ?",
                         (self.current_playlist, f"%{song_name}"))
            song_path = cursor.fetchone()
            if song_path:
                cursor.execute("DELETE FROM songs WHERE playlist_id=? AND path=?",
                             (self.current_playlist, song_path[0]))
                conn.commit()
                playlist_name = self.playlist_list.currentItem().text()
                if playlist_name in self.playlists:
                    if song_path[0] in self.playlists[playlist_name]["songs"]:
                        self.playlists[playlist_name]["songs"].remove(song_path[0])
                self.statusBar().showMessage(f"Removed song: {song_name}", 5000)
                self.save_to_json()
                self.update_songs_list()
                self.update_song_list(playlist_name)
            conn.close()
        else:
            self.statusBar().showMessage("Select a song to remove!", 5000)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.toLocalFile().lower().endswith('.mp3'):
                    event.acceptProposedAction()
                    return
        event.ignore()

    def dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            self.add_song_to_playlist(file_path)
        event.acceptProposedAction()

    def add_song(self):
        print("add_song triggered")
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Add Song", "", "Audio Files (*.mp3)"
        )
        if file_path:
            self.add_song_to_playlist(file_path)

    def add_playlist(self):
        print("add_playlist triggered")
        name, ok = QInputDialog.getText(self, "New Playlist", "Enter playlist name:")
        if ok and name:
            self.create_playlist(name)
            self.statusBar().showMessage(f"Created playlist: {name}", 5000)

    def show_about(self):
        print("show_about triggered")
        about_dialog = AboutDialog(self)
        about_dialog.exec()