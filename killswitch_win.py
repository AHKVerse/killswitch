import sys
import os
import json
import time
import threading
import urllib.request
import urllib.error
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox

CONFIG_DIR = os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')), 'VPNKillSwitch')
CONFIG_PATH = os.path.join(CONFIG_DIR, 'config.json')

def load_config():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {
        'target_ip': '',
        'check_interval': 3
    }

def save_config(cfg):
    try:
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(cfg, f, indent=2)
    except Exception as e:
        print(f"Error saving config: {e}")

class WindowsKillSwitchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("VPN Kill Switch - Windows Edition")
        self.root.geometry("450x460")
        self.root.resizable(False, False)

        base_dir = os.path.dirname(os.path.abspath(__file__))
        ico_path = os.path.join(base_dir, "vpn-killswitch.ico")
        if os.path.exists(ico_path):
            try:
                self.root.iconbitmap(ico_path)
            except Exception:
                pass

        self.config = load_config()
        self.is_monitoring = False
        self.stop_requested = False
        self.monitor_thread = None

        self.setup_ui()

    def setup_ui(self):
        style = ttk.Style()
        style.theme_use('clam')

        header_frame = tk.Frame(self.root, bg="#1e293b", pady=12)
        header_frame.pack(fill=tk.X)

        title = tk.Label(header_frame, text="🛡️ VPN Kill Switch", font=("Segoe UI", 16, "bold"), fg="#ffffff", bg="#1e293b")
        title.pack()

        subtitle = tk.Label(header_frame, text="Public IP Monitor & Instant Network Cut for Windows", font=("Segoe UI", 9), fg="#94a3b8", bg="#1e293b")
        subtitle.pack(pady=2)

        content = tk.Frame(self.root, padx=16, pady=12)
        content.pack(fill=tk.BOTH, expand=True)

        ip_group = ttk.LabelFrame(content, text=" Authorized IP (Target IP) ", padding=10)
        ip_group.pack(fill=tk.X, pady=(0, 10))

        self.ip_entry = ttk.Entry(ip_group, font=("Segoe UI", 11))
        self.ip_entry.insert(0, self.config.get("target_ip", ""))
        self.ip_entry.pack(fill=tk.X, pady=(0, 6))

        self.btn_detect = ttk.Button(ip_group, text="🔍 Detect Current System IP", command=self.detect_current_ip)
        self.btn_detect.pack(fill=tk.X)

        status_group = ttk.LabelFrame(content, text=" Live Status ", padding=10)
        status_group.pack(fill=tk.X, pady=(0, 10))

        self.lbl_current_ip = tk.Label(status_group, text="Current IP: Awaiting check...", font=("Segoe UI", 10), anchor="w")
        self.lbl_current_ip.pack(fill=tk.X, pady=2)

        self.lbl_switch_status = tk.Label(status_group, text="Switch Status: Inactive (OFF)", font=("Segoe UI", 10, "bold"), fg="#64748b", anchor="w")
        self.lbl_switch_status.pack(fill=tk.X, pady=2)

        self.btn_toggle = tk.Button(content, text="Enable Kill Switch", font=("Segoe UI", 11, "bold"),
                                    bg="#16a34a", fg="#ffffff", activebackground="#15803d", activeforeground="#ffffff",
                                    relief=tk.FLAT, pady=6, cursor="hand2", command=self.toggle_monitoring)
        self.btn_toggle.pack(fill=tk.X, pady=(0, 6))

        self.btn_restore = tk.Button(content, text="🌐 Restore Network", font=("Segoe UI", 10),
                                     bg="#e2e8f0", fg="#1e293b", relief=tk.FLAT, pady=4, cursor="hand2", command=self.restore_network)
        self.btn_restore.pack(fill=tk.X, pady=(0, 10))

        adv_group = ttk.LabelFrame(content, text=" Check Settings ", padding=8)
        adv_group.pack(fill=tk.X)

        lbl_interval = ttk.Label(adv_group, text="Check Interval (seconds):")
        lbl_interval.pack(side=tk.LEFT, padx=(0, 8))

        self.spin_interval = ttk.Spinbox(adv_group, from_=1, to=30, width=5)
        self.spin_interval.set(self.config.get("check_interval", 3))
        self.spin_interval.pack(side=tk.LEFT)

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def fetch_public_ip(self, timeout=2.5):
        endpoints = [
            "https://api.ipify.org",
            "https://icanhazip.com",
            "https://ifconfig.me/ip",
            "https://checkip.amazonaws.com"
        ]
        for url in endpoints:
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'curl/7.81.0'})
                with urllib.request.urlopen(req, timeout=timeout) as response:
                    ip = response.read().decode('utf-8').strip()
                    if ip and len(ip) <= 45:
                        return ip
            except Exception:
                continue
        return None

    def detect_current_ip(self):
        self.btn_detect.config(state=tk.DISABLED, text="Detecting...")
        def worker():
            ip = self.fetch_public_ip(timeout=4.0)
            def update():
                if ip:
                    self.ip_entry.delete(0, tk.END)
                    self.ip_entry.insert(0, ip)
                    self.lbl_current_ip.config(text=f"Current IP: {ip}", fg="#16a34a")
                else:
                    messagebox.showwarning("Error", "Could not fetch current public IP. Please check connection.")
                self.btn_detect.config(state=tk.NORMAL, text="🔍 Detect Current System IP")
            self.root.after(0, update)
        threading.Thread(target=worker, daemon=True).start()

    def toggle_monitoring(self):
        if not self.is_monitoring:
            target_ip = self.ip_entry.get().strip()
            if not target_ip:
                messagebox.showerror("Error", "Please enter a valid target IP.")
                return

            self.config["target_ip"] = target_ip
            try:
                self.config["check_interval"] = int(self.spin_interval.get())
            except Exception:
                self.config["check_interval"] = 3
            save_config(self.config)

            self.is_monitoring = True
            self.stop_requested = False
            self.ip_entry.config(state=tk.DISABLED)
            self.btn_detect.config(state=tk.DISABLED)
            self.spin_interval.config(state=tk.DISABLED)

            self.btn_toggle.config(text="Disable Kill Switch (Stop)", bg="#dc2626", activebackground="#b91c1c")
            self.lbl_switch_status.config(text="Switch Status: 🟢 Active (Protected)", fg="#16a34a")

            self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
            self.monitor_thread.start()
        else:
            self.stop_monitoring()

    def stop_monitoring(self):
        self.is_monitoring = False
        self.stop_requested = True
        self.ip_entry.config(state=tk.NORMAL)
        self.btn_detect.config(state=tk.NORMAL)
        self.spin_interval.config(state=tk.NORMAL)

        self.btn_toggle.config(text="Enable Kill Switch", bg="#16a34a", activebackground="#15803d")
        self.lbl_switch_status.config(text="Switch Status: ⚪ Inactive (OFF)", fg="#64748b")

    def monitor_loop(self):
        target_ip = self.config["target_ip"].strip()
        interval = max(1, int(self.config.get("check_interval", 3)))

        while not self.stop_requested:
            current_ip = self.fetch_public_ip(timeout=2.5)
            if self.stop_requested:
                break

            if current_ip is None:
                self.root.after(0, lambda: self.lbl_current_ip.config(text="Connection slow or unavailable", fg="#d97706"))
            elif current_ip != target_ip:
                self.root.after(0, lambda cip=current_ip, tip=target_ip: self.trigger_killswitch(cip, tip))
                break
            else:
                self.root.after(0, lambda cip=current_ip: self.lbl_current_ip.config(text=f"Current IP: {cip} (Safe)", fg="#16a34a"))

            for _ in range(interval * 2):
                if self.stop_requested:
                    break
                time.sleep(0.5)

    def trigger_killswitch(self, detected_ip, target_ip):
        try:
            cmd = "Get-NetAdapter | Where-Object { $_.Status -eq 'Up' } | Disable-NetAdapter -Confirm:$false"
            subprocess.run(["powershell", "-NoProfile", "-WindowStyle", "Hidden", "-Command", cmd], check=False, creationflags=0x08000000 if os.name == 'nt' else 0)
        except Exception as e:
            print(f"Error disabling adapters: {e}")

        self.stop_monitoring()
        self.lbl_switch_status.config(text="Status: 🚨 Internet Cut (Kill Switch Triggered)!", fg="#dc2626")
        self.lbl_current_ip.config(text=f"IP Leak Detected: {detected_ip}", fg="#dc2626")

        messagebox.showerror(
            "Security Alert: IP Leak! (Kill Switch Triggered)",
            f"⚠️ Your system's public IP changed to {detected_ip} (Authorized IP was {target_ip})!\n\nInternet connectivity was killed instantly to prevent data leaks.\nTo restore connection after reconnecting your VPN, click 'Restore Network'."
        )

    def restore_network(self):
        try:
            cmd = "Get-NetAdapter | Enable-NetAdapter -Confirm:$false"
            subprocess.run(["powershell", "-NoProfile", "-WindowStyle", "Hidden", "-Command", cmd], check=False, creationflags=0x08000000 if os.name == 'nt' else 0)
            messagebox.showinfo("Success", "Network adapters re-enabled successfully.")
            self.lbl_switch_status.config(text="Switch Status: ⚪ Inactive (Ready)", fg="#64748b")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to enable network adapters: {e}")

    def on_close(self):
        self.stop_requested = True
        self.root.destroy()

if __name__ == '__main__':
    root = tk.Tk()
    app = WindowsKillSwitchApp(root)
    root.mainloop()
