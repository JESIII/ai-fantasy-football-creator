# Overwrite malformed file: ensure project root is on sys.path then import src
import os
import sys

# Ensure repo root is on sys.path so `src` package can be imported during tests
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.data_sources import mock
from src.optimizer import generate_n_lineups, lineup_salary, lineup_proj


def test_generate_three_lineups():
    players = mock.fetch_players_for_week()
    lineups = generate_n_lineups(players, n=3)
    assert len(lineups) == 3
    for lu in lineups:
        assert lineup_salary(lu) <= 50000
        assert abs(lineup_proj(lu)) >= 0

