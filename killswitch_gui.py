#!/usr/bin/env python3
import sys
import os
import json
import time
import threading
import urllib.request
import urllib.error
import subprocess
import gi

gi.require_version('Gtk', '3.0')
gi.require_version('GLib', '2.0')
from gi.repository import Gtk, GLib, Gdk

CONFIG_DIR = os.path.expanduser("~/.config/vpn-killswitch")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")

def load_config():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "target_ip": "",
        "check_interval": 3
    }

def save_config(cfg):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    try:
        with open(CONFIG_PATH, "w") as f:
            json.dump(cfg, f, indent=2)
    except Exception as e:
        print(f"Error saving config: {e}")

class KillSwitchApp(Gtk.Window):
    def __init__(self):
        super().__init__(title="VPN Kill Switch")
        self.set_default_size(440, 480)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_border_width(18)
        self.set_icon_name("vpn-killswitch")

        self.config = load_config()
        self.is_monitoring = False
        self.monitor_thread = None
        self.stop_requested = False

        self.setup_ui()
        self.apply_styles()

    def setup_ui(self):
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        self.add(main_box)

        # Header Title
        title_label = Gtk.Label()
        title_label.set_markup("<span size='x-large' weight='bold'>🛡️ VPN Kill Switch</span>")
        title_label.set_halign(Gtk.Align.CENTER)
        main_box.pack_start(title_label, False, False, 4)

        subtitle = Gtk.Label()
        subtitle.set_markup("<span size='small' color='#888888'>Public IP Monitor & Instant Leak Protection</span>")
        subtitle.set_halign(Gtk.Align.CENTER)
        main_box.pack_start(subtitle, False, False, 0)

        # Target IP Entry Section
        ip_frame = Gtk.Frame(label="Authorized IP (VPN Target IP)")
        ip_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        ip_box.set_border_width(10)
        ip_frame.add(ip_box)
        main_box.pack_start(ip_frame, False, False, 0)

        self.ip_entry = Gtk.Entry()
        self.ip_entry.set_placeholder_text("e.g. 198.51.100.45")
        self.ip_entry.set_text(self.config.get("target_ip", ""))
        ip_box.pack_start(self.ip_entry, False, False, 0)

        btn_detect_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.detect_btn = Gtk.Button(label="🔍 Detect Current System IP")
        self.detect_btn.connect("clicked", self.on_detect_current_ip)
        btn_detect_box.pack_start(self.detect_btn, True, True, 0)
        ip_box.pack_start(btn_detect_box, False, False, 0)

        # Status Display Box
        status_frame = Gtk.Frame(label="Live Status")
        status_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        status_box.set_border_width(10)
        status_frame.add(status_box)
        main_box.pack_start(status_frame, False, False, 0)

        self.current_ip_label = Gtk.Label()
        self.current_ip_label.set_markup("<b>Current IP:</b> <span color='#777'>Awaiting check...</span>")
        self.current_ip_label.set_halign(Gtk.Align.START)
        status_box.pack_start(self.current_ip_label, False, False, 0)

        self.status_label = Gtk.Label()
        self.status_label.set_markup("<b>Switch Status:</b> <span color='#888'>Inactive (OFF)</span>")
        self.status_label.set_halign(Gtk.Align.START)
        status_box.pack_start(self.status_label, False, False, 0)

        # Toggle Button & Action Buttons
        self.toggle_btn = Gtk.Button(label="Enable Kill Switch")
        self.toggle_btn.get_style_context().add_class("suggested-action")
        self.toggle_btn.connect("clicked", self.on_toggle_clicked)
        main_box.pack_start(self.toggle_btn, False, False, 4)

        # Re-enable Network Button
        self.restore_btn = Gtk.Button(label="🌐 Restore Network")
        self.restore_btn.connect("clicked", self.on_restore_network)
        main_box.pack_start(self.restore_btn, False, False, 0)

        # Settings Expander
        expander = Gtk.Expander(label="Advanced Settings")
        exp_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        exp_box.set_border_width(8)

        interval_label = Gtk.Label(label="Check Interval (seconds):")
        exp_box.pack_start(interval_label, False, False, 0)

        self.interval_spin = Gtk.SpinButton.new_with_range(1, 30, 1)
        self.interval_spin.set_value(float(self.config.get("check_interval", 3)))
        exp_box.pack_start(self.interval_spin, False, False, 0)

        expander.add(exp_box)
        main_box.pack_start(expander, False, False, 0)

        self.connect("destroy", self.on_window_destroy)

    def apply_styles(self):
        css_provider = Gtk.CssProvider()
        css = b"""
        window {
            background-color: #f7f9fa;
        }
        button.suggested-action {
            background-color: #2e7d32;
            color: #ffffff;
            font-weight: bold;
            padding: 8px;
            border-radius: 6px;
        }
        button.destructive-action {
            background-color: #c62828;
            color: #ffffff;
            font-weight: bold;
            padding: 8px;
            border-radius: 6px;
        }
        frame {
            border-radius: 8px;
        }
        """
        css_provider.load_from_data(css)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def fetch_public_ip(self, timeout=2.5):
        endpoints = [
            "https://api.ipify.org",
            "https://icanhazip.com",
            "https://ifconfig.me/ip",
            "https://checkip.amazonaws.com"
        ]
        for url in endpoints:
            try:
                req = urllib.request.Request(
                    url,
                    headers={'User-Agent': 'curl/7.81.0'}
                )
                with urllib.request.urlopen(req, timeout=timeout) as response:
                    ip = response.read().decode('utf-8').strip()
                    if ip and len(ip) <= 45:
                        return ip
            except Exception:
                continue
        return None

    def on_detect_current_ip(self, widget):
        self.detect_btn.set_sensitive(False)
        self.detect_btn.set_label("Detecting...")

        def worker():
            ip = self.fetch_public_ip(timeout=4.0)
            def update_ui():
                if ip:
                    self.ip_entry.set_text(ip)
                    self.current_ip_label.set_markup(f"<b>Current IP:</b> <span color='#2e7d32'>{ip}</span>")
                else:
                    self.show_message_dialog("Error", "Could not fetch current public IP. Please check internet connection.", Gtk.MessageType.WARNING)
                self.detect_btn.set_sensitive(True)
                self.detect_btn.set_label("🔍 Detect Current System IP")
            GLib.idle_add(update_ui)

        threading.Thread(target=worker, daemon=True).start()

    def on_toggle_clicked(self, widget):
        if not self.is_monitoring:
            target_ip = self.ip_entry.get_text().strip()
            if not target_ip:
                self.show_message_dialog("Error", "Please enter a valid target IP.", Gtk.MessageType.ERROR)
                return

            self.config["target_ip"] = target_ip
            self.config["check_interval"] = int(self.interval_spin.get_value())
            save_config(self.config)

            self.is_monitoring = True
            self.stop_requested = False
            self.ip_entry.set_sensitive(False)
            self.detect_btn.set_sensitive(False)
            self.interval_spin.set_sensitive(False)

            self.toggle_btn.set_label("Disable Kill Switch (Stop)")
            self.toggle_btn.get_style_context().remove_class("suggested-action")
            self.toggle_btn.get_style_context().add_class("destructive-action")
            self.status_label.set_markup("<b>Switch Status:</b> <span color='#2e7d32'>🟢 Active (Protected)</span>")

            self.monitor_thread = threading.Thread(target=self.run_monitor_loop, daemon=True)
            self.monitor_thread.start()
        else:
            self.stop_monitoring()

    def stop_monitoring(self):
        self.is_monitoring = False
        self.stop_requested = True
        self.ip_entry.set_sensitive(True)
        self.detect_btn.set_sensitive(True)
        self.interval_spin.set_sensitive(True)

        self.toggle_btn.set_label("Enable Kill Switch")
        self.toggle_btn.get_style_context().remove_class("destructive-action")
        self.toggle_btn.get_style_context().add_class("suggested-action")
        self.status_label.set_markup("<b>Switch Status:</b> <span color='#888888'>⚪ Inactive (OFF)</span>")

    def run_monitor_loop(self):
        target_ip = self.config["target_ip"].strip()
        interval = max(1, int(self.config.get("check_interval", 3)))

        while not self.stop_requested:
            current_ip = self.fetch_public_ip(timeout=2.5)

            if self.stop_requested:
                break

            if current_ip is None:
                GLib.idle_add(self.update_status_ui, "Connection failed or slow", "#d97706")
            elif current_ip != target_ip:
                GLib.idle_add(self.trigger_killswitch, current_ip, target_ip)
                break
            else:
                GLib.idle_add(self.update_status_ui, f"Safe ({current_ip})", "#2e7d32")

            for _ in range(interval * 2):
                if self.stop_requested:
                    break
                time.sleep(0.5)

    def update_status_ui(self, ip_text, color):
        self.current_ip_label.set_markup(f"<b>Current IP:</b> <span color='{color}'>{ip_text}</span>")

    def trigger_killswitch(self, detected_ip, target_ip):
        try:
            subprocess.run(["nmcli", "networking", "off"], check=False)
        except Exception as e:
            print(f"Failed to run nmcli: {e}")

        try:
            subprocess.run([
                "notify-send",
                "-u", "critical",
                "⚠️ IP Leak Detected!",
                f"Detected IP ({detected_ip}) does not match authorized IP ({target_ip}).\nInternet connection disabled instantly!"
            ], check=False)
        except Exception:
            pass

        self.stop_monitoring()
        self.status_label.set_markup("<b>Switch Status:</b> <span color='#c62828'>🚨 Internet Cut (Kill Switch Triggered)!</span>")
        self.current_ip_label.set_markup(f"<b>IP Leak:</b> <span color='#c62828'>{detected_ip}</span>")

        self.show_message_dialog(
            "Security Alert: IP Leak! (Kill Switch Triggered)",
            f"⚠️ Your system's public IP changed to {detected_ip} (Authorized IP was {target_ip})!\n\nTo prevent data leaks, internet connectivity was immediately killed.\nAfter reconnecting your VPN, click 'Restore Network' to regain internet access.",
            Gtk.MessageType.ERROR
        )

    def on_restore_network(self, widget):
        try:
            subprocess.run(["nmcli", "networking", "on"], check=True)
            self.show_message_dialog("Success", "Internet connection restored successfully.", Gtk.MessageType.INFO)
            self.status_label.set_markup("<b>Switch Status:</b> <span color='#888888'>⚪ Inactive (Ready)</span>")
        except Exception as e:
            self.show_message_dialog("Error", f"Failed to enable network: {e}", Gtk.MessageType.ERROR)

    def show_message_dialog(self, title, message, msg_type):
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=msg_type,
            buttons=Gtk.ButtonsType.OK,
            text=title
        )
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()

    def on_window_destroy(self, widget):
        self.stop_requested = True
        Gtk.main_quit()

def main():
    app = KillSwitchApp()
    app.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()
