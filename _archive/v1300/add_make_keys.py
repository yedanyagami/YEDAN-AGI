import os

# Append Make.com keys to .env
with open(".env", "a", encoding="utf-8") as f:
    f.write("\nMAKE_WEBHOOK_URL=https://hook.us2.make.com/md8xg7xrl2hqfo3qtfgtylapxfumrftz\n")
    f.write("MAKE_KEY_CHAIN=r-7S6BAZe7GC3ex\n")

print("Added Make.com keys to .env")
