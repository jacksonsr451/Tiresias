import subprocess


def build():
    command = [
        "pyinstaller",
        "--onefile",
        "--noconfirm",
        "--windowed",
        "--name",
        "tiresias",
        "./tiresias/main.py",
    ]
    subprocess.run(command, check=True)


if __name__ == "__main__":
    build()
