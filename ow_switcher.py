import os
import sys
import ctypes
import subprocess
import traceback
import tkinter as tk
from tkinter import messagebox

RULE_NAME = "OWJapan_BlockAll"

# Refined & Expanded IP Blocklist
# Sources: original list + live AWS ip-ranges.json (ap-northeast-1/3) +
# community-sourced ranges from r/Competitiveoverwatch. Every entry below
# has been run through a CIDR-overlap check against the JAPAN allow-list
# so nothing here accidentally blocks real Japan address space. Two more
# JP leaks were found and fixed this round: 104.198.0.0/16 and part of
# 35.187.0.0/16 both turned out to be Japan (per community data), not
# Singapore - the Singapore entries below have been trimmed accordingly.
BLOCK_MATCH_SERVERS = [
    # Middle East - Dubai / Bahrain (mes1) / Saudi Arabia
    "3.28.0.0/14",       # ME (AWS me-central-1)
    "8.228.0.0/16",      # ME
    "15.184.0.0/14",     # ME (covers 15.184-15.187, includes mes1 Bahrain)
    "34.160.0.0/13",     # ME (GCP)
    "157.175.0.0/16",    # ME - mes1 Bahrain (reddit)

    # Singapore (gsg1 / sin1)
    "3.0.0.0/14", "13.212.0.0/14", "13.228.0.0/14", "13.250.0.0/15", "15.196.0.0/15", "18.136.0.0/13",
    "34.87.0.0/16", "34.101.0.0/16", "34.124.0.0/16", "34.126.0.0/16", "34.128.0.0/16", "34.142.0.0/15",
    "35.185.128.0/18", "35.198.192.0/18", "35.240.0.0/14", "35.247.0.0/16",
    "47.128.0.0/14", "52.72.0.0/14", "52.220.0.0/15", "54.178.0.0/15",
    "54.251.0.0/16", "175.41.128.0/18",
    "104.199.0.0/16",    # SG - NOTE: was 104.198.0.0/15 (2 blocks); .198 is
                          # actually Japan per reddit data, only .199 is SG
    "136.110.0.0/16",    # SG (GCP)
    "136.85.0.0/16",     # SG (GCP)
    "35.187.0.0/17",     # SG - NOTE: trimmed from 35.187.0.0/16; upper
    "35.187.128.0/18",   # SG   half (35.187.192.0/18) is actually Japan

    # Taiwan (tpe1)
    "5.42.160.0/24",     # TW - NOTE: was /19; community correction says
                          # the /19 also covered France/Netherlands by mistake

    # Korea (icn1)
    "3.32.0.0/14", "13.124.0.0/14", "13.209.0.0/16", "15.164.0.0/14",
    "34.64.0.0/16", "34.118.0.0/15", "52.76.0.0/14", "54.180.0.0/14",
    "35.216.0.0/14", "35.220.0.0/16", "35.222.0.0/15",  # KR - NOTE: split from
                          # 35.216.0.0/13; 35.221.0.0/16 carved out (it's Japan)
    "117.52.0.0/16",     # KR (icn1, reddit-confirmed)
    "121.254.0.0/16",    # KR (icn1, reddit)
    "182.162.0.0/16", "211.115.0.0/16", "211.233.0.0/16",
    "103.4.114.0/24",    # KR - Blizzard-owned (AS57976) Seoul

    # Australia (syd1 / syd2)
    "13.52.0.0/14", "13.210.0.0/15", "15.196.0.0/16", "34.129.0.0/16",
    "35.189.0.0/16", "35.197.0.0/16", "35.244.0.0/14", "54.66.0.0/15",
    "37.244.42.0/24",    # AU - syd2 (reddit)

    # EU / US / Americas
    "24.105.0.0/18", "34.82.0.0/15", "34.90.0.0/15", "34.92.0.0/15", "34.104.96.0/21",
    "35.198.0.0/15", "35.204.0.0/14", "35.217.0.0/18", "35.220.26.0/24",
    "35.228.0.0/14", "35.232.0.0/14", "35.242.26.0/24", "52.16.0.0/12",
    "54.192.0.0/15", "64.224.0.0/16", "104.155.0.0/16", "185.60.112.0/22", "185.60.114.0/23",
    "24.105.40.0/21",    # US - ord1 Chicago (reddit)

    # South America / Brazil - not covered by the original list at all
    "177.71.0.0/16",     # BR
    "54.94.0.0/16",      # BR
    "54.207.0.0/16",     # BR
    "18.231.0.0/16",     # BR
    "54.232.0.0/16",     # BR
    "54.233.0.0/16",     # BR
    "52.207.0.0/16",     # BR
    "18.228.0.0/16",     # BR
    "200.29.0.0/16",     # BR
    "170.84.0.0/16",     # BR
    "200.32.0.0/16",     # BR
    "200.10.0.0/16",     # BR
    "18.229.0.0/16",     # BR
    "18.230.0.0/16",     # BR
    "15.177.0.0/16",     # BR
    "64.252.0.0/16",     # BR
    "54.240.0.0/16",     # BR
    "15.228.0.0/16",     # BR
    "34.151.0.0/16",     # BR - Sao Paulo GCP (confirmed via ipinfo 34.151.219.108)
    # BR fragments below are trimmed - the original /16 partially overlapped Japan
    "52.95.0.0/17", "52.95.128.0/19", "52.95.160.0/20", "52.95.176.0/22",
    "52.95.180.0/23", "52.95.184.0/21", "52.95.192.0/18",   # BR (was 52.95.0.0/16)
    "52.94.0.0/21", "52.94.9.0/24", "52.94.10.0/23", "52.94.12.0/22",
    "52.94.16.0/20", "52.94.32.0/19", "52.94.64.0/18", "52.94.128.0/17",  # BR (was 52.94.0.0/16)
    "99.77.0.0/17", "99.77.128.0/18", "99.77.192.0/19", "99.77.224.0/20",
    "99.77.240.0/22", "99.77.245.0/24", "99.77.246.0/23", "99.77.248.0/21",  # BR (was 99.77.0.0/16)
    # NOTE: 52.67.0.0/16 from the reddit BR list was skipped entirely -
    # it's fully inside real Japan address space, not blocked here.

    # US / EU extras - confirmed via ipinfo from in-game Resource Monitor traffic
    "34.48.0.0/16",      # US - Washington DC GCP (confirmed 34.48.183.189)
    "8.234.0.0/16",      # US - Washington DC GCP (confirmed 8.234.247.255)
    "34.88.0.0/16",      # FI - Finland GCP (confirmed 34.88.120.139)

    # NOTE: 158.115.196.251 (Irvine, California - Blizzard-owned AS57976)
    # was seen in traffic but is intentionally NOT blocked here. Like
    # 137.221.0.0/16, this looks like it could be a shared Blizzard
    # backend network used across all regions rather than a per-region
    # game server - blocking it risks repeating the "can't reach lobby"
    # issue from before. Confirm with netstat (protocol/port + whether it
    # still appears while just sitting in the lobby, not queued) before
    # adding 158.115.0.0/16 here.
]

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def check_admin_privileges():
    if not is_admin():
        try:
            script_path = os.path.abspath(sys.argv[0])
            params = " ".join([f'"{arg}"' for arg in sys.argv[1:]])
            cmd_args = f'"{script_path}" {params}'.strip()

            result = ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, cmd_args, None, 1
            )
            if result <= 32:
                messagebox.showerror("Permission Error", "Administrator rights are required to run this app.")
            sys.exit(0)
        except Exception as e:
            messagebox.showerror("Elevation Error", f"Failed to request Admin rights:\n{str(e)}")
            sys.exit(1)

