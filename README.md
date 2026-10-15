# FixMyMods

FixMyMods is a cross-platform desktop application that checks Minecraft logs
and crash reports for known mod problems. It currently recognizes explicit
reports of incompatible mods and missing mod dependencies. A clean result does
not guarantee that a log contains no problems; the rule set is intentionally
small and will grow over time.

## Features

- Open `latest.log` and text crash reports through a native file picker.
- View known diagnostics, explanations, suggested next steps, and the original
  matching log lines.
- Run on Windows, Linux (including Ubuntu and Arch Linux), and macOS.

## Requirements

- Python 3.10 or newer
- PySide6 6.6 or newer

PySide6 provides the same Qt-based interface on each supported operating
system. The steps below install the Python Qt wheels in an isolated virtual
environment, rather than relying on distribution-specific PySide packages.

### Windows

Install Python from [python.org](https://www.python.org/downloads/) and enable
the Python launcher during setup. In PowerShell, from the project directory:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
fixmymods
```

If PowerShell blocks activation, use Command Prompt and activate with
`.venv\Scripts\activate.bat`, or run `.venv\Scripts\python.exe -m fixmymods.main`
without activating the environment.

### Ubuntu

Install Python and virtual-environment support:

```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip
```

Then, from the project directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
fixmymods
```

### Arch Linux

Install Python and pip with pacman:

```bash
sudo pacman -S python python-pip
```

Then, from the project directory:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
fixmymods
```

### macOS

Install Python 3.10+ from [python.org](https://www.python.org/downloads/) or
with [Homebrew](https://brew.sh/):

```bash
brew install python
```

Then, from the project directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
fixmymods
```

On any platform, the application can also be started with
`python -m fixmymods.main` after installation.

## Run tests

With the development dependencies installed:

```bash
python -m pytest
```

## Build a standalone application

PyInstaller must build on the same operating system and CPU architecture that
the application targets. After installing the development dependencies, run
the following from the project directory:

```bash
pyinstaller --noconfirm --clean --windowed --onefile --name FixMyMods \
  --paths src tools/launch_gui.py
```

The executable is written to `dist/` (`FixMyMods.exe` on Windows). Build
separately on Windows, macOS, and Linux for native executables. A Linux build
made against an older glibc may run on newer Linux distributions, including
Arch Linux, but this is not guaranteed for every system; test the generated
application on the target distribution.

## Current limitations

- Only a small number of explicit loader messages are recognized.
- No automatic mod downloading or changes to the Minecraft installation are
  performed.
- Standalone binaries are built per operating system; the repository does not
  currently distribute signed installers.
