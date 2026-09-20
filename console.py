import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import subprocess
import os
import sys
import json

# ==========================================
# CONFIGURATION & DOMAIN LISTS (EXPANDED)
# ==========================================

CATEGORY_DOMAINS = {
    "Major Ad & Tracking Networks": [
        # Google/Alphabet
        "doubleclick.net", "google-analytics.com", "adservice.google.com", "googlesyndication.com",
        "googletagmanager.com", "googleadservices.com", "2mdn.net", "invitemedia.com",
        "googleoptimize.com", "fcmatch.google.com", "pagead2.googlesyndication.com",
        # Meta/Facebook
        "facebook.com", "facebook.net", "fbcdn.net", "connect.facebook.net", "graph.facebook.com",
        "staticxx.facebook.com", "instagram.com", "atdmt.com", "fb.com", "messenger.com",
        "accountkit.com", "fbsbx.com", "tfbnw.net",
        # Microsoft
        "telemetry.microsoft.com", "vortex.data.microsoft.com", "settings-win.data.microsoft.com",
        "watson.telemetry.microsoft.com", "bing.com", "msn.com", "microsoftonline.com",
        "office.net", "skype.com", "live.com", "onestore.ms",
        # Amazon
        "amazon-adsystem.com", "fls-na.amazon.com", "unagi.amazon.com", "assoc-amazon.com",
        "aax.amazon.com", "aaxads.com", "device-metrics-us.amazon.com",
        # General AdTech & Analytics
        "scorecardresearch.com", "quantserve.com", "outbrain.com", "taboola.com", "criteo.com",
        "appnexus.com", "rubiconproject.com", "openx.net", "pubmatic.com", "smartadserver.com",
        "hotjar.com", "mouseflow.com", "fullstory.com", "clarity.ms", "mixpanel.com",
        "segment.io", "amplitude.com", "newrelic.com", "datadome.co", "cloudflareinsights.com",
        "bugsnag.com", "sentry.io", "rollbar.com", "chartbeat.com", "parsely.com",
        "moatads.com", "adnxs.com", "casalemedia.com", "indexexchange.com", "spotxchange.com",
        "teads.tv", "yieldmo.com", "sharethrough.com", "bidswitch.net", "adform.net"
    ],
    "Social Media Widgets & Trackers": [
        "twitter.com", "twimg.com", "t.co", "x.com",
        "linkedin.com", "licdn.com", "slideshare.net",
        "pinterest.com", "pinimg.com",
        "tiktok.com", "byteoversea.com", "musical.ly", "tiktokcdn.com",
        "snapchat.com", "sc-cdn.net", "snapkit.com",
        "reddit.com", "redd.it", "redditstatic.com",
        "tumblr.com", "wp.com", "wordpress.com",
        "discord.com", "discord.gg", "discordapp.com",
        "telegram.org", "t.me",
        "whatsapp.com", "whatsapp.net"
    ],
    "Malware, Phishing & Exploits": [
        "malware-traffic-analysis.net", "badssl.com", "testsafebrowsing.appspot.com",
        "exploit-db.com", "phishtank.com", "urlhaus.abuse.ch", "virustotal.com",
        "hybrid-analysis.com", "any.run", "joesandbox.com", "cuckoo.cert.ee"
    ],
    "URL Shorteners (High Risk)": [
        "bit.ly", "tinyurl.com", "t.co", "ow.ly", "shorturl.at", "is.gd", "bit.do",
        "cutt.ly", "rb.gy", "bl.ink", "rebrandly.com", "soo.gd", "cli.gs",
        "adf.ly", "bc.vc", "j.mp", "goo.gl", "tr.im", "lnkd.in"
    ],
    "Adult Content & Gambling": [
        "pornhub.com", "xvideos.com", "xnxx.com", "onlyfans.com", "xhamster.com",
        "brazzers.com", "chaturbate.com", "livejasmin.com", "redtube.com", "youporn.com",
        "bet365.com", "draftkings.com", "fanduel.com", "888casino.com", "pokerstars.com"
    ]
}

COMPANY_DOMAINS = {
    "Google (Ads, Search, YouTube)": [
        "google.com", "youtube.com", "googleapis.com", "gstatic.com", "googlevideo.com",
        "googleusercontent.com", "ggpht.com", "blogspot.com", "android.com",
        "google-analytics.com", "doubleclick.net", "adservice.google.com",
        "googlesyndication.com", "googletagmanager.com", "googleadservices.com",
        "2mdn.net", "invitemedia.com", "googleoptimize.com", "withgoogle.com",
        "googlemail.com", "gmail.com", "chromium.org", "web.dev", "firebase.google.com"
    ],
    "Microsoft (Windows, Office, Telemetry)": [
        "microsoft.com", "windows.com", "live.com", "bing.com", "msn.com", "office.com",
        "office365.com", "azure.com", "skype.com", "hotmail.com", "xbox.com",
        "telemetry.microsoft.com", "vortex.data.microsoft.com", "settings-win.data.microsoft.com",
        "watson.telemetry.microsoft.com", "microsoftonline.com", "office.net",
        "onestore.ms", "msedge.net", "windowsupdate.com", "github.com", "linkedin.com"
    ],
    "Apple (iCloud, Services, Tracking)": [
        "apple.com", "icloud.com", "mzstatic.com", "apple-dns.net", "itunes.com",
        "appstore.com", "me.com", "mac.com", "icloud-content.com", "apple.news",
        "beats1radio.com", "shazam.com", "darksky.net", "workflow.is"
    ],
    "Amazon (Shopping, AWS, Ads)": [
        "amazon.com", "amazonaws.com", "aiv-cdn.net", "amazon-adsystem.com",
        "media-amazon.com", "primevideo.com", "twitch.tv", "audible.com", "imdb.com",
        "assoc-amazon.com", "aax.amazon.com", "aaxads.com", "device-metrics-us.amazon.com",
        "wholefoodsmarket.com", "zappos.com", "ring.com", "blinkforhome.com"
    ],
    "Meta (Facebook, Instagram, WhatsApp)": [
        "facebook.com", "facebook.net", "fbcdn.net", "instagram.com", "whatsapp.com",
        "messenger.com", "oculus.com", "meta.com", "atdmt.com", "fb.com",
        "accountkit.com", "fbsbx.com", "tfbnw.net", "threads.net", "mapillary.com"
    ]
}

