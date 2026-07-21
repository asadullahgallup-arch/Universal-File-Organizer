# Field Operations Toolkit

A Windows desktop application that organizes files from an Excel worksheet in a few clicks.

## What it does

1. Select the folder containing your files and a destination folder.
2. Select an Excel workbook, worksheet, and the column containing the file names.
3. Optionally choose up to five Excel columns to create the destination folder structure.
4. Choose exact, prefix, or contains matching, then copy or move the matching files.

The app produces a timestamped Excel report of copied, moved, missing, skipped, and failed rows. Existing destination files are never overwritten: a numbered suffix is added instead.

## Team-safe behavior

- Matching is case-insensitive, which suits normal Windows file workflows.
- Blank Excel file-name cells are skipped and recorded.
- Folder names generated from Excel are cleaned of invalid Windows characters.
- A destination inside the source folder is rejected to prevent accidental re-processing.
- Move mode now genuinely moves files; use Copy for a non-destructive first run.

## Run from source

Install Python 3.11 or newer, then run:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

## Build a Windows executable

```powershell
pip install pyinstaller
pyinstaller --noconfirm "Universal File Organizer.spec"
```

The distributable will be in `dist\Universal File Organizer`. Share the generated installer with teammates rather than only the internal `.exe` file.

## Build the setup installer locally

Install [Inno Setup](https://jrsoftware.org/isinfo.php), build the PyInstaller folder, then run:

```powershell
pyinstaller --noconfirm "Universal File Organizer.spec"
iscc installer.iss
```

The setup executable will be generated in `dist`. It creates a Start Menu entry, an optional desktop shortcut, and an uninstaller.

## Publish a team update through GitHub Releases

This project includes a GitHub Actions workflow that builds and attaches the Windows app whenever you publish a GitHub Release.

1. Create a **private** GitHub repository and upload this project.
2. On GitHub, open **Releases** → **Draft a new release**.
3. Create a tag that matches the version in `app/version.py`, for example `v1.0.2`.
4. Add short release notes and click **Publish release**.
5. Wait for the **Build Windows release** workflow to complete, then send teammates the ZIP attached to that release.

For every update, increase `APP_VERSION`, commit and push your code, then publish a new release tag. Team members can enable GitHub's release notifications by watching the repository and choosing **Custom** → **Releases**.

The app also checks GitHub automatically shortly after it opens and displays an update prompt when a newer published release exists. Teammates can use **Settings** → **Check for Updates** at any time. The button opens the newest release download; they should close the app and replace their existing installed application folder after downloading it.
