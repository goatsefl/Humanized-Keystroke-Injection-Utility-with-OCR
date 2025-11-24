import tkinter
import customtkinter
from tkinter import filedialog
from PIL import Image
import pytesseract
import threading
import time
import random
from pynput.keyboard import Controller, Key

# --- Tesseract OCR Configuration ---
# Okay, so first things first. If I want the 'Load Text from Image' button to work,
# I need to tell the script where to find the Tesseract program. If I don't do this,
# the OCR part will just crash. I should probably add this to my system's PATH
# so I don't have to hardcode the path here.
#
# For example, on my Windows machine, it might look like this:
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class AutoTyperApp(customtkinter.CTk):
    """
    So this is the main class for the whole app. I'm building it on top of
    customtkinter because it looks way better than the default tkinter stuff.
    It's going to hold all the GUI elements and the typing logic.
    """
    def __init__(self):
        super().__init__()

        # I need to set up the basic window here. A good title, a decent starting size,
        # and I'll make it so it can't be resized too small. Dark mode is a must.
        self.title("Undetectable AI Autotyper")
        self.geometry("800x600")
        self.minsize(600, 450)
        customtkinter.set_appearance_mode("dark")
        customtkinter.set_default_color_theme("blue")

        # This makes the main frame expand to fill the whole window when I resize it.
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Main container frame ---
        # I'm putting everything inside this main_frame so I can have consistent padding.
        self.main_frame = customtkinter.CTkFrame(self)
        self.main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1) # The textbox row should expand.

        # --- Top controls for loading files ---
        # This frame will just hold the buttons at the top.
        self.controls_frame = customtkinter.CTkFrame(self.main_frame)
        self.controls_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        self.load_image_button = customtkinter.CTkButton(self.controls_frame, text="Load Text from Image", command=self.load_image)
        self.load_image_button.pack(side="left", padx=5)

        self.clear_text_button = customtkinter.CTkButton(self.controls_frame, text="Clear Text", command=self.clear_textbox)
        self.clear_text_button.pack(side="left", padx=5)

        # --- Main text input area ---
        # This is the big textbox where I'll paste the text I want to type.
        # I'll put some helpful placeholder text in it to get started.
        self.textbox = customtkinter.CTkTextbox(self.main_frame, font=("Arial", 14), wrap="word")
        self.textbox.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.initial_text = """’I honestly confess that my features dropped as I heard this piece of information, for my suspects had for the
moment outwitted me. Stronachlacher, as most people know, is at the head of Loch Katrine. Thence a
steamer runs to the foot of the Loch, where it is met by coaches that convey the passengers to Callender, and
so on to Edinburgh. It seemed obvious to me that Mrs. Donaldson and her nephew had hurried on to catch
the steamer that would be waiting for the coach people, and that their intention was to reach Edinburgh, thus
giving me the slip. Turning to the stableman, I asked: “Have you another machine?”
“No,” was the gruff answer.
“But have you nothing you can let me have?” I asked with some anxiety.
“No, they’re a’ out.”
Here was a dilemma; but still I was determined not to be baffled, and I sought out the landlord, told him who I
was, and insisted that it was imperatively necessary that I should go forward without delay. The distance to
cover was only about five miles, but, though an excellent walker, I could not hope to reach Stronachlacher in
time to catch the boat."""
        self.textbox.insert("1.0", self.initial_text)

        # --- Sliders and playback controls frame ---
        # This frame on the right is for all the controls. I have to set grid_propagate to False
        # so I can give it a fixed width, otherwise it'll resize with the widgets inside it.
        self.sliders_frame = customtkinter.CTkFrame(self.main_frame, width=250)
        self.sliders_frame.grid(row=1, column=1, padx=10, pady=10, sticky="ns")
        self.sliders_frame.grid_propagate(False)

        # --- Playback Controls ---
        # The main action buttons. I need to make sure their states (enabled/disabled) are managed
        # properly so I can't, for example, click "Pause" when it's not even typing.
        self.start_button = customtkinter.CTkButton(self.sliders_frame, text="Start", command=self.start_typing)
        self.start_button.pack(pady=10, padx=10, fill="x")

        self.pause_button = customtkinter.CTkButton(self.sliders_frame, text="Pause", command=self.pause_typing, state="disabled")
        self.pause_button.pack(pady=5, padx=10, fill="x")

        self.resume_button = customtkinter.CTkButton(self.sliders_frame, text="Resume", command=self.resume_typing, state="disabled")
        self.resume_button.pack(pady=5, padx=10, fill="x")

        self.stop_button = customtkinter.CTkButton(self.sliders_frame, text="Stop", command=self.stop_typing, state="disabled")
        self.stop_button.pack(pady=(5, 20), padx=10, fill="x")

        # --- Parameter Sliders ---
        # These sliders are the core of making the typing look human.
        self.wpm_label = customtkinter.CTkLabel(self.sliders_frame, text="WPM: 60")
        self.wpm_label.pack()
        self.wpm_slider = customtkinter.CTkSlider(self.sliders_frame, from_=20, to=300, number_of_steps=280, command=self.update_wpm_label)
        self.wpm_slider.set(60)
        self.wpm_slider.pack(pady=(0, 10), padx=10, fill="x")

        self.accuracy_label = customtkinter.CTkLabel(self.sliders_frame, text="Accuracy: 98%")
        self.accuracy_label.pack()
        self.accuracy_slider = customtkinter.CTkSlider(self.sliders_frame, from_=80, to=100, number_of_steps=20, command=self.update_accuracy_label)
        self.accuracy_slider.set(98)
        self.accuracy_slider.pack(pady=(0, 10), padx=10, fill="x")

        self.backspace_label = customtkinter.CTkLabel(self.sliders_frame, text="Backspace Fix Rate: 95%")
        self.backspace_label.pack()
        self.backspace_slider = customtkinter.CTkSlider(self.sliders_frame, from_=0, to=100, number_of_steps=100, command=self.update_backspace_label)
        self.backspace_slider.set(95)
        self.backspace_slider.pack(pady=(0, 10), padx=10, fill="x")

        self.delay_label = customtkinter.CTkLabel(self.sliders_frame, text="Key Press Variation: 50ms")
        self.delay_label.pack()
        self.delay_slider = customtkinter.CTkSlider(self.sliders_frame, from_=0, to=200, number_of_steps=200, command=self.update_delay_label)
        self.delay_slider.set(50)
        self.delay_slider.pack(pady=(0, 10), padx=10, fill="x")

        # A little status label at the bottom to give feedback.
        self.status_label = customtkinter.CTkLabel(self.sliders_frame, text="Status: Idle", text_color="gray")
        self.status_label.pack(side="bottom", pady=10)

        # --- Threading and keyboard control attributes ---
        # These are crucial. The thread lets the typing happen in the background so the GUI doesn't freeze.
        # The events are flags to signal pausing and stopping to the thread.
        self.typing_thread = None
        self.is_paused = threading.Event()
        self.is_stopped = threading.Event()
        self.keyboard = Controller()
        
        # Okay, this was the big fix for capitalization. I realized just sending '!' doesn't work in some
        # apps because they're looking for SHIFT + '1'. This map will help me simulate that.
        self.shift_map = {
            '!': '1', '@': '2', '#': '3', '$': '4', '%': '5',
            '^': '6', '&': '7', '*': '8', '(': '9', ')': '0',
            '_': '-', '+': '=', '{': '[', '}': ']', '|': '\\',
            ':': ';', '"': "'", '<': ',', '>': '.', '?': '/'
        }

    # These next functions are just simple helpers to update the labels next to the sliders.
    def update_wpm_label(self, value):
        self.wpm_label.configure(text=f"WPM: {int(value)}")

    def update_accuracy_label(self, value):
        self.accuracy_label.configure(text=f"Accuracy: {int(value)}%")

    def update_backspace_label(self, value):
        self.backspace_label.configure(text=f"Backspace Fix Rate: {int(value)}%")

    def update_delay_label(self, value):
        self.delay_label.configure(text=f"Key Press Variation: {int(value)}ms")

    def update_status(self, message):
        self.status_label.configure(text=message)
        
    def clear_textbox(self):
        """Super simple, just a function to nuke all the text in the box."""
        self.textbox.delete("1.0", "end")

    def load_image(self):
        """This handles the OCR. It opens a file dialog for me to pick an image."""
        file_path = filedialog.askopenfilename(
            title="Select an Image File",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.tiff")]
        )
        if not file_path:
            return # I didn't pick a file, so just do nothing.
        try:
            image = Image.open(file_path)
            extracted_text = pytesseract.image_to_string(image)
            self.clear_textbox() # Get rid of old text first.
            self.textbox.insert("1.0", extracted_text)
        except Exception as e:
            # If Tesseract isn't installed or something goes wrong, I should show an error
            # message in the textbox instead of just crashing the whole app.
            self.clear_textbox()
            self.textbox.insert("1.0", f"Error processing image:\n\n{e}\n\nPlease ensure Tesseract OCR is installed and correctly configured.")

    def set_controls_state(self, is_active):
        """This is a super important helper function for the UX. It disables all the
        other controls when the typing starts so I can't mess things up mid-type."""
        if is_active:
            state = "disabled"
            typing_state = "normal"
        else: # Idle/Stopped
            state = "normal"
            typing_state = "disabled"

        self.start_button.configure(state=state)
        self.load_image_button.configure(state=state)
        self.clear_text_button.configure(state=state)
        self.textbox.configure(state=state)
        
        self.pause_button.configure(state=typing_state)
        self.stop_button.configure(state=typing_state)
        self.resume_button.configure(state="disabled") # Resume should always start as disabled.

    def start_typing(self):
        """This function kicks off the whole process."""
        if self.typing_thread and self.typing_thread.is_alive():
            return # Don't start a new thread if one is already running.

        # I need to clear the stop/pause flags from any previous run.
        self.is_stopped.clear()
        self.is_paused.clear()

        text_to_type = self.textbox.get("1.0", "end-1c")
        if not text_to_type:
            return # If there's no text, don't do anything.

        self.set_controls_state(is_active=True) # Lock the UI.
        
        # Here I'm creating the thread. I set it as a 'daemon' so it automatically closes
        # if I close the main window. This is good practice.
        self.typing_thread = threading.Thread(target=self.type_text_worker, args=(text_to_type,), daemon=True)
        self.typing_thread.start()

    def pause_typing(self):
        """When I hit pause, this sets the pause event, which the typing thread will see."""
        self.is_paused.set()
        self.pause_button.configure(state="disabled")
        self.resume_button.configure(state="normal")
        self.update_status("Status: Paused")

    def resume_typing(self):
        """This just clears the pause event, letting the typing thread continue."""
        self.is_paused.clear()
        self.pause_button.configure(state="normal")
        self.resume_button.configure(state="disabled")
        self.update_status("Status: Typing...")

    def stop_typing(self):
        """This is my emergency stop. It sets the stop event and immediately resets the UI
        so it feels responsive. The thread will see the event and shut itself down."""
        self.is_stopped.set()
        self.typing_thread = None # Ditch the old thread object.
        self.set_controls_state(is_active=False) # Unlock the UI.
        self.update_status("Status: Idle")

    def type_text_worker(self, text):
        """This is the function that does all the heavy lifting. It runs in the background thread."""
        # I need a countdown. This gives me a few seconds to click into the window
        # where I want the text to be typed. It's a critical feature.
        for i in range(3, 0, -1):
            if self.is_stopped.is_set():
                self.after(0, self.stop_typing) # Make sure the UI updates on the main thread.
                return
            self.after(0, self.update_status, f"Starting in {i}...")
            time.sleep(1)
        
        if self.is_stopped.is_set():
            self.after(0, self.stop_typing)
            return
            
        self.after(0, self.update_status, "Status: Typing...")

        # I'll grab all the slider values right at the beginning.
        wpm = self.wpm_slider.get()
        accuracy = self.accuracy_slider.get() / 100.0
        backspace_rate = self.backspace_slider.get() / 100.0
        delay_variation_ms = self.delay_slider.get()
        
        # Defining punctuation sets here so I can add extra pauses after them to seem more human.
        major_punctuation = {'.', '!', '?'}
        minor_punctuation = {',', ';', ':'}

        # Convert Words Per Minute to a delay in seconds. Average word is 5 chars.
        cpm = wpm * 5 
        base_delay = 60.0 / cpm if cpm > 0 else 0.1

        # This is the main loop, going through the text one character at a time.
        for char in text:
            # The very first thing in the loop should be to check if I've hit stop.
            if self.is_stopped.is_set():
                break

            # This is the pause logic. The 'while' loop will just spin here until I hit resume.
            while self.is_paused.is_set():
                if self.is_stopped.is_set():
                    break
                time.sleep(0.1) # Sleep a little to avoid using 100% CPU while paused.

            # Here I'm calculating the human-like delay. I take the base delay for the WPM
            # and add or subtract a random amount based on the 'variation' slider.
            random_offset_ms = (random.random() - 0.5) * 2 * delay_variation_ms
            total_delay = max(0.01, base_delay + (random_offset_ms / 1000.0))
            time.sleep(total_delay)
            
            # I need a special case for newline characters. I can't 'type' \n, I have to press Enter.
            if char == '\n':
                self.keyboard.press(Key.enter)
                self.keyboard.release(Key.enter)
            else:
                # This is the accuracy simulation. I "roll the dice", and if it's above my
                # accuracy setting, I'll make a mistake on purpose.
                if random.random() > accuracy:
                    nearby_keys = "asdfghjklqwertyuiopzxcvbnm" # Just a plausible set of mistake keys.
                    mistake = random.choice(nearby_keys)
                    self.keyboard.press(mistake)
                    self.keyboard.release(mistake)

                    # Then, I roll the dice again to see if I should fix the mistake with a backspace.
                    if random.random() < backspace_rate:
                        time.sleep(random.uniform(0.1, 0.2)) # Pause before correcting, like a human would.
                        self.keyboard.press(Key.backspace)
                        self.keyboard.release(Key.backspace)
                        time.sleep(random.uniform(0.05, 0.1)) # Pause after correcting.
                        self.type_character(char) # Now type the correct character.
                else:
                    # If I didn't make a mistake, just type the character normally.
                    self.type_character(char)
            
            # After typing the character, I check if it was punctuation and add an extra pause.
            if char in major_punctuation:
                time.sleep(random.uniform(0.3, 0.5))
            elif char in minor_punctuation:
                time.sleep(random.uniform(0.1, 0.2))
        
        # When the loop finishes, I need to reset the UI back to the idle state.
        if not self.is_stopped.is_set():
            self.after(100, self.stop_typing) # A small delay before resetting feels smoother.

    def type_character(self, char):
        """
        Okay, this is my new helper function and the solution to the capitalization problem.
        It handles typing a single character correctly, especially if it needs the Shift key.
        """
        # If the character is an uppercase letter or one of the special symbols in my shift_map...
        if char.isupper() or char in self.shift_map:
            # ...then I'll use this 'with' block from pynput. It simulates holding down
            # the shift key for the duration of the block.
            with self.keyboard.pressed(Key.shift):
                # If it's a special character like '!', I look up its base key ('1') in the map.
                # Otherwise, for a capital letter like 'A', I just use its lowercase version 'a'.
                key_to_press = self.shift_map.get(char, char.lower())
                self.keyboard.press(key_to_press)
                self.keyboard.release(key_to_press)
        else:
            # If it's a regular lowercase character, just press it normally.
            self.keyboard.press(char)
            self.keyboard.release(char)


# This is the standard Python entry point. If I run this script directly,
# it will create my app instance and start the main GUI loop.
if __name__ == "__main__":
    app = AutoTyperApp()
    app.mainloop()