BLOCKLIST_FILE = "/etc/dnsmasq.d/portmaster_block.conf"
CONFIG_FILE = os.path.expanduser("~/.pi_netmaster_config.json")

# ==========================================
# BACKEND: NETWORK & FIREWALL MANAGEMENT
# ==========================================
class NetworkManager:
    def __init__(self):
        self.blocked_ips = set()
        self.engine_active = self._check_engine()

    def _run_cmd(self, cmd, shell=False):
        try:
            return subprocess.run(cmd, shell=shell, capture_output=True, text=True, check=False)
        except Exception:
            return None

    def _check_engine(self):
        res = self._run_cmd(["sysctl", "net.ipv4.ip_forward"])
        forwarding = res and "1" in res.stdout
        res2 = self._run_cmd(["lsmod"])
        module = res2 and "nf_conntrack" in res2.stdout
        return forwarding and module

    def fix_router_engine(self):
        self._run_cmd(["modprobe", "nf_conntrack"])
        self._run_cmd(["sysctl", "-w", "net.ipv4.ip_forward=1"])
        self._run_cmd("sh -c 'grep -qxF \"net.ipv4.ip_forward=1\" /etc/sysctl.conf || echo \"net.ipv4.ip_forward=1\" >> /etc/sysctl.conf'", shell=True)
        self._run_cmd("sh -c 'grep -qxF \"nf_conntrack\" /etc/modules || echo \"nf_conntrack\" >> /etc/modules'", shell=True)
        self.engine_active = self._check_engine()
        return self.engine_active

    def update_company_block(self, company, domain_states):
        domains_to_block = [domain for domain, is_blocked in domain_states.items() if is_blocked]
        os.makedirs("/etc/dnsmasq.d", exist_ok=True)
        existing_lines = []
        if os.path.exists(BLOCKLIST_FILE):
            with open(BLOCKLIST_FILE, "r") as f:
                existing_lines = f.readlines()

        new_lines = []
        skip = False
        for line in existing_lines:
            if f"# {company} Blocklist" in line:
                skip = True
                continue
            if skip and line.strip() == "":
                skip = False
                continue
            if not skip:
                new_lines.append(line)

        if domains_to_block:
            new_lines.append(f"\n# {company} Blocklist\n")
            for domain in domains_to_block:
                new_lines.append(f"address=/{domain}/0.0.0.0\n")

        with open(BLOCKLIST_FILE, "w") as f:
            f.writelines(new_lines)
        self._run_cmd(["systemctl", "restart", "dnsmasq"])

    def update_category_block(self, category, is_enabled):
        domains = CATEGORY_DOMAINS.get(category, [])
        os.makedirs("/etc/dnsmasq.d", exist_ok=True)
        existing_lines = []
        if os.path.exists(BLOCKLIST_FILE):
            with open(BLOCKLIST_FILE, "r") as f:
                existing_lines = f.readlines()

        new_lines = []
        skip = False
        for line in existing_lines:
            if f"# {category} Blocklist" in line:
                skip = True
                continue
            if skip and line.strip() == "":
                skip = False
                continue
            if not skip:
                new_lines.append(line)

        if is_enabled:
            new_lines.append(f"\n# {category} Blocklist\n")
            for domain in domains:
                new_lines.append(f"address=/{domain}/0.0.0.0\n")

        with open(BLOCKLIST_FILE, "w") as f:
            f.writelines(new_lines)
        self._run_cmd(["systemctl", "restart", "dnsmasq"])

    def clear_all_firewall_rules(self):
        self._run_cmd("iptables -t nat -F PI_NETMASTER || true", shell=True)
        self._run_cmd("iptables -t nat -X PI_NETMASTER || true", shell=True)
        self._run_cmd("iptables -t nat -D POSTROUTING -j PI_NETMASTER || true", shell=True)
        self._run_cmd("iptables -F PI_NETMASTER_FWD || true", shell=True)
        self._run_cmd("iptables -X PI_NETMASTER_FWD || true", shell=True)
        self._run_cmd("iptables -D FORWARD -j PI_NETMASTER_FWD || true", shell=True)
        self._run_cmd("iptables -F FORWARD", shell=True)
        self._run_cmd("iptables -F OUTPUT", shell=True)
        if os.path.exists(BLOCKLIST_FILE):
            os.remove(BLOCKLIST_FILE)
        self._run_cmd(["systemctl", "restart", "dnsmasq"])


