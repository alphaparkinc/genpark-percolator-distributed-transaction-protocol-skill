import sys
import json
from client import PercolatorTransactionEngine

engine = PercolatorTransactionEngine()

def handle_request(req):
    method = req.get("method")
    params = req.get("params", {})
    req_id = req.get("id")

    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": [
                    {
                        "name": "percolator_transaction",
                        "description": "Execute Percolator snapshot-isolated transaction with primary and secondary cell writes",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "primary": {"type": "array", "items": {"type": "string"}},
                                "secondaries": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}},
                                "values": {"type": "object"}
                            },
                            "required": ["primary", "values"]
                        }
                    }
                ]
            }
        }
    elif method == "tools/call":
        name = params.get("name")
        args = params.get("arguments", {})
        if name == "percolator_transaction":
            p = tuple(args["primary"])
            secs = [tuple(s) for s in args.get("secondaries", [])]
            writes = {}
            for k, v in args.get("values", {}).items():
                parts = tuple(k.split(","))
                writes[parts] = v
            s_ts = engine.get_ts()
            ok_pre, msg_pre = engine.prewrite(p, secs, writes, s_ts)
            if not ok_pre:
                return {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": json.dumps({"status": "FAILED_PREWRITE", "error": msg_pre})}]}}
            c_ts = engine.get_ts()
            ok_com, msg_com = engine.commit(p, secs, s_ts, c_ts)
            return {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": json.dumps({"status": "COMMITTED" if ok_com else "FAILED_COMMIT", "start_ts": s_ts, "commit_ts": c_ts})}]}}
    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": "Method not found"}}

def main():
    for line in sys.stdin:
        if line.strip():
            req = json.loads(line)
            res = handle_request(req)
            sys.stdout.write(json.dumps(res) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
