# IMPORTS

# General
import sys
import os
import time
import traceback
import threading as th

# GUI
import pygame as pg
import easygui

# Audio
import pyaudio
import speech_recognition as sp_rec
import wave

# Clipboard
import pyperclip

# Constants
from constants import *

# Color
import color

# Font
import font

# Draw
if not "draw" in sys.modules: import draw


# CLASSES

# Recorder
class Recorder(th.Thread):

    # CONSTRUCTOR
    def __init__(self):

        # Initialize thread
        th.Thread.__init__(self, name="Recorder Thread")

        # Define recorder variables
        self.recording = False
        self.stream = None
        self.frames = []
        self.record_start_time = 0
        self.record_end_time = 0

        # Print confirmation
        print("RECORDER: Initialized.")


    # METHODS

    # Run and start recording
    def run(self) -> None:

        # Create and open a audio stream
        self.stream = pa.open(format=SAMPLE_FORMAT, channels=CHANNELS, rate=SAMPLES_PER_SECOND, frames_per_buffer=CHUNK_SIZE, input=True)

        # Set recording to true
        self.recording = True

        # Set the start record time
        self.record_start_time = time.time()

        # Recording loop
        print("RECORDER: Start recording ...")
        while self.recording:

            # Store the data in chunks
            for i in range(int(SAMPLES_PER_SECOND / CHUNK_SIZE)):
                data = self.stream.read(CHUNK_SIZE, False)
                self.frames.append(data)
                self.record_end_time = time.time()

        # Stop and close the stream
        print(f"RECORDER: Stopped recording. (Length: {format_time(self.get_record_time())})")
        self.stream.stop_stream()
        self.stream.close()
        self.save()

    # Stop recording
    def stop(self) -> None:

        # Set recording to false
        self.recording = False

    # Save the recorded audio to file
    def save(self) -> None:

        # Open the wav file
        print(f"RECORDER: Save audio at '{OUTPUT_AUDIO}' ...")
        with wave.open(OUTPUT_AUDIO, "wb") as file:

            # Set the data
            file.setnchannels(CHANNELS)
            file.setsampwidth(pa.get_sample_size(SAMPLE_FORMAT))
            file.setframerate(SAMPLES_PER_SECOND)

            # Write the frames
            file.writeframes(b''.join(self.frames))
        print(f"RECORDER: Audio saved.")

    # Get recording time
    def get_record_time(self) -> float:

        # Return the calculated time
        if self.record_start_time == 0 or self.record_end_time == 0:
            return 0
        else:
            return float(f"{self.record_end_time - self.record_start_time:.2f}")


# Player
class Player(th.Thread):

    # CONSTRUCTOR
    def __init__(self):

        # Initialize thread
        th.Thread.__init__(self, name="Player Thread")

        # Define player variables
        self.playing = False
        self.stream = None
        self.frames = []

        # Print confirmation
        print("PLAYER: Initialized.")


    # METHODS

    # Run and start playing
    def run(self) -> None:

        # Create and open a audio stream
        self.stream = pa.open(format=SAMPLE_FORMAT, channels=CHANNELS, rate=SAMPLES_PER_SECOND, frames_per_buffer=CHUNK_SIZE, output=True)

        # Set playing to true
        self.playing = True

        # Playing loop
        print("PLAYER: Start playing ...")
        for data in self.frames:
            if not self.playing:
                break
            self.stream.write(data)

        # Stop and close the stream
        print("PLAYER: Stopped playing.")
        self.playing = False
        self.stream.stop_stream()
        self.stream.close()

    # Stop playing
    def stop(self) -> None:

        # Set playing to false
        self.playing = False


