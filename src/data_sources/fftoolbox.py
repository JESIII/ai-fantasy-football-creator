from typing import List
import re
import requests
from bs4 import BeautifulSoup
from io import StringIO
import csv

from ..models import Player


def _clean_name(name: str) -> str:
    return re.sub(r"\s+", " ", name).strip()


def _parse_csv_text(csv_text: str) -> List[Player]:
    players: List[Player] = []
    reader = csv.DictReader(StringIO(csv_text))
    for r in reader:
        # try common column names
        name = r.get('Player') or r.get('Name') or r.get('player') or r.get('name')
        salary = r.get('DK Salary') or r.get('Salary') or r.get('salary') or r.get('dk_salary') or r.get('Salary ($)')
        position = r.get('Pos') or r.get('Position') or r.get('pos')
        team = r.get('Team') or r.get('team') or r.get('Tm')
        proj = r.get('FPTS') or r.get('Proj') or r.get('Projection') or r.get('fpts') or r.get('proj')
        if not name:
            continue
        try:
            salary_val = int(re.sub(r'[^0-9]', '', salary)) if salary else 0
        except Exception:
            salary_val = 0
        try:
            proj_val = float(re.sub(r'[^0-9\.]', '', proj)) if proj else 0.0
        except Exception:
            proj_val = 0.0

        # Normalize position strings without truncating so we correctly detect DST/Def and other variants
        pos_raw = (position or '').strip().upper()
        if pos_raw.startswith('QB'):
            pos = 'QB'
        elif pos_raw.startswith('RB'):
            pos = 'RB'
        elif pos_raw.startswith('WR'):
            pos = 'WR'
        elif pos_raw.startswith('TE'):
            pos = 'TE'
        elif pos_raw.startswith('DEF') or pos_raw in ('DST', 'D/ST', 'D', 'DEFENSE', 'Def'):
            pos = 'DST'
        else:
            # fallback: take first two characters trimmed (but prefer full tokens above)
            pos = pos_raw[:3] if len(pos_raw) >= 3 else pos_raw

        pid = f"FT_{(team or '').upper()}_{_clean_name(name).replace(' ','_')}"
        players.append(Player(id=pid, name=_clean_name(name), position=pos, team=(team or '').upper(), opponent=None, proj=proj_val, salary=salary_val, is_dst=(pos == 'DST')))

    return players


def fetch_players_from_page(url: str) -> List[Player]:
    """Fetch an fftoolbox/fulltimefantasy page and try to extract a CSV of DraftKings salaries or parse an HTML table.

    Returns a list of Player objects. This is best-effort and tailored to the FFToolbox pages which often include a CSV download link.
    """
    players: List[Player] = []
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'html.parser')

        # Look for links that end with .csv or contain 'download'
        csv_link = None
        for a in soup.find_all('a', href=True):
            href = a['href']
            if '.csv' in href.lower() or 'download' in href.lower():
                csv_link = href
                break

        if csv_link:
            if not csv_link.startswith('http'):
                # make absolute
                from urllib.parse import urljoin

                csv_link = urljoin(url, csv_link)
            rr = requests.get(csv_link, timeout=15)
            rr.raise_for_status()
            players = _parse_csv_text(rr.text)
            if players:
                return players

        # Fallback: parse any table for headers like Player, Salary, Pos
        tables = soup.find_all('table')
        for table in tables:
            headers = [th.get_text(strip=True).lower() for th in table.find_all('th')]
            if any('salary' in h for h in headers) and any('player' in h or 'name' in h for h in headers):
                # parse rows
                rows = []
                for tr in table.find_all('tr'):
                    cols = [td.get_text(strip=True) for td in tr.find_all(['td','th'])]
                    if cols:
                        rows.append(cols)
                # first row headers
                if not rows:
                    continue
                hdr = [c.lower() for c in rows[0]]
                csv_buf = StringIO()
                writer = csv.writer(csv_buf)
                writer.writerow(rows[0])
                for rrow in rows[1:]:
                    writer.writerow(rrow)
                csv_buf.seek(0)
                players = _parse_csv_text(csv_buf.getvalue())
                if players:
                    return players

    except Exception:
        return []

    return players


def parse_csv_file(file_path: str) -> List[Player]:
    """Parse a local CSV file (downloaded from FFToolbox) into Player objects."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        return _parse_csv_text(text)
    except Exception:
        return []
