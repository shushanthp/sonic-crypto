import pyaudio
import tkinter as tk
from tkinter import messagebox, filedialog
from cryptography.fernet import Fernet
import wave
from PIL import Image, ImageTk
import base64
import threading
import numpy as np
key = Fernet.generate_key()
farnet = Fernet(key)
recorded_audio = b'' 
fake_image_path = ''  
def record_audio(seconds, sample_rate=44100, chunk_size=1024):
    audio = pyaudio.PyAudio()
    stream = audio.open(format=pyaudio.paInt16, channels=1,
                        rate=sample_rate, input=True,
                        frames_per_buffer=chunk_size)
    frames = []
    for _ in range(0, int(sample_rate / chunk_size * seconds)):
        data = stream.read(chunk_size)
        frames.append(data)
    stream.stop_stream()
    stream.close()
    audio.terminate()
    return b''.join(frames)
def start_recording():
    global recorded_audio
    recorded_audio = record_audio(seconds=5)
    messagebox.showinfo("Recording Complete", "Recording completed successfully!")
def encrypt_audio():
    if recorded_audio:
        threading.Thread(target=encrypt_and_embed_audio, args=(recorded_audio,)).start()
    else:
        messagebox.showwarning("No Recording", "Please record audio first.")
def encrypt_selected_audio():
    file_path = filedialog.askopenfilename(title="Select Audio File",
                                           filetypes=[("Audio Files", "*.wav;*.mp3")])
    if file_path:
        with open(file_path, 'rb') as audio_file:
            audio_data = audio_file.read()
        threading.Thread(target=encrypt_and_embed_audio, args=(audio_data,)).start()
    else:
        messagebox.showwarning("No File Selected", "Please select an audio file first.")
def encrypt_and_embed_audio(audio_data):
    try:
        encrypted_audio = farnet.encrypt(audio_data)
        encrypted_audio_base64 = base64.b64encode(encrypted_audio).decode()
        if fake_image_path:
            with open(fake_image_path, 'rb') as f:
                fake_image_data = f.read()
            fake_image = Image.open(fake_image_path)
            binary_audio = ''.join(format(byte, '08b') for byte in encrypted_audio)
            audio_length = len(binary_audio)

            img_width, img_height = fake_image.size
            max_audio_length = img_width * img_height * 3  
            if audio_length <= max_audio_length:
                img_data = np.array(fake_image)
                audio_index = 0
                for y in range(img_height):
                    for x in range(img_width):
                        for c in range(3):  
                            if audio_index < audio_length:
                                pixel = img_data[y, x, c]
                                img_data[y, x, c] = (pixel & ~1) | int(binary_audio[audio_index])
                                audio_index += 1
                encrypted_image = Image.fromarray(img_data)
                encrypted_image.save("encrypted_audio.png")
                messagebox.showinfo("Encryption Complete", "Audio encrypted successfully with watermark!")
            else:
                messagebox.showerror("Audio Too Long", "Audio is too long to be embedded in the image.")
        else:
            messagebox.showwarning("No Fake Image", "Please select a fake image first.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
def decrypt_audio():
    file_path = filedialog.askopenfilename(title="Select Encrypted Audio File",
                                           filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
    if file_path:
        threading.Thread(target=decrypt_audio_image, args=(file_path,)).start()
    else:
        messagebox.showwarning("No File Selected", "Please select an encrypted audio image.")
def decrypt_audio_image(file_path):
    try:
        encrypted_image = Image.open(file_path)
        img_width, img_height = encrypted_image.size
        img_data = np.array(encrypted_image)
        binary_audio = []
        for y in range(img_height):
            for x in range(img_width):
                for c in range(3):
                    pixel = img_data[y, x, c]
                    binary_audio.append(format(pixel, '08b')[-1])
        audio_data = bytearray(int(''.join(binary_audio[i:i+8]), 2) for i in range(0, len(binary_audio), 8))        
        decrypted_audio = farnet.decrypt(bytes(audio_data))
        with wave.open('decrypted_audio.wav', 'wb') as decrypted_file:
            decrypted_file.setnchannels(1)
            decrypted_file.setsampwidth(2)
            decrypted_file.setframerate(44100)
            decrypted_file.writeframes(decrypted_audio)
        messagebox.showinfo("Decryption Complete", "Audio decrypted successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
def select_fake_image():
    global fake_image_path
    fake_image_path = filedialog.askopenfilename(title="Select Fake Image File",
                                                 filetypes=[("Image Files", "*.jpg;*.png;*.jpeg")])
root = tk.Tk()
root.title("Sonic Crypto")
root.configure(bg="#2C3E50")
button_bg = "#1ABC9C"
button_fg = "#FFFFFF"
label_fg = "#ECF0F1"
title_fg = "#E74C3C"
bg_image_path = "C:/Users/bunty/Downloads/free-website-background-01.jpg"  
bg_image = Image.open(bg_image_path)
bg_image = bg_image.resize((root.winfo_screenwidth(), root.winfo_screenheight()), Image.LANCZOS)
bg_image_tk = ImageTk.PhotoImage(bg_image)
background_label = tk.Label(root, image=bg_image_tk)
background_label.place(x=0, y=0, relwidth=1, relheight=1)
title_label = tk.Label(root, text="Sonic Crypto", fg=title_fg, bg="#2C3E50", font=("Helvetica", 24, "bold"))
title_label.pack(pady=20)
label = tk.Label(root, text="Click 'Record' to start recording live audio for 5 seconds.", fg=label_fg, bg="#2C3E50", font=("Helvetica", 14, "bold"))
label.pack(pady=10)
record_button = tk.Button(root, text="Record", command=start_recording, bg=button_bg, fg=button_fg, font=("Helvetica", 12, "bold"), width=25)
record_button.pack(pady=10)
fake_image_button = tk.Button(root, text="Select Fake Image", command=select_fake_image, bg=button_bg, fg=button_fg, font=("Helvetica", 12, "bold"), width=25)
fake_image_button.pack(pady=10)
encrypt_button = tk.Button(root, text="Encrypt Recorded Audio", command=encrypt_audio, bg=button_bg, fg=button_fg, font=("Helvetica", 12, "bold"), width=25)
encrypt_button.pack(pady=10)
encrypt_selected_button = tk.Button(root, text="Encrypt Selected Audio File", command=encrypt_selected_audio, bg=button_bg, fg=button_fg, font=("Helvetica", 12, "bold"), width=25)
encrypt_selected_button.pack(pady=10)
decrypt_button = tk.Button(root, text="Decrypt Audio", command=decrypt_audio, bg=button_bg, fg=button_fg, font=("Helvetica", 12, "bold"), width=25)
decrypt_button.pack(pady=10)
root.mainloop()