# ==========================================
# STATE MANAGER
# ==========================================
class StateManager:
    def __init__(self):
        self.config = self._load_config()

    def _load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        return self._default_config()

    def _default_config(self):
        return {
            "bridge": {
                "upstream": "",
                "downstream": {},
                "mac_mode": "None",
                "specific_mac": "",
                "ap_ssid": "PiNetMaster_AP",
                "ap_password": "raspberry123",
                "ap_band": "2.4GHz",
                "ap_encryption": "WPA2",
                "vpn_interface": "None (Use Direct Upstream)",
                "bypass_interface": "None (All use VPN)"
            },
            "settings": {
                "companies": {},
                "domains": {},
                "categories": {}
            }
        }

    def save_config(self):
        try:
            os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
            with open(CONFIG_FILE, "w") as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save config: {e}")

    def get_bridge_state(self):
        return self.config.get("bridge", self._default_config()["bridge"])

    def save_bridge_state(self, state):
        self.config["bridge"] = state
        self.save_config()

    def get_settings_state(self):
        return self.config.get("settings", self._default_config()["settings"])

    def save_settings_state(self, state):
        self.config["settings"] = state
        self.save_config()


# ==========================================
# GUI APPLICATION
# ==========================================
class PiNetMasterApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        if os.geteuid() != 0:
            print("ERROR: This script must be run as root. Please use: sudo python3 pi_netmaster.py")
            sys.exit(1)

        self.title("Pi NetMaster - Router & Firewall")
        self.geometry("1100x850")
        self.minsize(900, 650)
        self.resizable(True, True)

        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")
        self.configure(fg_color="#121212")

        self.net_mgr = NetworkManager()
        if not self.net_mgr.engine_active:
            self.net_mgr.fix_router_engine()

        self.interfaces = self._get_interfaces()
        self.downstream_vars = {}
        self.state_manager = StateManager()

        self.current_view = None
        self.bridge_state_initialized = False
        self.settings_state_initialized = False

        self._build_ui()

    def _get_interfaces(self):
        res = subprocess.run(
            "ip -o link show | awk -F': ' '{print $2}' | tr -d '@' | grep -v '^lo$'",
            shell=True, capture_output=True, text=True
        )
        if res.returncode == 0:
            return sorted([iface.strip() for iface in res.stdout.split('\n') if iface.strip()])
        return ["eth0", "wlan0"]

    def _get_vpn_interfaces(self):
        res = subprocess.run(
            "ip -o link show | awk -F': ' '{print $2}' | tr -d '@' | grep -E '^(tun|wg|vpn)'",
            shell=True, capture_output=True, text=True
        )
        vpn_ifaces = [iface.strip() for iface in res.stdout.split('\n') if iface.strip()]
        return ["None (Use Direct Upstream)"] + vpn_ifaces

    def _build_ui(self):
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color="#1A1A1A")
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        ctk.CTkLabel(
            self.sidebar, text="Pi NetMaster",
            font=ctk.CTkFont(size=22, weight="bold"), text_color="#0078D4"
        ).pack(pady=30, padx=20)

        self.btn_bridge = ctk.CTkButton(
            self.sidebar, text="Network Bridge", command=self.show_bridge,
            fg_color="#252525", hover_color="#333333", anchor="w", height=40
        )
        self.btn_bridge.pack(pady=5, padx=20, fill="x")

        self.btn_settings = ctk.CTkButton(
            self.sidebar, text="Settings", command=self.show_settings,
            fg_color="#252525", hover_color="#333333", anchor="w", height=40
        )
        self.btn_settings.pack(pady=5, padx=20, fill="x")

        self.main_area = ctk.CTkFrame(self, fg_color="#121212", corner_radius=0)
        self.main_area.pack(side="right", fill="both", expand=True)

        self.show_bridge()

    def _clear_main_area(self):
        for widget in self.main_area.winfo_children():
            widget.destroy()

    def _set_active_btn(self, active_btn):
        for btn in [self.btn_bridge, self.btn_settings]:
            btn.configure(fg_color="#333333" if btn == active_btn else "#252525")

    # ==========================================
    # VIEW 1: NETWORK BRIDGE
    # ==========================================
    def show_bridge(self):
        if self.current_view == "settings" and self.settings_state_initialized:
            self._save_settings_state()

        self._clear_main_area()
        self._set_active_btn(self.btn_bridge)
        self.current_view = "bridge"

        scroll_frame = ctk.CTkScrollableFrame(self.main_area, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(
            scroll_frame, text="Network Bridge & Sharing",
            font=ctk.CTkFont(size=24, weight="bold"), anchor="w"
        ).pack(pady=20, padx=20, fill="x")

        # Engine Status
        status_frame = ctk.CTkFrame(scroll_frame, fg_color="#1E1E1E", corner_radius=8)
        status_frame.pack(pady=(0, 15), padx=20, fill="x")
        self.lbl_engine_status = ctk.CTkLabel(status_frame, text="", font=ctk.CTkFont(size=14, weight="bold"))
        self.lbl_engine_status.pack(side="left", padx=20, pady=10)
        self.btn_fix_engine = ctk.CTkButton(
            status_frame, text="Fix Router Engine", command=self._fix_engine_click,
            fg_color="#D32F2F", hover_color="#B71C1C"
        )
        self._update_engine_status_ui()

        saved_state = self.state_manager.get_bridge_state()

        # Upstream
        iface_frame = ctk.CTkFrame(scroll_frame, fg_color="#1E1E1E", corner_radius=10)
        iface_frame.pack(pady=10, padx=20, fill="x")
        ctk.CTkLabel(iface_frame, text="1. Upstream Interface (Internet Source)",
                      font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        default_upstream = self.interfaces[0] if self.interfaces else "eth0"
        saved_upstream = saved_state.get("upstream", default_upstream)
        if saved_upstream not in self.interfaces:
            saved_upstream = default_upstream
        self.upstream_var = ctk.StringVar(value=saved_upstream)
        ctk.CTkComboBox(iface_frame, values=self.interfaces, variable=self.upstream_var).pack(padx=20, pady=5, fill="x")

        # Downstream
        ds_frame = ctk.CTkFrame(scroll_frame, fg_color="#1E1E1E", corner_radius=10)
        ds_frame.pack(pady=10, padx=20, fill="x")
        ctk.CTkLabel(ds_frame, text="2. Downstream Interfaces (Client Output)",
                      font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        ctk.CTkLabel(ds_frame, text="Select one or more interfaces. Only ONE Wi-Fi interface can be selected.",
                      text_color="#888888", font=ctk.CTkFont(size=12)).pack(pady=(0, 10))
        ds_scroll = ctk.CTkScrollableFrame(ds_frame, fg_color="transparent", height=120)
        ds_scroll.pack(padx=20, pady=5, fill="x")
        self.downstream_vars = {}
        saved_downstream = saved_state.get("downstream", {})
        for iface in self.interfaces:
            var = ctk.BooleanVar(value=saved_downstream.get(iface, False))
            self.downstream_vars[iface] = var
            ctk.CTkCheckBox(
                ds_scroll, text=iface, variable=var,
                command=lambda i=iface, v=var: self._on_downstream_toggle(i, v),
                font=ctk.CTkFont(size=14)
            ).pack(anchor="w", pady=2)

        # MAC Config
        mac_frame = ctk.CTkFrame(scroll_frame, fg_color="#1E1E1E", corner_radius=10)
        mac_frame.pack(pady=10, padx=20, fill="x")
        ctk.CTkLabel(mac_frame, text="3. Downstream MAC Address Configuration",
                      font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        saved_mac_mode = saved_state.get("mac_mode", "None")
        self.mac_mode_var = ctk.StringVar(value=saved_mac_mode)
        ctk.CTkLabel(mac_frame, text="MAC Randomization Mode:", anchor="w").pack(padx=20, fill="x")
        ctk.CTkComboBox(
            mac_frame, values=["None", "Randomize", "Specific"],
            variable=self.mac_mode_var, command=self._on_mac_mode_change
        ).pack(padx=20, pady=5, fill="x")
        saved_specific_mac = saved_state.get("specific_mac", "")
        self.specific_mac_var = ctk.StringVar(value=saved_specific_mac)
        self.entry_specific_mac = ctk.CTkEntry(
            mac_frame, placeholder_text="XX:XX:XX:XX:XX:XX",
            textvariable=self.specific_mac_var, state="disabled"
        )

        self.downstream_config_frame = ctk.CTkFrame(scroll_frame, fg_color="#1E1E1E", corner_radius=10)

        # VPN
        vpn_frame = ctk.CTkFrame(scroll_frame, fg_color="#1E1E1E", corner_radius=10)
        vpn_frame.pack(pady=10, padx=20, fill="x")
        ctk.CTkLabel(vpn_frame, text="4. VPN Routing & Bypass Configuration",
                      font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        ctk.CTkLabel(vpn_frame, text="Force Downstream Traffic Through VPN:", anchor="w").pack(padx=20, fill="x")
        saved_vpn = saved_state.get("vpn_interface", "None (Use Direct Upstream)")
        self.vpn_var = ctk.StringVar(value=saved_vpn)
        ctk.CTkComboBox(vpn_frame, values=self._get_vpn_interfaces(), variable=self.vpn_var).pack(padx=20, pady=5, fill="x")
        ctk.CTkLabel(vpn_frame, text="Bypass VPN for Specific Interface (e.g., Work PC):",
                      anchor="w").pack(padx=20, pady=(15, 0), fill="x")
        ctk.CTkLabel(vpn_frame, text="Traffic from this downstream interface will ignore the VPN and use the direct upstream.",
                      text_color="#888888", font=ctk.CTkFont(size=12)).pack(padx=20, fill="x")
        saved_bypass = saved_state.get("bypass_interface", "None (All use VPN)")
        self.bypass_var = ctk.StringVar(value=saved_bypass)
        ctk.CTkComboBox(vpn_frame, values=["None (All use VPN)"] + self.interfaces, variable=self.bypass_var).pack(padx=20, pady=5, fill="x")

        # Buttons
        btn_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        btn_frame.pack(pady=20)
        self.btn_share_on = ctk.CTkButton(btn_frame, text="Turn ON Sharing", command=self.toggle_bridge_on,
                                           fg_color="#28A745", hover_color="#218838", width=150)
        self.btn_share_on.pack(side="left", padx=15)
        self.btn_share_off = ctk.CTkButton(btn_frame, text="Turn OFF Sharing", command=self.toggle_bridge_off,
                                            fg_color="#DC3545", hover_color="#C82333", width=150)
        self.btn_share_off.pack(side="right", padx=15)

        self.bridge_status = ctk.StringVar(value="Status: OFF")
        ctk.CTkLabel(scroll_frame, textvariable=self.bridge_status,
                      font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)

        self._update_downstream_config_ui()
        self.bridge_state_initialized = True

    def _on_downstream_toggle(self, iface, var):
        if var.get() and iface.startswith("wlan"):
            for other_iface, other_var in self.downstream_vars.items():
                if other_iface.startswith("wlan") and other_iface != iface:
                    other_var.set(False)
        self._update_downstream_config_ui()
        if self.bridge_state_initialized:
            self._save_bridge_state()

    def _on_mac_mode_change(self, value):
        if value == "Specific":
            self.entry_specific_mac.configure(state="normal")
            self.entry_specific_mac.pack(padx=20, pady=5, fill="x")
        else:
            self.entry_specific_mac.configure(state="disabled")
            self.entry_specific_mac.pack_forget()
        if self.bridge_state_initialized:
            self._save_bridge_state()

    def _save_bridge_state(self):
        state = {
            "upstream": self.upstream_var.get(),
            "downstream": {iface: var.get() for iface, var in self.downstream_vars.items()},
            "mac_mode": self.mac_mode_var.get(),
            "specific_mac": self.specific_mac_var.get(),
            "ap_ssid": getattr(self, 'ap_ssid_var', ctk.StringVar(value="PiNetMaster_AP")).get(),
            "ap_password": getattr(self, 'ap_pass_var', ctk.StringVar(value="raspberry123")).get(),
            "ap_band": getattr(self, 'ap_band_var', ctk.StringVar(value="2.4GHz")).get(),
            "ap_encryption": getattr(self, 'ap_enc_var', ctk.StringVar(value="WPA2")).get(),
            "vpn_interface": self.vpn_var.get(),
            "bypass_interface": self.bypass_var.get()
        }
        self.state_manager.save_bridge_state(state)

    def _update_downstream_config_ui(self):
        for widget in self.downstream_config_frame.winfo_children():
            widget.destroy()
        selected_ds = [iface for iface, var in self.downstream_vars.items() if var.get()]
        has_wlan = any(iface.startswith("wlan") for iface in selected_ds)
        has_eth = any(iface.startswith("eth") for iface in selected_ds)

        if not selected_ds:
            ctk.CTkLabel(self.downstream_config_frame, text="No downstream interfaces selected.",
                          text_color="#888888").pack(pady=20)
            self.downstream_config_frame.pack(pady=10, padx=20, fill="x")
            return

        saved_state = self.state_manager.get_bridge_state()

        if has_wlan:
            ctk.CTkLabel(self.downstream_config_frame, text="Wi-Fi Hotspot Configuration",
                          font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
            ctk.CTkLabel(self.downstream_config_frame, text="Hotspot SSID:", anchor="w").pack(padx=20, fill="x")
            self.ap_ssid_var = ctk.StringVar(value=saved_state.get("ap_ssid", "PiNetMaster_AP"))
            ctk.CTkEntry(self.downstream_config_frame, textvariable=self.ap_ssid_var).pack(padx=20, pady=5, fill="x")
            ctk.CTkLabel(self.downstream_config_frame, text="Hotspot Password (min 8 chars):", anchor="w").pack(padx=20, fill="x")
            self.ap_pass_var = ctk.StringVar(value=saved_state.get("ap_password", "raspberry123"))
            ctk.CTkEntry(self.downstream_config_frame, textvariable=self.ap_pass_var, show="*").pack(padx=20, pady=5, fill="x")
            row_frame = ctk.CTkFrame(self.downstream_config_frame, fg_color="transparent")
            row_frame.pack(fill="x", padx=20, pady=5)
            ctk.CTkLabel(row_frame, text="Frequency:").pack(side="left", padx=5)
            self.ap_band_var = ctk.StringVar(value=saved_state.get("ap_band", "2.4GHz"))
            ctk.CTkComboBox(row_frame, values=["2.4GHz", "5GHz"], variable=self.ap_band_var, width=100).pack(side="left", padx=5)
            ctk.CTkLabel(row_frame, text="Encryption:").pack(side="left", padx=20)
            self.ap_enc_var = ctk.StringVar(value=saved_state.get("ap_encryption", "WPA2"))
            ctk.CTkComboBox(row_frame, values=["WPA2", "WPA3", "Open"], variable=self.ap_enc_var, width=100).pack(side="left", padx=5)

        if has_eth:
            ctk.CTkLabel(self.downstream_config_frame, text="Ethernet DHCP Configuration",
                          font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
            ctk.CTkLabel(self.downstream_config_frame,
                          text="Will automatically assign unique subnets to each selected Ethernet port.",
                          anchor="w", justify="left", text_color="#AAAAAA").pack(padx=20, pady=5, fill="x")

        self.downstream_config_frame.pack(pady=10, padx=20, fill="x")

    def toggle_bridge_on(self):
        upstream = self.upstream_var.get()
        selected_ds = [iface for iface, var in self.downstream_vars.items() if var.get()]
        vpn_iface = self.vpn_var.get()
        bypass_iface = self.bypass_var.get()

        if not selected_ds:
            return messagebox.showerror("Error", "Please select at least one Downstream interface.")
        if upstream in selected_ds:
            return messagebox.showerror("Error", "Upstream and Downstream interfaces cannot be the same.")

        self.btn_share_on.configure(state="disabled")
        self.update()

        out_iface_vpn = vpn_iface if vpn_iface != "None (Use Direct Upstream)" else upstream
        out_iface_bypass = upstream

        cmds = []
        cmds.append("iptables -t nat -N PI_NETMASTER 2>/dev/null || true")
        cmds.append("iptables -t nat -I POSTROUTING 1 -j PI_NETMASTER")
        cmds.append("iptables -N PI_NETMASTER_FWD 2>/dev/null || true")
        cmds.append("iptables -I FORWARD 1 -j PI_NETMASTER_FWD")

        base_ip = 77
        dnsmasq_lines = []

        for iface in selected_ds:
            current_out_iface = out_iface_bypass if iface == bypass_iface else out_iface_vpn
            mac_mode = self.mac_mode_var.get()
            if mac_mode != "None":
                cmds.append(f"ip link set {iface} down")
                if mac_mode == "Randomize":
                    cmds.append(f"macchanger -r {iface}")
                else:
                    mac = self.specific_mac_var.get().strip()
                    if len(mac) == 17:
                        cmds.append(f"macchanger --mac={mac} {iface}")
                cmds.append(f"ip link set {iface} up")
                cmds.append("sleep 1")

            if iface.startswith("wlan"):
                ssid = self.ap_ssid_var.get().strip()
                password = self.ap_pass_var.get().strip()
                band = "bg" if self.ap_band_var.get() == "2.4GHz" else "a"
                if len(password) < 8 and self.ap_enc_var.get() != "Open":
                    messagebox.showerror("Error", "Password must be at least 8 characters for WPA2/WPA3.")
                    self.btn_share_on.configure(state="normal")
                    return
                cmds.append("systemctl stop dnsmasq || true")
                cmds.append("nmcli connection delete Hotspot || true")
                cmds.append("nmcli connection delete 'Hotspot 1' || true")
                cmds.append(f"nmcli device wifi hotspot ifname {iface} ssid '{ssid}' password '{password}' band {band}")
                cmds.append("nmcli connection modify Hotspot ipv4.dns '127.0.0.1' || true")
                cmds.append("nmcli connection modify 'Hotspot 1' ipv4.dns '127.0.0.1' || true")
                cmds.append("nmcli connection up Hotspot || nmcli connection up 'Hotspot 1'")
                cmds.append(f"iptables -t nat -A PI_NETMASTER -s 10.42.0.0/24 -o {current_out_iface} -j MASQUERADE")
                cmds.append(f"iptables -A PI_NETMASTER_FWD -i {iface} -o {current_out_iface} -j ACCEPT")
                cmds.append(f"iptables -A PI_NETMASTER_FWD -i {current_out_iface} -o {iface} -m state --state RELATED,ESTABLISHED -j ACCEPT")

            elif iface.startswith("eth"):
                subnet_ip = f"192.168.{base_ip}.1/24"
                dhcp_start = f"192.168.{base_ip}.10"
                dhcp_end = f"192.168.{base_ip}.100"
                base_ip += 1
                cmds.append(f"nmcli device set {iface} managed no || true")
                cmds.append(f"ip link set {iface} down")
                cmds.append(f"ip addr flush dev {iface}")
                cmds.append(f"ip link set {iface} up")
                cmds.append(f"ip addr add {subnet_ip} dev {iface}")
                dnsmasq_lines.append(f"interface={iface}")
                dnsmasq_lines.append(f"dhcp-range={dhcp_start},{dhcp_end},255.255.255.0,24h")
                cmds.append(f"iptables -t nat -A PI_NETMASTER -s 192.168.{base_ip-1}.0/24 -o {current_out_iface} -j MASQUERADE")
                cmds.append(f"iptables -A PI_NETMASTER_FWD -i {iface} -o {current_out_iface} -j ACCEPT")
                cmds.append(f"iptables -A PI_NETMASTER_FWD -i {current_out_iface} -o {iface} -m state --state RELATED,ESTABLISHED -j ACCEPT")

        if dnsmasq_lines:
            dnsmasq_lines.append("bind-interfaces")
            try:
                os.makedirs("/etc/dnsmasq.d", exist_ok=True)
                with open("/etc/dnsmasq.d/pi-bridge.conf", "w") as f:
                    f.write("\n".join(dnsmasq_lines) + "\n")
                cmds.append("systemctl restart dnsmasq")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to write dnsmasq config: {e}")
                self.btn_share_on.configure(state="normal")
                return

        cmds.append("sysctl -w net.ipv4.ip_forward=1")
        for cmd in cmds:
            self.net_mgr._run_cmd(cmd)

        ds_names = ", ".join(selected_ds)
        bypass_text = f" (Bypassing VPN for {bypass_iface})" if bypass_iface != "None (All use VPN)" else ""
        self.bridge_status.set(f"Status: ON ({ds_names} -> {out_iface_vpn}){bypass_text}")
        self.btn_share_on.configure(state="normal")
        messagebox.showinfo("Success", f"Internet sharing is ON.\n\nDownstream: {ds_names}\nRouting via: {out_iface_vpn}{bypass_text}")

    def toggle_bridge_off(self):
        selected_ds = [iface for iface, var in self.downstream_vars.items() if var.get()]
        cmds = [
            "iptables -t nat -D POSTROUTING -j PI_NETMASTER || true",
            "iptables -t nat -F PI_NETMASTER || true",
            "iptables -t nat -X PI_NETMASTER || true",
            "iptables -D FORWARD -j PI_NETMASTER_FWD || true",
            "iptables -F PI_NETMASTER_FWD || true",
            "iptables -X PI_NETMASTER_FWD || true",
        ]
        for iface in selected_ds:
            if iface.startswith("wlan"):
                cmds.append("nmcli connection delete Hotspot || true")
                cmds.append("nmcli connection delete 'Hotspot 1' || true")
            elif iface.startswith("eth"):
                cmds.append(f"nmcli device set {iface} managed yes || true")
                cmds.append(f"ip link set {iface} down")
                cmds.append(f"ip addr flush dev {iface}")
        cmds.append("systemctl stop dnsmasq || true")
        cmds.append("sysctl -w net.ipv4.ip_forward=0 || true")
        for cmd in cmds:
            self.net_mgr._run_cmd(cmd)
        self.bridge_status.set("Status: OFF")
        messagebox.showinfo("Success", "Internet sharing is now OFF.")

    def _update_engine_status_ui(self):
        if self.net_mgr.engine_active:
            self.lbl_engine_status.configure(text="[OK] Router Engine: Active", text_color="#28A745")
            self.btn_fix_engine.pack_forget()
        else:
            self.lbl_engine_status.configure(text="[FAIL] Router Engine: Inactive", text_color="#DC3545")
            self.btn_fix_engine.pack(side="right", padx=20, pady=10)

    def _fix_engine_click(self):
        self.btn_fix_engine.configure(text="Fixing...", state="disabled")
        self.update()
        success = self.net_mgr.fix_router_engine()
        self._update_engine_status_ui()
        if success:
            messagebox.showinfo("Success", "Router Engine Fixed!")
        else:
            messagebox.showerror("Error", "Failed to initialize engine.")
        self.btn_fix_engine.configure(text="Fix Router Engine", state="normal")

    # ==========================================
    # VIEW 2: SETTINGS (WITH SELECT ALL)
    # ==========================================
    def show_settings(self):
        if self.current_view == "bridge" and self.bridge_state_initialized:
            self._save_bridge_state()

        self._clear_main_area()
        self._set_active_btn(self.btn_settings)
        self.current_view = "settings"

        scroll_frame = ctk.CTkScrollableFrame(self.main_area, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(scroll_frame, text="Filter Lists & Settings",
                      font=ctk.CTkFont(size=24, weight="bold"), anchor="w").pack(pady=20, padx=20, fill="x")

        # --- Big Tech Filtering ---
        ctk.CTkLabel(scroll_frame, text="Big Tech Filtering (Customizable)",
                      font=ctk.CTkFont(size=16, weight="bold"), anchor="w").pack(pady=(20, 10), padx=20, fill="x")

        self.company_frames = {}
        self.company_vars = {}
        self.domain_vars = {}

        current_blocks = ""
        if os.path.exists(BLOCKLIST_FILE):
            with open(BLOCKLIST_FILE, "r") as f:
                current_blocks = f.read()

        saved_settings = self.state_manager.get_settings_state()
        saved_companies = saved_settings.get("companies", {})
        saved_domains = saved_settings.get("domains", {})
        saved_categories = saved_settings.get("categories", {})

        for company, domains in COMPANY_DOMAINS.items():
            frame = ctk.CTkFrame(scroll_frame, fg_color="#1E1E1E", corner_radius=10)
            frame.pack(pady=5, padx=20, fill="x")

            is_main_blocked = saved_companies.get(company, f"# {company} Blocklist" in current_blocks)
            main_var = ctk.BooleanVar(value=is_main_blocked)
            self.company_vars[company] = main_var

            header_frame = ctk.CTkFrame(frame, fg_color="transparent")
            header_frame.pack(fill="x", padx=15, pady=10)

            ctk.CTkCheckBox(
                header_frame, text=f"Block {company}", variable=main_var,
                command=lambda c=company: self._toggle_company_domains(c),
                font=ctk.CTkFont(size=16, weight="bold")
            ).pack(side="left")

            # SELECT ALL / DESELECT ALL button per company
            select_all_var = ctk.StringVar(value="Select All")
            select_all_btn = ctk.CTkButton(
                header_frame, text="Select All", width=90, height=28,
                font=ctk.CTkFont(size=11),
                fg_color="#2A2A2A", hover_color="#3A3A3A",
                command=lambda c=company, btn=None, sv=select_all_var: self._toggle_select_all_company(c, btn, sv)
            )
            select_all_btn.pack(side="right", padx=5)
            # Store reference so we can update label later
            select_all_btn._select_all_var = select_all_var

            domain_frame = ctk.CTkFrame(frame, fg_color="#252525", corner_radius=8)
            self.company_frames[company] = domain_frame
            self.domain_vars[company] = {}
            row, col = 0, 0
            for domain in domains:
                is_domain_blocked = saved_domains.get(f"{company}:{domain}", f"address=/{domain}/0.0.0.0" in current_blocks)
                d_var = ctk.BooleanVar(value=is_domain_blocked)
                self.domain_vars[company][domain] = d_var
                cb = ctk.CTkCheckBox(
                    domain_frame, text=domain, variable=d_var,
                    command=lambda c=company: self._update_company_blocklist(c),
                    font=ctk.CTkFont(size=13)
                )
                cb.grid(row=row, column=col, padx=10, pady=5, sticky="w")
                col += 1
                if col > 1:
                    col = 0
                    row += 1
            domain_frame.pack(fill="x", padx=15, pady=(0, 15))
            self._toggle_company_domains(company)

        # --- Content Filtering ---
        ctk.CTkLabel(scroll_frame, text="Content Filtering",
                      font=ctk.CTkFont(size=16, weight="bold"), anchor="w").pack(pady=(20, 10), padx=20, fill="x")

        self.cat_vars = {}
        self.cat_select_all_vars = {}

        for category in CATEGORY_DOMAINS.keys():
            cat_frame = ctk.CTkFrame(scroll_frame, fg_color="#1E1E1E", corner_radius=10)
            cat_frame.pack(pady=5, padx=20, fill="x")

            is_cat_blocked = saved_categories.get(category, f"# {category} Blocklist" in current_blocks)
            var = ctk.BooleanVar(value=is_cat_blocked)
            self.cat_vars[category] = var

            header = ctk.CTkFrame(cat_frame, fg_color="transparent")
            header.pack(fill="x", padx=15, pady=10)

            ctk.CTkCheckBox(
                header, text=f"Block {category}", variable=var,
                command=lambda c=category, v=var: self._on_category_toggle(c, v),
                font=ctk.CTkFont(size=15, weight="bold")
            ).pack(side="left")

            # Category-level enable/disable acts as its own "select all" since it blocks the whole list
            status_label = ctk.CTkLabel(header, text="", font=ctk.CTkFont(size=11), text_color="#888888")
            status_label.pack(side="right", padx=10)
            domain_count = len(CATEGORY_DOMAINS.get(category, []))
            status_label.configure(text=f"{domain_count} domains")

        ctk.CTkButton(
            scroll_frame, text="EMERGENCY: Clear All Firewall & DNS Rules",
            fg_color="#D32F2F", hover_color="#B71C1C", command=self.clear_all_rules,
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=30, padx=20, fill="x")

        self.settings_state_initialized = True

    def _toggle_select_all_company(self, company, btn_widget, str_var):
        """Toggle all domains in a company block on/off"""
        domain_dict = self.domain_vars.get(company, {})
        if not domain_dict:
            return

        # Determine current state: if ANY are unchecked, select all; otherwise deselect all
        all_checked = all(v.get() for v in domain_dict.values())

        new_state = not all_checked
        for d_var in domain_dict.values():
            d_var.set(new_state)

        # Update button label
        if btn_widget and hasattr(btn_widget, '_select_all_var'):
            btn_widget._select_all_var.set("Deselect All" if new_state else "Select All")
            btn_widget.configure(text="Deselect All" if new_state else "Select All")

        self._update_company_blocklist(company)
        if self.settings_state_initialized:
            self._save_settings_state()

    def _on_category_toggle(self, category, var):
        self.net_mgr.update_category_block(category, var.get())
        if self.settings_state_initialized:
            self._save_settings_state()

    def _toggle_company_domains(self, company):
        is_enabled = self.company_vars[company].get()
        if is_enabled:
            self.company_frames[company].pack(fill="x", padx=15, pady=(0, 15))
        else:
            self.company_frames[company].pack_forget()
            for d_var in self.domain_vars[company].values():
                d_var.set(False)
        self._update_company_blocklist(company)
        if self.settings_state_initialized:
            self._save_settings_state()

    def _update_company_blocklist(self, company):
        domain_states = {domain: var.get() for domain, var in self.domain_vars[company].items()}
        self.net_mgr.update_company_block(company, domain_states)
        if self.settings_state_initialized:
            self._save_settings_state()

    def _save_settings_state(self):
        companies = {}
        domains = {}
        categories = {}
        for company, var in self.company_vars.items():
            companies[company] = var.get()
        for company, domain_dict in self.domain_vars.items():
            for domain, var in domain_dict.items():
                domains[f"{company}:{domain}"] = var.get()
        for category, var in self.cat_vars.items():
            categories[category] = var.get()
        state = {"companies": companies, "domains": domains, "categories": categories}
        self.state_manager.save_settings_state(state)

    def clear_all_rules(self):
        self.net_mgr.clear_all_firewall_rules()
        if hasattr(self, 'company_vars'):
            for company, var in self.company_vars.items():
                var.set(False)
                self._toggle_company_domains(company)
        if hasattr(self, 'cat_vars'):
            for var in self.cat_vars.values():
                var.set(False)
        if self.settings_state_initialized:
            self._save_settings_state()
        messagebox.showinfo("Success", "All firewall and DNS block rules cleared.")


if __name__ == "__main__":
    app = PiNetMasterApp()
    app.mainloop()
