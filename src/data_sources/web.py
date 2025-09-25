import csv
from io import StringIO
from typing import List, Optional
import requests
from bs4 import BeautifulSoup

from ..models import Player


def _parse_salary_csv(csv_text: str) -> List[Player]:
    players = []
    reader = csv.DictReader(StringIO(csv_text))
    for r in reader:
        try:
            name = r.get('Name') or r.get('name')
            salary = int(r.get('Salary') or r.get('salary') or 0)
            position = (r.get('Position') or r.get('position') or '').upper()
            team = (r.get('Team') or r.get('team') or '').upper()
            pid = f"CSV_{team}_{name.replace(' ','_')}"
            players.append(Player(id=pid, name=name, position=position, team=team, opponent=None, proj=0.0, salary=salary, is_dst=(position=='DST')))
        except Exception:
            continue
    return players


def fetch_players_for_week(week: Optional[int] = None, salary_csv_url: Optional[str] = None) -> List[Player]:
    """Attempt to fetch players for the week.

    This function is intentionally conservative: it will try to fetch a salary CSV if provided. If not, it attempts to scrape a simple public scoreboard for team matchups and creates placeholder players. Real production usage should use an official API.
    """
    players: List[Player] = []

    if salary_csv_url:
        try:
            r = requests.get(salary_csv_url, timeout=10)
            r.raise_for_status()
            players = _parse_salary_csv(r.text)
            if players:
                return players
        except Exception:
            # ignore and fallback
            pass

    # Fallback: scrape NFL.com scoreboard to get teams for the week and create placeholder DST players
    try:
        url = 'https://www.nfl.com/schedules/'
        if week:
            url += f'{week}'
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'html.parser')
        # Find team abbreviations in schedule (best-effort)
        teams = set()
        for a in soup.select('abbr'):
            txt = a.get_text(strip=True)
            if len(txt) <= 3:
                teams.add(txt.upper())

        # Create placeholder DST entries and a handful of generic players
        for t in list(teams)[:16]:
            pid = f'DST_{t}'
            players.append(Player(id=pid, name=f'DST {t}', position='DST', team=t, opponent=None, proj=6.0, salary=3500, is_dst=True))

        # Add a few placeholder skill players per team
        for t in list(teams)[:8]:
            players.append(Player(id=f'QB_{t}', name=f'QB {t}', position='QB', team=t, opponent=None, proj=18.0, salary=7000))
            players.append(Player(id=f'RB_{t}_1', name=f'RB1 {t}', position='RB', team=t, opponent=None, proj=12.0, salary=6000))
            players.append(Player(id=f'WR_{t}_1', name=f'WR1 {t}', position='WR', team=t, opponent=None, proj=14.0, salary=6500))

    except Exception:
        # As a final fallback, return an empty list which will be handled by the caller
        return []

    return players
