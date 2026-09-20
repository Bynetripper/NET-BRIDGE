import os
import subprocess
import time
import re
from datetime import datetime
import customtkinter as ctk
from tkinter import messagebox, ttk

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
ACCENT      = "#3b82f6"   # Primary blue
ACCENT_HOV  = "#2563eb"
TEXT        = "#e4e6eb"
TEXT_DIM    = "#8b8d94"
TEXT_MUTED  = "#5a5d66"
SUCCESS     = "#22c55e"
WARNING     = "#f59e0b"
DANGER      = "#ef4444"
INFO        = "#06b6d4"


# =========================================================
# MODERN REUSABLE WIDGETS
# =========================================================
class Card(ctk.CTkFrame):
    """A clean card container"""
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
    """Page header with title + subtitle"""
    def __init__(self, master, title, subtitle=""):
        super().__init__(master, fg_color="transparent")
        ctk.CTkLabel(self, text=title, font=ctk.CTkFont(size=22, weight="bold"),
                     text_color=TEXT, anchor="w").pack(fill="x")
        if subtitle:
            ctk.CTkLabel(self, text=subtitle, font=ctk.CTkFont(size=12),
                         text_color=TEXT_DIM, anchor="w").pack(fill="x", pady=(2, 0))


class StatBox(ctk.CTkFrame):
    """Dashboard stat card"""
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
                         fg_color="transparent", hover_color=BG_CARD,
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
            self.configure(fg_color="transparent", hover_color=BG_CARD, text_color=TEXT_DIM)


