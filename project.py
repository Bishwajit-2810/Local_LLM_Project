import tkinter as tk
from tkinter import ttk
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
import markdown2
from tkhtmlview import HTMLLabel
import pyttsx3  
import speech_recognition as sr  
from tkinter import PhotoImage  
import psutil  
import GPUtil  
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

# Define the prompt template for the chatbot
template = """
You are john wick, a friendly and knowledgeable assistant working for Bishwajit who is a computer science student. 
Respond in a polite, helpful, and professional manner.

Here is the conversation history: {context}

Question: {question}

Answer: 
"""

# Function to load and display the markdown file
def load_markdown(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        markdown_text = file.read()
    return markdown2.markdown(markdown_text)

# Main chat application
def handle_conversation():
    # Create the main Tkinter root window
    root = tk.Tk()
    root.title("AI Assistant")
    root.geometry("1220x930")  # Increased width to accommodate the monitor
    root.configure(bg='#2E2E2E')  # Dark grey background color for root window

    # Initialize conversation context
    context = ""
    
    # Initialize voice toggle flag
    voice_support = tk.BooleanVar(value=True)  # Default is True (voice support enabled)

    # Define available models
    models = ["llama3.2", "llama3.1", "qwen2.5-coder", "qwen2", "mistral", "gemma"]
    selected_model = tk.StringVar(value=models[0])  # Default selection is the first model

    # Initialize the model and chain
    model = OllamaLLM(model=models[0])
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | model

    # Update model selection dynamically
    def update_model(*args):
        nonlocal chain
        model_name = selected_model.get()
        model = OllamaLLM(model=model_name)
        chain = prompt | model

    # Trace changes in model selection
    selected_model.trace_add("write", update_model)

    # Save the chat history to a Markdown file
    def save_to_markdown(chat_history):
        file_path = "chat_history.md"
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(chat_history)

    # Function to view chat history in a new window
    def view_chat_history():
        chat_viewer = tk.Toplevel(root)
        chat_viewer.title("Chat History Viewer")
        chat_viewer.geometry("600x600")

        html_content = load_markdown("chat_history.md")
        html_label = HTMLLabel(chat_viewer, html=html_content, width=80, height=40)
        html_label.pack(expand=True, fill="both")

    # Initialize the text-to-speech engine
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)  # Set speech rate (optional)
    except Exception as e:
        print(f"Error initializing text-to-speech engine: {e}")
        engine = None

    # Function to speak a given text
    def speak(text):
        if engine and voice_support.get():  # Check if voice support is enabled
            engine.say(text)
            engine.runAndWait()

    # Function to use speech recognition to get user input
    def recognize_speech():
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("Adjusting for background noise... Please wait.")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            print("Listening... Speak now.")
            
            try:
                # Capture the audio
                audio = recognizer.listen(source)
                print("Recognizing...")
                
                # Recognize speech using Google Web Speech API
                text = recognizer.recognize_google(audio)
                speak("Working on it, boss")
                print(f"You said: {text}")
                
                # Process recognized text and pass it to the chatbot
                process_user_input(text)

            except sr.UnknownValueError:
                print("Sorry, I could not understand the audio.")
                speak("Sorry, I could not understand the audio.")
            except sr.RequestError as e:
                print(f"Error with the recognition service: {e}")
                speak("Sorry, there was an error with the recognition service.")

    # Function to process user input (either typed or spoken)
    def process_user_input(user_input):
        nonlocal context

        if not user_input:
            return
        if user_input.lower() == "exit":
            root.quit()
            return

        # Get the model's response
        result = chain.invoke({"context": context, "question": user_input})

        # Update the conversation history display
        conversation_history.config(state=tk.NORMAL)
        conversation_history.insert(tk.END, "User: ", "user_label")
        conversation_history.insert(tk.END, f"{user_input}\n", "user_text")
        conversation_history.insert(tk.END, "AI: ", "ai_label")
        conversation_history.insert(tk.END, f"{result}\n\n", "ai_text")
        conversation_history.config(state=tk.DISABLED)

        # Update the context and save to the markdown file
        context += f"User: {user_input}\nAI: {result}\n"
        save_to_markdown(context)

        # Clear the input field and scroll to the latest message
        conversation_history.yview(tk.END)

        # Speak the AI's response if voice support is enabled
        speak(result)

    # Create conversation history display with increased size
    conversation_history = tk.Text(root, height=40, width=90, wrap=tk.WORD, state=tk.DISABLED, bg="#2E2E2E", fg="#E0E0E0")
    conversation_history.grid(row=0, column=0, padx=10, pady=10, columnspan=2)

    # Configure text tags with colors for User and AI labels and responses
    conversation_history.tag_configure("user_label", foreground="#00FFFF", font=("Courier", 12, "bold"))
    conversation_history.tag_configure("user_text", foreground="#00B0FF", font=("Courier", 12))
    conversation_history.tag_configure("ai_label", foreground="#FFFF00", font=("Courier", 12, "bold"))
    conversation_history.tag_configure("ai_text", foreground="#90EE90", font=("Courier", 12))

    # Add model selection dropdown
    model_label = tk.Label(root, text="Select Model:", fg="#E0E0E0", bg="#2E2E2E", font=("Courier", 14, "bold"))
    model_label.grid(row=1, column=0, padx=10, pady=5, sticky="e")

    # Create a custom style for the ttk.Combobox
    style = ttk.Style()
    style.configure("TCombobox",
                    background="#424242",
                    foreground="#E0E0E0",
                    fieldbackground="#424242",
                    font=("Courier", 14),
                    padding=5)

    # Use ttk.Combobox for a more modern dropdown
    model_selector = ttk.Combobox(root, textvariable=selected_model, values=models, state="readonly", 
                                   font=("Courier", 14), width=15, height=5, 
                                   style="TCombobox")
    model_selector.grid(row=1, column=1, padx=10, pady=5, sticky="w")

    # Add input label, entry, and send button for text input
    entry_label = tk.Label(root, text="Your Message:", fg="#E0E0E0", bg="#2E2E2E", font=("Courier", 14, "bold"))
    entry_label.grid(row=2, column=0, padx=10, pady=5, sticky="e")

    entry = tk.Entry(root, width=50, bg="#424242", fg="#E0E0E0", font=("Courier", 14))
    entry.grid(row=2, column=1, padx=10, pady=5)

    # Function to send the typed message
    def on_send_button_click(event=None):
        user_input = entry.get().strip()

        if user_input:
            # Speak the "working on it, boss" message
            speak("Working on it, boss")
            
            # Process the user input and get the response
            process_user_input(user_input)
            
            # Clear the input field
            entry.delete(0, tk.END)

    send_button = tk.Button(root, text="Send", bg="#607D8B", fg="white", font=("Courier", 14, "bold"), command=on_send_button_click)
    send_button.grid(row=3, column=0, columnspan=2, pady=10)

    # Bind Enter key to the send button
    root.bind('<Return>', on_send_button_click)

    # Add view history button
    view_button = tk.Button(root, text="Chat History", bg="#78909C", fg="black", font=("Courier", 14), command=view_chat_history)
    view_button.grid(row=4, column=0, columnspan=2, pady=10)

    # Add the Speak button with mic icon
    mic_icon = PhotoImage(file="mic_icon.png").subsample(10, 10)  # Resize mic icon to a larger size
    speak_button = tk.Button(root, image=mic_icon, command=recognize_speech, relief="flat", bg="#2E2E2E")
    speak_button.grid(row=2, column=2, padx=10, pady=5)  # Place the mic button beside the input field
    speak_button.image = mic_icon  # Keep a reference to the image to prevent garbage collection

    # Add Voice Support Toggle Button
    def toggle_voice_support():
        if voice_support.get():
            voice_support.set(False)
            toggle_button.config(text="Enable")
        else:
            voice_support.set(True)
            toggle_button.config(text="Disable")
    
    toggle_button = tk.Button(root, text="Disable", bg="#607D8B", fg="white", font=("Courier", 14, "bold"), command=toggle_voice_support)
    toggle_button.grid(row=1, column=2, padx=5, pady=5)  # Reduced the padding between model selector and toggle button

    # System Monitor Section
    def update_system_usage():
        # Get CPU, Memory, and GPU Usage
        cpu = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory().percent
        
        # Get GPU usage (only for NVIDIA)
        gpus = GPUtil.getGPUs()
        gpu_usage = gpus[0].memoryUtil * 100 if gpus else 0

        # Update plots with new data
        cpu_data.append(cpu)
        memory_data.append(memory)
        gpu_data.append(gpu_usage)

        if len(cpu_data) > 30:
            cpu_data.pop(0)
            memory_data.pop(0)
            gpu_data.pop(0)

        # Plot the updated data
        ax1.clear()
        ax2.clear()
        ax3.clear()
        
        ax1.plot(cpu_data, color='red')
        ax1.set_title('CPU Usage (%)')
        ax1.text(0.05, 0.95, f"CPU: {cpu:.1f}%", transform=ax1.transAxes, verticalalignment='top', fontsize=12, color='red')
        
        ax2.plot(memory_data, color='blue')
        ax2.set_title('Memory Usage (%)')
        ax2.text(0.05, 0.95, f"Memory: {memory:.1f}%", transform=ax2.transAxes, verticalalignment='top', fontsize=12, color='blue')
        
        ax3.plot(gpu_data, color='green')
        ax3.set_title('GPU Usage (%)')
        ax3.text(0.05, 0.95, f"GPU: {gpu_usage:.1f}%", transform=ax3.transAxes, verticalalignment='top', fontsize=12, color='green')

        # Redraw the canvas
        canvas.draw()

        # Repeat the update every 1000ms (1 second)
        root.after(1000, update_system_usage)

    # Create plots for system monitor
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(4.5, 6.5))
    
    fig.tight_layout(pad=3.0)

    cpu_data = []
    memory_data = []
    gpu_data = []

    # Embed the matplotlib figure into Tkinter window using FigureCanvasTkAgg
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.get_tk_widget().grid(row=0, column=2, padx=10, pady=10)

    # Start the system usage updates
    update_system_usage()

    root.mainloop()

# Start the conversation
handle_conversation()
