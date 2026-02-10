import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import random
import time
import threading

class QemuManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("QEMU Virtual Machine Manager")
        self.root.geometry("800x600")
        
        # Style configuration
        style = ttk.Style()
        style.theme_use('clam')
        
        self.create_layout()
        self.populate_mock_machines()

    def create_layout(self):
        # -- Main Container --
        main_pane = tk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True)

        # -- Left Sidebar (VM List) --
        sidebar_frame = ttk.Frame(main_pane, width=250, padding="10")
        main_pane.add(sidebar_frame)

        # New VM Button
        self.btn_new = ttk.Button(sidebar_frame, text="+ Create New VM", command=self.open_create_vm_window)
        self.btn_new.pack(fill=tk.X, pady=(0, 10))

        # VM List
        ttk.Label(sidebar_frame, text="Your Machines:", font=("Arial", 10, "bold")).pack(anchor="w")
        self.vm_list = tk.Listbox(sidebar_frame, height=20)
        self.vm_list.pack(fill=tk.BOTH, expand=True, pady=5)
        self.vm_list.bind("<<ListboxSelect>>", self.on_vm_select)

        # Start/Stop Buttons
        self.btn_start = ttk.Button(sidebar_frame, text="Start / Boot", state=tk.DISABLED, command=self.start_vm)
        self.btn_start.pack(fill=tk.X, pady=5)
        
        self.btn_delete = ttk.Button(sidebar_frame, text="Delete VM", state=tk.DISABLED, command=self.delete_vm)
        self.btn_delete.pack(fill=tk.X, pady=5)

        # -- Right Area (Details / Console) --
        right_frame = ttk.Frame(main_pane, padding="10")
        main_pane.add(right_frame)

        # VM Details Label
        self.lbl_details = ttk.Label(right_frame, text="Select a virtual machine to view details or start.", 
                                     font=("Arial", 12), foreground="#555")
        self.lbl_details.pack(pady=20)

        # Console Output Area
        ttk.Label(right_frame, text="QEMU Console Output:").pack(anchor="w")
        self.console_output = scrolledtext.ScrolledText(right_frame, height=20, bg="black", fg="#00ff00", font=("Consolas", 10))
        self.console_output.pack(fill=tk.BOTH, expand=True, pady=5)
        self.console_output.insert(tk.END, "QEMU 7.0.0 monitor - type 'help' for commands\n")
        
    def populate_mock_machines(self):
        """Add some existing mock VMs to the list."""
        mock_vms = ["Ubuntu-Server-22.04", "Windows-11-Dev", "Debian-Testing"]
        for vm in mock_vms:
            self.vm_list.insert(tk.END, vm)

    def open_create_vm_window(self):
        """Opens the 'Create New Virtual Machine' dialog."""
        create_win = tk.Toplevel(self.root)
        create_win.title("Create New Virtual Machine")
        create_win.geometry("500x400")
        create_win.grab_set() # Modal window

        # Form Frame
        form_frame = ttk.Frame(create_win, padding="20")
        form_frame.pack(fill=tk.BOTH, expand=True)

        # 1. Name Input
        ttk.Label(form_frame, text="VM Name:").grid(row=0, column=0, sticky="w", pady=10)
        entry_name = ttk.Entry(form_frame, width=40)
        entry_name.grid(row=0, column=1, pady=10, padx=10)
        entry_name.focus_set()

        # 2. Type Selection (OS)
        ttk.Label(form_frame, text="OS Type:").grid(row=1, column=0, sticky="w", pady=10)
        combo_os = ttk.Combobox(form_frame, values=["Linux", "Windows 10/11", "Other"], width=37)
        combo_os.current(0)
        combo_os.grid(row=1, column=1, pady=10, padx=10)

        # 3. ISO Image Selection
        ttk.Label(form_frame, text="ISO Image:").grid(row=2, column=0, sticky="w", pady=10)
        
        iso_frame = ttk.Frame(form_frame)
        iso_frame.grid(row=2, column=1, sticky="ew", pady=10, padx=10)
        
        entry_iso = ttk.Entry(iso_frame, width=30)
        entry_iso.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        iso_path = {"path": ""} # Store path in mutable dict

        def browse_iso():
            filename = filedialog.askopenfilename(
                title="Select ISO File",
                filetypes=[("ISO Files", "*.iso"), ("All Files", "*.*")]
            )
            if filename:
                entry_iso.delete(0, tk.END)
                entry_iso.insert(0, filename)
                iso_path["path"] = filename

        btn_browse = ttk.Button(iso_frame, text="Browse...", command=browse_iso)
        btn_browse.pack(side=tk.LEFT, padx=(5,0))

        # Memory Slider
        ttk.Label(form_frame, text="Memory (RAM):").grid(row=3, column=0, sticky="w", pady=10)
        scale_mem = ttk.Scale(form_frame, from_=512, to=8192, orient=tk.HORIZONTAL)
        scale_mem.set(2048)
        scale_mem.grid(row=3, column=1, sticky="ew", pady=10, padx=10)
        
        lbl_mem_val = ttk.Label(form_frame, text="2048 MB")
        lbl_mem_val.grid(row=3, column=2, padx=5)
        
        def update_mem(val):
            lbl_mem_val.config(text=f"{int(float(val))} MB")
        scale_mem.configure(command=update_mem)

        # 4. Create Button
        def confirm_create():
            name = entry_name.get().strip()
            iso = entry_iso.get().strip()
            
            if not name:
                messagebox.showerror("Error", "Please enter a VM Name.")
                return
            if not iso:
                messagebox.showerror("Error", "Please select an ISO Image file.")
                return

            # Add to list
            self.vm_list.insert(tk.END, name)
            self.console_log(f"VM '{name}' created successfully.")
            self.console_log(f"ISO: {iso}")
            create_win.destroy()

        btn_create = ttk.Button(form_frame, text="Create Virtual Machine", command=confirm_create)
        btn_create.grid(row=4, column=0, columnspan=3, pady=20, sticky="ew")

    def on_vm_select(self, event):
        """Enable buttons when a VM is selected."""
        selection = self.vm_list.curselection()
        if selection:
            self.btn_start.config(state=tk.NORMAL)
            self.btn_delete.config(state=tk.NORMAL)
            vm_name = self.vm_list.get(selection[0])
            self.lbl_details.config(text=f"Selected: {vm_name}")
            self.console_log(f"Selected VM: {vm_name}")
        else:
            self.btn_start.config(state=tk.DISABLED)
            self.btn_delete.config(state=tk.DISABLED)

    def delete_vm(self):
        selection = self.vm_list.curselection()
        if selection:
            vm_name = self.vm_list.get(selection[0])
            if messagebox.askyesno("Delete VM", f"Are you sure you want to delete '{vm_name}'?"):
                self.vm_list.delete(selection[0])
                self.lbl_details.config(text="Select a virtual machine...")
                self.console_log(f"VM '{vm_name}' deleted.")
                self.btn_start.config(state=tk.DISABLED)
                self.btn_delete.config(state=tk.DISABLED)

    def start_vm(self):
        """Simulates starting a QEMU VM in a separate thread."""
        selection = self.vm_list.curselection()
        if not selection:
            return

        vm_name = self.vm_list.get(selection[0])
        self.btn_start.config(state=tk.DISABLED)
        self.console_log(f"Executing: qemu-system-x86_64 -name {vm_name} -m 2048 -cdrom {vm_name}.iso ...")
        
        # Start simulation thread
        threading.Thread(target=self.simulate_boot_sequence, args=(vm_name,), daemon=True).start()

    def simulate_boot_sequence(self, vm_name):
        """Generates fake BIOS boot logs."""
        boot_logs = [
            f"qemu-system-x86_64: -machine accel=kvm",
            f"SeaBIOS (version 1.16.0)",
            "",
            f"QEMU VGABIOS: VGABIOS ptser, build date",
            "",
            f"Found VBE device at 0x...",
            f"Booting from DVD/CD {vm_name}.iso...",
            "",
            f"Loading Linux kernel ...",
            f"Loading initial ramdisk ...",
            f"[    0.000000] Linux version 5.15.0-generic (buildd@lgw01-amd64-001)",
            f"[    0.000001] Command line: BOOT_IMAGE=/casper/vmlinuz file=/cdrom/preseed/ubuntu.seed boot=casper quiet splash --",
            f"[    0.000002] x86/fpu: Supporting XSAVE feature 0x001: 'x87 floating point registers'",
            f"[    0.123456] ACPI: DSDT 00000000000 (v02 BOCHS  BXPCDSDT 00000001 BXPC 00000001)",
            f"[    0.456789] systemd[1]: Detected architecture x86-64.",
            "",
            f"Welcome to {vm_name} Installer!",
            "",
            "Starting graphical installer..."
        ]

        self.console_log("-" * 50)
        
        for line in boot_logs:
            time.sleep(random.uniform(0.1, 0.5)) # Simulate processing time
            self.console_log(line)
        
        self.console_log("-" * 50)
        self.console_log("VM Boot Complete. (Simulation)")
        
        # Re-enable button after boot
        self.root.after(0, lambda: self.btn_start.config(state=tk.NORMAL))

    def console_log(self, message):
        """Thread-safe way to update the console."""
        self.root.after(0, self._update_console, message)

    def _update_console(self, message):
        timestamp = time.strftime("%H:%M:%S")
        self.console_output.insert(tk.END, f"[{timestamp}] {message}\n")
        self.console_output.see(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = QemuManagerApp(root)
    root.mainloop()
