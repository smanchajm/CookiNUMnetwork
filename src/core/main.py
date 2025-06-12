# src/core/main.py
import time

print("App is starting...")
with open("logs/cookinum.log", "w") as f:
    for i in range(5):
        f.write(f"Line {i+1}\n")
        f.flush()
        time.sleep(1)
print("App finished.")
