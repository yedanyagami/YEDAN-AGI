"""
SECRET SENTINEL 🔒
Scans the codebase for high-entropy strings and potentially hardcoded secrets.
"""
import os
import re
import sys
import math

# Keywords that suggest a secret might be nearby
SUSPICIOUS_KEYWORDS = [
    "api_key", "apikey", "secret", "token", "password", "passwd", "pwd", "private_key", "auth"
]

# Regex for common secret patterns (e.g., long hex strings, AWS keys)
PATTERNS = {
    "Generic High Entropy": r'(["\'])[a-zA-Z0-9]{20,}(["\'])',
    "Slack Token": r'xox[baprs]-([0-9a-zA-Z]{10,48})',
    "AWS Access Key": r'AKIA[0-9A-Z]{16}',
    "Google API Key": r'AIza[0-9A-Za-z\\-_]{35}',
    "Private Key": r'-----BEGIN PRIVATE KEY-----'
}

def shannon_entropy(data):
    """Calculate Shannon entropy of string."""
    if not data:
        return 0
    entropy = 0
    for x in range(256):
        p_x = float(data.count(chr(x))) / len(data)
        if p_x > 0:
            entropy += - p_x * math.log(p_x, 2)
    return entropy

def scan_file(filepath):
    """Scans a single file for secrets."""
    issues = []
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            
        for i, line in enumerate(lines):
            # Check for suspicious keywords
            for kw in SUSPICIOUS_KEYWORDS:
                if kw in line.lower() and "=" in line and "os.getenv" not in line and "config" not in line.lower():
                    # It has a keyword, an assignment, and isn't loading from env/config
                    # Check entropy of the value
                    parts = line.split("=")
                    if len(parts) > 1:
                        val = parts[1].strip().strip('"').strip("'")
                        if len(val) > 10 and shannon_entropy(val) > 4.5:
                             issues.append(f"Line {i+1}: Potential hardcoded {kw} (High Entropy)")

            # Check for regex patterns
            for name, pattern in PATTERNS.items():
                if re.search(pattern, line):
                    # Exclude common false positives
                    if "EXAMPLE" not in line and "TODO" not in line:
                         issues.append(f"Line {i+1}: Matched {name}")
                         
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        
    return issues

def main():
    print("[Scan] Starting Secret Sentinel Scan...")
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    found_secrets = False
    
    for root, dirs, files in os.walk(root_dir):
        if ".git" in dirs:
            dirs.remove(".git")
        if "__pycache__" in dirs:
            dirs.remove("__pycache__")
        if "node_modules" in dirs:
            dirs.remove("node_modules")
            
        for file in files:
            if file.endswith((".py", ".json", ".md", ".env")) and not file.endswith("scan_secrets.py"):
                path = os.path.join(root, file)
                issues = scan_file(path)
                if issues:
                    print(f"\n[File] {file}:")
                    for issue in issues:
                        print(f"   [!]  {issue}")
                        found_secrets = True

    if found_secrets:
        print("\n[ALERT] POTENTIAL SECRETS DETECTED! Review above.")
        # sys.exit(1) # Don't crash the build for now, just warn
    else:
        print("\n[OK] Clean Audit. No obvious secrets found.")

if __name__ == "__main__":
    main()
