import tkinter as tk
from tkinter import scrolledtext
import random
import time
import threading
import datetime

class WslTerminalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ubuntu - WSL Terminal")
        self.root.geometry("800x500")
        
        # Configure the window to look like a terminal
        self.root.configure(bg="#0c0c0c")
        
        self.username = "user"
        self.hostname = "DESKTOP-LINUX"
        self.current_dir = "~"
        
        self.create_widgets()
        
        # Simulate WSL startup sequence in a thread
        threading.Thread(target=self.simulate_startup, daemon=True).start()

    def create_widgets(self):
        # Main Console Output Area
        self.console = scrolledtext.ScrolledText(
            self.root, 
            bg="#0c0c0c", 
            fg="#cccccc", 
            font=("Consolas", 11), 
            insertbackground="#ffffff",
            state='normal',
            wrap=tk.WORD,
            padx=10, pady=10
        )
        self.console.pack(fill=tk.BOTH, expand=True)
        
        # Color Tags for styling
        self.console.tag_config("prompt", foreground="#2aa198") # Cyan for user@host
        self.console.tag_config("path", foreground="#859900")   # Green for directory
        self.console.tag_config("command", foreground="#ffffff")# White for input
        self.console.tag_config("success", foreground="#268bd2")# Blue for success messages
        self.console.tag_config("error", foreground="#dc322f")  # Red for errors
        self.console.tag_config("output", foreground="#b58900") # Yellow for file lists
        
        # Bind keys
        self.console.bind("<Return>", self.handle_enter)
        self.console.bind("<BackSpace>", self.handle_backspace)
        self.console.bind("<Key>", self.handle_key_press)
        
        self.input_start_index = "1.0"
        self.disable_editing()

    def simulate_startup(self):
        """Simulates the WSL initialization process."""
        time.sleep(0.5)
        self.print_output("Installing, this may take a few minutes...", "output")
        time.sleep(1.0)
        self.print_output("Welcome to Ubuntu 22.04.2 LTS (GNU/Linux 5.15.0-76-generic x86_64)", "output")
        time.sleep(0.2)
        self.print_output(" * Documentation:  https://help.ubuntu.com", "output")
        self.print_output(" * Management:     https://landscape.canonical.com", "output")
        self.print_output(" * Support:        https://ubuntu.com/advantage", "output")
        time.sleep(0.5)
        self.print_output("", "output")
        
        # Show new message
        self.print_output("0 updates can be applied immediately.", "output")
        self.print_output("", "output")
        
        self.show_prompt()

    def print_output(self, text, tag="output"):
        """Thread-safe print to console."""
        self.console.config(state='normal')
        self.console.insert(tk.END, text + "\n", tag)
        self.console.see(tk.END)
        self.console.config(state='disabled')

    def show_prompt(self):
        """Displays the user@hostname:directory$ prompt."""
        self.console.config(state='normal')
        
        # Construct prompt: user@hostname:~$         prompt_text = f"{self.username}@{self.hostname}:{self.current_dir}$ "
        
        self.console.insert(tk.END, prompt_text, "prompt")
        
        # Mark where the user starts typing
        self.input_start_index = self.console.index("end-1c")
        self.console.config(state='disabled')
        
        # Ensure cursor is at the end
        self.console.mark_set(tk.INSERT, tk.END)

    def enable_editing(self):
        self.console.config(state='normal')

    def disable_editing(self):
        self.console.config(state='disabled')

    def handle_key_press(self, event):
        """Restrict typing to only after the prompt."""
        cursor_index = self.console.index(tk.INSERT)
        
        # Compare indices to see if cursor is before the input start
        # We do a simple check: is the line number same? if so, check char position
        # A robust way involves comparing the actual string indices
        
        current_line = int(cursor_index.split('.')[0])
        start_line = int(self.input_start_index.split('.')[0])
        
        if current_line < start_line:
            return "break" # Block typing
            
        if current_line == start_line:
            current_col = int(cursor_index.split('.')[1])
            start_col = int(self.input_start_index.split('.')[1])
            if current_col < start_col:
                return "break"

    def handle_backspace(self, event):
        """Prevent deleting the prompt."""
        cursor_index = self.console.index(tk.INSERT)
        if self.console.compare(cursor_index, "<=", self.input_start_index):
            return "break"

    def handle_enter(self, event):
        """Process the command entered by the user."""
        # Get the text typed by the user
        self.console.config(state='normal')
        end_index = self.console.index("end-1c")
        
        # Extract command text between input_start and end
        cmd_range = f"{self.input_start_index}+1c"
        # Handle empty line case
        try:
            command = self.console.get(self.input_start_index, end_index).strip()
        except:
            command = ""
            
        self.console.insert(tk.END, "\n") # Move to new line
        self.console.config(state='disabled')
        
        if command:
            self.process_command(command)
            
        # Show next prompt
        self.root.after(100, self.show_prompt)
        return "break"

    def process_command(self, cmd):
        """Simulate Linux commands."""
        parts = cmd.split()
        cmd_name = parts[0].lower()
        args = parts[1:]

        if cmd_name == "clear":
            self.console.config(state='normal')
            self.console.delete(1.0, tk.END)
            self.console.config(state='disabled')
            
        elif cmd_name == "ls":
            files = ["Documents", "Downloads", "script.py", "main.cpp", "test.txt", "workflow.yml"]
            self.print_output("  ".join(files), "output")
            
        elif cmd_name == "pwd":
            self.print_output(f"/home/{self.username}", "output")
            
        elif cmd_name == "whoami":
            self.print_output(self.username, "output")
            
        elif cmd_name == "date":
            now = datetime.datetime.now().strftime("%a %b %d %H:%M:%S %Z %Y")
            self.print_output(now, "output")
            
        elif cmd_name == "echo":
            self.print_output(" ".join(args), "output")
            
        elif cmd_name == "python3" or cmd_name == "python":
            if not args:
                self.start_python_interpreter()
            else:
                self.run_python_script(args[0])
                
        elif cmd_name == "exit":
            self.print_output("logout", "output")
            self.root.after(1000, self.root.destroy)
            
        else:
            self.print_output(f"bash: {cmd_name}: command not found", "error")

    def run_python_script(self, script_name):
        """Simulate running a python script file."""
        self.print_output(f"Running {script_name}...", "success")
        time.sleep(0.2)
        
        if "loop" in script_name or "heavy" in script_name:
            # Simulate a long running script
            for i in range(1, 6):
                time.sleep(0.3)
                self.print_output(f"Processing item {i}/5...", "output")
            self.print_output("Done.", "success")
        else:
            # Standard hello world or math
            outputs = [
                "Hello, World!",
                "Calculation result: 42",
                "Script executed successfully.",
                f"Random Number: {random.randint(1, 100)}"
            ]
            self.print_output(random.choice(outputs), "output")
            self.print_output(f"[Process completed]", "success")

    def start_python_interpreter(self):
        """Simulate entering the Python REPL."""
        self.print_output("Python 3.10.6 (main, Nov 14 2022, 16:30:00) [GCC 11.3.0] on linux", "output")
        self.print_output('Type "help", "copyright", "credits" or "license" for more information.', "output")
        self.print_output(">>> ", "command")
        
        # In a real simulation, we would change the input handling here.
        # For this simple script, we will just print a sample interaction and exit back to shell.
        time.sleep(0.5)
        self.print_output("print('WSL is working!')", "command")
        time.sleep(0.2)
        self.print_output("WSL is working!", "output")
        time.sleep(0.2)
        self.print_output(">>> exit()", "command")
        self.print_output("")

if __name__ == "__main__":
    root = tk.Tk()
    app = WslTerminalApp(root)
    root.mainloop()
