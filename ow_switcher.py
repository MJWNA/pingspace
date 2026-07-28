import os
import sys
import ctypes
import subprocess
import traceback
import tkinter as tk
from tkinter import messagebox

RULE_NAME = "OWJapan_BlockAll"

# Refined & Expanded IP Blocklist
BLOCK_MATCH_SERVERS = [
    # Middle East (Dubai / Bahrain)
    "3.28.0.0/14", "15.184.0.0/14", "15.185.0.0/16", "34.163.0.0/14", "34.165.0.0/15", "34.166.0.0/15",
    
    # Singapore (Expanded GCP & AWS subnets)
    "3.0.0.0/14", "13.212.0.0/14", "13.228.0.0/14", "13.250.0.0/15", "15.197.0.0/15", "18.136.0.0/13",
    "34.87.0.0/16", "34.101.0.0/16", "34.124.0.0/16", "34.126.0.0/16", "34.128.0.0/16", "34.142.0.0/16", 
    "34.143.0.0/16", "35.185.128.0/18", "35.198.192.0/18", "35.240.0.0/14", "35.247.0.0/16", 
    "47.128.0.0/14", "52.74.0.0/14", "52.220.0.0/15", "54.151.0.0/15", "54.169.0.0/15", 
    "54.179.0.0/15", "54.251.0.0/14", "104.198.0.0/15", "104.199.0.0/15", "175.41.128.0/18",
    
    # Taiwan (TPE)
    "5.42.160.0/19",
    
    # Korea (Precise Subnets only)
    "3.34.0.0/14", "13.124.0.0/14", "13.209.0.0/15", "15.164.0.0/14",
    "34.64.0.0/16", "34.118.0.0/15", "35.216.0.0/13", "52.78.0.0/14", "54.180.0.0/14", 
    "117.52.0.0/16", "182.162.0.0/16", "211.115.0.0/16", "211.233.0.0/16",
    
    # Australia
    "13.54.0.0/14", "13.210.0.0/15", "15.196.0.0/16", "34.129.0.0/16",
    "35.189.0.0/16", "35.197.0.0/16", "35.201.0.0/16", "35.244.0.0/14", "54.66.0.0/15",
    
    # EU / US / Americas
    "24.105.0.0/18", "34.82.0.0/15", "34.90.0.0/15", "34.92.0.0/15", "34.104.96.0/21",
    "35.198.0.0/15", "35.203.232.0/21", "35.204.0.0/14", "35.217.0.0/18", "35.220.26.0/24",
    "35.228.0.0/16", "35.230.0.0/14", "35.234.0.0/14", "35.242.26.0/24", "52.28.0.0/12",
    "54.193.0.0/15", "104.155.0.0/16", "185.60.112.0/22", "185.60.114.0/23"
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