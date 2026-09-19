import os
import subprocess
import time
import re
import json
import threading
from datetime import datetime
import customtkinter as ctk
from tkinter import messagebox, filedialog
import tkinter as tk

# Require root
if os.geteuid() != 0:
    print("❌ This script must be run as root. Please use: sudo python3 console.py")
    exit(1)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# =========================================================
# MODERN ROUTER PORTAL PALETTE
# =========================================================
BG_MAIN     = "#1a1d23"
BG_SIDEBAR  = "#0f1115"
BG_CARD     = "#242831"
BG_INPUT    = "#1a1d23"
BORDER      = "#2f343d"
ACCENT      = "#3b82f6"
ACCENT_HOV  = "#2563eb"
TEXT        = "#e4e6eb"
TEXT_DIM    = "#8b8d94"
TEXT_MUTED  = "#5a5d66"
SUCCESS     = "#22c55e"
WARNING     = "#f59e0b"
DANGER      = "#ef4444"
INFO        = "#06b6d4"

# Wave background color - white at ~10% opacity
WAVE_COLOR = "#2e3138"
WAVE_BG = (
    "⠀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
    "⠇⡅⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
    "⠧⡇⠀⠀⠒⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠀⠀⠀⠀⠀⠀⠀⡤⡆⠦⠆⢀⠠⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
    "⠧⣷⣆⠅⢦⠀⠀⠀⠀⠀⠀⠀⠀⠠⠀⠈⠀⠀⠀⠀⠀⢤⣤⣆⢇⣶⣤⡤⡯⣦⣌⡡⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
    "⠷⣿⣷⣆⣐⡆⠀⠀⠀⠀⢀⠤⠊⠀⠀⢀⣠⣾⢯⣦⣴⣜⣺⣾⣿⣤⠟⠋⣷⢛⡣⠭⠢⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
    "⠯⣿⣷⢫⡯⠄⠀⠀⢀⠐⠁⠀⠀⠀⠠⣤⣿⣿⣾⣿⣿⣿⣿⣿⣿⣿⣿⣙⣷⡗⢤⡤⠀⠈⣰⠶⡤⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
    "⣩⣿⡏⠉⠉⠀⢠⡔⠁⠀⠀⠀⠀⠀⠀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡟⠑⣏⠶⡉⠖⣡⠂⣈⣤⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
    "⣮⣿⣧⣤⣤⠖⠁⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⢉⡻⣿⣿⣿⣿⣿⣿⣿⣿⠟⠓⠈⠅⠈⠀⠀⠘⢒⣽⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
    "⣿⡿⠛⠉⠀⠀⠀⣀⠔⢀⡴⣃⠀⠀⢀⠷⠲⡄⠸⠟⢋⣿⣿⣿⣿⣿⡇⠀⠀⠀⠐⠁⠀⠀⠂⠀⠀⠰⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
    "⡆⣷⣆⡐⠶⠤⢤⣷⣀⣀⣩⢐⣟⣥⠜⣤⣀⣠⣤⠀⠈⠉⢀⣹⣿⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠐⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
    "⢃⣿⣞⣫⡔⢆⡸⡿⣿⣿⣄⣰⣿⠁⢀⣛⠿⣻⣿⣿⣧⣬⣿⣿⣿⣿⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠀⠀⠀⢀\n"
    "⢼⣿⣟⢿⣧⣾⣵⣷⣿⣿⣟⡿⢿⣶⣞⣍⡴⢿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠀⣠⠈⠀⢀⣀⣼\n"
    "⠋⣿⣟⡛⢿⣿⣿⣿⣿⣿⣭⣿⣿⣿⣿⣯⣽⣿⣿⣿⣿⠟⠛⠿⢽⣿⣿⣆⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⣀⢀⡠⣤⣤⣰⣿⠟⠁⠀⠀⡼⢾⣿\n"
    "⣻⣿⣟⣇⠈⣉⣯⠿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠿⠃⠀⠀⠀⠀⠀⠻⣿⣿⣿⣿⣴⣶⣤⣤⣤⣤⣴⣴⣴⣶⣦⣦⣤⣦⣀⣦⣤⣶⣿⣿⣿⣿⣿⣿⣿⠿⠁⠀⠀⡀⣤⣬⣾⣿\n"
    "⡝⣿⣿⣇⣤⣶⣿⣷⣾⣭⡿⠻⢿⣿⣿⣿⣿⠿⠃⠀⠀⠀⠀⡄⠀⠀⠀⢊⡻⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡟⠋⢻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣟⢿⠟⢉⠀⡀⢤⣴⣿⣿⣿⠿⠻\n"
    "⡁⣻⣿⣿⣿⣿⣷⣿⣿⣿⣿⠾⣿⡿⠞⠁⠀⠀⠀⠀⠀⠔⠫⡅⠀⠀⠀⠀⠁⣀⠀⠈⠻⣿⣿⣿⣿⣻⢟⣁⣄⡄⣀⠙⠻⣿⣿⡿⠿⠛⡋⠕⠂⢀⣀⣄⣓⣳⢿⠟⢛⣩⠴⠈⠀\n"
    "⠂⡁⠈⠛⠛⠛⠛⠋⠁⠀⠈⠈⡀⠀⠀⠀⠀⢀⠘⠀⠀⠀⠆⠀⡀⡢⣀⣆⠄⠈⠨⢦⡀⣈⠙⠛⠿⢿⣿⣿⣿⣿⣿⡿⡿⠿⠟⠆⠒⠁⠀⢶⣾⠿⠟⠛⢉⣀⣠⡶⠚⠁⠀⠀⣠\n"
    "⠀⡇⡄⣀⡀⠀⠀⠀⠀⠀⠀⠀⢬⠠⠀⡀⠀⠋⠁⠀⡀⠀⠀⡀⠆⢱⣿⣿⣧⣧⣄⠛⣿⣞⣵⣤⣷⣄⠀⠀⠀⠐⠀⠀⠀⠀⠀⠈⠉⠁⠁⠀⠠⢤⣶⣾⣿⡿⠋⢀⣀⣰⣶⣾⣿\n"
    "⡀⡆⠀⡉⡁⢿⣉⢀⠀⣰⣷⣿⣟⠠⡽⢂⡀⡄⠀⠰⣖⢱⢖⢂⡆⠈⣿⣿⣿⣿⣿⣶⣄⡙⠻⢿⣿⣿⣷⣦⣀⠀⠠⣤⣀⡀⢈⣓⣶⣶⣿⣿⣿⣿⣿⠟⠉⠀⠀⠀⣉⣭⣽⣿⣿\n"
    "⡇⣯⣿⣿⣿⣾⣿⣿⣿⠿⠟⡡⢞⣹⠾⢻⣚⣛⢺⠞⢋⣭⣾⣧⡃⢄⡈⢿⣿⣿⣿⣿⣿⣿⣯⣿⣮⣽⣿⣿⣿⣿⣷⣬⣽⣿⣿⣿⣽⡿⣿⡿⠟⠋⢀⣀⣐⣺⣿⣿⣟⣫⣭⣿⣿\n"
    "⢳⣿⣿⣿⣿⣿⣿⣿⣿⣤⣿⣿⣿⣿⣿⣦⠒⠉⢁⡀⠀⣙⣛⢿⣷⣶⣅⠀⠙⠻⣿⣿⣿⣿⣟⡚⠛⠻⠞⠿⠿⡿⡿⠯⠁⠟⣊⠾⠝⢋⣁⣀⣤⣤⣿⣿⣿⡿⠿⠿⠻⠛⠻⠻⠿\n"
    "⣸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣟⣐⣾⡿⡟⢶⠾⢋⢹⠿⢿⣿⣿⣷⣦⡈⠙⠛⠿⠿⢿⣶⣶⣶⣶⣶⢶⠟⠚⠀⠁⠀⠀⠙⠛⠛⠛⠛⠛⠋⠉⠁⠀⠀⠀⠀⠀⢀⠀⠀\n"
)

MANUFACTURER_OUIS = {
    "Apple": ["00:03:93", "AC:61:EA", "F0:18:98"],
    "Samsung": ["00:12:FB", "00:16:32", "B8:5A:73"],
    "Dell": ["00:14:22", "00:06:5B", "D4:BE:D9"],
    "HP": ["00:04:23", "00:0B:CD", "30:8D:99"],
    "Lenovo": ["00:26:2D", "00:1E:4F", "50:7B:9D"],
    "Intel": ["00:13:20", "00:15:00", "8C:85:90"],
    "Realtek": ["00:E0:4C", "52:54:00", "00:0A:C0"],
    "Broadcom": ["00:10:18", "00:0A:F7", "B8:27:EB"],
    "Qualcomm": ["00:03:7F", "00:A0:C6", "DC:A6:32"],
    "Google": ["3C:5A:B4", "54:60:09", "F4:F5:D8"],
    "Amazon": ["0C:47:C9", "40:B4:CD", "68:37:E9"],
    "Microsoft": ["00:15:5D", "00:17:FA", "7C:1E:52"],
    "Raspberry Pi": ["B8:27:EB", "DC:A6:32", "E4:5F:01"],
    "TP-Link": ["50:C7:BF", "00:27:19", "14:CC:20"],
    "Netgear": ["00:09:5B", "00:0F:B5", "C4:3D:C7"],
    "Linksys": ["00:04:5A", "00:14:BF", "20:AA:4B"],
    "ASUS": ["00:E0:18", "00:1D:60", "04:92:26"],
    "D-Link": ["00:05:5D", "00:0D:88", "1C:7E:E5"],
    "Sony": ["00:01:4A", "00:04:1F", "28:0D:FC"],
    "Generic": ["00:11:22", "00:1A:2B", "00:2C:3D"]
}

