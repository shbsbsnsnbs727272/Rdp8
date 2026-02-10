import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import random
import time
import threading

class AndroidInstallerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Android-x86 Installer")
        self.root.geometry("700x550")
        self.root.resizable(False, False)

        # Setup dark/tech theme
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TFrame", background="#f0f0f0")
        style.configure("TLabel", background="#f0f0f0", font=("Arial", 10))
        style.configure("Header.TLabel", font=("Arial", 14, "bold"), background="#0099cc", foreground="white")
        style.configure("TButton", font=("Arial", 10, "bold"), padding=5)

        self.current_step = 0
        self.iso_path = ""
        self.target_drive = ""
        
        self.create_widgets()
        self.show_step(0)

    def create_widgets(self):
        # 1. Header Area (Android Blue)
        self.header_frame = tk.Frame(self.root, bg="#0099cc", height=60)
        self.header_frame.pack(fill=tk.X)
        self.header_label = tk.Label(self.header_frame, text="Install Android-x86", 
                                     bg="#0099cc", fg="white", font=("Arial", 18, "bold"))
        self.header_label.pack(pady=15)

        # 2. Content Area (Dynamic)
        self.content_frame = ttk.Frame(self.root, padding="20")
        self.content_frame.pack(fill=tk.BOTH, expand=True)

        # 3. Footer (Progress/Log)
        self.footer_frame = ttk.Frame(self.root, padding=10)
        self.footer_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        ttk.Label(self.footer_frame, text="Installation Log:").pack(anchor="w")
        self.log_text = scrolledtext.ScrolledText(self.footer_frame, height=6, state='disabled', 
                                                  bg="#222", fg="#0f0", font=("Consolas", 9))
        self.log_text.pack(fill=tk.X)

        # --- Step 0: Select ISO ---
        self.step_0 = ttk.Frame(self.content_frame)
        ttk.Label(self.step_0, text="Select ISO File", font=("Arial", 16, "bold")).pack(pady=20)
        ttk.Label(self.step_0, text="Locate the Android-x86 ISO image to install:").pack(pady=10)
        
        self.iso_entry = ttk.Entry(self.step_0, width=50)
        self.iso_entry.pack(pady=5)
        
        btn_browse = ttk.Button(self.step_0, text="Browse...", command=self.browse_iso)
        btn_browse.pack(pady=10)
        
        btn_next_iso = ttk.Button(self.step_0, text="Next >", command=lambda: self.validate_step_0())
        btn_next_iso.pack(pady=20)

        # --- Step 1: Select Target Drive ---
        self.step_1 = ttk.Frame(self.content_frame)
        ttk.Label(self.step_1, text="Select Target Drive", font=("Arial", 16, "bold")).pack(pady=20)
        ttk.Label(self.step_1, text="Choose a partition to install Android-x86:").pack(pady=10)
        
        self.drive_list = tk.Listbox(self.step_1, height=6, font=("Courier", 10), selectmode=tk.SINGLE)
        self.drive_list.pack(fill=tk.X, pady=10)
        
        # Mock drives
        drives = [
            "1. /dev/sda1   Windows NTFS   120 GB",
            "2. /dev/sda2   Data NTFS      200 GB",
            "3. /dev/sdb    Unallocated    500 GB"
        ]
        for d in drives:
            self.drive_list.insert(tk.END, d)
        
        btn_next_drive = ttk.Button(self.step_1, text="Next >", command=lambda: self.validate_step_1())
        btn_next_drive.pack(pady=20)

        # --- Step 2: Data Size ---
        self.step_2 = ttk.Frame(self.content_frame)
        ttk.Label(self.step_2, text="Data Size", font=("Arial", 16, "bold")).pack(pady=20)
        ttk.Label(self.step_2, text="Choose the size of the /data partition (MB):").pack(pady=10)
        
        self.data_scale = ttk.Scale(self.step_2, from_=2048, to=65536, orient=tk.HORIZONTAL, length=400)
        self.data_scale.set(8192) # Default 8GB
        self.data_scale.pack(pady=10)
        
        self.data_label = ttk.Label(self.step_2, text="8192 MB")
        self.data_scale.configure(command=lambda v: self.data_label.config(text=f"{int(float(v))} MB"))
        self.data_label.pack()
        
        btn_next_size = ttk.Button(self.step_2, text="Install >", command=lambda: self.show_step(3))
        btn_next_size.pack(pady=20)

        # --- Step 3: Installation / Copying ---
        self.step_3 = ttk.Frame(self.content_frame)
        ttk.Label(self.step_3, text="Installing Android-x86", font=("Arial", 16, "bold")).pack(pady=20)
        
        self.progress_bar = ttk.Progressbar(self.step_3, orient=tk.HORIZONTAL, length=500, mode='determinate')
        self.progress_bar.pack(pady=20)
        
        self.status_label = ttk.Label(self.step_3, text="Preparing...")
        self.status_label.pack(pady=5)
        
        # Buttons hidden initially
        self.btn_finish_frame = ttk.Frame(self.step_3)
        
        self.btn_reboot_pc = ttk.Button(self.btn_finish_frame, text="Reboot PC Now", command=self.reboot_pc)
        self.btn_reboot_pc.pack(side=tk.LEFT, padx=10)
        
        self.btn_reboot_device = ttk.Button(self.btn_finish_frame, text="Reboot Device", command=self.reboot_device)
        self.btn_reboot_device.pack(side=tk.LEFT, padx=10)

    def log(self, message):
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, f"> {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')

    def show_step(self, step_index):
        # Hide all steps
        for widget in self.content_frame.winfo_children():
            widget.pack_forget()
        
        # Show requested step
        if step_index == 0: self.step_0.pack(fill=tk.BOTH, expand=True)
        elif step_index == 1: self.step_1.pack(fill=tk.BOTH, expand=True)
        elif step_index == 2: self.step_2.pack(fill=tk.BOTH, expand=True)
        elif step_index == 3: self.step_3.pack(fill=tk.BOTH, expand=True)

        self.current_step = step_index

    def browse_iso(self):
        filename = filedialog.askopenfilename(
            title="Select Android ISO",
            filetypes=[("ISO Files", "*.iso"), ("All Files", "*.*")]
        )
        if filename:
            self.iso_path = filename
            self.iso_entry.delete(0, tk.END)
            self.iso_entry.insert(0, filename)

    def validate_step_0(self):
        if not self.iso_path:
            messagebox.showerror("Error", "Please select an ISO file.")
            return
        self.log(f"ISO Selected: {self.iso_path.split('/')[-1]}")
        self.show_step(1)

    def validate_step_1(self):
        selection = self.drive_list.curselection()
        if not selection:
            messagebox.showerror("Error", "Please select a target drive.")
            return
        self.target_drive = self.drive_list.get(selection[0]).split()[1] # Get /dev/sdX
        self.log(f"Target Drive: {self.target_drive}")
        self.show_step(2)

    def show_step(self, index):
        self.show_step(index)
        if index == 3:
            # Start installation in a separate thread to keep GUI responsive
            threading.Thread(target=self.run_installation_process, daemon=True).start()

    def run_installation_process(self):
        steps = [
            ("Formatting partition...", 5),
            ("Creating file system...", 10),
            ("Copying ISO files...", 30),
            ("Extracting system.sfs...", 50),
            ("Installing bootloader...", 75),
            ("Writing configuration...", 90),
            ("Installation Complete!", 100)
        ]
        
        for status, percentage in steps:
            time.sleep(random.uniform(0.5, 1.5)) # Simulate work
            self.update_progress(percentage, status)
            self.log(status)

        # Enable buttons at the end
        self.root.after(0, lambda: self.btn_finish_frame.pack(pady=20))

    def update_progress(self, value, text):
        self.root.after(0, lambda: self.progress_bar.configure(value=value))
        self.root.after(0, lambda: self.status_label.configure(text=text))

    def reboot_pc(self):
        self.log("Rebooting PC Now...")
        self.root.after(1000, self.root.destroy)

    def reboot_device(self):
        self.log("Rebooting Device...")
        self.root.after(1000, self.root.destroy)

if __name__ == "__main__":
    root = tk.Tk()
    app = AndroidInstallerApp(root)
    root.mainloop()
