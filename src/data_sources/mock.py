from typing import List
from ..models import Player


def fetch_players_for_week(week: int = None) -> List[Player]:
    # Small mock slate with made-up salaries and projections for testing
    sample = [
        Player(id="QB1", name="Quarterback One", position="QB", team="NE", opponent="NYJ", proj=22.5, salary=8500),
        Player(id="QB2", name="Quarterback Two", position="QB", team="KC", opponent="DEN", proj=20.0, salary=8300),
        Player(id="RB1", name="Running Back A", position="RB", team="DAL", opponent="PHI", proj=18.0, salary=7600),
        Player(id="RB2", name="Running Back B", position="RB", team="GB", opponent="MIN", proj=15.0, salary=7000),
        Player(id="RB3", name="Running Back C", position="RB", team="TEN", opponent="HOU", proj=12.0, salary=6200),
        Player(id="WR1", name="Wideout A", position="WR", team="GB", opponent="MIN", proj=17.0, salary=7400),
        Player(id="WR2", name="Wideout B", position="WR", team="KC", opponent="DEN", proj=16.0, salary=7200),
        Player(id="WR3", name="Wideout C", position="WR", team="NE", opponent="NYJ", proj=14.0, salary=6800),
        Player(id="TE1", name="Tight End One", position="TE", team="KC", opponent="DEN", proj=10.0, salary=5000),
        Player(id="TE2", name="Tight End Two", position="TE", team="DAL", opponent="PHI", proj=8.0, salary=4200),
        Player(id="FLEX_RB", name="Flex RB", position="RB", team="MIA", opponent="BUF", proj=9.0, salary=4500),
        Player(id="DST1", name="Defense Team 1", position="DST", team="NE", opponent="NYJ", proj=7.0, salary=3500, is_dst=True),
        Player(id="DST2", name="Defense Team 2", position="DST", team="KC", opponent="DEN", proj=6.0, salary=3000, is_dst=True),
    ]
    return sample
