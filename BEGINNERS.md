# Stock Repo Search — complete beginner guide

You do **not** need to know Python to use this tool.

Think of Python as an engine, the terminal as a text remote control, and Streamlit as a website that runs on your computer. You will type a few commands once. After that you click buttons in a browser.

This guide assumes a home Windows or Mac computer.

---

## 1. The words you will see

| Word | Plain meaning |
|---|---|
| Terminal / PowerShell / Command Prompt | A window where you type commands instead of clicking |
| Python | A programming language. Here it just runs the app |
| Package / library | Extra Python parts someone else already wrote (Streamlit, pandas) |
| Virtual environment (`.venv`) | A private folder so this project’s tools do not mix with other software |
| GitHub | A website that stores project files |
| Token | A password that lets the app ask GitHub for search results |
| Streamlit | Turns our Python files into a web page on your computer |

A command is just a sentence the computer understands. Press **Enter** after each one.

---

## 2. Install Python

### Windows

1. Open https://www.python.org/downloads/
2. Click the big yellow **Download Python** button.
3. Run the installer.
4. **Important:** check the box **Add python.exe to PATH** at the bottom of the first screen.
5. Click **Install Now**.
6. When it finishes, close the installer.

### Mac

1. Open https://www.python.org/downloads/
2. Download the macOS installer and run it.
3. Click through with the defaults.

If you already have Python from school or work, you can skip this section.

---

## 3. Open a terminal

### Windows

1. Click the Start menu.
2. Type `PowerShell`.
3. Open **Windows PowerShell**.

A dark or light window with a blinking cursor appears. That is your terminal.

### Mac

1. Press Command + Space.
2. Type `Terminal`.
3. Press Enter.

---

## 4. Check that Python works

Type this and press Enter:

```text
python --version
```

Good answer: something like `Python 3.12.4` or `Python 3.13.1`.

If Windows says `python` is not recognized, try:

```text
py --version
```

If that works, use `py` everywhere this guide says `python`.

On some Macs you need:

```text
python3 --version
```

If that works, use `python3` everywhere this guide says `python`.

---

## 5. Get the project files (easiest: ZIP)

You do not need Git for the first run.

1. Open https://github.com/pwilly5876-lgtm/stock-repo-search
2. Click the green **Code** button.
3. Click **Download ZIP**.
4. Unzip the file. On Windows, right-click the ZIP → **Extract All**.
5. You should now have a folder named `stock-repo-search-main`.
6. Move that folder somewhere easy, such as your Documents folder.

---

## 6. Point the terminal at that folder

The terminal only sees the folder you tell it to use. That command is `cd`, short for “change directory.”

### Windows example

If the folder is in Documents:

```text
cd $env:USERPROFILE\Documents\stock-repo-search-main
```

### Mac example

```text
cd ~/Documents/stock-repo-search-main
```

Then check that you are in the right place:

```text
ls
```

On Windows PowerShell, `ls` also works. You should see names like `app.py`, `requirements.txt`, and `README.md`.

If you see “cannot find path,” the folder name or location is different. In File Explorer / Finder, open the folder, copy the path from the address bar, and use:

**Windows**

```text
cd "C:\Users\YourName\Documents\stock-repo-search-main"
```

**Mac**

```text
cd "/Users/YourName/Documents/stock-repo-search-main"
```

Keep the quotes if the path has spaces.

---

## 7. Create a private workspace for this app

Still in that folder, run:

```text
python -m venv .venv
```

Nothing flashy happens. That is normal. You just created a hidden folder named `.venv`.

Turn it on:

**Windows PowerShell**

```text
.\.venv\Scripts\Activate.ps1
```
