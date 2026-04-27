from littlefs import LittleFS
import os

fs = LittleFS(block_size=4096, block_count=512)

for filename in os.listdir("src"):
    filepath = os.path.join("src", filename)
    if os.path.isfile(filepath):
        with open(filepath, "rb") as f:
            content = f.read()
        with fs.open(filename, "wb") as f:
            f.write(content)
        print(f"  + {filename}")

with open("fs.bin", "wb") as f:
    f.write(fs.context.buffer)

print("fs.bin atualizado com sucesso!")