"""Percolator Distributed Transaction Protocol Engine.
100% Python Standard Library.
"""

import collections

class PercolatorTransactionEngine:
    """Percolator snapshot-isolated two-phase distributed transactions with primary locks."""
    def __init__(self):
        self.storage = collections.defaultdict(lambda: collections.defaultdict(lambda: {"data": {}, "lock": None, "write": {}}))
        self.cur_ts = 100

    def get_ts(self):
        self.cur_ts += 1
        return self.cur_ts

    def prewrite(self, primary_cell, secondary_cells, writes, start_ts):
        all_cells = [primary_cell] + secondary_cells
        p_row, p_col = primary_cell

        for r, c in all_cells:
            cell = self.storage[r][c]
            if any(commit_ts >= start_ts for commit_ts in cell["write"]):
                return False, f"Write conflict at ({r}, {c})"
            if cell["lock"] is not None:
                return False, f"Locked at ({r}, {c})"

        self.storage[p_row][p_col]["lock"] = (p_row, p_col, start_ts)
        self.storage[p_row][p_col]["data"][start_ts] = writes[primary_cell]

        for r, c in secondary_cells:
            self.storage[r][c]["lock"] = (p_row, p_col, start_ts)
            self.storage[r][c]["data"][start_ts] = writes[(r, c)]

        return True, "Prewrite OK"

    def commit(self, primary_cell, secondary_cells, start_ts, commit_ts):
        p_row, p_col = primary_cell
        p_cell = self.storage[p_row][p_col]

        if p_cell["lock"] != (p_row, p_col, start_ts):
            return False, "Primary lock missing or modified"
        p_cell["write"][commit_ts] = start_ts
        p_cell["lock"] = None

        for r, c in secondary_cells:
            s_cell = self.storage[r][c]
            s_cell["write"][commit_ts] = start_ts
            s_cell["lock"] = None

        return True, "Commit OK"

    def read_snapshot(self, row, col, snapshot_ts):
        cell = self.storage[row][col]
        valid_commits = [cts for cts in cell["write"] if cts <= snapshot_ts]
        if not valid_commits:
            return None
        latest_commit = max(valid_commits)
        start_ts = cell["write"][latest_commit]
        return cell["data"].get(start_ts)