# =========================================================
# MODERN REUSABLE WIDGETS
# =========================================================
class Card(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        kwargs.setdefault("fg_color", BG_CARD)
        kwargs.setdefault("corner_radius", 12)
        kwargs.setdefault("border_width", 1)
        kwargs.setdefault("border_color", BORDER)
        super().__init__(master, **kwargs)

class PrimaryButton(ctk.CTkButton):
    def __init__(self, master, text, command=None, danger=False, **kwargs):
        color = DANGER if danger else ACCENT
        hover = "#dc2626" if danger else ACCENT_HOV
        kwargs.setdefault("fg_color", color)
        kwargs.setdefault("hover_color", hover)
        kwargs.setdefault("text_color", "#ffffff")
        kwargs.setdefault("corner_radius", 8)
        kwargs.setdefault("height", 38)
        kwargs.setdefault("font", ctk.CTkFont(size=13, weight="bold"))
        super().__init__(master, text=text, command=command, **kwargs)

class SecondaryButton(ctk.CTkButton):
    def __init__(self, master, text, command=None, **kwargs):
        kwargs.setdefault("fg_color", "transparent")
        kwargs.setdefault("hover_color", BG_CARD)
        kwargs.setdefault("text_color", TEXT)
        kwargs.setdefault("border_width", 1)
        kwargs.setdefault("border_color", BORDER)
        kwargs.setdefault("corner_radius", 8)
        kwargs.setdefault("height", 38)
        kwargs.setdefault("font", ctk.CTkFont(size=13))
        super().__init__(master, text=text, command=command, **kwargs)

class ModernEntry(ctk.CTkEntry):
    def __init__(self, master, **kwargs):
        kwargs.setdefault("fg_color", BG_INPUT)
        kwargs.setdefault("border_color", BORDER)
        kwargs.setdefault("border_width", 1)
        kwargs.setdefault("text_color", TEXT)
        kwargs.setdefault("corner_radius", 8)
        kwargs.setdefault("height", 38)
        kwargs.setdefault("font", ctk.CTkFont(size=13))
        super().__init__(master, **kwargs)

class PageTitle(ctk.CTkFrame):
    def __init__(self, master, title, subtitle=""):
        super().__init__(master, fg_color="transparent")
        ctk.CTkLabel(self, text=title, font=ctk.CTkFont(size=22, weight="bold"),
                     text_color=TEXT, anchor="w").pack(fill="x")
        if subtitle:
            ctk.CTkLabel(self, text=subtitle, font=ctk.CTkFont(size=12),
                         text_color=TEXT_DIM, anchor="w").pack(fill="x", pady=(2, 0))

class StatBox(ctk.CTkFrame):
    def __init__(self, master, label, value, color=ACCENT, icon=""):
        super().__init__(master, fg_color=BG_CARD, corner_radius=10,
                         border_width=1, border_color=BORDER)
        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.pack(padx=18, pady=16, fill="both", expand=True)
        ctk.CTkLabel(inner, text=f"{icon}  {label}", font=ctk.CTkFont(size=11),
                     text_color=TEXT_DIM, anchor="w").pack(fill="x")
        self.value_lbl = ctk.CTkLabel(inner, text=value,
                                      font=ctk.CTkFont(size=18, weight="bold"),
                                      text_color=color, anchor="w")
        self.value_lbl.pack(fill="x", pady=(6, 0))

    def set(self, value, color=None):
        self.value_lbl.configure(text=value)
        if color:
            self.value_lbl.configure(text_color=color)

class SidebarButton(ctk.CTkButton):
    def __init__(self, master, text, icon, command, key):
        super().__init__(master, text=f"  {icon}   {text}", command=command,
                         fg_color=BG_SIDEBAR, hover_color=BG_CARD,
                         text_color=TEXT_DIM, anchor="w", corner_radius=8,
                         height=42, font=ctk.CTkFont(size=13),
                         text_color_disabled=TEXT_DIM)
        self.key = key
        self._active = False

    def set_active(self, active):
        self._active = active
        if active:
            self.configure(fg_color=ACCENT, hover_color=ACCENT_HOV, text_color="#ffffff")
        else:
            self.configure(fg_color=BG_SIDEBAR, hover_color=BG_CARD, text_color=TEXT_DIM)

# =========================================================
# MAIN APPLICATION
# =========================================================
class WaveInterface(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Wave Interface Router Portal")
        self.geometry("1180x780")
        self.minsize(1000, 700)
        self.configure(fg_color=BG_MAIN)

        self.interfaces = {}
        self.selected_wan = None
        self.selected_lans = {}
        self.current_wifi = "Not Connected"
        self.wifi_networks = []
        self.last_auto_mac_time = 0
        self.auto_mac_cooldown = 3600
        self.current_page = "dashboard"
        self.page_frames = {}
        self.vpn_configs = []
        self.last_ip_data = {}
        
        # Tor Exit Node Controls
        self.hourly_rotation_active = False

        self._build_sidebar()
        self._build_content_area()
        self._refresh_interfaces()
        self._detect_current_wifi()
        self.show_page("dashboard")
        self._start_status_loop()

    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, fg_color=BG_SIDEBAR, corner_radius=0,
                                    border_width=0, width=240)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        brand = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        brand.pack(fill="x", padx=20, pady=(22, 20))
        ctk.CTkLabel(brand, text="Wave Interface",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color=TEXT).pack(anchor="w")
        ctk.CTkLabel(brand, text="Router Portal",
                     font=ctk.CTkFont(size=11), text_color=TEXT_DIM).pack(anchor="w")

        ctk.CTkFrame(self.sidebar, fg_color=BORDER, height=1).pack(fill="x", padx=16, pady=(0, 12))

        nav_items = [
            ("dashboard", "Dashboard", "📊"),
            ("network",   "Network",    "🌐"),
            ("wifi",      "Wi-Fi",      "📶"),
            ("sharing",   "Sharing",    "🔗"),
            ("vpn",       "VPN / Tor",  "🛡️"),
            ("mac",       "MAC Address","🎭"),
            ("firewall",  "Firewall",   "🔥"),
            ("system",    "System",     "⚙️"),
        ]

        self.nav_buttons = {}
        nav_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        nav_frame.pack(fill="both", expand=True, padx=10, pady=6)

        for key, label, icon in nav_items:
            btn = SidebarButton(nav_frame, label, icon,
                                lambda k=key: self.show_page(k), key)
            btn.pack(fill="x", pady=2)
            self.nav_buttons[key] = btn

        ctk.CTkFrame(self.sidebar, fg_color=BORDER, height=1).pack(fill="x", padx=16, pady=(8, 8))

        self.sidebar_status = ctk.CTkLabel(self.sidebar, text="● System Ready",
                                           font=ctk.CTkFont(size=11), text_color=SUCCESS)
        self.sidebar_status.pack(padx=20, pady=(0, 18), anchor="w")

    def _build_content_area(self):
        self.content = ctk.CTkFrame(self, fg_color=BG_MAIN, corner_radius=0, border_width=0)
        self.content.pack(side="left", fill="both", expand=True)

        # Top bar
        self.topbar = ctk.CTkFrame(self.content, fg_color=BG_SIDEBAR, corner_radius=0,
                                   border_width=0, height=56)
        self.topbar.pack(fill="x")
        self.topbar.pack_propagate(False)

        self.topbar_title = ctk.CTkLabel(self.topbar, text="Dashboard",
                                         font=ctk.CTkFont(size=16, weight="bold"),
                                         text_color=TEXT)
        self.topbar_title.pack(side="left", padx=28, pady=16)

        self.topbar_info = ctk.CTkLabel(self.topbar, text="",
                                        font=ctk.CTkFont(size=12), text_color=TEXT_DIM)
        self.topbar_info.pack(side="right", padx=28)

        # === WAVE BACKGROUND ===
        self.wave_label = ctk.CTkLabel(
            self.content, text=WAVE_BG,
            font=ctk.CTkFont(family="monospace", size=9),
            text_color=WAVE_COLOR,
            justify="left", anchor="nw"
        )
        self.wave_label.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.wave_label.lower()

        # Scrollable page container
        self.page_container = ctk.CTkScrollableFrame(
            self.content, fg_color="transparent",
            corner_radius=0, border_width=0,
            scrollbar_button_color=BG_CARD,
            scrollbar_button_hover_color=BORDER
        )
        self.page_container.pack(fill="both", expand=True)

        try:
            self.page_container._parent_frame.configure(fg_color="transparent")
        except:
            pass

        # Build all pages
        self.page_frames["dashboard"] = self._build_dashboard()
        self.page_frames["network"]   = self._build_network_page()
        self.page_frames["wifi"]      = self._build_wifi_page()
        self.page_frames["sharing"]   = self._build_sharing_page()
        self.page_frames["vpn"]       = self._build_vpn_page()
        self.page_frames["mac"]       = self._build_mac_page()
        self.page_frames["firewall"]  = self._build_firewall_page()
        self.page_frames["system"]    = self._build_system_page()

    def show_page(self, key):
        for f in self.page_frames.values():
            f.pack_forget()
        self.page_frames[key].pack(fill="both", expand=True, padx=28, pady=22)

        for k, btn in self.nav_buttons.items():
            btn.set_active(k == key)

        titles = {
            "dashboard": "Dashboard", "network": "Network Interfaces",
            "wifi": "Wi-Fi", "sharing": "Internet Sharing",
            "vpn": "VPN / Tor", "mac": "MAC Address",
            "firewall": "Firewall", "system": "System"
        }
        self.topbar_title.configure(text=titles.get(key, ""))
        self.current_page = key

        if key == "dashboard": self._refresh_dashboard()
        if key == "network":   self._refresh_network_page()
        if key == "vpn":       self._refresh_vpn_page()
        if key == "firewall":  self._refresh_firewall_page()
        if key == "mac":       self._refresh_mac_page()

        self.wave_label.lower()

    def _run_cmd(self, cmd):
        try:
            r = subprocess.run(cmd, shell=True, check=True,
                               capture_output=True, text=True)
            return True, r.stdout.strip()
        except subprocess.CalledProcessError as e:
            return False, (e.stderr or e.stdout).strip()

    def _refresh_interfaces(self):
        self.interfaces = {}
        ok, out = self._run_cmd("ip -o link show")
        if not ok:
            return

        for line in out.splitlines():
            parts = line.split(": ")
            if len(parts) < 2:
                continue
            name = parts[1].split("@")[0].strip()
            if name == "lo":
                continue

            flags = parts[2] if len(parts) > 2 else ""
            status = "UP" if "UP" in flags else "DOWN"

            ok2, ip = self._run_cmd(f"ip -4 addr show {name} | awk '/inet/ {{print $2}}' | head -1")
            ip = ip if ok2 else ""
            ok3, mac = self._run_cmd(f"ip link show {name} | awk '/link\\/ether/ {{print $2}}' | head -1")
            mac = mac if ok3 else ""

            if name.startswith("wlan") or name.startswith("wlp"):
                itype = "Wi-Fi"
            elif name.startswith("eth") or name.startswith("enp") or name.startswith("enx"):
                itype = "Ethernet"
            elif name.startswith("br") or name.startswith("docker"):
                itype = "Bridge/Virtual"
            else:
                itype = "Other"

            self.interfaces[name] = {
                "name": name, "status": status, "ip": ip,
                "mac": mac, "type": itype
            }

    def _detect_current_wifi(self):
        ok, out = self._run_cmd("nmcli -t -f ACTIVE,SSID dev wifi | grep '^yes' | cut -d: -f2")
        self.current_wifi = out.strip() if ok and out.strip() else "Not Connected"

    def _get_lan_subnets(self):
        subnets = {}
        subnet_idx = 77
        for lan in self.selected_lans:
            subnets[lan] = f"192.168.{subnet_idx}"
            subnet_idx += 1
        return subnets

    def _build_dashboard(self):
        frame = ctk.CTkFrame(self.page_container, fg_color="transparent")
        PageTitle(frame, "Dashboard", "System overview and quick status").pack(fill="x", pady=(0, 18))

        stats = ctk.CTkFrame(frame, fg_color="transparent")
        stats.pack(fill="x")
        for i in range(4):
            stats.columnconfigure(i, weight=1, uniform="s")

        self.stat_wan = StatBox(stats, "WAN (Incoming)", "Not set", ACCENT, "🌐")
        self.stat_wan.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        self.stat_lans = StatBox(stats, "LAN Interfaces", "0 active", INFO, "🔌")
        self.stat_lans.grid(row=0, column=1, sticky="nsew", padx=4)
        self.stat_vpn = StatBox(stats, "VPN Bypass", "Inactive", WARNING, "🛡️")
        self.stat_vpn.grid(row=0, column=2, sticky="nsew", padx=4)
        self.stat_wifi = StatBox(stats, "Wi-Fi", self.current_wifi, SUCCESS, "📶")
        self.stat_wifi.grid(row=0, column=3, sticky="nsew", padx=(8, 0))

        if_card = Card(frame)
        if_card.pack(fill="x", pady=(18, 0))
        ctk.CTkLabel(if_card, text="Detected Interfaces",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=TEXT).pack(anchor="w", padx=18, pady=(16, 10))

        self.dash_if_table = ctk.CTkFrame(if_card, fg_color="transparent")
        self.dash_if_table.pack(fill="x", padx=18, pady=(0, 16))

        btn_row = ctk.CTkFrame(if_card, fg_color="transparent")
        btn_row.pack(fill="x", padx=18, pady=(0, 16))
        PrimaryButton(btn_row, "🔄  Refresh", command=self._refresh_all).pack(side="right")

        return frame

    def _refresh_dashboard(self):
        self._refresh_interfaces()
        self._detect_current_wifi()

        if self.selected_wan and self.selected_wan in self.interfaces:
            self.stat_wan.set(self.selected_wan, ACCENT)
        else:
            self.stat_wan.set("Not set", TEXT_DIM)

        n_lans = len(self.selected_lans)
        n_bypass = sum(1 for v in self.selected_lans.values() if v.get("vpn_bypass"))
        self.stat_lans.set(f"{n_lans} selected", INFO)

        if n_bypass > 0:
            self.stat_vpn.set(f"{n_bypass} active", WARNING)
        else:
            self.stat_vpn.set("Inactive", TEXT_DIM)

        color = SUCCESS if self.current_wifi != "Not Connected" else TEXT_DIM
        self.stat_wifi.set(self.current_wifi, color)

        for w in self.dash_if_table.winfo_children():
            w.destroy()

        hdr = ctk.CTkFrame(self.dash_if_table, fg_color="transparent")
        hdr.pack(fill="x", pady=(0, 4))
        for txt, w in [("NAME", 1), ("TYPE", 1), ("STATUS", 1), ("IP ADDRESS", 2), ("ROLE", 1)]:
            ctk.CTkLabel(hdr, text=txt, font=ctk.CTkFont(size=10, weight="bold"),
                         text_color=TEXT_MUTED, anchor="w", width=0).pack(
                side="left", expand=True, fill="x")

        for name, info in self.interfaces.items():
            row = ctk.CTkFrame(self.dash_if_table, fg_color=BG_INPUT, corner_radius=6, height=34)
            row.pack(fill="x", pady=2)
            row.pack_propagate(False)

            role, role_color = "—", TEXT_DIM
            if name == self.selected_wan:
                role, role_color = "WAN", ACCENT
            elif name in self.selected_lans:
                role, role_color = "LAN", INFO
                if self.selected_lans[name].get("vpn_bypass"):
                    role += " +BYPASS"
                    role_color = WARNING

            status_color = SUCCESS if info["status"] == "UP" else TEXT_DIM

            for txt, c in [(info["name"], TEXT), (info["type"], TEXT_DIM),
                           (f"● {info['status']}", status_color),
                           (info["ip"] or "—", TEXT_DIM), (role, role_color)]:
                ctk.CTkLabel(row, text=txt, font=ctk.CTkFont(size=12),
                             text_color=c, anchor="w").pack(side="left", expand=True, fill="x", padx=8)

    def _refresh_all(self):
        self._refresh_interfaces()
        self._detect_current_wifi()
        self._refresh_dashboard()
        messagebox.showinfo("Refreshed", "Interface list updated.")

    def _build_network_page(self):
        frame = ctk.CTkFrame(self.page_container, fg_color="transparent")
        PageTitle(frame, "Network Interfaces",
                  "Choose which interface receives internet (WAN) and which distribute it (LAN)").pack(fill="x", pady=(0, 18))

        wan_card = Card(frame)
        wan_card.pack(fill="x", pady=(0, 14))
        ctk.CTkLabel(wan_card, text="🌐  Incoming Internet (WAN)",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=TEXT).pack(anchor="w", padx=18, pady=(16, 4))
        ctk.CTkLabel(wan_card, text="The interface currently providing your internet connection.",
                     font=ctk.CTkFont(size=11), text_color=TEXT_DIM).pack(anchor="w", padx=18, pady=(0, 12))

        self.wan_selector = ctk.CTkFrame(wan_card, fg_color="transparent")
        self.wan_selector.pack(fill="x", padx=18, pady=(0, 16))

        lan_card = Card(frame)
        lan_card.pack(fill="x", pady=(0, 14))
        ctk.CTkLabel(lan_card, text="🔌  Outgoing Interfaces (LAN)",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=TEXT).pack(anchor="w", padx=18, pady=(16, 4))
        ctk.CTkLabel(lan_card, text="Select which interfaces will distribute internet to connected devices.",
                     font=ctk.CTkFont(size=11), text_color=TEXT_DIM).pack(anchor="w", padx=18, pady=(0, 12))

        self.lan_selector = ctk.CTkFrame(lan_card, fg_color="transparent")
        self.lan_selector.pack(fill="x", padx=18, pady=(0, 16))

        act = ctk.CTkFrame(frame, fg_color="transparent")
        act.pack(fill="x")
        PrimaryButton(act, "💾  Save Configuration", command=self._save_network_config).pack(side="right")
        SecondaryButton(act, "🔄  Rescan Interfaces", command=self._refresh_network_page).pack(side="right", padx=(0, 10))

        return frame

    def _refresh_network_page(self):
        self._refresh_interfaces()
        self._detect_current_wifi()

        for w in self.wan_selector.winfo_children():
            w.destroy()
        self.wan_var = ctk.StringVar(value=self.selected_wan or "")

        for name, info in self.interfaces.items():
            row = ctk.CTkFrame(self.wan_selector, fg_color=BG_INPUT, corner_radius=8)
            row.pack(fill="x", pady=3)

            rb = ctk.CTkRadioButton(row, text="", variable=self.wan_var, value=name,
                                    fg_color=ACCENT, hover_color=ACCENT_HOV,
                                    border_color=BORDER)
            rb.pack(side="left", padx=12, pady=10)

            info_frame = ctk.CTkFrame(row, fg_color="transparent")
            info_frame.pack(side="left", fill="x", expand=True, padx=(0, 12))
            ctk.CTkLabel(info_frame, text=f"{name}   •   {info['type']}",
                         font=ctk.CTkFont(size=13, weight="bold"),
                         text_color=TEXT, anchor="w").pack(fill="x")

            status_color = SUCCESS if info["status"] == "UP" else TEXT_DIM
            ctk.CTkLabel(info_frame,
                         text=f"● {info['status']}   |   {info['ip'] or 'No IP'}   |   MAC: {info['mac'] or '—'}",
                         font=ctk.CTkFont(size=11), text_color=status_color, anchor="w").pack(fill="x")

        for w in self.lan_selector.winfo_children():
            w.destroy()
        self.lan_vars = {}

        for name, info in self.interfaces.items():
            if name == self.wan_var.get():
                continue

            row = ctk.CTkFrame(self.lan_selector, fg_color=BG_INPUT, corner_radius=8)
            row.pack(fill="x", pady=3)

            var = ctk.BooleanVar(value=name in self.selected_lans)
            self.lan_vars[name] = var

            cb = ctk.CTkCheckBox(row, text="", variable=var,
                                 fg_color=INFO, hover_color=INFO,
                                 border_color=BORDER)
            cb.pack(side="left", padx=12, pady=10)

            info_frame = ctk.CTkFrame(row, fg_color="transparent")
            info_frame.pack(side="left", fill="x", expand=True, padx=(0, 12))
            ctk.CTkLabel(info_frame, text=f"{name}   •   {info['type']}",
                         font=ctk.CTkFont(size=13, weight="bold"),
                         text_color=TEXT, anchor="w").pack(fill="x")

            status_color = SUCCESS if info["status"] == "UP" else TEXT_DIM
            ctk.CTkLabel(info_frame,
                         text=f"● {info['status']}   |   {info['ip'] or 'No IP'}   |   MAC: {info['mac'] or '—'}",
                         font=ctk.CTkFont(size=11), text_color=status_color, anchor="w").pack(fill="x")

    def _save_network_config(self):
        wan = self.wan_var.get()
        if not wan:
            return messagebox.showerror("Error", "Please select a WAN interface.")

        self.selected_wan = wan
        self.selected_lans = {
            name: {"vpn_bypass": self.selected_lans.get(name, {}).get("vpn_bypass", False),
                   "dhcp": True}
            for name, var in self.lan_vars.items() if var.get()
        }

        messagebox.showinfo("Saved",
                            f"WAN: {wan}\nLANs: {', '.join(self.selected_lans) or 'None'}\n\n"
                            f"Configure DHCP and VPN bypass in their respective tabs.")
        self._refresh_dashboard()

    def _build_wifi_page(self):
        frame = ctk.CTkFrame(self.page_container, fg_color="transparent")
        PageTitle(frame, "Wi-Fi", "Connect to an upstream wireless network").pack(fill="x", pady=(0, 18))

        cur = Card(frame)
        cur.pack(fill="x", pady=(0, 14))
        ctk.CTkLabel(cur, text="Current Connection",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=TEXT).pack(anchor="w", padx=18, pady=(16, 8))

        self.wifi_cur_lbl = ctk.CTkLabel(cur, text=f"● {self.current_wifi}",
                                         font=ctk.CTkFont(size=13, weight="bold"),
                                         text_color=SUCCESS if self.current_wifi != "Not Connected" else TEXT_DIM)
        self.wifi_cur_lbl.pack(anchor="w", padx=18, pady=(0, 16))

        scan = Card(frame)
        scan.pack(fill="x", pady=(0, 14))
        ctk.CTkLabel(scan, text="Available Networks",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=TEXT).pack(anchor="w", padx=18, pady=(16, 10))

        row1 = ctk.CTkFrame(scan, fg_color="transparent")
        row1.pack(fill="x", padx=18, pady=(0, 10))

        self.wifi_var = ctk.StringVar()
        self.wifi_dropdown = ctk.CTkComboBox(row1, variable=self.wifi_var,
                                             values=["Click 'Scan' to find networks..."],
                                             fg_color=BG_INPUT, border_color=BORDER,
                                             button_color=ACCENT, button_hover_color=ACCENT_HOV,
                                             text_color=TEXT, dropdown_fg_color=BG_CARD,
                                             dropdown_text_color=TEXT,
                                             font=ctk.CTkFont(size=12), height=38, corner_radius=8)
        self.wifi_dropdown.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.btn_scan = PrimaryButton(row1, "🔍  Scan", command=self.scan_wifi, width=110)
        self.btn_scan.pack(side="right")

        self.pass_var = ctk.StringVar()
        ModernEntry(scan, placeholder_text="Password (if required)",
                    textvariable=self.pass_var, show="*").pack(fill="x", padx=18, pady=(0, 12))

        btn_row = ctk.CTkFrame(scan, fg_color="transparent")
        btn_row.pack(fill="x", padx=18, pady=(0, 16))
        PrimaryButton(btn_row, "⚡  Connect", command=self.connect_wifi).pack(side="left")
        SecondaryButton(btn_row, "✖  Disconnect", command=self.disconnect_wifi).pack(side="left", padx=(10, 0))

        return frame

    def scan_wifi(self):
        self.btn_scan.configure(text="⏳  Scanning...", state="disabled")
        self.update()
        self._run_cmd("nmcli dev wifi rescan 2>/dev/null || true")
        time.sleep(2)

        ok, out = self._run_cmd(
            "nmcli -t -f SSID,SIGNAL,SECURITY dev wifi list | "
            "awk -F: '!seen[$1]++' | sort -t: -k2 -nr | head -20"
        )

        networks = []
        if ok and out:
            for line in out.split("\n"):
                parts = line.split(":")
                if len(parts) >= 3 and parts[0].strip():
                    ssid, signal, sec = parts[0].strip(), parts[1].strip(), parts[2].strip() or "Open"
                    try:
                        s = int(signal)
                        bars = "▂▄▆█" if s > 75 else "▂▄▆" if s > 50 else "▂▄" if s > 25 else "▂"
                    except:
                        bars, s = "▂", 0
                    networks.append((ssid, s, sec, f"{bars}  {ssid}    [{signal}% • {sec}]"))

        if networks:
            self.wifi_networks = networks
            self.wifi_dropdown.configure(values=[n[3] for n in networks])
            self.wifi_var.set(networks[0][3])
        else:
            self.wifi_dropdown.configure(values=["No networks found"])
            self.wifi_var.set("No networks found")

        self.btn_scan.configure(text="🔍  Scan", state="normal")

    def _get_ssid(self):
        val = self.wifi_var.get()
        if not val or val.startswith("No ") or val.startswith("Click"):
            return None
        try:
            cleaned = val.lstrip("▂▄▆█ ").strip()
            return cleaned.split("    [")[0].strip()
        except:
            return None

    def connect_wifi(self):
        ssid = self._get_ssid()
        if not ssid:
            return messagebox.showerror("Error", "Select a network first.")

        password = self.pass_var.get().strip()
        self._run_cmd(f'nmcli connection delete "{ssid}" 2>/dev/null || true')

        if password:
            cmd = f'nmcli dev wifi connect "{ssid}" password "{password}"'
        else:
            cmd = f'nmcli dev wifi connect "{ssid}"'

        ok, out = self._run_cmd(cmd)
        if ok:
            self.current_wifi = ssid
            self.wifi_cur_lbl.configure(text=f"● {ssid}", text_color=SUCCESS)
            messagebox.showinfo("Connected", f"Connected to {ssid}")
        else:
            messagebox.showerror("Error", f"Failed:\n{out}")

    def disconnect_wifi(self):
        ok, _ = self._run_cmd("nmcli connection show --active | awk '/wifi/ {print $1}'")
        if ok:
            for c in ok.splitlines():
                self._run_cmd(f'nmcli connection down "{c.strip()}" 2>/dev/null || true')

        self.current_wifi = "Not Connected"
        self.wifi_cur_lbl.configure(text="● Not Connected", text_color=TEXT_DIM)

    def _build_sharing_page(self):
        frame = ctk.CTkFrame(self.page_container, fg_color="transparent")
        PageTitle(frame, "Internet Sharing",
                  "Bridge your WAN connection to selected LAN interfaces via NAT/DHCP").pack(fill="x", pady=(0, 18))

        info = Card(frame)
        info.pack(fill="x", pady=(0, 14))
        ctk.CTkLabel(info, text="How it works",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=TEXT).pack(anchor="w", padx=18, pady=(16, 8))
        ctk.CTkLabel(info,
                     text="• WAN interface provides upstream internet\n"
                          "• Each selected LAN interface gets a /24 subnet (192.168.X.1)\n"
                          "• Dnsmasq provides DHCP to plugged-in devices\n"
                          "• Traffic is NAT'd through the WAN interface",
                     font=ctk.CTkFont(size=12), text_color=TEXT_DIM, justify="left").pack(
            anchor="w", padx=18, pady=(0, 16))

        self.sharing_status = Card(frame)
        self.sharing_status.pack(fill="x", pady=(0, 14))
        self.sharing_status_lbl = ctk.CTkLabel(self.sharing_status, text="● Sharing OFFLINE",
                                               font=ctk.CTkFont(size=13, weight="bold"),
                                               text_color=DANGER)
        self.sharing_status_lbl.pack(anchor="w", padx=18, pady=16)

        ctrl = Card(frame)
        ctrl.pack(fill="x")
        ctk.CTkLabel(ctrl, text="Controls",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=TEXT).pack(anchor="w", padx=18, pady=(16, 10))

        btn_row = ctk.CTkFrame(ctrl, fg_color="transparent")
        btn_row.pack(fill="x", padx=18, pady=(0, 16))
        PrimaryButton(btn_row, "▶  Start Sharing", command=self.start_sharing).pack(side="left")
        PrimaryButton(btn_row, "■  Stop Sharing", command=self.stop_sharing, danger=True).pack(side="left", padx=(10, 0))

        return frame

    def start_sharing(self):
        if not self.selected_wan:
            return messagebox.showerror("Error", "Select a WAN interface in the Network tab first.")
        if not self.selected_lans:
            return messagebox.showerror("Error", "Select at least one LAN interface in the Network tab.")

        # Enable IP forwarding
        self._run_cmd("sysctl -w net.ipv4.ip_forward=1")
        self._run_cmd("echo 'net.ipv4.ip_forward=1' >> /etc/sysctl.conf")
        
        subnets = self._get_lan_subnets()
        
        for lan, subnet in subnets.items():
            # Step 1: Completely disable NetworkManager for this interface
            self._run_cmd(f"nmcli device set {lan} managed no 2>/dev/null || true")
            self._run_cmd(f"nmcli connection delete {lan} 2>/dev/null || true")
            
            # Step 2: Bring interface down and flush all addresses
            self._run_cmd(f"ip link set {lan} down")
            time.sleep(0.5)
            self._run_cmd(f"ip addr flush dev {lan}")
            
            # Step 3: Bring interface UP first (before adding IP)
            self._run_cmd(f"ip link set {lan} up")
            time.sleep(0.5)
            
            # Step 4: Add IP address
            ok, out = self._run_cmd(f"ip addr add {subnet}.1/24 dev {lan}")
            if not ok:
                return messagebox.showerror("Error", f"Failed to assign IP to {lan}: {out}")
            
            # Step 5: Verify interface is UP and has IP
            time.sleep(0.5)
            ok, status = self._run_cmd(f"ip link show {lan} | grep -o 'state [A-Z]*' | cut -d' ' -f2")
            ok2, ip_check = self._run_cmd(f"ip -4 addr show {lan} | grep inet | awk '{{print $2}}'")
            
            if status != "UP" or not ip_check:
                return messagebox.showerror("Error", 
                    f"Interface {lan} failed to initialize.\n"
                    f"Status: {status}\nIP: {ip_check or 'None'}\n"
                    f"Try disconnecting and reconnecting the ethernet cable.")
            
            # Step 6: Configure dnsmasq for DHCP
            conf_path = f"/etc/dnsmasq.d/bridge-{lan}.conf"
            try:
                os.makedirs("/etc/dnsmasq.d", exist_ok=True)
                with open(conf_path, "w") as f:
                    f.write(f"# DHCP for {lan}\n")
                    f.write(f"interface={lan}\n")
                    f.write(f"listen-address={subnet}.1\n")
                    f.write(f"dhcp-range={subnet}.10,{subnet}.200,255.255.255.0,24h\n")
                    f.write(f"dhcp-option=3,{subnet}.1\n")  # Default gateway
                    f.write(f"dhcp-option=6,{subnet}.1\n")  # DNS server
                    f.write(f"dhcp-leasefile=/var/lib/misc/dnsmasq.{lan}.leases\n")
                    f.write(f"bind-interfaces\n")
                    f.write(f"except-interface=lo\n")
                    f.write(f"no-resolv\n")
                    f.write(f"server=8.8.8.8\n")
                    f.write(f"server=1.1.1.1\n")
            except Exception as e:
                return messagebox.showerror("Error", f"Config write failed: {e}")

            # Step 7: Configure iptables for NAT and forwarding
            nat_cmds = [
                # Remove existing rules to avoid duplicates
                f"iptables -t nat -D POSTROUTING -s {subnet}.0/24 -o {self.selected_wan} -j MASQUERADE 2>/dev/null || true",
                f"iptables -D FORWARD -i {lan} -o {self.selected_wan} -j ACCEPT 2>/dev/null || true",
                f"iptables -D FORWARD -i {self.selected_wan} -o {lan} -m state --state ESTABLISHED,RELATED -j ACCEPT 2>/dev/null || true",
                
                # Add NAT masquerade rule
                f"iptables -t nat -A POSTROUTING -s {subnet}.0/24 -o {self.selected_wan} -j MASQUERADE",
                
                # Allow forwarding from LAN to WAN
                f"iptables -A FORWARD -i {lan} -o {self.selected_wan} -j ACCEPT",
                
                # Allow return traffic from WAN to LAN
                f"iptables -A FORWARD -i {self.selected_wan} -o {lan} -m state --state ESTABLISHED,RELATED -j ACCEPT",
                
                # Allow DHCP traffic
                f"iptables -A INPUT -i {lan} -p udp --dport 67:68 -j ACCEPT",
            ]
            for c in nat_cmds:
                self._run_cmd(c)

        # Restart dnsmasq to apply new configuration
        self._run_cmd("systemctl restart dnsmasq")
        time.sleep(1)
        
        # Verify dnsmasq is running
        ok, _ = self._run_cmd("systemctl is-active dnsmasq")
        if not ok:
            return messagebox.showerror("Error", "dnsmasq failed to start. Check /var/log/syslog for details.")
        
        self.sharing_status_lbl.configure(text="● Sharing ONLINE", text_color=SUCCESS)
        
        lans_info = "\n".join([f"• {lan} → {subnet}.0/24 (Gateway: {subnet}.1)" for lan, subnet in subnets.items()])
        messagebox.showinfo("Sharing Started",
                            f"WAN: {self.selected_wan}\nLANs:\n{lans_info}\n\n"
                            f"Connected devices should receive IP addresses in the {subnet}.10-{subnet}.200 range.")

    def stop_sharing(self, show_msg=True):
        subnets = self._get_lan_subnets()
        for lan, subnet in subnets.items():
            cmds = [
                f"iptables -t nat -D POSTROUTING -s {subnet}.0/24 -o {self.selected_wan} -j MASQUERADE 2>/dev/null || true",
                f"iptables -D FORWARD -i {lan} -o {self.selected_wan} -j ACCEPT 2>/dev/null || true",
                f"iptables -D FORWARD -i {self.selected_wan} -o {lan} -m state --state ESTABLISHED,RELATED -j ACCEPT 2>/dev/null || true",
                f"iptables -D INPUT -i {lan} -p udp --dport 67:68 -j ACCEPT 2>/dev/null || true",
                f"ip link set {lan} down",
                f"ip addr flush dev {lan}",
                f"nmcli device set {lan} managed yes 2>/dev/null || true",
                f"rm -f /etc/dnsmasq.d/bridge-{lan}.conf",
            ]
            for c in cmds:
                self._run_cmd(c)

        self._run_cmd("systemctl restart dnsmasq")
        self.sharing_status_lbl.configure(text="● Sharing OFFLINE", text_color=DANGER)
        if show_msg:
            messagebox.showinfo("Stopped", "Internet sharing stopped.")

    def _build_vpn_page(self):
        frame = ctk.CTkFrame(self.page_container, fg_color="transparent")
        PageTitle(frame, "VPN / Tor", "Import VPN configs, manage bypass rules, and Tor routing").pack(fill="x", pady=(0, 18))

        import_card = Card(frame)
        import_card.pack(fill="x", pady=(0, 14))
        ctk.CTkLabel(import_card, text="Import VPN Configuration",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=TEXT).pack(anchor="w", padx=18, pady=(16, 8))
        btn_row = ctk.CTkFrame(import_card, fg_color="transparent")
        btn_row.pack(fill="x", padx=18, pady=(0, 16))
        PrimaryButton(btn_row, "📄 Import WireGuard (.conf)", command=self._import_wireguard).pack(side="left")
        PrimaryButton(btn_row, "📄 Import OpenVPN (.ovpn)", command=self._import_openvpn).pack(side="left", padx=(10, 0))

        self.vpn_list_card = Card(frame)
        self.vpn_list_card.pack(fill="x", pady=(0, 14))
        ctk.CTkLabel(self.vpn_list_card, text="Imported Configurations",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=TEXT).pack(anchor="w", padx=18, pady=(16, 8))
        self.vpn_configs_list = ctk.CTkFrame(self.vpn_list_card, fg_color="transparent")
        self.vpn_configs_list.pack(fill="x", padx=18, pady=(0, 16))

        bypass_card = Card(frame)
        bypass_card.pack(fill="x", pady=(0, 14))
        ctk.CTkLabel(bypass_card, text="VPN Bypass (Split Tunnel)",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=TEXT).pack(anchor="w", padx=18, pady=(16, 4))
        ctk.CTkLabel(bypass_card,
                     text="Enable to let traffic on selected LAN interfaces bypass the VPN tunnel.",
                     font=ctk.CTkFont(size=11), text_color=TEXT_DIM).pack(anchor="w", padx=18, pady=(0, 12))
        self.vpn_bypass_list = ctk.CTkFrame(bypass_card, fg_color="transparent")
        self.vpn_bypass_list.pack(fill="x", padx=18, pady=(0, 16))
        btn_row2 = ctk.CTkFrame(bypass_card, fg_color="transparent")
        btn_row2.pack(fill="x", padx=18, pady=(0, 16))
        PrimaryButton(btn_row2, "💾  Apply Bypass Rules", command=self._apply_vpn_bypass).pack(side="right")

        # === TORI (TOR NETWORK) TRANSPARENT ROUTING ===
        tori_card = Card(frame)
        tori_card.pack(fill="x", pady=(0, 14))
        ctk.CTkLabel(tori_card, text="🧅 Tori (Tor Network) Transparent Routing",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=TEXT).pack(anchor="w", padx=18, pady=(16, 4))
        ctk.CTkLabel(tori_card,
                     text="Route all traffic from selected LAN interfaces through the Tor network.\n"
                          "Requires Tor to be installed. Uses Transparent Proxy (PREROUTING).",
                     font=ctk.CTkFont(size=11), text_color=TEXT_DIM, justify="left").pack(anchor="w", padx=18, pady=(0, 12))
        
        self.tori_status_lbl = ctk.CTkLabel(tori_card, text="● Tor Routing: OFFLINE",
                                            font=ctk.CTkFont(size=12, weight="bold"),
                                            text_color=DANGER)
        self.tori_status_lbl.pack(anchor="w", padx=18, pady=(0, 12))

        # IP Display Section
        ip_display_frame = ctk.CTkFrame(tori_card, fg_color=BG_INPUT, corner_radius=8)
        ip_display_frame.pack(fill="x", padx=18, pady=(0, 12))
        
        self.tori_ip_lbl = ctk.CTkLabel(ip_display_frame, text="Current IP: ---",
                                        font=ctk.CTkFont(size=14, family="monospace", weight="bold"),
                                        text_color=ACCENT)
        self.tori_ip_lbl.pack(anchor="w", padx=14, pady=(10, 2))
        
        self.tori_loc_lbl = ctk.CTkLabel(ip_display_frame, text="Location: ---",
                                         font=ctk.CTkFont(size=11), text_color=TEXT_DIM)
        self.tori_loc_lbl.pack(anchor="w", padx=14, pady=(0, 2))

        self.tori_isp_lbl = ctk.CTkLabel(ip_display_frame, text="ISP / Org: ---",
                                         font=ctk.CTkFont(size=11), text_color=TEXT_DIM)
        self.tori_isp_lbl.pack(anchor="w", padx=14, pady=(0, 10))

        # Exit Node Controls
        exit_card = ctk.CTkFrame(tori_card, fg_color=BG_INPUT, corner_radius=8)
        exit_card.pack(fill="x", padx=18, pady=(0, 12))
        
        ctk.CTkLabel(exit_card, text="Exit Node Controls", 
                     font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT).pack(anchor="w", padx=14, pady=(10, 5))
        
        self.avoid_usa_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(exit_card, text="Avoid USA Exit Nodes (Strict)", variable=self.avoid_usa_var,
                        command=self._toggle_avoid_usa, text_color=TEXT,
                        fg_color=ACCENT, hover_color=ACCENT_HOV, border_color=BORDER).pack(anchor="w", padx=14, pady=4)
        
        self.hourly_rotation_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(exit_card, text="Rotate Exit Node Every Hour", variable=self.hourly_rotation_var,
                        command=self._toggle_hourly_rotation, text_color=TEXT,
                        fg_color=ACCENT, hover_color=ACCENT_HOV, border_color=BORDER).pack(anchor="w", padx=14, pady=4)
        
        btn_row3 = ctk.CTkFrame(exit_card, fg_color="transparent")
        btn_row3.pack(fill="x", padx=14, pady=(0, 10))
        PrimaryButton(btn_row3, "🔄 Force New Exit Node", command=self._force_newnym).pack(side="left")

        tori_btn_row = ctk.CTkFrame(tori_card, fg_color="transparent")
        tori_btn_row.pack(fill="x", padx=18, pady=(0, 8))
        PrimaryButton(tori_btn_row, "⚡ Enable Tor Routing", command=self._apply_tor_routing).pack(side="left")
        PrimaryButton(tori_btn_row, "✖ Disable Tor Routing", command=self._remove_tor_routing, danger=True).pack(side="left", padx=(10, 0))
        
        tori_btn_row2 = ctk.CTkFrame(tori_card, fg_color="transparent")
        tori_btn_row2.pack(fill="x", padx=18, pady=(0, 8))
        PrimaryButton(tori_btn_row2, "🔍 Check IP (Popup)", command=self._show_ip_popup).pack(side="left")
        
        # PANIC RESET BUTTON
        PrimaryButton(tori_btn_row2, "⚠️ Reset Network Settings", command=self._panic_reset_network, danger=True).pack(side="left", padx=(10, 0))

        return frame

    def _refresh_vpn_page(self):
        for w in self.vpn_configs_list.winfo_children():
            w.destroy()
        if not self.vpn_configs:
            ctk.CTkLabel(self.vpn_configs_list, text="No VPN configs imported yet.",
                         font=ctk.CTkFont(size=12), text_color=TEXT_DIM).pack(anchor="w", pady=12)
        else:
            for cfg in self.vpn_configs:
                row = ctk.CTkFrame(self.vpn_configs_list, fg_color=BG_INPUT, corner_radius=8)
                row.pack(fill="x", pady=4)
                inner = ctk.CTkFrame(row, fg_color="transparent")
                inner.pack(side="left", fill="x", expand=True, padx=14, pady=12)
                ctk.CTkLabel(inner, text=cfg["name"],
                             font=ctk.CTkFont(size=13, weight="bold"),
                             text_color=TEXT, anchor="w").pack(fill="x")
                ctk.CTkLabel(inner,
                             text=f"{cfg['type']} • {cfg.get('username', 'No auth')}",
                             font=ctk.CTkFont(size=11), text_color=TEXT_DIM, anchor="w").pack(fill="x")

        for w in self.vpn_bypass_list.winfo_children():
            w.destroy()
        self.vpn_toggles = {}

        if not self.selected_lans:
            ctk.CTkLabel(self.vpn_bypass_list, text="No LAN interfaces selected. Go to Network tab first.",
                         font=ctk.CTkFont(size=12), text_color=TEXT_DIM).pack(anchor="w", pady=12)
            return

        for name in self.selected_lans:
            info = self.interfaces.get(name, {})
            row = ctk.CTkFrame(self.vpn_bypass_list, fg_color=BG_INPUT, corner_radius=8)
            row.pack(fill="x", pady=4)
            inner = ctk.CTkFrame(row, fg_color="transparent")
            inner.pack(side="left", fill="x", expand=True, padx=14, pady=12)
            ctk.CTkLabel(inner, text=name,
                         font=ctk.CTkFont(size=13, weight="bold"),
                         text_color=TEXT, anchor="w").pack(fill="x")
            ctk.CTkLabel(inner,
                         text=f"{info.get('type', '?')} • {info.get('ip') or 'No IP'} • {info.get('status', '?')}",
                         font=ctk.CTkFont(size=11), text_color=TEXT_DIM, anchor="w").pack(fill="x")

            current = self.selected_lans[name].get("vpn_bypass", False)
            var = ctk.BooleanVar(value=current)
            self.vpn_toggles[name] = var

            sw = ctk.CTkSwitch(row, text="", variable=var,
                               fg_color=BORDER, button_color=ACCENT,
                               button_hover_color=ACCENT_HOV,
                               progress_color=ACCENT)
            sw.pack(side="right", padx=14)

    def _import_wireguard(self):
        filepath = filedialog.askopenfilename(
            title="Select WireGuard Config",
            filetypes=[("WireGuard Config", "*.conf"), ("All files", "*.*")]
        )
        if not filepath:
            return
        try:
            with open(filepath, 'r') as f:
                content = f.read()
            name = os.path.basename(filepath)
            self.vpn_configs.append({
                "name": name,
                "type": "WireGuard",
                "path": filepath,
                "content": content
            })
            messagebox.showinfo("Success", f"WireGuard config '{name}' imported.")
            self._refresh_vpn_page()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import: {e}")

    def _import_openvpn(self):
        filepath = filedialog.askopenfilename(
            title="Select OpenVPN Config",
            filetypes=[("OpenVPN Config", "*.ovpn"), ("All files", "*.*")]
        )
        if not filepath:
            return
        dialog = ctk.CTkToplevel(self)
        dialog.title("OpenVPN Credentials")
        dialog.geometry("400x200")
        dialog.configure(fg_color=BG_CARD)

        ctk.CTkLabel(dialog, text="Optional: Enter credentials",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=TEXT).pack(pady=(20, 10))

        username_var = ctk.StringVar()
        password_var = ctk.StringVar()

        ModernEntry(dialog, placeholder_text="Username (optional)",
                    textvariable=username_var).pack(fill="x", padx=20, pady=5)
        ModernEntry(dialog, placeholder_text="Password (optional)",
                    textvariable=password_var, show="*").pack(fill="x", padx=20, pady=5)

        def confirm():
            try:
                with open(filepath, 'r') as f:
                    content = f.read()
                name = os.path.basename(filepath)
                username = username_var.get().strip()
                password = password_var.get().strip()

                self.vpn_configs.append({
                    "name": name,
                    "type": "OpenVPN",
                    "path": filepath,
                    "content": content,
                    "username": username if username else "No auth",
                    "password": password
                })
                messagebox.showinfo("Success", f"OpenVPN config '{name}' imported.")
                dialog.destroy()
                self._refresh_vpn_page()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import: {e}")

        PrimaryButton(dialog, "✓ Import", command=confirm).pack(pady=15)

    def _apply_vpn_bypass(self):
        for name, var in self.vpn_toggles.items():
            self.selected_lans[name]["vpn_bypass"] = var.get()

        has_nft, _ = self._run_cmd("nft list tables | grep -q mullvad && echo yes")

        for name, data in self.selected_lans.items():
            if data.get("vpn_bypass"):
                if has_nft:
                    self._run_cmd(f'nft insert rule inet mullvad output oifname "{name}" accept 2>/dev/null || true')
                    self._run_cmd(f'nft insert rule inet mullvad forward oifname "{name}" accept 2>/dev/null || true')
                    self._run_cmd(f'nft insert rule inet mullvad forward iifname "{name}" accept 2>/dev/null || true')
                self._run_cmd(f"iptables -I OUTPUT 1 -o {name} -j ACCEPT 2>/dev/null || true")
                self._run_cmd(f"iptables -I FORWARD 1 -o {name} -j ACCEPT 2>/dev/null || true")
                self._run_cmd(f"iptables -I FORWARD 1 -i {name} -j ACCEPT 2>/dev/null || true")
            else:
                if has_nft:
                    self._run_cmd(f'nft delete rule inet mullvad output oifname "{name}" accept 2>/dev/null || true')
                self._run_cmd(f"iptables -D OUTPUT -o {name} -j ACCEPT 2>/dev/null || true")
                self._run_cmd(f"iptables -D FORWARD -o {name} -j ACCEPT 2>/dev/null || true")
                self._run_cmd(f"iptables -D FORWARD -i {name} -j ACCEPT 2>/dev/null || true")

        n_on = sum(1 for d in self.selected_lans.values() if d.get("vpn_bypass"))
        messagebox.showinfo("Applied", f"VPN bypass rules applied.\n{n_on} interface(s) bypassing VPN.")

    # =========================================================
    # TORI (TOR NETWORK) INTEGRATION
    # =========================================================
    def _setup_tor(self):
        ok, _ = self._run_cmd("which tor")
        if not ok:
            ok, out = self._run_cmd("apt-get update && apt-get install -y tor")
            if not ok:
                messagebox.showerror("Error", f"Failed to install tor: {out}")
                return False
                
        torrc_path = "/etc/tor/torrc"
        try:
            with open(torrc_path, 'r') as f:
                content = f.read()
            
            additions = []
            if "TransPort 9040" not in content:
                additions.append("TransPort 9040")
            if "DNSPort 5353" not in content:
                additions.append("DNSPort 5353")
            if "AutomapHostsOnResolve 1" not in content:
                additions.append("AutomapHostsOnResolve 1")
                
            if additions:
                content += "\n# Tori Transparent Routing\n" + "\n".join(additions) + "\n"
                with open(torrc_path, 'w') as f:
                    f.write(content)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to configure torrc: {e}")
            return False
            
        self._run_cmd("systemctl enable tor")
        self._run_cmd("systemctl restart tor")
        return True

    def _apply_tor_routing(self):
        if not self.selected_wan:
            messagebox.showerror("Error", "Select a WAN interface in Network tab first.")
            return
        if not self.selected_lans:
            messagebox.showerror("Error", "Select LAN interfaces in Network tab first.")
            return
        
        if not self._setup_tor():
            return

        ok, tor_uid = self._run_cmd("id -u debian-tor 2>/dev/null || id -u _tor 2>/dev/null || id -u tor 2>/dev/null")
        if not ok or not tor_uid:
            messagebox.showerror("Error", "Could not determine Tor user UID.")
            return
        tor_uid = tor_uid.strip()

        # Clear previous Tor LAN rules
        self._run_cmd("iptables -t nat -F TOR_LAN 2>/dev/null || true")
        self._run_cmd("iptables -t nat -X TOR_LAN 2>/dev/null || true")
        self._run_cmd("iptables -t nat -N TOR_LAN")

        # Allow Tor's own traffic to bypass
        self._run_cmd(f"iptables -t nat -A TOR_LAN -m owner --uid-owner {tor_uid} -j RETURN")
        # Redirect DNS
        self._run_cmd("iptables -t nat -A TOR_LAN -p udp --dport 53 -j REDIRECT --to-ports 5353")
        self._run_cmd("iptables -t nat -A TOR_LAN -p tcp --dport 53 -j REDIRECT --to-ports 5353")
        # Redirect TCP
        self._run_cmd("iptables -t nat -A TOR_LAN -p tcp -j REDIRECT --to-ports 9040")

        # Apply to each LAN subnet
        subnets = self._get_lan_subnets()
        for lan, subnet in subnets.items():
            self._run_cmd(f"iptables -t nat -A PREROUTING -s {subnet}.0/24 -i {lan} -j TOR_LAN")

        self.tori_status_lbl.configure(text="● Tor Routing: ONLINE", text_color=SUCCESS)
        messagebox.showinfo("Success", "Tor transparent routing applied to selected LANs.\nAll LAN traffic is now routed through Tor.")
        
        # Update IP display after a short delay to allow Tor to establish circuits
        self.tori_ip_lbl.configure(text="Current IP: ...establishing Tor circuit...", text_color=WARNING)
        self.after(4000, lambda: self._check_ip_async(self._update_ip_display))

    def _remove_tor_routing(self, show_msg=True):
        subnets = self._get_lan_subnets()
        for lan, subnet in subnets.items():
            self._run_cmd(f"iptables -t nat -D PREROUTING -s {subnet}.0/24 -i {lan} -j TOR_LAN 2>/dev/null || true")
        
        self._run_cmd("iptables -t nat -F TOR_LAN 2>/dev/null || true")
        self._run_cmd("iptables -t nat -X TOR_LAN 2>/dev/null || true")
        
        self.tori_status_lbl.configure(text="● Tor Routing: OFFLINE", text_color=DANGER)
        if show_msg:
            messagebox.showinfo("Disabled", "Tor transparent routing disabled.")

    def _check_ip_async(self, callback, use_socks=False):
        def worker():
            urls = ["https://ipinfo.io/json", "https://api.ipify.org?format=json"]
            for url in urls:
                if use_socks:
                    cmd = ['curl', '-s', '--socks5-hostname', '127.0.0.1:9050', '--max-time', '10', url]
                else:
                    cmd = ['curl', '-s', '--max-time', '10', url]
                try:
                    res = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
                    if res.returncode == 0 and res.stdout:
                        data = json.loads(res.stdout)
                        if "ip" in data:
                            self.after(0, lambda d=data: callback(d))
                            return
                        if "origin" in data:
                            self.after(0, lambda d={"ip": data["origin"]}: callback(d))
                            return
                except Exception:
                    pass
            self.after(0, lambda: callback(None))
        threading.Thread(target=worker, daemon=True).start()

    def _update_ip_display(self, data):
        if data:
            ip = data.get("ip", "Unknown")
            city = data.get("city", "")
            reg = data.get("region", "")
            ctry = data.get("country", "")
            org = data.get("org", "Unknown")
            loc = ", ".join(x for x in [city, reg, ctry] if x) or "Unknown"
            
            self.tori_ip_lbl.configure(text=f"Current IP: {ip}", text_color=SUCCESS)
            self.tori_loc_lbl.configure(text=f"Location: {loc}")
            self.tori_isp_lbl.configure(text=f"ISP / Org: {org}")
            self.last_ip_data = data
        else:
            self.tori_ip_lbl.configure(text="Current IP: [Check Failed]", text_color=DANGER)
            self.tori_loc_lbl.configure(text="Location: ---")
            self.tori_isp_lbl.configure(text="ISP / Org: ---")

    def _show_ip_popup(self):
        self.tori_ip_lbl.configure(text="Current IP: ...querying...", text_color=WARNING)
        
        def on_complete(data):
            self._update_ip_display(data)
            if data:
                self._open_ip_popup(data)
            else:
                messagebox.showerror("Error", "Failed to retrieve IP information.")
                
        self._check_ip_async(on_complete)

    def _open_ip_popup(self, data):
        popup = ctk.CTkToplevel(self)
        popup.title("IP Information")
        popup.geometry("420x380")
        popup.configure(fg_color=BG_CARD)
        popup.transient(self)
        popup.grab_set()
        
        ctk.CTkLabel(popup, text="🌐 IP & Network Details",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=TEXT).pack(pady=(20, 10))
                     
        info_frame = ctk.CTkFrame(popup, fg_color=BG_INPUT, corner_radius=10)
        info_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        details = [
            ("IP Address", data.get("ip", "Unknown")),
            ("City", data.get("city", "Unknown")),
            ("Region", data.get("region", "Unknown")),
            ("Country", data.get("country", "Unknown")),
            ("ISP / Org", data.get("org", "Unknown")),
            ("Timezone", data.get("timezone", "Unknown")),
            ("Hostname", data.get("hostname", "Unknown"))
        ]
        
        for label, value in details:
            row = ctk.CTkFrame(info_frame, fg_color="transparent")
            row.pack(fill="x", padx=15, pady=6)
            ctk.CTkLabel(row, text=f"{label}:", font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=TEXT_DIM, anchor="w", width=100).pack(side="left")
            ctk.CTkLabel(row, text=str(value), font=ctk.CTkFont(size=12, family="monospace"),
                         text_color=ACCENT, anchor="w").pack(side="left", fill="x", expand=True)
                         
        PrimaryButton(popup, "✓ Close", command=popup.destroy).pack(pady=15)

    # =========================================================
    # TOR EXIT NODE CONTROLS
    # =========================================================
    def _toggle_avoid_usa(self):
        torrc_path = "/etc/tor/torrc"
        try:
            with open(torrc_path, 'r') as f:
                lines = f.readlines()
            
            # Remove existing ExcludeExitNodes and StrictNodes
            new_lines = [l for l in lines if not l.startswith("ExcludeExitNodes") and not l.startswith("StrictNodes")]
            
            if self.avoid_usa_var.get():
                new_lines.append("ExcludeExitNodes {us}\n")
                new_lines.append("StrictNodes 1\n")
                
            with open(torrc_path, 'w') as f:
                f.writelines(new_lines)
                
            self._run_cmd("systemctl restart tor")
            
            # If Tor is currently routing, force a new circuit to apply the change
            if self.tori_status_lbl.cget("text").startswith("● Tor Routing: ONLINE"):
                self._force_newnym()
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update torrc: {e}")

    def _toggle_hourly_rotation(self):
        if self.hourly_rotation_var.get():
            self.hourly_rotation_active = True
            self._schedule_newnym()
        else:
            self.hourly_rotation_active = False

    def _schedule_newnym(self):
        if not self.hourly_rotation_active:
            return
        self._force_newnym(silent=True)
        # Schedule next rotation in 1 hour (3600000 ms)
        self.after(3600000, self._schedule_newnym)

    def _force_newnym(self, silent=False):
        # Send SIGHUP to Tor to request new circuits (NEWNYM)
        ok, _ = self._run_cmd("pkill -HUP tor")
        if ok:
            if not silent:
                messagebox.showinfo("Tor", "Requested new Tor circuit (NEWNYM).")
            # Update IP display after a delay to allow circuit to build
            self.after(5000, lambda: self._check_ip_async(self._update_ip_display))
        else:
            if not silent:
                messagebox.showwarning("Tor", "Failed to signal Tor. Is it running?")

    # =========================================================
    # PANIC RESET NETWORK (Inspired by tori.py)
    # =========================================================
    def _panic_reset_network(self):
        if not messagebox.askyesno("PANIC RESET", 
                                   "This will completely reset all network settings, flush iptables, "
                                   "stop Tor, and restart network managers.\n\nProceed?"):
            return
            
        self.tori_status_lbl.configure(text="● PANIC RESET IN PROGRESS...", text_color=WARNING)
        self.update()
        
        # 1. Stop Tor routing
        self._remove_tor_routing(show_msg=False)
        
        # 2. Stop Internet Sharing
        self.stop_sharing(show_msg=False)
        
        # 3. Kill Tor daemon
        self._run_cmd("pkill -9 tor")
        self._run_cmd("systemctl stop tor")
        
        # 4. Flush ALL iptables rules and set policies to ACCEPT
        flush_cmds = [
            "iptables -F",
            "iptables -t nat -F",
            "iptables -t mangle -F",
            "iptables -X",
            "iptables -P INPUT ACCEPT",
            "iptables -P FORWARD ACCEPT",
            "iptables -P OUTPUT ACCEPT"
        ]
        for c in flush_cmds:
            self._run_cmd(c)
            
        # 5. Restart network managers (handles Pi OS dhcpcd/NetworkManager)
        for svc in ['NetworkManager', 'dhcpcd', 'systemd-networkd', 'networking', 'systemd-resolved']:
            self._run_cmd(f"systemctl restart {svc} 2>/dev/null || true")
            
        # 6. Reset UI state for Tor controls
        self.hourly_rotation_var.set(False)
        self.hourly_rotation_active = False
        self.avoid_usa_var.set(False)
        
        self.tori_status_lbl.configure(text="● Tor Routing: OFFLINE (Reset)", text_color=DANGER)
        self.tori_ip_lbl.configure(text="Current IP: ---", text_color=ACCENT)
        self.tori_loc_lbl.configure(text="Location: ---")
        self.tori_isp_lbl.configure(text="ISP / Org: ---")
        
        messagebox.showinfo("PANIC COMPLETE", 
                            "Network interfaces and DNS restored.\nAll proxy and routing rules flushed.")
        self._refresh_interfaces()

    def _build_mac_page(self):
        frame = ctk.CTkFrame(self.page_container, fg_color="transparent")
        PageTitle(frame, "MAC Address", "Change or randomize the MAC address of an interface").pack(fill="x", pady=(0, 18))

        pick = Card(frame)
        pick.pack(fill="x", pady=(0, 14))
        ctk.CTkLabel(pick, text="Target Interface",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=TEXT).pack(anchor="w", padx=18, pady=(16, 10))

        self.mac_iface_var = ctk.StringVar()
        self.mac_iface_cb = ctk.CTkComboBox(pick, variable=self.mac_iface_var,
                                            values=[], state="readonly",
                                            fg_color=BG_INPUT, border_color=BORDER,
                                            button_color=ACCENT, button_hover_color=ACCENT_HOV,
                                            text_color=TEXT, dropdown_fg_color=BG_CARD,
                                            dropdown_text_color=TEXT,
                                            font=ctk.CTkFont(size=13), height=38, corner_radius=8)
        self.mac_iface_cb.pack(fill="x", padx=18, pady=(0, 10))

        self.auto_mac_wan_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(pick, text="🔄 Auto-change MAC for WAN interface when internet drops",
                        variable=self.auto_mac_wan_var, text_color=TEXT,
                        fg_color=ACCENT, hover_color=ACCENT_HOV,
                        border_color=BORDER, font=ctk.CTkFont(size=12)).pack(anchor="w", padx=18, pady=(0, 10))

        self.auto_mac_status = ctk.CTkLabel(pick, text="Auto-MAC: Disabled",
                                            text_color=TEXT_DIM, font=ctk.CTkFont(size=11))
        self.auto_mac_status.pack(anchor="w", padx=18, pady=(0, 16))

        cur = Card(frame)
        cur.pack(fill="x", pady=(0, 14))
        ctk.CTkLabel(cur, text="Current MAC",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=TEXT).pack(anchor="w", padx=18, pady=(16, 8))

        self.mac_current_lbl = ctk.CTkLabel(cur, text="—",
                                            font=ctk.CTkFont(size=16, family="monospace", weight="bold"),
                                            text_color=ACCENT)
        self.mac_current_lbl.pack(anchor="w", padx=18, pady=(0, 16))

        mode_card = Card(frame)
        mode_card.pack(fill="x", pady=(0, 14))
        ctk.CTkLabel(mode_card, text="Mode",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=TEXT).pack(anchor="w", padx=18, pady=(16, 10))

        self.mac_mode = ctk.StringVar(value="Random")
        mode_row = ctk.CTkFrame(mode_card, fg_color="transparent")
        mode_row.pack(fill="x", padx=18, pady=(0, 10))

        ctk.CTkRadioButton(mode_row, text="🎲 Random", variable=self.mac_mode,
                           value="Random", fg_color=ACCENT, hover_color=ACCENT_HOV,
                           border_color=BORDER, text_color=TEXT,
                           command=self._toggle_mac_entry).pack(side="left", padx=(0, 20))
        ctk.CTkRadioButton(mode_row, text="✏️ Specific", variable=self.mac_mode,
                           value="Specific", fg_color=ACCENT, hover_color=ACCENT_HOV,
                           border_color=BORDER, text_color=TEXT,
                           command=self._toggle_mac_entry).pack(side="left", padx=(0, 20))
        ctk.CTkRadioButton(mode_row, text="🏭 Manufacturer", variable=self.mac_mode,
                           value="Manufacturer", fg_color=ACCENT, hover_color=ACCENT_HOV,
                           border_color=BORDER, text_color=TEXT,
                           command=self._toggle_mac_entry).pack(side="left")

        mfr_row = ctk.CTkFrame(mode_card, fg_color="transparent")
        mfr_row.pack(fill="x", padx=18, pady=(0, 10))

        self.mfr_var = ctk.StringVar(value="Apple")
        self.mfr_dropdown = ctk.CTkComboBox(mfr_row, variable=self.mfr_var,
                                            values=list(MANUFACTURER_OUIS.keys()),
                                            state="readonly",
                                            fg_color=BG_INPUT, border_color=BORDER,
                                            button_color=ACCENT, button_hover_color=ACCENT_HOV,
                                            text_color=TEXT, dropdown_fg_color=BG_CARD,
                                            dropdown_text_color=TEXT,
                                            font=ctk.CTkFont(size=12), height=38, corner_radius=8)
        self.mfr_dropdown.pack(fill="x")
        self.mfr_dropdown.configure(state="disabled")

        self.mac_entries = []
        mac_row = ctk.CTkFrame(mode_card, fg_color="transparent")
        mac_row.pack(pady=(0, 16))

        for i in range(6):
            e = ModernEntry(mac_row, width=58, height=42, justify="center",
                            font=ctk.CTkFont(size=14, family="monospace", weight="bold"),
                            placeholder_text="XX")
            e.pack(side="left", padx=2)
            e.bind("<KeyRelease>", lambda ev, idx=i: self._mac_key_handler(ev, idx))
            e.configure(state="disabled")
            self.mac_entries.append(e)

            if i < 5:
                ctk.CTkLabel(mac_row, text=":", font=ctk.CTkFont(size=18, weight="bold"),
                             text_color=TEXT_DIM).pack(side="left", padx=2)

        btn_row = ctk.CTkFrame(frame, fg_color="transparent")
        btn_row.pack(fill="x")
        PrimaryButton(btn_row, "⚡  Apply MAC Change", command=self.apply_mac).pack(side="left")
        SecondaryButton(btn_row, "🔄  Refresh", command=self._refresh_mac_page).pack(side="left", padx=(10, 0))

        return frame

    def _refresh_mac_page(self):
        self._refresh_interfaces()
        names = list(self.interfaces.keys())
        self.mac_iface_cb.configure(values=names)
        if names and not self.mac_iface_var.get():
            self.mac_iface_var.set(names[0])
        self._update_mac_display()

    def _update_mac_display(self):
        name = self.mac_iface_var.get()
        info = self.interfaces.get(name, {})
        mac = info.get("mac") or "—"
        self.mac_current_lbl.configure(text=mac)

    def _toggle_mac_entry(self):
        mode = self.mac_mode.get()
        state = "normal" if mode == "Specific" else "disabled"
        mfr_state = "readonly" if mode == "Manufacturer" else "disabled"

        for e in self.mac_entries:
            e.configure(state=state)
            if state == "disabled":
                e.delete(0, "end")

        self.mfr_dropdown.configure(state=mfr_state)

        if mode == "Manufacturer":
            self._apply_manufacturer_preset()

    def _apply_manufacturer_preset(self):
        mfr = self.mfr_var.get()
        if mfr in MANUFACTURER_OUIS:
            oui = MANUFACTURER_OUIS[mfr][0]
            parts = oui.split(":")
            for i, part in enumerate(parts):
                if i < len(self.mac_entries):
                    self.mac_entries[i].delete(0, "end")
                    self.mac_entries[i].insert(0, part)
            for i in range(3, 6):
                self.mac_entries[i].delete(0, "end")
                self.mac_entries[i].configure(state="normal")

    def _mac_key_handler(self, event, idx):
        e = self.mac_entries[idx]
        val = e.get().replace(":", "").replace("-", "").upper()
        if len(val) > 2:
            val = val[:2]
            e.delete(0, "end")
            e.insert(0, val)
        if len(val) == 2 and idx < 5:
            self.mac_entries[idx + 1].focus()

    def apply_mac(self):
        iface = self.mac_iface_var.get()
        if not iface:
            return messagebox.showerror("Error", "Select an interface.")

        mode = self.mac_mode.get()
        if mode == "Specific":
            parts = [e.get().strip().upper() for e in self.mac_entries]
            if any(len(p) != 2 for p in parts):
                return messagebox.showerror("Error", "Each segment must be 2 hex chars.")
            mac_cmd = f"macchanger --mac={':'.join(parts)} {iface}"
        elif mode == "Manufacturer":
            parts = [e.get().strip().upper() for e in self.mac_entries]
            for i, p in enumerate(parts):
                if not p or len(p) != 2:
                    parts[i] = f"{int(time.time()) % 256:02X}"
            mac_cmd = f"macchanger --mac={':'.join(parts)} {iface}"
        else:
            mac_cmd = f"macchanger -r {iface}"

        for c in [f"ip link set {iface} down", mac_cmd, f"ip link set {iface} up"]:
            ok, out = self._run_cmd(c)
            if not ok and "cannot find device" in out.lower():
                return messagebox.showerror("Error", f"Interface {iface} not found.")

        ok, out = self._run_cmd(f"macchanger -s {iface}")
        self._refresh_interfaces()
        self._update_mac_display()
        messagebox.showinfo("Applied", out or "MAC changed.")

    def _build_firewall_page(self):
        frame = ctk.CTkFrame(self.page_container, fg_color="transparent")
        PageTitle(frame, "Firewall", "View active firewall rules and NAT configuration").pack(fill="x", pady=(0, 18))

        ipt = Card(frame)
        ipt.pack(fill="x", pady=(0, 14))
        ctk.CTkLabel(ipt, text="iptables Rules",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=TEXT).pack(anchor="w", padx=18, pady=(16, 8))

        self.iptables_lbl = ctk.CTkLabel(ipt, text="Loading...",
                                         font=ctk.CTkFont(size=11, family="monospace"),
                                         text_color=TEXT_DIM, justify="left", anchor="w")
        self.iptables_lbl.pack(fill="x", padx=18, pady=(0, 16))

        nft = Card(frame)
        nft.pack(fill="x", pady=(0, 14))
        ctk.CTkLabel(nft, text="nftables Rules",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=TEXT).pack(anchor="w", padx=18, pady=(16, 8))

        self.nftables_lbl = ctk.CTkLabel(nft, text="Loading...",
                                         font=ctk.CTkFont(size=11, family="monospace"),
                                         text_color=TEXT_DIM, justify="left", anchor="w")
        self.nftables_lbl.pack(fill="x", padx=18, pady=(0, 16))

        btn_row = ctk.CTkFrame(frame, fg_color="transparent")
        btn_row.pack(fill="x")
        SecondaryButton(btn_row, "🔄  Refresh", command=self._refresh_firewall_page).pack(side="right")

        return frame

    def _refresh_firewall_page(self):
        ok, out = self._run_cmd("iptables -L -n -v --line-numbers 2>&1 | head-60")
        self.iptables_lbl.configure(text=(out or "No rules")[:2000])

        ok, out = self._run_cmd("nft list ruleset 2>&1 | head-80")
        self.nftables_lbl.configure(text=(out or "No rules")[:2500])

    def _build_system_page(self):
        frame = ctk.CTkFrame(self.page_container, fg_color="transparent")
        PageTitle(frame, "System", "Device info and power controls").pack(fill="x", pady=(0, 18))

        info = Card(frame)
        info.pack(fill="x", pady=(0, 14))
        ctk.CTkLabel(info, text="Device Information",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=TEXT).pack(anchor="w", padx=18, pady=(16, 10))

        self.sys_info_lbl = ctk.CTkLabel(info, text="Loading...",
                                         font=ctk.CTkFont(size=12),
                                         text_color=TEXT_DIM, justify="left", anchor="w")
        self.sys_info_lbl.pack(fill="x", padx=18, pady=(0, 16))

        ctrl = Card(frame)
        ctrl.pack(fill="x")
        ctk.CTkLabel(ctrl, text="Power",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=TEXT).pack(anchor="w", padx=18, pady=(16, 10))

        btn_row = ctk.CTkFrame(ctrl, fg_color="transparent")
        btn_row.pack(fill="x", padx=18, pady=(0, 16))
        PrimaryButton(btn_row, "🔄  Reboot", command=self._reboot).pack(side="left")
        PrimaryButton(btn_row, "⏻  Shutdown", command=self._shutdown, danger=True).pack(side="left", padx=(10, 0))

        return frame

    def _refresh_system_info(self):
        ok, h = self._run_cmd("hostname")
        ok2, k = self._run_cmd("uname -r")
        ok3, up = self._run_cmd("uptime -p")
        ok4, temp = self._run_cmd("vcgencmd measure_temp 2>/dev/null || echo 'N/A'")

        info = (f"Hostname:  {h or '—'}\n"
                f"Kernel:    {k or '—'}\n"
                f"Uptime:    {up or '—'}\n"
                f"CPU Temp:  {temp or '—'}")
        self.sys_info_lbl.configure(text=info)

    def _reboot(self):
        if messagebox.askyesno("Confirm", "Reboot the device now?"):
            self._run_cmd("reboot")

    def _shutdown(self):
        if messagebox.askyesno("Confirm", "Shut down the device now?"):
            self._run_cmd("shutdown now")

    def _start_status_loop(self):
        self._detect_current_wifi()
        if self.current_wifi != "Not Connected":
            self.sidebar_status.configure(text=f"● {self.current_wifi}", text_color=SUCCESS)
        else:
            self.sidebar_status.configure(text="● No Wi-Fi", text_color=TEXT_DIM)

        self.topbar_info.configure(text=f"{datetime.now().strftime('%H:%M')}  •  {self.selected_wan or 'No WAN'}")

        if self.auto_mac_wan_var.get() and self.selected_wan:
            internet_ok, _ = self._run_cmd("ping -c 1 -W 2 1.1.1.1")
            if not internet_ok:
                if time.time() - self.last_auto_mac_time > self.auto_mac_cooldown:
                    self.auto_mac_status.configure(text="Auto-MAC: ⚠️ Internet down! Changing...", text_color=WARNING)
                    self.last_auto_mac_time = time.time()
                    self._run_cmd(f"ip link set {self.selected_wan} down")
                    self._run_cmd(f"macchanger -r {self.selected_wan}")
                    self._run_cmd(f"ip link set {self.selected_wan} up")
                    self._refresh_interfaces()
                    self._update_mac_display()
                else:
                    remaining = int(self.auto_mac_cooldown - (time.time() - self.last_auto_mac_time))
                    self.auto_mac_status.configure(text=f"Auto-MAC: ⏳ Cooldown ({remaining//60}m)", text_color=TEXT_DIM)
            else:
                self.auto_mac_status.configure(text="Auto-MAC: ✓ Monitoring", text_color=SUCCESS)
        else:
            self.auto_mac_status.configure(text="Auto-MAC: Disabled", text_color=TEXT_DIM)

        if self.current_page == "dashboard":
            self._refresh_dashboard()
        elif self.current_page == "system":
            self._refresh_system_info()

        self.after(60000, self._start_status_loop)

if __name__ == "__main__":
    app = WaveInterface()
    app.mainloop()
