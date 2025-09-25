AI Fantasy Football Creator
==========================

A small DraftKings Classic NFL lineup generator prototype.

What this repo provides
- An integer-programming-based optimizer (PuLP) that builds DraftKings Classic lineups.
- Parsers for FFToolbox CSVs and a small web fallback.
- A CLI and a minimal Tkinter GUI for selecting a CSV and generating lineups.
- A unit test for the optimizer (pytest).

Quick setup (Windows PowerShell)

1) Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2) Install dependencies

```powershell
pip install -r requirements.txt
```

Data source (FFT oolbox CSV)

This tool expects a DraftKings salary/projection CSV exported from FFToolbox (or a similar source). Example FFToolbox page:

https://fftoolbox.fulltimefantasy.com/football/draftkings-fulltimefantasy-scores.php

The parser looks for common headers such as: Contest, Pos, Team, Name, Salary, Game Info, Proj.

CLI usage

- Generate 3 lineups by selecting the FFToolbox CSV via a file picker:

```powershell
python -m src.cli --source fftoolbox --count 3
```

- Or pass a local CSV path directly:

```powershell
python -m src.cli --source fftoolbox --salary-url "g:\Repos\ai-fantasy-football-creator\data\Draftkings Salary and FullTime Score as of 09-25-2025.csv" --count 3
```

- Common CLI options:
	- --count N (how many lineups)
	- --overlap-max N (max shared players with previous lineups)
	- --team-max N (max teammates from same NFL team)
	- --stack-penalty N (soft penalty for QB without same-team WR)
	- --preset <default|heavy_stacking|contrarian|cash>
	- --gui (launch the GUI)

Run the GUI

Start the Tkinter GUI:

```powershell
python -m src.gui
```

The GUI lets you browse to a downloaded FFToolbox CSV, tweak options (count, overlap, team max, stacking), generate lineups, and export results to a text file. There's also a "Download FFToolbox" button that opens the FFToolbox page in your browser.

Troubleshooting

- If you see "No module named tkinter", reinstall Python from python.org and ensure Tcl/Tk support is installed.
- If the CSV fails to parse, open it in Excel or a text editor and verify headers include Name, Pos, Team, Salary, Proj and is UTF-8 encoded.

License / Disclaimer

Use responsibly. Respect third-party site terms of service when using exported data.
Troubleshooting
- If the CLI can't find or parse the CSV, verify the CSV has the required headers and is UTF-8 encoded.
- If tkinter file picker doesn't open on your system, pass the CSV path using `--salary-url`.

Run the GUI (one-click)
-----------------------

If you prefer a simple graphical interface, a small Tkinter GUI is included. From the project root run:

```powershell
python -m src.gui
```

What the GUI does:
- Lets you browse to the FFToolbox CSV you downloaded (or click "Download FFToolbox" to open the page in your browser).
- Provides fields for count, overlap, team max, stack penalty and presets.
- Click "Generate" to produce lineups and "Export" to save them to a text file.

GUI troubleshooting
- If the GUI fails to start with "No module named tkinter", reinstall Python from python.org and ensure Tcl/Tk support is included.
