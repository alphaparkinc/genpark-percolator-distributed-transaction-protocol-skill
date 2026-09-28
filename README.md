# Percolator Distributed Transaction Protocol Skill

Robust, zero-dependency Python implementation of Google's **Percolator Distributed Transaction Protocol** for snapshot-isolated ACID transactions built over distributed key-value storage.

## Features
- **Primary-Lock 2PC Protocol**: Atomicity anchored around a single designated primary cell lock.
- **Snapshot Isolation (SI)**: Eliminates dirty reads, non-repeatable reads, and phantom reads using monotonic timestamp ordering.
- **Zero External Dependencies**: 100% Python standard library.
- **Native MCP Protocol**: JSON-RPC 2.0 stdio server compatible with Claude Desktop, Cursor, and Windsurf.

## Architecture
```mermaid
sequenceDiagram
    participant Client
    participant PrimaryCell
    participant SecondaryCell
    participant TimestampOracle

    Client->>TimestampOracle: Request start_ts
    TimestampOracle-->>Client: start_ts = 101
    Client->>PrimaryCell: Prewrite (Lock primary + data@101)
    Client->>SecondaryCell: Prewrite (Lock pointing to primary + data@101)
    Client->>TimestampOracle: Request commit_ts
    TimestampOracle-->>Client: commit_ts = 102
    Client->>PrimaryCell: Commit (Write roll@102 -> 101, release lock)
    Client->>SecondaryCell: Asynchronous Commit Rollout
```
