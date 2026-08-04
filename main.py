import os
import sys
import ctypes
import subprocess
import traceback
import json
import tkinter.messagebox as messagebox
import customtkinter as ctk

# Set dark UI theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

# Set prefix for rule names so they can be easily removed
RULE_PREFIX = "OW_Server_Lock"

def load_ips_from_file():
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ips.json")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        messagebox.showerror("File Error", f"Cannot find file or ips.json is malformed:\n{e}")
        sys.exit(1)

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

            result = ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, cmd_args, None, 1)
            if result <= 32:
                sys.exit(0)
            sys.exit(0)
        except:
            sys.exit(1)

def run_powershell(command):
    try:
        res = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command],
            capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW
        )
        return res.returncode == 0, res.stderr
    except Exception as e:
        return False, str(e)

def remove_rule():
    # Remove all rules that start with OW_Server_Lock
    cmd = f'Remove-NetFirewallRule -DisplayName "{RULE_PREFIX}*" -ErrorAction SilentlyContinue'
    run_powershell(cmd)

def lock_server(target_region):
    try:
        status_label.configure(text=f"Status: Applying {target_region}...", text_color="#AAAAAA")
        app.update()
        
        # 1. Remove existing old rules first
        remove_rule()
        
        # 2. If "Default" is selected, just remove the rules and finish
        if target_region == "Default":
            status_label.configure(text="Status: Default Matchmaking (Success!)", text_color="#00FF00")
            return
            
        # 3. Load all IP addresses
        data = load_ips_from_file()
        block_list = []
        
        # 4. Collect IPs from every region except the selected one and Blizzard_Global
        for region, ips in data.items():
            if region != target_region and region != "Blizzard_Global":
                block_list.extend(ips)
                
        if not block_list:
            messagebox.showwarning("Warning", "No IPs found to block")
            return

        # 5. Block all the remaining IPs; name the rule after the chosen server
        rule_name = f"{RULE_PREFIX}_{target_region}"
        ps_ip_array = "@(" + ",".join([f"'{ip}'" for ip in block_list]) + ")"
        cmd = f'New-NetFirewallRule -DisplayName "{rule_name}" -Direction Outbound -Action Block -RemoteAddress {ps_ip_array} -Protocol UDP | Out-Null'

        success, error_msg = run_powershell(cmd)

        if success:
            # Notify success status at the top
            status_label.configure(text=f"Status: Locked to {target_region} (Success!)", text_color="#00FF00")
        else:
            status_label.configure(text="Status: Failed to Apply", text_color="#FF0000")
            messagebox.showerror("Error", f"Firewall Error:\n{error_msg}")
            
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred:\n{str(e)}")

# --- GUI Setup ---
if __name__ == "__main__":
    check_admin_privileges()

    try:
        app = ctk.CTk()
        app.title("OW Server Selector")
        # Adjust window height slightly to fit the increased number of buttons
        app.geometry("320x580") 
        app.resizable(False, False)
        app.configure(fg_color="#0D0D0D")

        # Title
        title_label = ctk.CTkLabel(app, text="OVERWATCH", font=("Segoe UI", 20, "bold"), text_color="#FFFFFF")
        title_label.pack(pady=(25, 2))
        
        subtitle_label = ctk.CTkLabel(app, text="SERVER SELECTOR", font=("Segoe UI", 12), text_color="#AAAAAA")
        subtitle_label.pack(pady=(0, 10))

        # Status label at the top
        status_label = ctk.CTkLabel(app, text="Status: Ready", font=("Segoe UI", 12, "bold"), text_color="#FFFFFF")
        status_label.pack(pady=(0, 15))

        # Button style: white background, black text
        btn_kwargs = {
            "font": ("Segoe UI", 14, "bold"),
            "fg_color": "#FFFFFF",
            "text_color": "#000000",
            "hover_color": "#CCCCCC",
            "corner_radius": 4,
            "width": 200,
            "height": 35
        }

        # Server list generated from the JSON data
        regions = ["Japan", "Singapore", "Korea", "Taiwan", "Australia", "Americas", "Netherlands"]
        for region in regions:
            btn = ctk.CTkButton(app, text=region, command=lambda r=region: lock_server(r), **btn_kwargs)
            btn.pack(pady=5)

        # Divider line
        divider = ctk.CTkFrame(app, height=1, width=200, fg_color="#333333")
        divider.pack(pady=15)

        # Default button: black background with white border
        btn_default = ctk.CTkButton(app, text="Default", command=lambda: lock_server("Default"),
                                    font=("Segoe UI", 14, "bold"), fg_color="#0D0D0D", text_color="#FFFFFF",
                                    hover_color="#1A1A1A", border_width=1, border_color="#FFFFFF",
                                    corner_radius=4, width=200, height=35)
        btn_default.pack(pady=5)

        # Check readiness when the program starts
        load_ips_from_file()

        app.mainloop()
    except Exception as fatal_err:
        ctypes.windll.user32.MessageBoxW(0, f"Fatal GUI Error:\n{traceback.format_exc()}", "Application Crash", 0x10)