import tkinter as tk
from tkinter import ttk
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
import markdown2
from tkhtmlview import HTMLLabel
import pyttsx3  # Import pyttsx3 for text-to-speech
import speech_recognition as sr  # Import SpeechRecognition for voice input
from tkinter import PhotoImage  # Import PhotoImage for using images in buttons

# Define the prompt template for the chatbot
template = """
You are Lucy, a friendly and knowledgeable assistant working for Bishwajit. 
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
    root.title("AI ChatBot")
    root.geometry("915x895")
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
    conversation_history = tk.Text(root, height=38, width=96, wrap=tk.WORD, state=tk.DISABLED, bg="#2E2E2E", fg="#E0E0E0")
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

    root.mainloop()

# Start the conversation
handle_conversation()
