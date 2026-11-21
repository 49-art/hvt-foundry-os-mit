#!/usr/bin/env bash
# Browser-free walk through the whole DOC-0005 loop using curl.
# Usage: start the Studio (python3 studio/app.py --no-browser), then run: bash studio/curl_walkthrough.sh
set -euo pipefail
B=${STUDIO_URL:-http://localhost:8000}/api
j() { python3 -c "import sys,json;d=json.load(sys.stdin);print(eval(sys.argv[1]))" "$1"; }
post() { curl -s -X POST -H 'Content-Type: application/json' -d "$2" "$B/$1"; }
echo "== 1. Boot the kernel";            post boot '{}' | j '"ok=%s  "%d["ok"] + ", ".join(s["gate"]+":"+s["outcome"] for s in d["steps"])'
echo "== 2. Open a session (BUT-0001)";  R=$(post sessions '{"business_type_id":"BUT-0001","business_name":"curl test"}'); SID=$(echo "$R" | j 'd["result"]["id"]'); echo "$SID  review: $(echo "$R" | j 'd["review_status"]')"
echo "== 3. Owner corrects classification"; post "sessions/$SID/classify" '{"owner_words":"We are a salon but we also do nails"}' | j 'd["result"]["classification"]["source"]'
echo "== 4. Run configurator (2-5 staff, £0-50, Basic)"
R=$(post "sessions/$SID/configure" '{"size":"2–5 Staff","budget":"£0–50","tech":"Basic"}'); PID=$(echo "$R" | j 'd["result"]["id"]')
echo "$R" | j '"%s: engines=%s | tools=%s"%(d["result"]["id"],[e["id"] for e in d["result"]["configuration"]["engines"]],[(c["name"],c["factcheck"]["overall"],c["budget_fit"]) for c in d["result"]["configuration"]["components"]])'
echo "== 5. Owner rejects, then accepts";  post "sessions/$SID/response" "{\"proposal_id\":\"$PID\",\"decision\":\"reject\",\"owner_words\":\"too many apps\"}" | j 'd["result"]["id"]'
post "sessions/$SID/response" "{\"proposal_id\":\"$PID\",\"decision\":\"accept\",\"owner_words\":\"ok with Square\"}" | j 'd["result"]["id"]+" "+d["review_status"]'
echo "== 6. Capture three wishes";  W1=$(post "sessions/$SID/wishes" '{"description":"Tell me on my phone when the colour is running out","priority":"Must","linked_problems":["PRB-0004"],"customer_asset_flag":true}' | j 'd["result"]["id"]')
W2=$(post "sessions/$SID/wishes" '{"description":"I want to sell gift cards online"}' | j 'd["result"]["id"]'); W3=$(post "sessions/$SID/wishes" '{"description":"Can it do my accounts for me"}' | j 'd["result"]["id"]'); echo "$W1 $W2 $W3"
echo "== 7. Empty wish is refused";  post "sessions/$SID/wishes" '{"description":"  "}' | j 'd.get("message")'
echo "== 8. Close session";  post "sessions/$SID/close" '{}' | j 'd["result"]["status"]'
echo "== 9. Wish after close is refused";  post "sessions/$SID/wishes" '{"description":"late"}' | j 'd.get("message")'
echo "== 10. Review queue"; curl -s "$B/queue" | j '[w["id"] for w in d]'
echo "== 11. Resolve: reconfigure / engine search / out of scope"
post "wishes/$W1/resolve" '{"outcome":"reconfigure","reason":"Square low-stock alerts, DOC-0006 path S1"}' | j 'd["result"]["status"]+" via "+d["kernel"]["action"]'
post "wishes/$W2/resolve" '{"outcome":"engine_search","reason":"No registered engine sells gift cards","capability":"Gift cards"}' | j 'd["result"]["status"]+" via "+d["kernel"]["action"]+" "+d["result"]["engine_search_id"]'
post "wishes/$W3/resolve" '{"outcome":"out_of_scope","reason":"Accounting is done by the owner in Xero/QuickBooks"}' | j 'd["result"]["status"]+" / "+d["result"]["resolution"]'
echo "== 12. Session is now"; curl -s "$B/sessions/$SID" | j 'd["session"]["status"]'
echo "== 13. Offer new configuration (follow-up session)"; F=$(post "sessions/$SID/follow-up" '{}' | j 'd["result"]["id"]'); echo "$F"
P2=$(post "sessions/$F/configure" '{}' | j 'd["result"]["id"]'); post "sessions/$F/response" "{\"proposal_id\":\"$P2\",\"decision\":\"accept\"}" > /dev/null
echo "== 14. Wish history (nothing deleted)"; curl -s "$B/wishes/$W1/history" | j '[(w["rev"],w["status"],w["supersedes"]) for w in d]'
echo "== 15. Authority tests"; for c in ceo_captures_wish architect_amends_constitution; do post authority-test "{\"case\":\"$c\"}" | j '"%s refused=%s"%(d["case"],d["refused"])'; done
echo "== 16. Audit"; curl -s "$B/audit" | j '"studio events=%d (refused=%d), kernel entries=%d"%(len(d["studio_events"]),sum(e["outcome"]=="refused" for e in d["studio_events"]),len(d["kernel_audit"]))'
