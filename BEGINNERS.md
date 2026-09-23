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
| Virtual environment (`.venv`) | A private folder so this project's tools do not mix with other software |
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
4. Unzip the file. On Windows, right-click the ZIP then Extract All.
5. You should now have a folder named `stock-repo-search-main`.
6. Move that folder somewhere easy, such as your Documents folder.

---

## 6. Point the terminal at that folder

The terminal only sees the folder you tell it to use. That command is `cd`, short for change directory.

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

If you see cannot find path, the folder name or location is different. In File Explorer / Finder, open the folder, copy the path from the address bar, and use:

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
.\ .venv\Scripts\Activate.ps1
```

Wait, use this exact command instead:

```text
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks that, run this once, then try Activate again:

```text
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

**Mac**

```text
source .venv/bin/activate
```

On Windows Command Prompt (not PowerShell):

```text
.venv\Scripts\activate
```

You will know it worked if the line starts with `(.venv)`.

---

## 8. Install the app extra parts

```text
python -m pip install -r requirements.txt
```

This downloads Streamlit and pandas. The first time can take a minute. Wait until the prompt comes back.

If pip complains about permissions, you are probably not inside `(.venv)`. Go back to step 7.

---

## 9. Start the website on your computer

```text
python -m streamlit run app.py
```

You should see text like You can now view your Streamlit app. Your browser often opens by itself.

If it does not, open a browser and go to:

```text
http://localhost:8501
```

localhost means this computer, not the public internet.

Leave the terminal window open while you use the app. Closing it shuts the page off.

To stop the app later, click the terminal and press Ctrl+C.

---

## 10. Create a GitHub token (needed for good search results)

GitHub limits anonymous searches. A token is a special password for programs.

1. Sign in at https://github.com
2. Open https://github.com/settings/tokens
3. Click Tokens (classic) if you see that option.
4. Click Generate new token, then Generate new token (classic).
5. Note: `Stock repo search`
6. Expiration: 90 days is fine while you learn.
7. Check the box `public_repo` (or `repo` if you only see that).
8. Click Generate token.
9. Copy the token now. GitHub will not show it again.
10. Keep it private, like a password. Do not paste it into chat or commit it to GitHub.

In the Streamlit sidebar, paste the token into Personal access token. You should see Token loaded for this session.

---

## 11. Use the three tabs

### Repository search

1. Pick a preset, such as `us` or `analysis`.
2. Leave Language on `python` unless you have a reason to change it.
3. Click Search repositories.
4. Click a GitHub link to open that project.

### Code search

This is the special part. It finds projects whose code imports libraries, not just projects that mention stocks in a description.

1. Choose yfinance + TA-Lib.
2. Click Search source code.
3. Open a matching repo, then open one of the listed files.

### Curated starter list

A short list of well-known finance projects if you do not want to search yet.

---

## 12. Next time you want to open the app

You do not install Python again. You only repeat the go to folder, turn workspace on, start app steps.

**Windows PowerShell**

```text
cd $env:USERPROFILE\Documents\stock-repo-search-main
.\.venv\Scripts\Activate.ps1
python -m streamlit run app.py
```

**Mac**

```text
cd ~/Documents/stock-repo-search-main
source .venv/bin/activate
python -m streamlit run app.py
```

---

## 13. If something goes wrong

**python is not recognized**
Python is not on PATH. Re-run the Python installer and check Add python.exe to PATH, or use `py` on Windows / `python3` on Mac.

**cannot find path after cd**
The folder is not where that command thinks it is. Find `app.py` in File Explorer / Finder and copy the real path.

**Activation is blocked on Windows**
Run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, then activate again.

**No module named streamlit**
The virtual environment is not active, or you skipped pip install. Look for `(.venv)` at the start of the line.

**The web page says GitHub API error 403 or 401**
The token is missing, expired, or mistyped. Create a new token and paste it again.

**Code search returns nothing**
Add the token. Code search almost never works without one.

**The browser page is blank**
Confirm the terminal is still running streamlit and visit http://localhost:8501

---

## 14. What you can ignore for now

You can skip these until you are curious:

- writing Python yourself
- Git commands (git clone, git pull)
- the CLI file stock_repo_search.py
- virtualenv theory

Those are useful later. They are not required to search for stock-analysis repositories today.
