#!/usr/bin/env python3
"""
Audio Player with GPIO Control
Plays random audio files from a directory on continuous loop.
Controlled by switch on GPIO 17.
"""

import os
import random
import time
import vlc
from gpiozero import Button
from pathlib import Path

# Configuration
MUSIC_DIR = os.path.expanduser("~/Music/parents")
SUPPORTED_FORMATS = ('.mp3', '.wav', '.ogg', '.flac', '.m4a', '.aac')

class RandomAudioPlayer:
    def __init__(self, music_directory):
        self.music_dir = music_directory
        self.playlist = []
        self.current_index = 0
        self.vlc_instance = vlc.Instance('--no-video', '--quiet')
        self.player = self.vlc_instance.media_player_new()
        self.is_playing = False
        
        # GPIO button on pin 17 (active low - connects to ground)
        self.button = Button(17)
        
        # Set up button event handlers
        self.button.when_pressed = self.start_playing
        self.button.when_released = self.stop_playing
        
        # Load all audio files from directory
        self.load_playlist()
        
    def load_playlist(self):
        """Scan directory recursively for audio files"""
        print(f"Scanning {self.music_dir} for audio files...")
        self.playlist = []
        
        if not os.path.exists(self.music_dir):
            print(f"Error: Directory {self.music_dir} does not exist!")
            return
            
        for root, dirs, files in os.walk(self.music_dir):
            for file in files:
                if file.lower().endswith(SUPPORTED_FORMATS):
                    full_path = os.path.join(root, file)
                    self.playlist.append(full_path)
        
        if self.playlist:
            random.shuffle(self.playlist)
            print(f"Found {len(self.playlist)} audio files")
        else:
            print(f"No audio files found in {self.music_dir}")
    
    def play_next(self):
        """Play the next track in the shuffled playlist"""
        if not self.playlist:
            print("No tracks to play")
            return
            
        # Get next track
        track = self.playlist[self.current_index]
        print(f"Playing: {os.path.basename(track)}")
        
        # Load and play media
        media = self.vlc_instance.media_new(track)
        self.player.set_media(media)
        self.player.play()
        
        # Move to next track, loop back to start if at end
        self.current_index = (self.current_index + 1) % len(self.playlist)
        
        # Reshuffle when we complete the playlist
        if self.current_index == 0:
            print("Reshuffling playlist...")
            random.shuffle(self.playlist)
    
    def start_playing(self):
        """Start playback when button is pressed"""
        if not self.is_playing:
            print("Switch ON - Starting playback")
            self.is_playing = True
            self.play_next()
    
    def stop_playing(self):
        """Stop playback when button is released"""
        if self.is_playing:
            print("Switch OFF - Stopping playback")
            self.is_playing = False
            self.player.stop()
    
    def run(self):
        """Main loop to monitor playback and switch to next track"""
        print("Audio player ready!")
        print(f"Music directory: {self.music_dir}")
        print("Toggle GPIO 17 switch to start/stop playback")
        print("Press Ctrl+C to exit\n")
        
        try:
            while True:
                # Check if we need to play the next track
                if self.is_playing:
                    # Check if current track has finished
                    state = self.player.get_state()
                    if state == vlc.State.Ended or state == vlc.State.Stopped:
                        self.play_next()
                
                time.sleep(0.5)  # Check every 500ms
                
        except KeyboardInterrupt:
            print("\nShutting down...")
            self.player.stop()
            print("Goodbye!")

if __name__ == "__main__":
    player = RandomAudioPlayer(MUSIC_DIR)
    player.run()
