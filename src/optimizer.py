from typing import List, Dict, Tuple, Optional
from pulp import LpProblem, LpMaximize, LpVariable, lpSum, LpBinary, PULP_CBC_CMD
from .models import Player


DK_SALARY_CAP = 50000
ROSTER_REQUIREMENTS = {
    'QB': 1,
    'RB': 2,
    'WR': 3,
    'TE': 1,
    'FLEX': 1,  # FLEX can be RB/WR/TE
    'DST': 1,
}

FLEX_ELIGIBLE = {'RB', 'WR', 'TE'}


def _build_player_map(players: List[Player]) -> Dict[str, Player]:
    return {p.id: p for p in players}


def _validate_players(players: List[Player]):
    if not players:
        raise ValueError("No players provided")


def generate_n_lineups(
    players: List[Player],
    n: int = 5,
    salary_cap: int = DK_SALARY_CAP,
    overlap_max: Optional[int] = None,
    team_max: Optional[int] = 3,
    prefer_qb_wr_stack: bool = False,
    stack_penalty: float = 0.0,
    avg_overlap_max: Optional[float] = None,
) -> List[Dict[str, Player]]:
    """Generate n lineups sequentially using integer programming.

    Strategy: solve for best lineup, then add a cut constraint forbidding that exact lineup (force selection sum <= 8) to get a different lineup, repeat.
    """
    _validate_players(players)
    player_map = _build_player_map(players)
    lineups: List[Dict[str, Player]] = []
    used_lineups: List[set] = []  # store sets of player ids for exclusion

    # Precompute roster size
    total_required = (
        ROSTER_REQUIREMENTS['QB']
        + ROSTER_REQUIREMENTS['RB']
        + ROSTER_REQUIREMENTS['WR']
        + ROSTER_REQUIREMENTS['TE']
        + ROSTER_REQUIREMENTS['FLEX']
        + ROSTER_REQUIREMENTS['DST']
    )

    for iteration in range(n):
        prob = LpProblem(f"dk_opt_{iteration}", LpMaximize)
        x = {p.id: LpVariable(f"x_{p.id}", cat=LpBinary) for p in players}

        # Teams and helper binary vars
        teams = sorted({p.team for p in players if p.team})
        z_wr = {t: LpVariable(f"z_wr_{t}", cat=LpBinary) for t in teams}
        s_stack = {t: LpVariable(f"s_stack_{t}", cat=LpBinary) for t in teams}

        # Objective: maximize projected points minus stacking penalties
        prob += lpSum([p.proj * x[p.id] for p in players]) - stack_penalty * lpSum([s_stack[t] for t in teams])

        # Salary cap
        prob += lpSum([p.salary * x[p.id] for p in players]) <= salary_cap

        # Position constraints (explicit flex assignment)
        # QB and DST (use is_dst to be robust to position naming)
        prob += lpSum([x[p.id] for p in players if p.position == 'QB']) == ROSTER_REQUIREMENTS['QB']
        prob += lpSum([x[p.id] for p in players if getattr(p, 'is_dst', False)]) == ROSTER_REQUIREMENTS['DST']

        # Create flex-type binary vars: which position supplies the FLEX (RB/WR/TE)
        z_flex_rb = LpVariable('z_flex_rb', cat=LpBinary)
        z_flex_wr = LpVariable('z_flex_wr', cat=LpBinary)
        z_flex_te = LpVariable('z_flex_te', cat=LpBinary)
        # Exactly one of these equals the FLEX requirement (usually 1)
        prob += z_flex_rb + z_flex_wr + z_flex_te == ROSTER_REQUIREMENTS['FLEX']

        # Enforce exact counts for RB/WR/TE including the flex slot when assigned
        prob += lpSum([x[p.id] for p in players if p.position == 'RB']) == ROSTER_REQUIREMENTS['RB'] + z_flex_rb
        prob += lpSum([x[p.id] for p in players if p.position == 'WR']) == ROSTER_REQUIREMENTS['WR'] + z_flex_wr
        prob += lpSum([x[p.id] for p in players if p.position == 'TE']) == ROSTER_REQUIREMENTS['TE'] + z_flex_te

        # Total players must equal roster size (defensive count uses is_dst above)
        prob += lpSum([x[p.id] for p in players]) == total_required

        # Team stacking / exposure constraints
        if team_max is not None:
            for t in teams:
                prob += lpSum([x[p.id] for p in players if p.team == t]) <= team_max

        # Soft QB-WR stack handling: define z_wr and s_stack relations
        for t in teams:
            wr_ids = [p.id for p in players if p.team == t and p.position == 'WR']
            if wr_ids:
                for pid in wr_ids:
                    prob += z_wr[t] >= x[pid]
                prob += z_wr[t] <= lpSum([x[pid] for pid in wr_ids])
            else:
                prob += z_wr[t] == 0

            qb_ids = [p.id for p in players if p.team == t and p.position == 'QB']
            if qb_ids:
                prob += s_stack[t] >= lpSum([x[pid] for pid in qb_ids]) - z_wr[t]
                prob += s_stack[t] <= lpSum([x[pid] for pid in qb_ids])
                prob += s_stack[t] <= 1
            else:
                prob += s_stack[t] == 0

        # Exclude previously found exact lineups (force at least one different player)
        for used in used_lineups:
            prob += lpSum([x[player_id] for player_id in used]) <= total_required - 1

        # Overlap constraint vs previous lineups: limit number of shared players
        if overlap_max is not None:
            for used in used_lineups:
                prob += lpSum([x[player_id] for player_id in used]) <= overlap_max

        # Average pairwise overlap: ensure average overlap between this candidate and previous lineups <= avg_overlap_max
        if avg_overlap_max is not None and used_lineups:
            for_used = lpSum([lpSum([x[player_id] for player_id in used]) for used in used_lineups])
            prob += for_used <= avg_overlap_max * len(used_lineups)

        # Solve
        solver = PULP_CBC_CMD(msg=False)
        res = prob.solve(solver)

        # Check feasibility
        chosen = [p.id for p in players if x[p.id].value() == 1]
        if not chosen:
            break

        lineup_players = {pid: player_map[pid] for pid in chosen}
        lineups.append(lineup_players)
        used_lineups.append(set(chosen))

    return lineups


def lineup_salary(lineup: Dict[str, Player]) -> int:
    return sum(p.salary for p in lineup.values())


def lineup_proj(lineup: Dict[str, Player]) -> float:
    return sum(p.proj for p in lineup.values())