# Controller
class Controller(th.Thread):

    # CONSTRUCTOR
    def __init__(self):

        # Initialize thread
        th.Thread.__init__(self, name="Controller Window Thread")

        # Define window variables
        self.s_width = 550
        self.s_height = 350
        self.fps = 30
        self.screen = pg.surface.Surface((self.s_width, self.s_height))
        self.clock = pg.time.Clock()
        self.running = True
        self.state = S_IDLE
        self.cannot_close_on_recording_msg_timer = 0
        self.result = None
        self.recognizing_start_time = 0
        self.recognizing_end_time = 0

        # Define mouse variables
        self.m_left_down = False
        self.m_left_up = False
        self.m_left_pressed = False
        self.m_right_down = False
        self.m_right_up = False
        self.m_right_pressed = False
        self.m_pos = (0, 0)

        # Print confirmation
        print("CONTROLLER: Initialized.")


    # METHODS

    # Run
    def run(self) -> None:

        # Create the window screen
        self.screen = pg.display.set_mode((self.s_width, self.s_height))
        pg.display.set_caption(f"Speech Recognition Engine (by {AUTHOR}) [{VERSION}] - Controller")

        # Window loop
        print("CONTROLLER: Open window ...")
        while self.running:

            # Tick the clock
            self.clock.tick(self.fps)

            # Handle events
            self.handle_events()

            # Update screen
            self.update_screen()

            # Update timers
            if self.cannot_close_on_recording_msg_timer > 0:
                self.cannot_close_on_recording_msg_timer -= 4

        # Quit the application
        quit()

    # Handle events
    def handle_events(self) -> None:

        # Set the recorder global
        global recorder

        # Reset variables
        self.m_left_down = False
        self.m_right_down = False
        self.m_left_up = False
        self.m_right_up = False

        # Update pressed mouse buttons
        self.m_left_pressed, self.m_right_pressed, _ = pg.mouse.get_pressed(3)

        # Update mouse position
        self.m_pos = pg.mouse.get_pos()

        # For in all new events
        for event in pg.event.get():

            # If the event type is QUIT
            if event.type == pg.QUIT:

                # If the recorder is not recording, set running to false
                if not recorder.recording and self.state != S_STOP_RECORD:
                    print("CONTROLLER: Closed window.")
                    self.running = False
                # Else, set cannot close on recording message timer to 255
                else:
                    print("CONTROLLER: Cannot close window, while recording!")
                    self.cannot_close_on_recording_msg_timer = 255

            # If the event type is KEY DOWN
            if event.type == pg.KEYDOWN:

                # If the escape key pressed
                if event.key == pg.K_ESCAPE:

                    # If the state is IDLE, quit program
                    if self.state == S_IDLE:
                        print("CONTROLLER: Closed window.")
                        self.running = False
                    # If the state is RECORD or STOP RECORD, set cannot close on recording message timer to 255
                    if self.state == S_RECORD or self.state == S_STOP_RECORD:
                        print("CONTROLLER: Cannot close window, while recording!")
                        self.cannot_close_on_recording_msg_timer = 255
                    # If the state is SHOW RECORD RESULT or RECOGNIZE RECORD, go to IDLE
                    if self.state == S_SHOW_RECORD_RESULT or self.state == S_RECOGNIZE_RECORD:
                        print("CONTROLLER: Switched back into menu.")
                        self.state = S_IDLE

                # If the state is IDLE
                if self.state == S_IDLE:

                    # If the number 1, 2 or 3 pressed, press the specific button
                    if event.key == pg.K_1:
                        print("CONTROLLER: Select file to recognize ...")
                        self.state = S_SELECT_FILE
                    elif event.key == pg.K_2:
                        print("CONTROLLER: Reinitialize the recorder ...")
                        recorder = Recorder()
                        print("CONTROLLER: Run the recorder ...")
                        recorder.start()
                        self.state = S_RECORD
                    elif event.key == pg.K_3:
                        print("CONTROLLER: Closed window.")
                        self.running = False

                # If the space key pressed and the state is RECORD, stop recording
                if event.key == pg.K_SPACE and self.state == S_RECORD and recorder.recording:
                    print("CONTROLLER: Waiting for recorder stopped ...")
                    recorder.stop()
                    th.Thread(name="Wait Recorder Stop and Recognizer Thread", target=self.wait_record_stop_and_recognize).start()
                    self.state = S_STOP_RECORD

            # If a mouse button pressed down
            if event.type == pg.MOUSEBUTTONDOWN:

                # Check for left click and right click
                if event.button == pg.BUTTON_LEFT: self.m_left_down = True
                if event.button == pg.BUTTON_RIGHT: self.m_right_down = True

            # If a mouse button hold up
            if event.type == pg.MOUSEBUTTONUP:

                # Check for left click and right click
                if event.button == pg.BUTTON_LEFT: self.m_left_up = True
                if event.button == pg.BUTTON_RIGHT: self.m_right_up = True

    # Update screen
    def update_screen(self) -> None:

        # Set the recorder and player global
        global recorder
        global player

        # Fill the screen
        self.screen.fill(color.GRAY)

        # If the state is IDLE, draw the menu
        if self.state == S_IDLE:
            menu_title = font.render_text("Menu", font.HARNGTON_60, color.ORANGE)
            pg.draw.rect(self.screen, color.DARK_RED, [self.s_width // 2 - menu_title.get_width() // 2 - 15, 30, menu_title.get_width() + 30, menu_title.get_height() + 10])
            pg.draw.rect(self.screen, color.BLACK, [self.s_width // 2 - menu_title.get_width() // 2 - 15, 30, menu_title.get_width() + 30, menu_title.get_height() + 10], 4)
            self.screen.blit(menu_title, (self.s_width // 2 - menu_title.get_width() // 2, 35))
            if draw.draw_color_text_button(125, 160, 300, 40, self, self.screen, "Recognize File", font.HP_SIMPLIFIED_22, color.YELLOW, (-30, -30, -30), color.BLACK)[1]:
                print("CONTROLLER: Select file to recognize ...")
                self.state = S_SELECT_FILE
            if draw.draw_color_text_button(125, 210, 300, 40, self, self.screen, "Record and Recognize", font.HP_SIMPLIFIED_22, color.DARK_LIME, (-30, -30, -30), color.BLACK)[1]:
                print("CONTROLLER: Reinitialize the recorder ...")
                recorder = Recorder()
                print("CONTROLLER: Run the recorder ...")
                recorder.start()
                self.state = S_RECORD
            if draw.draw_color_text_button(125, 260, 300, 40, self, self.screen, "Quit", font.HP_SIMPLIFIED_22, color.ORANGE, (-30, -30, -30), color.BLACK)[1]:
                print("CONTROLLER: Closed window.")
                self.running = False

        # If the state is RECORD or STOP RECORD, draw the record interface
        elif self.state == S_RECORD or self.state == S_STOP_RECORD:
            menu_title = font.render_text("Recording", font.HARNGTON_50, color.BLUE)
            pg.draw.rect(self.screen, color.LIGHT_GRAY, [self.s_width // 2 - menu_title.get_width() // 2 - 10, 60, menu_title.get_width() + 20, menu_title.get_height() + 8])
            pg.draw.rect(self.screen, color.BLACK, [self.s_width // 2 - menu_title.get_width() // 2 - 10, 60, menu_title.get_width() + 20, menu_title.get_height() + 8], 3)
            self.screen.blit(menu_title, (self.s_width // 2 - menu_title.get_width() // 2, 63))
            if recorder.get_record_time() >= 3599 and not self.state == S_STOP_RECORD:
                print("CONTROLLER: Waiting for recorder stopped ...")
                recorder.stop()
                th.Thread(name="Wait Recorder Stop and Recognizer Thread", target=self.wait_record_stop_and_recognize).start()
                self.state = S_STOP_RECORD
            if recorder.get_record_time() > 3540:
                recording_time = font.render_text(format_time(recorder.get_record_time()), font.HP_SIMPLIFIED_35, color.DARK_RED)
            else:
                recording_time = font.render_text(format_time(recorder.get_record_time()), font.HP_SIMPLIFIED_35, color.BLACK)
            pg.draw.rect(self.screen, color.YELLOW, [(self.s_width // 2 - recording_time.get_width() // 2) - 10, 160, recording_time.get_width() + 20, recording_time.get_height() + 20])
            pg.draw.rect(self.screen, color.BLACK, [(self.s_width // 2 - recording_time.get_width() // 2) - 10, 160, recording_time.get_width() + 20, recording_time.get_height() + 20], 3)
            self.screen.blit(recording_time, (self.s_width // 2 - recording_time.get_width() // 2, 170))
            if draw.draw_color_text_button(125, 250, 300, 40, self, self.screen, "Stop Recording", font.HP_SIMPLIFIED_22, color.RED, (-30, -30, -30), color.BLACK)[1] and self.state == S_RECORD and recorder.recording:
                print("CONTROLLER: Waiting for recorder stopped ...")
                recorder.stop()
                th.Thread(name="Wait Recorder Stop and Recognizer Thread", target=self.wait_record_stop_and_recognize).start()
                self.state = S_STOP_RECORD
            elif self.state == S_STOP_RECORD:
                black_mask = pg.Surface((self.s_width, self.s_height))
                black_mask.fill(color.BLACK)
                black_mask.set_alpha(120)
                self.screen.blit(black_mask, (0, 0))
                stop_record_text = font.render_text("Stop recording ...", font.MAIAN_30, color.WHITE)
                self.screen.blit(stop_record_text, (self.s_width // 2 - stop_record_text.get_width() // 2, 150))

        # If the state is RECOGNIZE RECORD, draw the recognize record message text
        elif self.state == S_RECOGNIZE_RECORD:
            self.recognizing_end_time = time.time()
            menu_title = font.render_text("Recognizing", font.HARNGTON_50, color.GREEN)
            pg.draw.rect(self.screen, color.LIGHT_GRAY, [self.s_width // 2 - menu_title.get_width() // 2 - 10, 30, menu_title.get_width() + 20, menu_title.get_height() + 8])
            pg.draw.rect(self.screen, color.BLACK, [self.s_width // 2 - menu_title.get_width() // 2 - 10, 30, menu_title.get_width() + 20, menu_title.get_height() + 8], 3)
            self.screen.blit(menu_title, (self.s_width // 2 - menu_title.get_width() // 2, 33))
            pg.draw.rect(self.screen, color.GRAY.modify((15, 15, 15)), [20, 110, self.s_width - 40, self.s_height - 150])
            current_recognizing_time = font.render_text(f"Recognizing recorded audio ... ({int(self.recognizing_end_time - self.recognizing_start_time)} sec)", font.NOTOMONO_20, color.BLACK)
            self.screen.blit(current_recognizing_time, (self.s_width // 2 - current_recognizing_time.get_width() // 2, 140))
            audio_length_text = font.render_text(f"Length of the recorded audio: {format_time(recorder.get_record_time())[:-3]}", font.NOTOMONO_20, color.BLACK)
            self.screen.blit(audio_length_text, (self.s_width // 2 - audio_length_text.get_width() // 2, 200))
            warning_text = font.render_text("This process can take some time ...", font.NOTOMONO_20, color.BLACK)
            self.screen.blit(warning_text, (self.s_width // 2 - warning_text.get_width() // 2, 260))
            if self.result != ("#LOADING#", "", ""):
                if self.result[0] == "#ERROR#":
                    print("RESULT: -")
                    print("--------------")
                else:
                    print("-------")
                    print("RESULT:")
                    print(self.result[0])
                    print("-------")
                self.state = S_SHOW_RECORD_RESULT

        # If the state is SHOW RECORD RESULT, draw the result data
        elif self.state == S_SHOW_RECORD_RESULT:
            menu_title = font.render_text("Result", font.HARNGTON_50, color.PURPLE)
            pg.draw.rect(self.screen, color.LIGHT_GRAY, [self.s_width // 2 - menu_title.get_width() // 2 - 10, 30, menu_title.get_width() + 20, menu_title.get_height() + 8])
            pg.draw.rect(self.screen, color.BLACK, [self.s_width // 2 - menu_title.get_width() // 2 - 10, 30, menu_title.get_width() + 20, menu_title.get_height() + 8], 3)
            self.screen.blit(menu_title, (self.s_width // 2 - menu_title.get_width() // 2, 33))
            pg.draw.rect(self.screen, color.GRAY.modify((15, 15, 15)), [20, 110, self.s_width - 40, 150])
            if self.result[0] == "#ERROR#":
                if draw.draw_color_text_button(30, 120, 200, 40, self, self.screen, "Show Error Report", font.HP_SIMPLIFIED_22, color.AQUA, (-30, -30, -30), color.BLACK)[1]:
                    print("CONTROLLER: Open error report ...")
                    easygui.textbox(self.result[2], "Speech Recognition - Error Report", self.result[1], True)
                    print("CONTROLLER: Closed error report.")
                if draw.draw_color_text_button(30, 165, 200, 40, self, self.screen, "Recognize again", font.HP_SIMPLIFIED_22, color.BROWN, (30, 30, 30), color.WHITE)[1]:
                    print("CONTROLLER: Try recognizing again ...")
                    th.Thread(name="Recognizer Thread", target=self.recognize_record).start()
                    self.state = S_RECOGNIZE_RECORD
            else:
                if draw.draw_color_text_button(30, 120, 200, 40, self, self.screen, "Show Text Result", font.HP_SIMPLIFIED_22, color.YELLOW, (-30, -30, -30), color.BLACK)[1]:
                    print("CONTROLLER: Open text result window ...")
                    easygui.textbox("Result text of the recorded audio:", "Speech Recognition - Text Result", self.result[0])
                    print("CONTROLLER: Closed text result window.")
                if draw.draw_color_text_button(30, 165, 200, 40, self, self.screen, "Copy Text Result", font.HP_SIMPLIFIED_22, color.BLUE, (30, 30, 30), color.WHITE)[1]:
                    print("CONTROLLER: Copied result text to clipboard.")
                    pyperclip.copy(self.result[0])
            if player.playing:
                if draw.draw_color_text_button(30, 210, 200, 40, self, self.screen, "Stop playing", font.HP_SIMPLIFIED_22, color.RED, (-30, -30, -30), color.BLACK)[1]:
                    print("CONTROLLER: Stop playing ...")
                    player.stop()
            else:
                if draw.draw_color_text_button(30, 210, 200, 40, self, self.screen, "Play Audio", font.HP_SIMPLIFIED_22, color.DARK_LIME, (-30, -30, -30), color.BLACK)[1]:
                    print("CONTROLLER: Reinitialize the player ...")
                    player = Player()
                    player.frames = recorder.frames
                    print("CONTROLLER: Run the player ...")
                    player.start()
            pg.draw.rect(self.screen, color.LIGHT_GRAY.modify((-40, -40, -40)), [240, 120, 280, 130])
            if self.result[0] == "#ERROR#":
                confirmation1_text = font.render_text("Error on recognizing!", font.NOTOMONO_20, color.RED)
                confirmation2_text = font.render_text("I'm sorry! :-(", font.NOTOMONO_20, color.RED)
                self.screen.blit(confirmation1_text, (255, 130))
                self.screen.blit(confirmation2_text, (290, 174))
            else:
                confirmation1_text = font.render_text("Successfully completed", font.NOTOMONO_20, color.DARK_LIME)
                confirmation2_text = font.render_text(f"recognition in {int(self.recognizing_end_time - self.recognizing_start_time)} sec.", font.NOTOMONO_20, color.DARK_LIME)
                self.screen.blit(confirmation1_text, (248, 130))
                self.screen.blit(confirmation2_text, (248, 174))
            audio_length_text = font.render_text(f"Audio length: {format_time(recorder.get_record_time())[:-3]}", font.NOTOMONO_20, color.BLACK)
            self.screen.blit(audio_length_text, (267, 217))
            if draw.draw_color_text_button(30, 270, 240, 40, self, self.screen, "Record again", font.HP_SIMPLIFIED_22, color.PURPLE, (30, 30, 30), color.WHITE)[1]:
                print("CONTROLLER: Reinitialize the recorder ...")
                recorder = Recorder()
                print("CONTROLLER: Run the recorder ...")
                recorder.start()
                self.state = S_RECORD
            if draw.draw_color_text_button(280, 270, 240, 40, self, self.screen, "Back to Menu", font.HP_SIMPLIFIED_22, color.ORANGE, (-30, -30, -30), color.BLACK)[1]:
                print("CONTROLLER: Switched back into menu.")
                self.state = S_IDLE

        # If the state is SELECT FILE, open the file selector
        elif self.state == S_SELECT_FILE:
            selecting_text = font.render_text("Selecting file ...", font.MAIAN_30, color.BLACK)
            self.screen.blit(selecting_text, (self.s_width // 2 - selecting_text.get_width() // 2, self.s_height // 2 - selecting_text.get_height()))
            draw.credit_line(self.screen, "Controller", color.WHITE, (self.s_width, self.s_height))
            pg.display.flip()
            recognition_file =  easygui.fileopenbox("Which file would you recognize?", "Speech Recognition", "./*.wav", ["*.wav"])
            print("SELECTED FILE:")
            print(recognition_file)
            self.state = S_IDLE

        # If the state is RECOGNIZE FILE,
        elif self.state == S_RECOGNIZE_FILE:
            pass

        # If the state is SHOW FILE RESULT,
        elif self.state == S_SHOW_FILE_RESULT:
            pass

        # Draw cannot close on recording message text
        if self.cannot_close_on_recording_msg_timer > 0:
            cannot_close_on_recording_msg_text = font.render_text("CANNOT CLOSE ON RECORDING!", font.MAIAN_25, color.RED)
            cannot_close_on_recording_msg_text.set_alpha(self.cannot_close_on_recording_msg_timer)
            self.screen.blit(cannot_close_on_recording_msg_text, (self.s_width // 2 - cannot_close_on_recording_msg_text.get_width() // 2, 20))

        # Draw the credit line
        draw.credit_line(self.screen, "Controller", color.WHITE, (self.s_width, self.s_height))

        # Flip the screen
        pg.display.flip()

    # Recognize recorded audio
    def recognize_record(self) -> None:

        # Start recognizing
        self.recognizing_start_time = time.time()
        self.result = ("#LOADING#", "", "")
        self.result = recognize_audio(recorder.frames)

    # Wait for recorder stopped and recognize than
    def wait_record_stop_and_recognize(self) -> None:

        # Join the recorder
        recorder.join()

        # Set the state to recognize record
        self.state = S_RECOGNIZE_RECORD

        # Recognize recorded audio
        self.recognize_record()


# METHODS

# Recognize audio
def recognize_audio(audio_frames: list) -> tuple[str, str, str]:

    # Get the SpeechRecognition audio data
    audio_data = sp_rec.AudioData(b''.join(audio_frames), SAMPLES_PER_SECOND, pa.get_sample_size(SAMPLE_FORMAT))

    # Recognize the audio data to text data
    try:
        print("RECOGNIZER: Recognize audio ...")
        print("[WARNING: This can take some time ...]")
        text_data = rec.recognize_google(audio_data, language="de")
    except sp_rec.UnknownValueError:
        print("RECOGNIZER: Error on recognizing! Unable to recognize data!")
        print("--------------")
        print("ERROR MESSAGE:")
        error = "".join(traceback.format_exception(*sys.exc_info()))[:-1]
        print(error)
        print("--------------")
        return "#ERROR#", error, "Error on recognizing: Unable to recognize data!"
    except sp_rec.RequestError:
        print("RECOGNIZER: Error on recognizing! Cannot request the API! Maybe no internet!")
        print("--------------")
        print("ERROR MESSAGE:")
        error = "".join(traceback.format_exception(*sys.exc_info()))[:-1]
        print(error)
        print("--------------")
        return "#ERROR#", error, "Error on recognizing: Cannot request the API! Maybe no internet!"
    except Exception:
        print("RECOGNIZER: Error on recognizing! UNKNOWN!")
        print("--------------")
        print("ERROR MESSAGE:")
        error = "".join(traceback.format_exception(*sys.exc_info()))[:-1]
        print(error)
        print("--------------")
        return "#ERROR#", error, "Error on recognizing: UNKNOWN!"

    # Open the txt file
    print(f"RECOGNIZER: Save text at '{OUTPUT_TEXT}' ...")
    with open(OUTPUT_TEXT, "w") as file:
        # Write the head
        file.write(f"Speech Recognition Engine Result\n")
        file.write("--------------------------------\n")
        file.write("\n")

        # Write the text
        file.write(text_data)
    print("RECOGNIZER: Text saved.")

    # Return the text data and print confirmation
    print("RECOGNIZER: Successfully recognized.")
    return text_data, "", ""


# Format time from seconds
def format_time(time: float) -> str:

    # Get time elements
    if time // 60 // 60 >= 1:
        return "#OVERFLOW#"
    minutes = 0
    if time // 60 >= 1:
        minutes = int(time // 60)
        time -= time // 60 * 60
    seconds = time

    # Build the string
    if minutes < 10:
        result = f"0{minutes}:"
    else:
        result = f"{minutes}:"
    if seconds < 10:
        result += f"0{seconds:.2f}"
    else:
        result += f"{seconds:.2f}"

    # Return the result
    return result


# Quit the application
def quit() -> None:

    # Quit Pygame
    print("MAIN: Quit Pygame ...")
    pg.quit()

    # Quit PyAudio
    print("MAIN: Quit PyAudio ...")
    pa.terminate()

    # Exit program
    print("MAIN: Exit ...")
    sys.exit(0)


# MAIN
if __name__ == '__main__':

    # Set console title and print head
    os.system(f"@title Speech Recognition Engine (by {AUTHOR}) [{VERSION}] - Console")
    print("Speech Recognition Engine")
    print("-------------------------")
    print("")
    print(f"Author: {AUTHOR}")
    print(f"Version: {VERSION}")
    print("")

    # Initialize Pygame
    print("MAIN: Initialize Pygame ...")
    pg.init()

    # Initialize PyAudio
    print("MAIN: Initialize PyAudio ...")
    pa = pyaudio.PyAudio()

    # Initialize SpeechRecognition
    print("MAIN: Initialize SpeechRecognition ...")
    rec = sp_rec.Recognizer()

    # Initialize the controller window
    print("MAIN: Initialize the controller ...")
    controller = Controller()

    # Initialize the recorder
    print("MAIN: Initialize the recorder ...")
    recorder = Recorder()

    # Initialize the player
    print("MAIN: Initialize the player ...")
    player = Player()

    # Print confirmation
    print("MAIN: Successfully initialized.\n")

    # Run the controller window
    print("MAIN: Run the controller ...")
    controller.start()
