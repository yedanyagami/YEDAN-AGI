import os
import sys
import subprocess
import platform
import socket

def print_header(title):
    print(f"\n{'='*10} [ {title} ] {'='*10}")

def get_command_output(command):
    try:
        return subprocess.check_output(command, shell=True, text=True, stderr=subprocess.STDOUT).strip()
    except subprocess.CalledProcessError:
        return "N/A (Command not found or failed)"
    except Exception as e:
        return f"Error: {e}"

def check_connection(host="8.8.8.8", port=53):
    try:
        socket.setdefaulttimeout(3)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return "[OK] Online"
    except Exception:
        return "[X] Offline"

def audit_system():
    print("RUNNING LEVIATHAN SYSTEM AUDIT PROTOCOL...")
    
    # 1. 核心環境 (Core Environment)
    print_header("CORE ENVIRONMENT")
    print(f"OS System:      {platform.system()} {platform.release()}")
    print(f"Machine:        {platform.machine()}")
    print(f"Python Ver:     {sys.version.split()[0]}")
    print(f"Python Path:    {sys.executable}")
    print(f"Work Dir:       {os.getcwd()}")
    print(f"Network Status: {check_connection()}")

    # 2. 軍火庫清單 (Pip Packages)
    print_header("PIP ARSENAL (INSTALLED LIBRARIES)")
    pip_list = get_command_output("pip list")
    # 只列出我們關心的關鍵庫
    key_packages = ["google-generativeai", "playwright", "requests", "python-dotenv", "flask", "numpy", "pandas"]
    print(f"{'Package':<25} {'Version'}")
    print("-" * 35)
    for line in pip_list.split('\n'):
        name = line.split()[0]
        if any(k in name.lower() for k in key_packages):
            print(line)
    
    # 3. 擴充功能偵測 (Extensions)
    print_header("ANTIGRAVITY EXTENSIONS")
    # 嘗試偵測 VS Code / Antigravity 擴充
    ext_list = get_command_output("code --list-extensions")
    if "N/A" in ext_list:
        # 如果 code 指令無法使用，嘗試讀取常見目錄 (Windows)
        print("[!] 'code' command not found. Checking typical directory...")
        vscode_dir = os.path.expanduser("~/.vscode/extensions")
        if os.path.exists(vscode_dir):
            extensions = [d for d in os.listdir(vscode_dir) if os.path.isdir(os.path.join(vscode_dir, d))]
            for ext in extensions[:10]: # 列出前10個
                print(f"- {ext}")
            if len(extensions) > 10: print(f"... and {len(extensions)-10} more.")
        else:
            print("[X] Cannot auto-detect extensions (CLI tools missing). Relying on manual inventory.")
    else:
        print(ext_list)

    # 4. 專案結構 (Project Map)
    print_header("PROJECT STRUCTURE")
    for root, dirs, files in os.walk("."):
        level = root.replace('.', '').count(os.sep)
        indent = ' ' * 4 * (level)
        print(f"{indent}[D] {os.path.basename(root)}/")
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            if f.endswith(".py") or f.endswith(".yml") or f.endswith(".env"):
                print(f"{subindent}[F] {f}")

    print("\n" + "="*40)
    print("[OK] SYSTEM AUDIT COMPLETE")
    print("="*40)

if __name__ == "__main__":
    audit_system()