def run_powershell(command):
    try:
        res = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command],
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        return res.returncode == 0, res.stderr
    except Exception as e:
        return False, str(e)

def remove_rule():
    cmd = f'Remove-NetFirewallRule -DisplayName "{RULE_NAME}*" -ErrorAction SilentlyContinue'
    run_powershell(cmd)

def enable_japan_only():
    try:
        status_label.config(text="Applying...", fg="#FFC107")
        root.update()

        remove_rule()

        ps_ip_array = "@(" + ",".join([f"'{ip}'" for ip in BLOCK_MATCH_SERVERS]) + ")"
        cmd = f'New-NetFirewallRule -DisplayName "{RULE_NAME}" -Direction Outbound -Action Block -RemoteAddress {ps_ip_array} -Protocol UDP | Out-Null'

        success, error_msg = run_powershell(cmd)

        if success:
            status_label.config(text="Japan Only Active", fg="#00E676")
            messagebox.showinfo("Status", "Server locked to Japan (TYO/GTK).")
        else:
            status_label.config(text="Failed to Apply", fg="#E53935")
            messagebox.showerror("PowerShell Error", f"Failed to set Firewall Rule:\n{error_msg}")
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred:\n{str(e)}")

def reset_rules():
    try:
        status_label.config(text="Resetting...", fg="#FFC107")
        root.update()
        remove_rule()
        status_label.config(text="Default Matchmaking", fg="#888888")
        messagebox.showinfo("Status", "Default matchmaking restored.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to reset rules:\n{str(e)}")

if __name__ == "__main__":
    check_admin_privileges()

    try:
        root = tk.Tk()
        root.title("OW2 JP Switcher")
        root.geometry("300x230")
        root.resizable(False, False)
        root.configure(bg="#121212")

        lbl_title = tk.Label(root, text="OW2 JAPAN SWITCHER", font=("Segoe UI", 11, "bold"), fg="#FFFFFF", bg="#121212")
        lbl_title.pack(pady=(22, 12))

        btn_jp = tk.Button(
            root, text="Japan Only", font=("Segoe UI", 10, "bold"),
            bg="#E53935", fg="#FFFFFF", activebackground="#C62828", activeforeground="#FFFFFF",
            relief="flat", cursor="hand2", width=18, pady=5, command=enable_japan_only
        )
        btn_jp.pack(pady=5)

        btn_reset = tk.Button(
            root, text="Reset", font=("Segoe UI", 10),
            bg="#2A2A2A", fg="#CCCCCC", activebackground="#3D3D3D", activeforeground="#FFFFFF",
            relief="flat", cursor="hand2", width=18, pady=5, command=reset_rules
        )
        btn_reset.pack(pady=5)

        status_label = tk.Label(root, text="Status: Ready", font=("Segoe UI", 9), fg="#888888", bg="#121212")
        status_label.pack(side="bottom", pady=15)

        root.mainloop()
    except Exception as fatal_err:
        ctypes.windll.user32.MessageBoxW(0, f"Fatal GUI Error:\n{traceback.format_exc()}", "Application Crash", 0x10)