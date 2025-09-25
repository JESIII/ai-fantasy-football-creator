import tkinter as tk
from tkinter import filedialog, messagebox
import webbrowser
from typing import Optional
from .data_sources import fftoolbox
from .optimizer import generate_n_lineups, lineup_salary, lineup_proj


PRESET_CONFIGS = {
    'default': {},
    'heavy_stacking': {'stack_penalty': 0.0, 'prefer_qb_wr_stack': True, 'team_max': 4},
    'contrarian': {'overlap_max': 3, 'team_max': 2, 'stack_penalty': 5.0},
    'cash': {'overlap_max': 5, 'team_max': 3, 'stack_penalty': 1.0},
}


class DGKGui:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('DraftKings Lineup Generator')

        # CSV selection
        tk.Label(self.root, text='FFT toolbox CSV:').grid(row=0, column=0, sticky='w')
        self.csv_var = tk.StringVar()
        tk.Entry(self.root, textvariable=self.csv_var, width=60).grid(row=0, column=1)
        tk.Button(self.root, text='Browse', command=self.browse_csv).grid(row=0, column=2)
        tk.Button(self.root, text='Download FFToolbox', command=self.open_fft_link).grid(row=0, column=3)

        # Options
        tk.Label(self.root, text='Count:').grid(row=1, column=0, sticky='w')
        self.count_var = tk.IntVar(value=5)
        tk.Entry(self.root, textvariable=self.count_var, width=10).grid(row=1, column=1, sticky='w')

        tk.Label(self.root, text='Overlap max:').grid(row=2, column=0, sticky='w')
        self.overlap_var = tk.IntVar(value=5)
        tk.Entry(self.root, textvariable=self.overlap_var, width=10).grid(row=2, column=1, sticky='w')

        tk.Label(self.root, text='Team max:').grid(row=3, column=0, sticky='w')
        self.team_var = tk.IntVar(value=3)
        tk.Entry(self.root, textvariable=self.team_var, width=10).grid(row=3, column=1, sticky='w')

        tk.Label(self.root, text='Stack penalty:').grid(row=4, column=0, sticky='w')
        self.penalty_var = tk.DoubleVar(value=1.0)
        tk.Entry(self.root, textvariable=self.penalty_var, width=10).grid(row=4, column=1, sticky='w')

        tk.Label(self.root, text='Avg overlap max:').grid(row=5, column=0, sticky='w')
        self.avg_overlap_var = tk.DoubleVar(value=4.0)
        tk.Entry(self.root, textvariable=self.avg_overlap_var, width=10).grid(row=5, column=1, sticky='w')

        # Preset
        tk.Label(self.root, text='Preset:').grid(row=6, column=0, sticky='w')
        self.preset_var = tk.StringVar(value='default')
        tk.OptionMenu(self.root, self.preset_var, *PRESET_CONFIGS.keys()).grid(row=6, column=1, sticky='w')

        tk.Button(self.root, text='Generate', command=self.on_generate).grid(row=7, column=0)
        tk.Button(self.root, text='Export', command=self.on_export).grid(row=7, column=1)

        self.output = tk.Text(self.root, width=100, height=30)
        self.output.grid(row=8, column=0, columnspan=3)

        self.last_lineups = []

    def browse_csv(self):
        path = filedialog.askopenfilename(title='Select FFToolbox CSV', filetypes=[('CSV files', '*.csv')])
        if path:
            self.csv_var.set(path)

    def open_fft_link(self):
        """Open the FFToolbox download page in the user's default browser."""
        fft_url = 'https://fftoolbox.fulltimefantasy.com/football/draftkings-fulltimefantasy-scores.php'
        try:
            webbrowser.open(fft_url)
        except Exception:
            messagebox.showerror('Open browser', f'Could not open browser. Please visit:\n{fft_url}')

    def on_generate(self):
        csv_path = self.csv_var.get()
        if not csv_path:
            messagebox.showerror('No CSV', 'Please select the FFToolbox CSV first (download from the FFToolbox page).')
            return

        preset = PRESET_CONFIGS.get(self.preset_var.get(), {})
        # Read players
        players = fftoolbox.parse_csv_file(csv_path)
        if not players:
            messagebox.showerror('Parse error', 'Could not parse players from CSV. Check format and headers.')
            return

        # Merge preset with fields
        opts = {
            'n': int(self.count_var.get()),
            'overlap_max': int(self.overlap_var.get()),
            'team_max': int(self.team_var.get()),
            'stack_penalty': float(self.penalty_var.get()),
            'avg_overlap_max': float(self.avg_overlap_var.get()),
            'prefer_qb_wr_stack': preset.get('prefer_qb_wr_stack', False),
        }
        opts.update({k: v for k, v in preset.items() if v is not None})

        self.output.delete('1.0', tk.END)
        try:
            lineups = generate_n_lineups(
                players,
                n=opts['n'],
                overlap_max=opts.get('overlap_max'),
                team_max=opts.get('team_max'),
                prefer_qb_wr_stack=opts.get('prefer_qb_wr_stack', False),
                stack_penalty=opts.get('stack_penalty', 0.0),
                avg_overlap_max=opts.get('avg_overlap_max'),
            )
        except Exception as e:
            messagebox.showerror('Error', f'Error generating lineups: {e}')
            return

        self.last_lineups = lineups
        for i, lu in enumerate(lineups, start=1):
            self.output.insert(tk.END, f"Lineup {i}: proj={lineup_proj(lu):.2f} salary={lineup_salary(lu)}\n")
            for p in sorted(lu.values(), key=lambda x: x.position):
                self.output.insert(tk.END, f"  {p.position} - {p.name} ({p.team}) ${p.salary} proj:{p.proj}\n")
            self.output.insert(tk.END, "\n")

    def on_export(self):
        if not self.last_lineups:
            messagebox.showinfo('No lineups', 'No lineups to export; generate first')
            return
        path = filedialog.asksaveasfilename(defaultextension='.txt', filetypes=[('Text files', '*.txt'), ('CSV', '*.csv')])
        if not path:
            return
        with open(path, 'w', encoding='utf-8') as f:
            for i, lu in enumerate(self.last_lineups, start=1):
                f.write(f"Lineup {i}: proj={lineup_proj(lu):.2f} salary={lineup_salary(lu)}\n")
                for p in sorted(lu.values(), key=lambda x: x.position):
                    f.write(f"  {p.position} - {p.name} ({p.team}) ${p.salary} proj:{p.proj}\n")
                f.write('\n')
        messagebox.showinfo('Exported', f'Exported to {path}')

    def run(self):
        self.root.mainloop()


def launch_gui():
    app = DGKGui()
    app.run()


if __name__ == '__main__':
    launch_gui()
