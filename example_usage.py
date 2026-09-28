from client import PercolatorTransactionEngine

tx = PercolatorTransactionEngine()
s_ts = tx.get_ts()
primary = ("user:101", "balance")
secondary = ("user:102", "balance")
writes = {primary: 500, secondary: 250}

ok, msg = tx.prewrite(primary, [secondary], writes, s_ts)
print("Prewrite status:", ok, msg)

c_ts = tx.get_ts()
ok, msg = tx.commit(primary, [secondary], s_ts, c_ts)
print("Commit status:", ok, msg)

print("Snapshot read user:101 at c_ts:", tx.read_snapshot("user:101", "balance", c_ts))
print("Snapshot read user:102 at c_ts:", tx.read_snapshot("user:102", "balance", c_ts))
