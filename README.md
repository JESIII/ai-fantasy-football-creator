AI Fantasy Football Creator

This project contains a DraftKings Classic NFL lineup generator prototype.

Features
- Mock data source (for development and testing)
- Optimizer that generates lineups respecting DraftKings Classic roster rules and salary cap
- CLI to generate lineups
- Unit test for the optimizer

How to run (Windows PowerShell)

1. Create a venv and activate it

```powershell
python -m venv .venv
AI Fantasy Football Creator

This project contains a DraftKings Classic NFL lineup generator prototype.

Features
- Mock data source (for development and testing)
- Optimizer that generates lineups respecting DraftKings Classic roster rules and salary cap
- CLI to generate lineups
- Unit test for the optimizer

Setup (Windows PowerShell)

1. Create a virtual environment and install dependencies

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Using the FFToolbox CSV (recommended)

1. Download the DraftKings CSV from FFToolbox (the site provides a CSV downloader). Example page:

	https://fftoolbox.fulltimefantasy.com/football/draftkings-fulltimefantasy-scores.php?dgi=134308

2. Run the CLI and either let the tool open a file picker or pass the CSV path directly.

	- Let the CLI open a file picker (recommended):

	```powershell
	python -m src.cli --source fftoolbox --count 5
	# The CLI will print the FFToolbox link and open a file chooser for the CSV you downloaded.
	```

	- Or pass the CSV path directly:

	```powershell
	python -m src.cli --source fftoolbox --salary-url "C:\path\to\Draftkings Salary and FullTime Score as of 09-25-2025.csv" --count 5
	```

Notes about the CSV
- The expected CSV columns (the parser looks for these) are: Contest, Pos, Team, Name, Salary, Game Info, Proj, FullTime Score
- Example rows:

  Contest,Pos,Team,Name,Salary,Game Info,Proj,FullTime Score
  Main Slate,RB,SF,Christian McCaffrey,8500,JAX@SF 4:05 PM ET,26.8,3.15
  Main Slate,RB,ATL,Bijan Robinson,8200,WAS@ATL 1:00 PM ET,22.7,2.77

CLI options
- --source: data source (mock, web, fftoolbox)
- --count: how many lineups to generate
- --salary-url: optional CSV path or URL for salary/projection data
- --data-url: optional URL for web sources

Examples

- Generate 3 lineups from the provided local FFToolbox CSV:

```powershell
python -m src.cli --source fftoolbox --salary-url "g:\Repos\ai-fantasy-football-creator\data\Draftkings Salary and FullTime Score as of 09-25-2025.csv" --count 3
```

Troubleshooting
- If the CLI can't find or parse the CSV, verify the CSV has the required headers and is UTF-8 encoded.
- If tkinter file picker doesn't open on your system, pass the CSV path using `--salary-url`.

Warnings
- This is a prototype. For production, integrate an official data feed and add error handling, rate limiting, and logging.
- Respect the terms of service of any website or data provider; prefer official APIs or paid data providers.

Next steps (suggestions)
- Add overlap/variance constraints to the optimizer to produce diversified lineups
- Export lineups in DraftKings upload-friendly CSV format
- Add a small GUI for one-click CSV select + lineup generation

If you'd like, I can implement any of the next steps above—tell me which one to prioritize.