# =========================================================
# MAIN APPLICATION
# =========================================================
class RouterPortal(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("NetBridge Router Portal")
        self.geometry("1180x780")
        self.minsize(1000, 700)
        self.configure(fg_color=BG_MAIN)

        # ---- STATE ----
        self.interfaces = {}          # {name: {type, status, ip, mac, ...}}
        self.selected_wan = None      # incoming internet interface
        self.selected_lans = {}       # {name: {"vpn_bypass": bool, "dhcp": bool, ...}}
        self.current_wifi = "Not Connected"
        self.wifi_networks = []
        self.last_auto_mac_time = 0
        self.auto_mac_cooldown = 3600
        self.current_page = "dashboard"
        self.page_frames = {}

        # ---- LAYOUT: SIDEBAR + CONTENT ----
        self._build_sidebar()
        self._build_content_area()

        # ---- INIT ----
        self._refresh_interfaces()
        self._detect_current_wifi()
        self.show_page("dashboard")
        self._start_status_loop()

    # =========================================================
    # SIDEBAR
    # =========================================================
    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, fg_color=BG_SIDEBAR, corner_radius=0,
                                    border_width=0, width=240)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Logo / brand
        brand = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        brand.pack(fill="x", padx=20, pady=(22, 20))
        ctk.CTkLabel(brand, text="⚡ NetBridge",
                     font=ctk.CTkFont(size=20, weight="bold"),
                     text_color=TEXT).pack(anchor="w")
        ctk.CTkLabel(brand, text="Router Portal",
                     font=ctk.CTkFont(size=11), text_color=TEXT_DIM).pack(anchor="w")

        ctk.CTkFrame(self.sidebar, fg_color=BORDER, height=1).pack(fill="x", padx=16, pady=(0, 12))

        # Nav items
        nav_items = [
            ("dashboard", "Dashboard", "📊"),
            ("network",   "Network",    "🌐"),
            ("wifi",      "Wi-Fi",      "📶"),
            ("sharing",   "Sharing",    "🔗"),
            ("vpn",       "VPN Bypass", "🛡️"),
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

        # Footer
        ctk.CTkFrame(self.sidebar, fg_color=BORDER, height=1).pack(fill="x", padx=16, pady=(8, 8))
        self.sidebar_status = ctk.CTkLabel(self.sidebar, text="● System Ready",
                                           font=ctk.CTkFont(size=11),
                                           text_color=SUCCESS)
        self.sidebar_status.pack(padx=20, pady=(0, 18), anchor="w")

    # =========================================================
    # CONTENT AREA
    # =========================================================
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

        # Scrollable page container
        self.page_container = ctk.CTkScrollableFrame(self.content, fg_color=BG_MAIN,
                                                     corner_radius=0, border_width=0,
                                                     scrollbar_button_color=BG_CARD,
                                                     scrollbar_button_hover_color=BORDER)
        self.page_container.pack(fill="both", expand=True)

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
        # Hide current
        for f in self.page_frames.values():
            f.pack_forget()
        # Show new
        self.page_frames[key].pack(fill="both", expand=True, padx=28, pady=22)
        # Update nav
        for k, btn in self.nav_buttons.items():
            btn.set_active(k == key)
        # Update topbar
        titles = {
            "dashboard": "Dashboard", "network": "Network Interfaces",
            "wifi": "Wi-Fi", "sharing": "Internet Sharing",
            "vpn": "VPN Bypass", "mac": "MAC Address",
            "firewall": "Firewall", "system": "System"
        }
        self.topbar_title.configure(text=titles.get(key, ""))
        self.current_page = key
        # Refresh page data
        if key == "dashboard": self._refresh_dashboard()
        if key == "network":   self._refresh_network_page()
        if key == "vpn":       self._refresh_vpn_page()
        if key == "firewall":  self._refresh_firewall_page()

    # =========================================================
    # INTERFACE DETECTION
    # =========================================================
    def _run_cmd(self, cmd):
        try:
            r = subprocess.run(cmd, shell=True, check=True,
                               capture_output=True, text=True)
            return True, r.stdout.strip()
        except subprocess.CalledProcessError as e:
            return False, (e.stderr or e.stdout).strip()

    def _refresh_interfaces(self):
        """Populate self.interfaces with all network interfaces"""
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
            # Get IP
            ok2, ip = self._run_cmd(f"ip -4 addr show {name} | awk '/inet/ {{print $2}}' | head -1")
            ip = ip if ok2 else ""
            # Get MAC
            ok3, mac = self._run_cmd(f"ip link show {name} | awk '/link\\/ether/ {{print $2}}' | head -1")
            mac = mac if ok3 else ""
            # Type guess
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

    # =========================================================
    # DASHBOARD PAGE
    # =========================================================
    def _build_dashboard(self):
        frame = ctk.CTkFrame(self.page_container, fg_color="transparent")
        PageTitle(frame, "Dashboard", "System overview and quick status").pack(fill="x", pady=(0, 18))

        # Stats row
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

        # Interface list card
        Card(frame).pack(fill="x", pady=(18, 0))  # spacer
        if_card = Card(frame)
        if_card.pack(fill="x", pady=(6, 0))
        ctk.CTkLabel(if_card, text="Detected Interfaces",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=TEXT).pack(anchor="w", padx=18, pady=(16, 10))

        self.dash_if_table = ctk.CTkFrame(if_card, fg_color="transparent")
        self.dash_if_table.pack(fill="x", padx=18, pady=(0, 16))

        # Refresh button
        btn_row = ctk.CTkFrame(if_card, fg_color="transparent")
        btn_row.pack(fill="x", padx=18, pady=(0, 16))
        PrimaryButton(btn_row, "🔄  Refresh", command=self._refresh_all).pack(side="right")

        return frame

    def _refresh_dashboard(self):
        self._refresh_interfaces()
        self._detect_current_wifi()

        # WAN
        if self.selected_wan and self.selected_wan in self.interfaces:
            self.stat_wan.set(self.selected_wan, ACCENT)
        else:
            self.stat_wan.set("Not set", TEXT_DIM)

        # LANs
        n_lans = len(self.selected_lans)
        n_bypass = sum(1 for v in self.selected_lans.values() if v.get("vpn_bypass"))
        self.stat_lans.set(f"{n_lans} selected", INFO)

        # VPN
        if n_bypass > 0:
            self.stat_vpn.set(f"{n_bypass} active", WARNING)
        else:
            self.stat_vpn.set("Inactive", TEXT_DIM)

        # Wi-Fi
        color = SUCCESS if self.current_wifi != "Not Connected" else TEXT_DIM
        self.stat_wifi.set(self.current_wifi, color)

        # Table
        for w in self.dash_if_table.winfo_children():
            w.destroy()
        # Header
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
            role = "—"
            role_color = TEXT_DIM
            if name == self.selected_wan:
                role, role_color = "WAN", ACCENT
            elif name in self.selected_lans:
                role, role_color = "LAN", INFO
                if self.selected_lans[name].get("vpn_bypass"):
                    role += " +BYPASS"
                    role_color = WARNING

            status_color = SUCCESS if info["status"] == "UP" else TEXT_DIM
            values = [
                (info["name"], TEXT),
                (info["type"], TEXT_DIM),
                (f"● {info['status']}", status_color),
                (info["ip"] or "—", TEXT_DIM),
                (role, role_color),
            ]
            for txt, color in values:
                ctk.CTkLabel(row, text=txt, font=ctk.CTkFont(size=12),
                             text_color=color, anchor="w").pack(
                    side="left", expand=True, fill="x", padx=8)

    def _refresh_all(self):
        self._refresh_interfaces()
        self._detect_current_wifi()
        self._refresh_dashboard()
        messagebox.showinfo("Refreshed", "Interface list updated.")

    # =========================================================
    # NETWORK PAGE (WAN / LAN selection)
    # =========================================================
    def _build_network_page(self):
        frame = ctk.CTkFrame(self.page_container, fg_color="transparent")
        PageTitle(frame, "Network Interfaces",
                  "Choose which interface receives internet (WAN) and which distribute it (LAN)").pack(fill="x", pady=(0, 18))

        # WAN card
        wan_card = Card(frame)
        wan_card.pack(fill="x", pady=(0, 14))
        ctk.CTkLabel(wan_card, text="🌐  Incoming Internet (WAN)",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=TEXT).pack(anchor="w", padx=18, pady=(16, 4))
        ctk.CTkLabel(wan_card, text="The interface currently providing your internet connection.",
                     font=ctk.CTkFont(size=11), text_color=TEXT_DIM).pack(anchor="w", padx=18, pady=(0, 12))

        self.wan_selector = ctk.CTkFrame(wan_card, fg_color="transparent")
        self.wan_selector.pack(fill="x", padx=18, pady=(0, 16))

        # LAN card
        lan_card = Card(frame)
        lan_card.pack(fill="x", pady=(0, 14))
        ctk.CTkLabel(lan_card, text="🔌  Outgoing Interfaces (LAN)",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=TEXT).pack(anchor="w", padx=18, pady=(16, 4))
        ctk.CTkLabel(lan_card, text="Select which interfaces will distribute internet to connected devices.",
                     font=ctk.CTkFont(size=11), text_color=TEXT_DIM).pack(anchor="w", padx=18, pady=(0, 12))

        self.lan_selector = ctk.CTkFrame(lan_card, fg_color="transparent")
        self.lan_selector.pack(fill="x", padx=18, pady=(0, 16))

        # Actions
        act = ctk.CTkFrame(frame, fg_color="transparent")
        act.pack(fill="x")
        PrimaryButton(act, "💾  Save Configuration", command=self._save_network_config).pack(side="right")
        SecondaryButton(act, "🔄  Rescan Interfaces", command=self._refresh_network_page).pack(side="right", padx=(0, 10))

        return frame

    def _refresh_network_page(self):
        self._refresh_interfaces()
        self._detect_current_wifi()

        # WAN selector
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

        # LAN selector
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

    # =========================================================
    # WI-FI PAGE
    # =========================================================
    def _build_wifi_page(self):
        frame = ctk.CTkFrame(self.page_container, fg_color="transparent")
        PageTitle(frame, "Wi-Fi", "Connect to an upstream wireless network").pack(fill="x", pady=(0, 18))

        # Current connection
        cur = Card(frame)
        cur.pack(fill="x", pady=(0, 14))
        ctk.CTkLabel(cur, text="Current Connection",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=TEXT).pack(anchor="w", padx=18, pady=(16, 8))
        self.wifi_cur_lbl = ctk.CTkLabel(cur, text=f"● {self.current_wifi}",
                                         font=ctk.CTkFont(size=13, weight="bold"),
                                         text_color=SUCCESS if self.current_wifi != "Not Connected" else TEXT_DIM)
        self.wifi_cur_lbl.pack(anchor="w", padx=18, pady=(0, 16))

        # Scanner
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

    # =========================================================
    # INTERNET SHARING PAGE
    # =========================================================
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

        # Status
        self.sharing_status = Card(frame)
        self.sharing_status.pack(fill="x", pady=(0, 14))
        self.sharing_status_lbl = ctk.CTkLabel(self.sharing_status, text="● Sharing OFFLINE",
                                               font=ctk.CTkFont(size=13, weight="bold"),
                                               text_color=DANGER)
        self.sharing_status_lbl.pack(anchor="w", padx=18, pady=16)

        # Controls
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

        subnet_idx = 77
        for lan in self.selected_lans:
            subnet = f"192.168.{subnet_idx}"
            # Configure interface
            cmds = [
                f"nmcli device set {lan} managed no || true",
                f"ip link set {lan} down",
                f"ip addr flush dev {lan}",
                f"ip link set {lan} up",
                f"ip addr add {subnet}.1/24 dev {lan}",
            ]
            for c in cmds:
                self._run_cmd(c)

            # Dnsmasq per interface
            conf_path = f"/etc/dnsmasq.d/bridge-{lan}.conf"
            try:
                os.makedirs("/etc/dnsmasq.d", exist_ok=True)
                with open(conf_path, "w") as f:
                    f.write(f"interface={lan}\n"
                            f"dhcp-range={subnet}.10,{subnet}.100,255.255.255.0,24h\n"
                            f"bind-interfaces\n")
            except Exception as e:
                return messagebox.showerror("Error", f"Config write failed: {e}")

            # NAT + FORWARD rules
            nat_cmds = [
                f"iptables -t nat -D POSTROUTING -s {subnet}.0/24 -j MASQUERADE || true",
                f"iptables -D FORWARD -s {subnet}.0/24 -j ACCEPT || true",
                f"iptables -D FORWARD -d {subnet}.0/24 -j ACCEPT || true",
                f"iptables -t nat -I POSTROUTING 1 -s {subnet}.0/24 -j MASQUERADE",
                f"iptables -I FORWARD 1 -s {subnet}.0/24 -j ACCEPT",
                f"iptables -I FORWARD 1 -d {subnet}.0/24 -j ACCEPT",
            ]
            for c in nat_cmds:
                self._run_cmd(c)
            subnet_idx += 1

        self._run_cmd("systemctl restart dnsmasq")
        self.sharing_status_lbl.configure(text="● Sharing ONLINE", text_color=SUCCESS)
        lans_info = "\n".join([f"• {lan} → 192.168.{77+i}.0/24" for i, lan in enumerate(self.selected_lans)])
        messagebox.showinfo("Sharing Started",
                            f"WAN: {self.selected_wan}\nLANs:\n{lans_info}")

    def stop_sharing(self):
        for i, lan in enumerate(self.selected_lans):
            subnet = f"192.168.{77+i}"
            cmds = [
                f"iptables -t nat -D POSTROUTING -s {subnet}.0/24 -j MASQUERADE || true",
                f"iptables -D FORWARD -s {subnet}.0/24 -j ACCEPT || true",
                f"iptables -D FORWARD -d {subnet}.0/24 -j ACCEPT || true",
                f"ip link set {lan} down",
                f"ip addr flush dev {lan}",
                f"nmcli device set {lan} managed yes || true",
                f"rm -f /etc/dnsmasq.d/bridge-{lan}.conf",
            ]
            for c in cmds:
                self._run_cmd(c)
        self._run_cmd("systemctl restart dnsmasq")
        self.sharing_status_lbl.configure(text="● Sharing OFFLINE", text_color=DANGER)
        messagebox.showinfo("Stopped", "Internet sharing stopped.")

    # =========================================================
    # VPN BYPASS PAGE
    # =========================================================
    def _build_vpn_page(self):
        frame = ctk.CTkFrame(self.page_container, fg_color="transparent")
        PageTitle(frame, "VPN Bypass",
                  "Punch holes in Mullvad's firewall so specific LAN interfaces bypass the VPN tunnel").pack(fill="x", pady=(0, 18))

        self.vpn_list_card = Card(frame)
        self.vpn_list_card.pack(fill="x", pady=(0, 14))
        ctk.CTkLabel(self.vpn_list_card, text="Per-Interface Bypass",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=TEXT).pack(anchor="w", padx=18, pady=(16, 4))
        ctk.CTkLabel(self.vpn_list_card,
                     text="Enable to let traffic on that interface go direct to internet, not through Mullvad.",
                     font=ctk.CTkFont(size=11), text_color=TEXT_DIM).pack(anchor="w", padx=18, pady=(0, 12))

        self.vpn_list = ctk.CTkFrame(self.vpn_list_card, fg_color="transparent")
        self.vpn_list.pack(fill="x", padx=18, pady=(0, 16))

        # Mullvad status
        mullvad = Card(frame)
        mullvad.pack(fill="x")
        ctk.CTkLabel(mullvad, text="Mullvad Status",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=TEXT).pack(anchor="w", padx=18, pady=(16, 8))
        self.mullvad_status_lbl = ctk.CTkLabel(mullvad, text="Checking...",
                                               font=ctk.CTkFont(size=12),
                                               text_color=TEXT_DIM)
        self.mullvad_status_lbl.pack(anchor="w", padx=18, pady=(0, 16))

        return frame

    def _refresh_vpn_page(self):
        # Mullvad status
        ok, _ = self._run_cmd("pgrep -f mullvad")
        if ok:
            self.mullvad_status_lbl.configure(text="● Mullvad is RUNNING", text_color=WARNING)
        else:
            self.mullvad_status_lbl.configure(text="● Mullvad is NOT running", text_color=TEXT_DIM)

        # LAN list
        for w in self.vpn_list.winfo_children():
            w.destroy()
        self.vpn_toggles = {}
        if not self.selected_lans:
            ctk.CTkLabel(self.vpn_list, text="No LAN interfaces selected. Go to Network tab first.",
                         font=ctk.CTkFont(size=12), text_color=TEXT_DIM).pack(anchor="w", pady=12)
            return

        for name in self.selected_lans:
            info = self.interfaces.get(name, {})
            row = ctk.CTkFrame(self.vpn_list, fg_color=BG_INPUT, corner_radius=8)
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

        # Apply button
        btn_row = ctk.CTkFrame(self.vpn_list_card, fg_color="transparent")
        btn_row.pack(fill="x", padx=18, pady=(0, 16))
        PrimaryButton(btn_row, "💾  Apply Bypass Rules", command=self._apply_vpn_bypass).pack(side="right")

    def _apply_vpn_bypass(self):
        # Update state
        for name, var in self.vpn_toggles.items():
            self.selected_lans[name]["vpn_bypass"] = var.get()

        # Detect firewall backend
        has_nft, _ = self._run_cmd("nft list tables | grep -q mullvad && echo yes")

        for name, data in self.selected_lans.items():
            if data.get("vpn_bypass"):
                # Add bypass rules
                if has_nft:
                    self._run_cmd(f'nft insert rule inet mullvad output oifname "{name}" accept 2>/dev/null || true')
                    self._run_cmd(f'nft insert rule inet mullvad forward oifname "{name}" accept 2>/dev/null || true')
                    self._run_cmd(f'nft insert rule inet mullvad forward iifname "{name}" accept 2>/dev/null || true')
                self._run_cmd(f"iptables -I OUTPUT 1 -o {name} -j ACCEPT 2>/dev/null || true")
                self._run_cmd(f"iptables -I FORWARD 1 -o {name} -j ACCEPT 2>/dev/null || true")
                self._run_cmd(f"iptables -I FORWARD 1 -i {name} -j ACCEPT 2>/dev/null || true")
            else:
                # Remove bypass rules
                if has_nft:
                    self._run_cmd(f'nft delete rule inet mullvad output oifname "{name}" accept 2>/dev/null || true')
                self._run_cmd(f"iptables -D OUTPUT -o {name} -j ACCEPT 2>/dev/null || true")
                self._run_cmd(f"iptables -D FORWARD -o {name} -j ACCEPT 2>/dev/null || true")
                self._run_cmd(f"iptables -D FORWARD -i {name} -j ACCEPT 2>/dev/null || true")

        n_on = sum(1 for d in self.selected_lans.values() if d.get("vpn_bypass"))
        messagebox.showinfo("Applied", f"VPN bypass rules applied.\n{n_on} interface(s) bypassing Mullvad.")

    # =========================================================
    # MAC ADDRESS PAGE
    # =========================================================
    def _build_mac_page(self):
        frame = ctk.CTkFrame(self.page_container, fg_color="transparent")
        PageTitle(frame, "MAC Address", "Change or randomize the MAC address of an interface").pack(fill="x", pady=(0, 18))

        # Interface picker
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
        self.mac_iface_cb.pack(fill="x", padx=18, pady=(0, 16))

        # Current MAC
        cur = Card(frame)
        cur.pack(fill="x", pady=(0, 14))
        ctk.CTkLabel(cur, text="Current MAC",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=TEXT).pack(anchor="w", padx=18, pady=(16, 8))
        self.mac_current_lbl = ctk.CTkLabel(cur, text="—",
                                            font=ctk.CTkFont(size=16, family="monospace", weight="bold"),
                                            text_color=ACCENT)
        self.mac_current_lbl.pack(anchor="w", padx=18, pady=(0, 16))

        # Mode
        mode_card = Card(frame)
        mode_card.pack(fill="x", pady=(0, 14))
        ctk.CTkLabel(mode_card, text="Mode",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=TEXT).pack(anchor="w", padx=18, pady=(16, 10))
        self.mac_mode = ctk.StringVar(value="Random")
        mode_row = ctk.CTkFrame(mode_card, fg_color="transparent")
        mode_row.pack(fill="x", padx=18, pady=(0, 10))
        ctk.CTkRadioButton(mode_row, text="🎲  Random", variable=self.mac_mode,
                           value="Random", fg_color=ACCENT, hover_color=ACCENT_HOV,
                           border_color=BORDER, text_color=TEXT,
                           command=self._toggle_mac_entry).pack(side="left", padx=(0, 20))
        ctk.CTkRadioButton(mode_row, text="✏️  Specific", variable=self.mac_mode,
                           value="Specific", fg_color=ACCENT, hover_color=ACCENT_HOV,
                           border_color=BORDER, text_color=TEXT,
                           command=self._toggle_mac_entry).pack(side="left")

        # 6 MAC boxes
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

        # Buttons
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
        state = "normal" if self.mac_mode.get() == "Specific" else "disabled"
        for e in self.mac_entries:
            e.configure(state=state)
            if state == "disabled":
                e.delete(0, "end")

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

    # =========================================================
    # FIREWALL PAGE
    # =========================================================
    def _build_firewall_page(self):
        frame = ctk.CTkFrame(self.page_container, fg_color="transparent")
        PageTitle(frame, "Firewall", "View active firewall rules and NAT configuration").pack(fill="x", pady=(0, 18))

        # iptables
        ipt = Card(frame)
        ipt.pack(fill="x", pady=(0, 14))
        ctk.CTkLabel(ipt, text="iptables Rules",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=TEXT).pack(anchor="w", padx=18, pady=(16, 8))
        self.iptables_lbl = ctk.CTkLabel(ipt, text="Loading...",
                                         font=ctk.CTkFont(size=11, family="monospace"),
                                         text_color=TEXT_DIM, justify="left", anchor="w")
        self.iptables_lbl.pack(fill="x", padx=18, pady=(0, 16))

        # nftables
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
        ok, out = self._run_cmd("iptables -L -n -v --line-numbers 2>&1 | head -60")
        self.iptables_lbl.configure(text=(out or "No rules")[:2000])
        ok, out = self._run_cmd("nft list ruleset 2>&1 | head -80")
        self.nftables_lbl.configure(text=(out or "No rules")[:2500])

    # =========================================================
    # SYSTEM PAGE
    # =========================================================
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

    # =========================================================
    # STATUS LOOP
    # =========================================================
    def _start_status_loop(self):
        self._detect_current_wifi()
        if self.current_wifi != "Not Connected":
            self.sidebar_status.configure(text=f"● {self.current_wifi}", text_color=SUCCESS)
        else:
            self.sidebar_status.configure(text="● No Wi-Fi", text_color=TEXT_DIM)
        self.topbar_info.configure(text=f"{datetime.now().strftime('%H:%M')}  •  {self.selected_wan or 'No WAN'}")
        # Refresh current page if needed
        if self.current_page == "dashboard":
            self._refresh_dashboard()
        elif self.current_page == "system":
            self._refresh_system_info()
        self.after(5000, self._start_status_loop)


if __name__ == "__main__":
    app = RouterPortal()
    app.mainloop()
