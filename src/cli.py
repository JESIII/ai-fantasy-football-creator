import argparse
import sys
from pathlib import Path
from .data_sources import mock
from .data_sources import web as web_source
from .data_sources import fftoolbox
from .optimizer import generate_n_lineups, lineup_salary, lineup_proj


def _ask_user_for_csv_via_dialog(prompt: str) -> str:
    """Open a simple file dialog for the user to pick a CSV file. Returns the selected path or empty string."""
    try:
        # Use tkinter file dialog
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        path = filedialog.askopenfilename(title=prompt, filetypes=[('CSV files', '*.csv'), ('All files', '*.*')])
        root.destroy()
        return path or ''
    except Exception:
        # Fallback: ask for path on stdin
        print(prompt)
        return input('Path to CSV: ').strip()


def main():
    parser = argparse.ArgumentParser(description="DraftKings Classic lineup generator (prototype)")
    parser.add_argument('--source', choices=['mock','web','fftoolbox'], default='mock', help='Data source to use')
    parser.add_argument('--count', type=int, default=5, help='Number of lineups to generate')
    parser.add_argument('--salary-url', type=str, default=None, help='Optional CSV URL with salary data (Name,Salary,Position,Team)')
    parser.add_argument('--week', type=int, default=None, help='Week number (optional for some sources)')
    parser.add_argument('--data-url', type=str, default=None, help='Data URL for specific sources (e.g., fftoolbox page)')
    parser.add_argument('--overlap-max', type=int, default=None, help='Maximum allowed overlap (shared players) with previous lineups')
    parser.add_argument('--team-max', type=int, default=3, help='Maximum teammates from same NFL team in a lineup')
    parser.add_argument('--prefer-qb-wr-stack', action='store_true', help='Prefer QB-WR stacking (if QB selected, require at least one WR from same team)')
    parser.add_argument('--stack-penalty', type=float, default=0.0, help='Penalty applied per QB without WR from same team (soft stack)')
    parser.add_argument('--avg-overlap-max', type=float, default=None, help='Maximum average overlap across generated set')
    parser.add_argument('--preset', type=str, default=None, choices=['default','heavy_stacking','contrarian','cash'], help='Strategy preset')
    parser.add_argument('--gui', action='store_true', help='Launch the GUI')
    args = parser.parse_args()

    if args.gui:
        # Lazy import to avoid tkinter requirement on CLI-only runs
        from .gui import launch_gui
        launch_gui()
        return

    if args.source == 'mock':
        players = mock.fetch_players_for_week()
    elif args.source == 'web':
        players = web_source.fetch_players_for_week(week=args.week, salary_csv_url=args.salary_url)
    elif args.source == 'fftoolbox':
        # Prefer a provided URL (data_url or salary_url). If none provided, instruct the user to download
        # the CSV from the FFToolbox page and select it via a file picker.
        fft_url = 'https://fftoolbox.fulltimefantasy.com/football/draftkings-fulltimefantasy-scores.php'
        if args.data_url or args.salary_url:
            url = args.data_url or args.salary_url
            # If URL points to a CSV file, try parsing it directly; otherwise try to fetch/parse the page
            if str(url).lower().endswith('.csv'):
                players = fftoolbox.parse_csv_file(url) if Path(url).exists() else fftoolbox.fetch_players_from_page(url)
            else:
                players = fftoolbox.fetch_players_from_page(url)
        else:
            print('\nPlease download the CSV from FFToolbox using this link:')
            print(f'{fft_url}\n')
            print('When the CSV is downloaded, select it in the file picker.')
            csv_path = _ask_user_for_csv_via_dialog('Select the FFToolbox CSV file you downloaded')
            if not csv_path:
                raise SystemExit('No CSV selected; aborting')
            players = fftoolbox.parse_csv_file(csv_path)
    else:
        raise SystemExit('Unknown source')

    # Apply preset adjustments
    preset_map = {
        'default': {},
        'heavy_stacking': {'prefer_qb_wr_stack': True, 'team_max': 4, 'stack_penalty': 0.0},
        'contrarian': {'overlap_max': 3, 'team_max': 2, 'stack_penalty': 5.0},
        'cash': {'overlap_max': 5, 'team_max': 3, 'stack_penalty': 1.0},
    }
    preset_opts = preset_map.get(args.preset) or {}

    # Merge CLI args with preset (CLI wins)
    stack_penalty = args.stack_penalty if args.stack_penalty is not None and args.stack_penalty > 0 else preset_opts.get('stack_penalty', 0.0)
    overlap = args.overlap_max if args.overlap_max is not None else preset_opts.get('overlap_max')
    team_max = args.team_max if args.team_max is not None else preset_opts.get('team_max')
    prefer_stack = args.prefer_qb_wr_stack or preset_opts.get('prefer_qb_wr_stack', False)

    lineups = generate_n_lineups(
        players,
        n=args.count,
        overlap_max=overlap,
        team_max=team_max,
        prefer_qb_wr_stack=prefer_stack,
        stack_penalty=stack_penalty,
        avg_overlap_max=args.avg_overlap_max,
    )

    for i, lu in enumerate(lineups, start=1):
        print(f"\nLineup {i}: proj={lineup_proj(lu):.2f} salary={lineup_salary(lu)}")
        for p in sorted(lu.values(), key=lambda x: x.position):
            print(f"  {p.position} - {p.name} ({p.team}) ${p.salary} proj:{p.proj}")


if __name__ == '__main__':
    main()
