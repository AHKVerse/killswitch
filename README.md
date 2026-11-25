# VPN Kill Switch 🛡️

A cross-platform (Ubuntu & Windows) VPN Kill Switch with a graphical user interface (GUI) designed to prevent public IP leaks.

Whenever your public IP deviates from your authorized VPN server IP (e.g., if the VPN drops or disconnects unexpectedly), **VPN Kill Switch** instantly severs your network connection to stop any unencrypted data from escaping.

---

## 🌟 Key Features

- **Instant Cut-off:** Immediately disables networking when an IP mismatch is detected.
- **Easy Verification:** One-click detection of your current public IP.
- **GUI & Desktop Integration:** Comes with custom icons and desktop application launchers.
- **One-Click Network Restore:** Easily restore your network connectivity with a single click after reconnecting your VPN.
- **Cross-Platform:** Available for both **Ubuntu / Debian** (GTK3 / NetworkManager) and **Windows** (Tkinter / PowerShell).

---

## 🐧 Ubuntu / Debian Installation

### Option A: Install via Debian Package (.deb)
1. Download `dist/vpn-killswitch_1.0.0_all.deb` from the releases or repo.
2. Install it using `apt`:
   ```bash
   sudo apt install ./dist/vpn-killswitch_1.0.0_all.deb
   ```
3. Open your application launcher and search for **VPN Kill Switch**.

### Option B: Run from Source
```bash
sudo apt install python3-gi gir1.2-gtk-3.0 network-manager libnotify-bin
python3 killswitch_gui.py
```

---

## 🪟 Windows Installation

### Option A: Installer / Portable Package
1. Extract `dist/vpn-killswitch-windows-installer.zip`.
2. Right-click `Install_Windows.bat` and select **Run as administrator**.
   - This creates shortcuts on your Desktop and Start Menu with the app icon.
3. Alternatively, right-click `Run_Directly.bat` to run without installation.

### Option B: Run from Source
Ensure Python 3.8+ is installed:
```cmd
python killswitch_win.py
```

---

## 🚀 How to Use

1. Connect to your VPN.
2. Launch **VPN Kill Switch**.
3. Click **Detect Current System IP** (or type your authorized VPN IP).
4. Click **Enable Kill Switch**.
5. If the VPN disconnects and your real IP is exposed, the app immediately disables internet connectivity and alerts you.
6. Once your VPN is re-established, click **Restore Network**.

---

## 📄 License
MIT License. Free to use and distribute.
