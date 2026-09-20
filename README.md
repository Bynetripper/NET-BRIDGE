<img width="1097" height="873" alt="image" src="https://github.com/user-attachments/assets/065ce439-80bc-4609-a24f-5098c100acee" />

# Pi NetMaster

**A unified dark-mode GUI for turning your Raspberry Pi into a VPN router, network bridge, and DNS firewall.**

Pi NetMaster combines a Wi-Fi-to-Ethernet internet sharing configurator, a MAC address randomizer, a Proton VPN-aware split-tunneling engine, and a Portmaster-style DNS blocklist manager into a single, lightweight Python application built with `customtkinter`.

---

## Features

### Network Bridge & Sharing
- **Dynamic interface scanning** -- automatically detects all available network interfaces (`eth0`, `eth1`, `wlan0`, `wlan1`, `tun0`, etc.)
- **Multi-interface downstream** -- select multiple Ethernet ports simultaneously, each automatically assigned a unique non-conflicting subnet (`192.168.77.x`, `192.168.78.x`, etc.)
- **Single Wi-Fi downstream enforcement** -- if you select a wireless interface as output, the app automatically prevents selecting a second one and expands a hotspot configuration panel
- **Wi-Fi hotspot creation** -- configure SSID, password, frequency (2.4GHz / 5GHz), and encryption type (WPA2 / WPA3 / Open)
- **MAC address randomization** -- apply random or specific MAC addresses to downstream interfaces before they come online
- **VPN routing** -- force all downstream client traffic through a selected VPN tunnel interface (e.g., `tun0`)
- **VPN bypass / split tunneling** -- designate a specific downstream interface (e.g., your work PC's Ethernet port) to bypass the VPN and use the direct upstream connection instead
- **Isolated firewall chains** -- all rules are placed in dedicated `PI_NETMASTER` iptables chains so turning sharing on/off will never break your Proton VPN kill-switch

### DNS Firewall (Settings)
- **Granular Big Tech blocking** -- expandable per-company panels (Google, Microsoft, Apple, Amazon) with individual domain checkboxes so you can, for example, block all of Google except `youtube.com`
- **Content filtering categories** -- one-click checkboxes for:
  - Ads and Trackers
  - Malware
  - Suspicious Websites (URL shorteners)
  - Adult Content
- **DNS-level enforcement** -- all blocking is done via `dnsmasq` NXDOMAIN responses, meaning it works for every device on your network without installing anything on the clients
- **Emergency clear button** -- instantly flushes all firewall and DNS rules if something goes wrong

### General
- **Dark mode UI** -- sleek, Portmaster-inspired dark theme using `customtkinter`
- **Scrollable panels** -- no UI elements are ever cut off, regardless of screen resolution
- **No emoji rendering issues** -- all icons use plain text labels for reliable display on Raspberry Pi OS
- **Auto router engine initialization** -- automatically enables IP forwarding and loads `nf_conntrack` on startup
- **Root privilege enforcement** -- refuses to run without `sudo` to prevent silent failures

---

## Screenshots

| Network Bridge | Settings |
|:---:|:---:|
| Interface selection, hotspot config, VPN routing, MAC changer | Granular Big Tech blocking, content filtering |
| *(add screenshot)* | *(add screenshot)* |

---

## Requirements

- **Hardware:** Raspberry Pi 3B+ or newer (4B/5 recommended) with at least one Ethernet port and one Wi-Fi adapter
- **OS:** Raspberry Pi OS (Bookworm or Bullseye) with desktop environment
- **Network:** For split tunneling and VPN routing, you need a second network interface (USB Ethernet adapter, second Wi-Fi dongle, etc.)
- **VPN:** Proton VPN CLI or any OpenVPN/WireGuard client that creates a `tun` or `wg` interface

---

## Installation

### 1. Install system dependencies

```bash
sudo apt update
sudo apt install python3-pip python3-tk network-manager dnsmasq iptables macchanger conntrack -y
```

### 2. Install Python dependencies

```bash
pip3 install customtkinter
```

### 3. Clone or download the project

```bash
git clone https://github.com/Bynetripper/NET-BRIDGE.git
cd NET-BRIDGE
```

### 4. Run the application

```bash
sudo python3 console.py
```

> **Note:** Root privileges are required because the app modifies `iptables` firewall rules, `dnsmasq` DNS configuration, and network interface settings.

---

## Usage

### Network Bridge Tab

1. **Select Upstream Interface** -- choose the interface that has your internet connection (e.g., `wlan0` for Wi-Fi, `tun0` for Proton VPN)
2. **Select Downstream Interfaces** -- check the boxes for the interfaces you want to share internet with
   - You can check multiple Ethernet ports at once
   - Only one Wi-Fi interface can be selected at a time
3. **Configure MAC Randomization** (optional) -- choose `None`, `Randomize`, or `Specific`
4. **Configure Hotspot** (if a Wi-Fi downstream is selected) -- set SSID, password, frequency, and encryption
5. **Configure VPN Routing** (optional) -- select your VPN interface (e.g., `tun0`) to force downstream traffic through the VPN
6. **Configure VPN Bypass** (optional) -- select a specific downstream interface that should skip the VPN and use direct internet (e.g., your work PC)
7. Click **Turn ON Sharing**

### Settings Tab

1. **Big Tech Filtering** -- check a company (e.g., "Block Google") to expand its domain list, then uncheck any domains you want to allow (e.g., uncheck `youtube.com` to keep YouTube working while blocking everything else Google)
2. **Content Filtering** -- check the categories you want to block network-wide
3. **Emergency Clear** -- use the red button at the bottom to instantly remove all firewall and DNS rules

---

## How It Works

### Architecture

```
[Internet]
    |
[Upstream Interface] (wlan0 / eth0 / tun0)
    |
[Raspberry Pi running Pi NetMaster]
    |
    +---> [Downstream eth0] --> 192.168.77.x subnet --> Client devices
    +---> [Downstream eth1] --> 192.168.78.x subnet --> Client devices
    +---> [Downstream wlan1] --> 10.42.0.x hotspot  --> Wi-Fi clients
    |
[dnsmasq DNS server]
    |-- Serves DHCP to downstream clients
    |-- Returns 0.0.0.0 for blocked domains
    |-- Forces DNS through Pi so blocklists apply to all clients
```

### Firewall Isolation

Pi NetMaster creates dedicated iptables chains to avoid interfering with Proton VPN or other system rules:

```
PI_NETMASTER      (nat/POSTROUTING) -- handles MASQUERADE for each downstream subnet
PI_NETMASTER_FWD  (filter/FORWARD)  -- handles ACCEPT rules for each downstream interface
```

When you turn sharing OFF, only these chains are flushed and removed. Your Proton VPN kill-switch and other system rules remain completely untouched.

### VPN Split Tunneling

When you select a VPN interface and a bypass interface, the app generates separate routing rules per downstream interface:

```
Downstream eth0 (VPN)    --> MASQUERADE out tun0
Downstream eth1 (Bypass) --> MASQUERADE out wlan0 (direct)
```

This means your work PC on `eth1` gets direct internet access while all other devices are forced through the Proton VPN tunnel.

### DNS Blocking

Blocked domains are written to `/etc/dnsmasq.d/portmaster_block.conf` in the format:

```
# Google Blocklist
address=/google.com/0.0.0.0
address=/googleapis.com/0.0.0.0
# youtube.com is NOT listed, so it resolves normally
```

When a client device tries to resolve a blocked domain, `dnsmasq` returns `0.0.0.0`, effectively blackholing the connection. The Wi-Fi hotspot is configured to use `127.0.0.1` as its DNS server, ensuring hotspot clients are also subject to the blocklists.

---

## File Structure

```
pi-netmaster/
  pi_netmaster.py        # Main application (single file, no external dependencies beyond customtkinter)
  README.md              # This file
```

### System Files Modified at Runtime

| File | Purpose |
|---|---|
| `/etc/dnsmasq.d/portmaster_block.conf` | DNS blocklist rules |
| `/etc/dnsmasq.d/pi-bridge.conf` | DHCP configuration for Ethernet downstream |
| `/etc/sysctl.conf` | Persistent IP forwarding setting |
| `/etc/modules` | Persistent `nf_conntrack` module loading |

---

## Troubleshooting

### "ERROR: This script must be run as root"
You forgot `sudo`. Run:
```bash
sudo python3 pi_netmaster.py
```

### Downstream devices get IP addresses but no internet
1. Make sure your upstream interface actually has internet access
2. Check that IP forwarding is enabled: `sysctl net.ipv4.ip_forward` should return `1`
3. Check iptables: `sudo iptables -t nat -L PI_NETMASTER -v`

### VPN bypass interface still routes through VPN
Make sure the bypass interface is selected in the "Bypass VPN for Specific Interface" dropdown AND that it is also checked as a downstream interface. The app matches the interface name exactly.

### Wi-Fi hotspot not showing up on devices
1. Ensure the Wi-Fi adapter supports AP mode: `iw list | grep -A5 "Supported interface modes"`
2. Check that no other service is using the interface: `sudo nmcli device status`
3. Some USB Wi-Fi adapters do not support 5GHz AP mode -- try switching to 2.4GHz

### DNS blocking not working for some devices
Devices that use hardcoded DNS servers (like `8.8.8.8`) will bypass the Pi's DNS filter. To force all DNS traffic through the Pi, add this iptables rule manually:
```bash
sudo iptables -t nat -A PREROUTING -p udp --dport 53 -j REDIRECT --to-port 53
```

### "ModuleNotFoundError: No module named 'customtkinter'"
Install it with:
```bash
pip3 install customtkinter
```

### dnsmasq fails to start
Check for conflicting services:
```bash
sudo systemctl status dnsmasq
sudo journalctl -u dnsmasq -n 20
```
If `systemd-resolved` is running, it may conflict. Disable it:
```bash
sudo systemctl disable systemd-resolved
sudo systemctl stop systemd-resolved
```

---

## Compatibility

| VPN Provider | Status | Notes |
|---|---|---|
| Proton VPN | Fully supported | Rules inserted at chain top to beat kill-switch |
| Mullvad | Supported | Same chain-isolation approach works |
| OpenVPN (generic) | Supported | Any `tun` interface works |
| WireGuard | Supported | Any `wg` interface works |

---

## Security Notes

- This application modifies system-level firewall rules, DNS configuration, and network interfaces. Only run it on a Raspberry Pi dedicated to routing.
- The DNS blocklists included are basic starter lists. For production-grade protection, consider supplementing with curated blocklists from projects like [StevenBlack/hosts](https://github.com/StevenBlack/hosts) or [oisd.nl](https://oisd.nl).
- MAC address randomization is a privacy measure, not a security guarantee. Some networks can still fingerprint devices through other means.
- The VPN bypass feature intentionally routes traffic outside the VPN tunnel. Only use it for devices that require direct internet access (e.g., work computers with corporate VPN requirements).

---

## License

This project is open source and available under the [MIT License](LICENSE).

---

## Acknowledgments

- Inspired by [Safing Portmaster](https://safing.io/portmaster/)
- Built with [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
- DNS blocking powered by [dnsmasq](https://thekelleys.org.uk/dnsmasq/doc.html)
