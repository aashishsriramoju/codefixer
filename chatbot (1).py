import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import requests
import json
from datetime import datetime

class CodeDebugChatbot:
    def __init__(self, root):
        self.root = root
        self.root.title("CodeFixer - AI Debugging Assistant")
        self.root.geometry("900x900")
        self.root.configure(bg="#1e1e1e")  # Dark theme background
        
        # Style configuration
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TButton", background="#2d5278", foreground="#ffffff", font=("Arial", 10, "bold"), padding=6)
        self.style.configure("TLabel", background="#1e1e1e", foreground="#c9d1d9", font=("Arial", 11))
        self.style.configure("TFrame", background="#1e1e1e")
        self.style.configure("Horizontal.TSeparator", background="#404040")
        
        self.create_widgets()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.configure(style="TFrame")

        # Header
        header_label = ttk.Label(main_frame, text="CodeFixer - Powered by CodeLlama 7B", font=("Arial", 14, "bold"))
        header_label.grid(row=0, column=0, columnspan=3, pady=(10, 20))

        # Code input area
        ttk.Label(main_frame, text="Enter Your Code:").grid(row=1, column=0, pady=5, sticky=tk.W)
        self.code_input = scrolledtext.ScrolledText(main_frame, height=10, width=80, bg="#2d2d2d", fg="white", 
                                                  insertbackground="white", font=("Consolas", 11),
                                                  tabs=(4, 'center'))
        # Configure syntax highlighting tags
        self.code_input.tag_configure('keyword', foreground='#569cd6')
        self.code_input.tag_configure('string', foreground='#ce9178')
        self.code_input.tag_configure('comment', foreground='#6a9955')
        self.code_input.bind('<KeyRelease>', self.update_syntax_highlighting)
        self.code_input.grid(row=2, column=0, columnspan=3, pady=5, padx=10)
        ttk.Separator(main_frame, orient="horizontal").grid(row=2, column=0, columnspan=3, sticky="ew", pady=10)

        # Buttons
        self.error_btn = ttk.Button(main_frame, text="Find Errors", command=self.find_errors)
        self.error_btn.grid(row=3, column=0, pady=10, padx=5)

        self.fix_btn = ttk.Button(main_frame, text="Fix Code", command=self.fix_code)
        self.fix_btn.grid(row=3, column=1, pady=10, padx=5)

        self.clear_btn = ttk.Button(main_frame, text="Clear", command=self.clear_fields)
        self.clear_btn.grid(row=3, column=2, pady=10, padx=5)
        ttk.Separator(main_frame, orient="horizontal").grid(row=4, column=0, columnspan=3, sticky="ew", pady=10)

        # Suggestion output area
        ttk.Label(main_frame, text="Analysis & Suggestions:").grid(row=4, column=0, pady=5, sticky=tk.W)
        self.suggestion_output = scrolledtext.ScrolledText(main_frame, height=15, width=80, bg="#1f1f1f", fg="#c9d1d9",
                                                         font=("Consolas", 11), state="disabled", wrap=tk.WORD)
        self.suggestion_output.grid(row=5, column=0, columnspan=3, pady=5)

        # Status bar
        self.status_label = ttk.Label(main_frame, text="Status: Ready", foreground="#aaaaaa")
        self.status_label.grid(row=6, column=0, columnspan=3, pady=5)

    def find_errors(self):
        code = self.code_input.get("1.0", tk.END).strip()
        if not code:
            messagebox.showwarning("Warning", "Please enter some code to analyze!")
            return

        self.status_label.config(text="Status: Finding Errors...")
        # Start loading animation
        self.animation_sequence = ['|', '/', '—', '\\']
        self.animation_index = 0
        self.after_id = self.root.after(150, self.update_loading_animation)
        self.suggestion_output.config(state="normal")
        self.suggestion_output.delete("1.0", tk.END)

        # Prompt for error detection
        prompt = f"""Analyze this code for potential errors:\n\n```python\n{code}\n```\n\nList any syntax errors, logical errors, or potential runtime issues with explanations. Do not suggest fixes yet."""

        try:
            response = self.query_codellama(prompt)
            self.suggestion_output.insert(tk.END, response)
        except Exception as e:
            self.suggestion_output.insert(tk.END, f"Error: Could not connect to CodeLlama - {str(e)}")
        
        self.suggestion_output.config(state="disabled")
        if hasattr(self, 'after_id'):
            self.root.after_cancel(self.after_id)
        self.status_label.config(text=f"Status: Errors Found - {datetime.now().strftime('%H:%M:%S')}")

    def fix_code(self):
        code = self.code_input.get("1.0", tk.END).strip()
        if not code:
            messagebox.showwarning("Warning", "Please enter some code to fix!")
            return

        self.status_label.config(text="Status: Generating Fixes...")
        # Start loading animation
        self.animation_sequence = ['|', '/', '—', '\\']
        self.animation_index = 0
        self.after_id = self.root.after(150, self.update_loading_animation)
        self.suggestion_output.config(state="normal")
        self.suggestion_output.delete("1.0", tk.END)

        # Prompt for code fixing
        prompt = f"""Fix this code by addressing any errors:\n\n```python\n{code}\n```\n\nProvide the corrected code and explain the changes made."""

        try:
            response = self.query_codellama(prompt)
            self.suggestion_output.insert(tk.END, response)
        except Exception as e:
            self.suggestion_output.insert(tk.END, f"Error: Could not connect to CodeLlama - {str(e)}")
        
        self.suggestion_output.config(state="disabled")
        if hasattr(self, 'after_id'):
            self.root.after_cancel(self.after_id)
        self.status_label.config(text=f"Status: Fixes Generated - {datetime.now().strftime('%H:%M:%S')}")

    def query_codellama(self, prompt):
        # Using Ollama's REST API (adjust URL/port if different)
        url = "http://localhost:11434/api/generate"
        payload = {
            "model": "codellama:7b",
            "prompt": prompt,
            "stream": False,
            "max_tokens": 500
        }
        
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            result = response.json()
            return result.get("response", "No response from model")
        else:
            raise Exception(f"API request failed with status {response.status_code}")

    def update_syntax_highlighting(self, event=None):
        code = self.code_input.get("1.0", "end-1c")
        self.code_input.tag_remove('keyword', '1.0', 'end')
        self.code_input.tag_remove('string', '1.0', 'end')
        self.code_input.tag_remove('comment', '1.0', 'end')
        
        # Highlight Python syntax
        keywords = ['def', 'class', 'import', 'from', 'try', 'except', 'if', 'else', 'for', 'while']
        for word in keywords:
            start = '1.0'
            while True:
                start = self.code_input.search(r'\b{}\b'.format(word), start, stopindex='end', regexp=True)
                if not start:
                    break
                end = f'{start}+{len(word)}c'
                self.code_input.tag_add('keyword', start, end)
                start = end
        
        # Highlight strings and comments
        self.code_input.highlight_pattern(r'\".*?\"', 'string', regexp=True)
        self.code_input.highlight_pattern(r'\'.*?\'', 'string', regexp=True)
        self.code_input.highlight_pattern(r'#.*$', 'comment', regexp=True)

    def update_loading_animation(self):
        if hasattr(self, 'animation_index'):
            current_status = self.status_label.cget('text')
            base_status = current_status.split(' [')[0]
            self.status_label.config(text=f"{base_status} [{self.animation_sequence[self.animation_index]}]")
            self.animation_index = (self.animation_index + 1) % len(self.animation_sequence)
            self.after_id = self.root.after(150, self.update_loading_animation)

    def clear_fields(self):
        self.code_input.delete("1.0", tk.END)
        self.suggestion_output.config(state="normal")
        self.suggestion_output.delete("1.0", tk.END)
        self.suggestion_output.config(state="disabled")
        self.status_label.config(text="Status: Ready")

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.root.destroy()

def main():
    root = tk.Tk()
    app = CodeDebugChatbot(root)
    root.mainloop()

if __name__ == "__main__":
    main()