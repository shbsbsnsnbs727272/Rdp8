import tkinter as tk
from tkinter import ttk, scrolledtext
import random
import time
import threading

class ReceiveSmsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Free Receive SMS - Temporary USA Number")
        self.root.geometry("500x600")
        self.root.resizable(False, False)

        # 1. Generate a random USA temporary number
        self.area_codes = ["212", "415", "646", "917", "202", "310", "312"]
        self.temp_number = f"+1 {random.choice(self.area_codes)} {random.randint(100, 999)}-{random.randint(1000, 9999)}"
        
        # Services that "send" codes
        self.services = ["Google", "Facebook", "WhatsApp", "Amazon", "Bank of America", "Instagram"]

        # Styles
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Header.TLabel", font=("Helvetica", 16, "bold"), foreground="#333")
        style.configure("Number.TLabel", font=("Courier", 20, "bold"), foreground="#0066cc")
        style.configure("Treeview", rowheight=25)

        self.create_widgets()
        
        # Start background thread to simulate incoming SMS
        self.running = True
        self.sms_thread = threading.Thread(target=self.simulate_incoming_sms, daemon=True)
        self.sms_thread.start()

        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_widgets(self):
        # Header Frame
        header_frame = ttk.Frame(self.root, padding="20")
        header_frame.pack(fill=tk.X)

        ttk.Label(header_frame, text="Your Temporary USA Number:", style="Header.TLabel").pack()
        ttk.Label(header_frame, text=self.temp_number, style="Number.TLabel").pack(pady=5)
        
        # Auto-copy button simulation
        copy_btn = ttk.Button(header_frame, text="Copy Number", command=self.copy_number)
        copy_btn.pack(pady=5)

        # Inbox List Frame
        list_frame = ttk.Frame(self.root)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        ttk.Label(list_frame, text="Recent SMS Messages:", font=("Helvetica", 10, "bold")).pack(anchor="w")

        columns = ("sender", "message", "time")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=10)
        
        self.tree.heading("sender", text="From")
        self.tree.heading("message", text="Message / Code")
        self.tree.heading("time", text="Time")
        
        self.tree.column("sender", width=100)
        self.tree.column("message", width=250)
        self.tree.column("time", width=80)
        
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Detail View
        self.detail_text = scrolledtext.ScrolledText(self.root, height=8, font=("Consolas", 10))
        self.detail_text.pack(fill=tk.BOTH, padx=20, pady=(0, 20), expand=False)
        self.detail_text.insert(tk.END, "Waiting for messages...")
        self.detail_text.configure(state='disabled')

        # Bind selection event
        self.tree.bind("<<TreeviewSelect>>", self.show_message_details)

    def copy_number(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.temp_number)
        print(f"Number {self.temp_number} copied to clipboard.")

    def simulate_incoming_sms(self):
        """
        Simulates receiving SMS codes and messages in the background.
        """
        # Wait a bit before the first message
        time.sleep(3)
        
        while self.running:
            # Random delay between messages (5 to 15 seconds)
            time.sleep(random.randint(5, 15))
            
            if not self.running:
                break

            # Pick a random service and generate a code
            service = random.choice(self.services)
            code = f"{random.randint(100000, 999999)}"
            
            # Message formats
            msg_types = [
                f"Your verification code is {code}. Don't share it.",
                f"{code} is your security code.",
                f"Use code {code} to log in.",
                f"Your OTP is: {code}. Valid for 5 minutes."
            ]
            message_content = random.choice(msg_types)
            
            current_time = time.strftime("%H:%M:%S")

            # Update UI safely using after()
            self.root.after(0, self.add_message_to_tree, service, message_content, current_time)

    def add_message_to_tree(self, sender, message, timestamp):
        # Insert into treeview at the top (index 0)
        self.tree.insert("", 0, values=(sender, message, timestamp))
        self.tree.selection_set(self.tree.get_children()[0]) # Select newest
        self.show_message_details(None) # Update details view

    def show_message_details(self, event):
        selected_item = self.tree.selection()
        if not selected_item:
            return
        
        item = self.tree.item(selected_item)
        sender = item['values'][0]
        message = item['values'][1]
        timestamp = item['values'][2]

        self.detail_text.configure(state='normal')
        self.detail_text.delete(1.0, tk.END)
        
        detail_str = (
            f"FROM:      {sender}\n"
            f"TO:        {self.temp_number}\n"
            f"RECEIVED:  {timestamp}\n"
            f"{'-'*40}\n"
            f"{message}\n"
            f"{'-'*40}\n"
            f"STATUS:    Received\n"
            f"TYPE:      Verification SMS"
        )
        self.detail_text.insert(tk.END, detail_str)
        self.detail_text.configure(state='disabled')

    def on_close(self):
        self.running = False
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ReceiveSmsApp(root)
    root.mainloop()
