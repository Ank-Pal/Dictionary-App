import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import requests
import json
from threading import Thread
import textwrap
from PIL import Image, ImageTk
from io import BytesIO
import os
import sys

class DictionaryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Dictionary App")
        self.root.geometry("800x600")
        
        # Set app icon (using placeholder since we can't download images)
        self.set_app_icon()
        
        # Base URL for Free Dictionary API
        self.api_url = "https://api.dictionaryapi.dev/api/v2/entries/en/"
        
        # Color scheme
        self.bg_color = "#f5f5f5"
        self.accent_color = "#4a86e8"
        self.text_color = "#333333"
        self.highlight_color = "#76a5d8"
        
        # Creating the main frame
        self.main_frame = tk.Frame(root, bg=self.bg_color)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Configure the grid layout
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(2, weight=1)
        
        # App title
        self.title_label = tk.Label(
            self.main_frame, 
            text="Dictionary", 
            font=("Helvetica", 24, "bold"),
            bg=self.bg_color,
            fg=self.accent_color
        )
        self.title_label.grid(row=0, column=0, pady=(0, 20), sticky="w")
        
        # Search frame
        self.search_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        self.search_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        self.search_frame.columnconfigure(0, weight=1)
        
        # Search input
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(
            self.search_frame, 
            textvariable=self.search_var,
            font=("Helvetica", 14)
        )
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        # History dropdown
        self.history = []
        self.history_var = tk.StringVar()
        self.history_menu = ttk.Combobox(
            self.search_frame, 
            textvariable=self.history_var,
            font=("Helvetica", 12),
            state="readonly",
            width=15
        )
        self.history_menu.grid(row=0, column=1, padx=(0, 10))
        self.history_menu.bind("<<ComboboxSelected>>", self.on_history_select)
        self.update_history_menu()
        
        # Search button
        self.search_button = tk.Button(
            self.search_frame, 
            text="Search", 
            bg=self.accent_color,
            fg="white",
            font=("Helvetica", 12, "bold"),
            cursor="hand2",
            relief=tk.FLAT,
            command=self.search_word
        )
        self.search_button.grid(row=0, column=2)
        
        # Bind Enter key to search
        self.search_entry.bind("<Return>", lambda event: self.search_word())
        
        # Create notebook for tabbed content
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.grid(row=2, column=0, sticky="nsew")
        
        # Definitions tab
        self.definition_frame = tk.Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(self.definition_frame, text="Definitions")
        
        self.definition_frame.columnconfigure(0, weight=1)
        self.definition_frame.rowconfigure(0, weight=1)
        
        # Create scrolled text widget for definitions
        self.definition_text = scrolledtext.ScrolledText(
            self.definition_frame,
            wrap=tk.WORD,
            font=("Helvetica", 12),
            bg="white",
            fg=self.text_color,
            padx=10,
            pady=10
        )
        self.definition_text.grid(row=0, column=0, sticky="nsew")
        self.definition_text.config(state=tk.DISABLED)
        
        # Examples tab
        self.examples_frame = tk.Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(self.examples_frame, text="Examples")
        
        self.examples_frame.columnconfigure(0, weight=1)
        self.examples_frame.rowconfigure(0, weight=1)
        
        # Create scrolled text widget for examples
        self.examples_text = scrolledtext.ScrolledText(
            self.examples_frame,
            wrap=tk.WORD,
            font=("Helvetica", 12),
            bg="white",
            fg=self.text_color,
            padx=10,
            pady=10
        )
        self.examples_text.grid(row=0, column=0, sticky="nsew")
        self.examples_text.config(state=tk.DISABLED)
        
        # Synonyms tab
        self.synonyms_frame = tk.Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(self.synonyms_frame, text="Synonyms & Antonyms")
        
        self.synonyms_frame.columnconfigure(0, weight=1)
        self.synonyms_frame.rowconfigure(0, weight=1)
        
        # Create scrolled text widget for synonyms and antonyms
        self.synonyms_text = scrolledtext.ScrolledText(
            self.synonyms_frame,
            wrap=tk.WORD,
            font=("Helvetica", 12),
            bg="white",
            fg=self.text_color,
            padx=10,
            pady=10
        )
        self.synonyms_text.grid(row=0, column=0, sticky="nsew")
        self.synonyms_text.config(state=tk.DISABLED)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = tk.Label(
            self.main_frame, 
            textvariable=self.status_var,
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W,
            bg=self.bg_color,
            fg=self.text_color
        )
        self.status_bar.grid(row=3, column=0, sticky="ew", pady=(10, 0))
        
        # Apply custom styles
        self.style = ttk.Style()
        self.style.configure("TNotebook", background=self.bg_color, borderwidth=0)
        self.style.configure("TNotebook.Tab", background=self.bg_color, padding=[10, 5])
        self.style.map("TNotebook.Tab", background=[("selected", self.accent_color)])
        self.style.map("TNotebook.Tab", foreground=[("selected", "white")])
        
        # Focus on search entry at startup
        self.search_entry.focus()
    
    def set_app_icon(self):
        try:
            # Create a simple icon for the app as a placeholder
            # We'll create a blue square with "D" on it
            img = Image.new('RGB', (64, 64), color=self.accent_color)
            from PIL import ImageDraw, ImageFont
            draw = ImageDraw.Draw(img)
            
            # Try to use a standard font
            try:
                # This would be platform-dependent, fallback handled in except
                if sys.platform == "win32":
                    font = ImageFont.truetype("arial.ttf", 40)
                elif sys.platform == "darwin":  # macOS
                    font = ImageFont.truetype("Arial.ttf", 40)
                else:  # Linux
                    font = ImageFont.truetype("DejaVuSans.ttf", 40)
            except:
                # Fallback to default
                font = ImageFont.load_default()
            
            # Draw "D" in white
            text_width, text_height = draw.textsize("D", font=font)
            position = ((64 - text_width) // 2, (64 - text_height) // 2)
            draw.text(position, "D", fill="white", font=font)
            
            # Convert to PhotoImage and set as icon
            photo = ImageTk.PhotoImage(img)
            self.root.iconphoto(False, photo)
        except Exception as e:
            # If any error occurs, just skip setting the icon
            pass
    
    def update_history_menu(self):
        if self.history:
            self.history_menu['values'] = self.history
            self.history_menu.set("History")
        else:
            self.history_menu['values'] = ["No history yet"]
            self.history_menu.set("No history yet")
    
    def on_history_select(self, event):
        selected = self.history_var.get()
        if selected and selected != "History" and selected != "No history yet":
            self.search_var.set(selected)
            self.search_word()
    
    def add_to_history(self, word):
        if word not in self.history:
            self.history.insert(0, word)
            if len(self.history) > 10:  # Keep only the 10 most recent searches
                self.history.pop()
        else:
            # Move word to the top if it already exists
            self.history.remove(word)
            self.history.insert(0, word)
        self.update_history_menu()
    
    def search_word(self):
        word = self.search_var.get().strip()
        if not word:
            messagebox.showinfo("Info", "Please enter a word to search.")
            return
        
        # Add word to history
        self.add_to_history(word)
        
        # Clear previous content
        self.clear_results()
        
        # Update status
        self.status_var.set(f"Searching for '{word}'...")
        
        # Start the search in a separate thread to keep the UI responsive
        Thread(target=self.fetch_word_data, args=(word,), daemon=True).start()
    
    def clear_results(self):
        for text_widget in [self.definition_text, self.examples_text, self.synonyms_text]:
            text_widget.config(state=tk.NORMAL)
            text_widget.delete(1.0, tk.END)
            text_widget.config(state=tk.DISABLED)
    
    def fetch_word_data(self, word):
        try:
            response = requests.get(self.api_url + word)
            
            if response.status_code == 200:
                data = response.json()
                self.display_results(data, word)
            elif response.status_code == 404:
                self.root.after(0, lambda: messagebox.showinfo("Not Found", f"No definitions found for '{word}'."))
                self.status_var.set("Word not found")
            else:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Error fetching data: {response.status_code}"))
                self.status_var.set(f"Error: {response.status_code}")
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Error occurred: {str(e)}"))
            self.status_var.set("Error occurred")
    
    def display_results(self, data, word):
        # Process the first item in data (first dictionary entry)
        if not data or not isinstance(data, list) or len(data) == 0:
            self.root.after(0, lambda: messagebox.showinfo("No Results", "No results found."))
            self.status_var.set("No results found")
            return
        
        entry = data[0]
        
        # Extract phonetics
        phonetics_text = ""
        if "phonetic" in entry and entry["phonetic"]:
            phonetics_text = f"Pronunciation: {entry['phonetic']}\n\n"
        elif "phonetics" in entry and entry["phonetics"]:
            for phonetic in entry["phonetics"]:
                if "text" in phonetic and phonetic["text"]:
                    phonetics_text = f"Pronunciation: {phonetic['text']}\n\n"
                    break
        
        # Process definitions
        definitions_content = ""
        examples_content = ""
        synonyms_content = ""
        antonyms_content = ""
        
        if "meanings" in entry:
            for i, meaning in enumerate(entry["meanings"]):
                part_of_speech = meaning.get("partOfSpeech", "")
                definitions_content += f"\n{i+1}. As {part_of_speech.upper()}:\n\n"
                
                # Process definitions
                for j, definition in enumerate(meaning.get("definitions", [])):
                    def_text = definition.get("definition", "")
                    def_text = textwrap.fill(def_text, width=80)
                    definitions_content += f"   {j+1}. {def_text}\n\n"
                
                # Process examples
                example_count = 0
                for j, definition in enumerate(meaning.get("definitions", [])):
                    if "example" in definition and definition["example"]:
                        example_text = textwrap.fill(definition["example"], width=80)
                        examples_content += f"• {example_text}\n\n"
                        example_count += 1
                
                # Process synonyms and antonyms
                if "synonyms" in meaning and meaning["synonyms"]:
                    synonyms_content += f"Synonyms for {part_of_speech}:\n"
                    syn_text = ", ".join(meaning["synonyms"])
                    syn_text = textwrap.fill(syn_text, width=80)
                    synonyms_content += f"{syn_text}\n\n"
                
                if "antonyms" in meaning and meaning["antonyms"]:
                    antonyms_content += f"Antonyms for {part_of_speech}:\n"
                    ant_text = ", ".join(meaning["antonyms"])
                    ant_text = textwrap.fill(ant_text, width=80)
                    antonyms_content += f"{ant_text}\n\n"
        
        # Update UI with the results (using root.after to ensure thread safety)
        self.root.after(0, lambda: self.update_ui(word, phonetics_text, definitions_content, 
                                             examples_content, synonyms_content, antonyms_content))
    
    def update_ui(self, word, phonetics, definitions, examples, synonyms, antonyms):
        # Update definitions tab
        self.definition_text.config(state=tk.NORMAL)
        title_text = f"WORD: {word.upper()}\n\n"
        self.definition_text.insert(tk.END, title_text, "title")
        self.definition_text.insert(tk.END, phonetics)
        self.definition_text.insert(tk.END, definitions)
        
        # Add tags for styling
        self.definition_text.tag_configure("title", font=("Helvetica", 16, "bold"), foreground=self.accent_color)
        self.definition_text.config(state=tk.DISABLED)
        
        # Update examples tab
        self.examples_text.config(state=tk.NORMAL)
        if examples:
            self.examples_text.insert(tk.END, f"Examples for '{word}':\n\n", "title")
            self.examples_text.insert(tk.END, examples)
        else:
            self.examples_text.insert(tk.END, f"No examples found for '{word}'.")
        self.examples_text.tag_configure("title", font=("Helvetica", 14, "bold"), foreground=self.accent_color)
        self.examples_text.config(state=tk.DISABLED)
        
        # Update synonyms tab
        self.synonyms_text.config(state=tk.NORMAL)
        if synonyms or antonyms:
            self.synonyms_text.insert(tk.END, f"Synonyms & Antonyms for '{word}':\n\n", "title")
            if synonyms:
                self.synonyms_text.insert(tk.END, synonyms)
            else:
                self.synonyms_text.insert(tk.END, "No synonyms found.\n\n")
            
            if antonyms:
                self.synonyms_text.insert(tk.END, antonyms)
            else:
                self.synonyms_text.insert(tk.END, "No antonyms found.\n\n")
        else:
            self.synonyms_text.insert(tk.END, f"No synonyms or antonyms found for '{word}'.")
        self.synonyms_text.tag_configure("title", font=("Helvetica", 14, "bold"), foreground=self.accent_color)
        self.synonyms_text.config(state=tk.DISABLED)
        
        # Update status
        self.status_var.set(f"Showing results for '{word}'")
        
        # Show first tab
        self.notebook.select(0)

def main():
    root = tk.Tk()
    app = DictionaryApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()