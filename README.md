# NET-BRIDGE
Modern dark mode router portal with network management, VPN bypass, MAC spoofing, and internet sharing specifically designed for Raspberry PI to work as a router
and should work on any other linux setup. Choose your upstream and downstream source(s) YOU MUST RUN YOUR VPN APP OF CHOICE BEFORE RUNNING NET BRIDGE.
<img width="1172" height="755" alt="image" src="https://github.com/user-attachments/assets/a1904bc8-9a67-49e6-ba30-03a2703d2193" />


✨ Features:
• Network interface management (WAN/LAN selection)
• Internet sharing with automatic DHCP via dnsmasq
• VPN import and split-tunnel bypass rules (WireGuard + OpenVPN)
• MAC address spoofing (random, specific, or manufacturer-based)
• Auto-MAC rotation when internet drops
• Real-time firewall rule viewer (iptables + nftables)
• Wi-Fi network scanning and connection
• System monitoring with temperature and uptime
• Dark mode UI with custom widgets
• Sidebar navigation with active state indicators
• Requires root for full functionality

Debian / Ubuntu / Linux Mint / Pop!_OS / Raspberry Pi OS
# Update package list
sudo apt update

# Install system dependencies
sudo apt install -y \
    python3 \
    python3-pip \
    python3-tk \
    network-manager \
    dnsmasq \
    iptables \
    nftables \
    iproute2 \
    macchanger \
    inetutils-ping \
    coreutils

# Install Python GUI library
pip3 install customtkinter

# Enable and start required services
sudo systemctl enable dnsmasq
sudo systemctl start dnsmasq
sudo systemctl enable NetworkManager

Important Notes
Root Required: The app must run with sudo because it manages network interfaces, firewall rules, and system services.
NetworkManager: Required for Wi-Fi scanning and connection. If you use a different network manager (like systemd-networkd), Wi-Fi features won't work.
dnsmasq: Used for DHCP when sharing internet. The app creates config files in /etc/dnsmasq.d/.
macchanger: May prompt for confirmation during installation - choose "Yes" to allow automatic MAC changes.
Firewall: The app uses both iptables (legacy) and nftables (modern). Most systems have both, but if you only have one, the app will still work.
sudo systemctl start NetworkManager
