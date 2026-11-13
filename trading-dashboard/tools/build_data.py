#!/usr/bin/env python3
"""Génère data/dashboard.json pour le tableau de bord.

Lance les 11 skills du pack day-trader-skill (dossier skills/) et rassemble
leurs sorties JSON dans un seul fichier que la page index.html affiche.

    python3 tools/build_data.py                 # données en direct (Yahoo, SEC, House Clerk)
    python3 tools/build_data.py --demo DIR --now "2026-10-19 10:15"   # test hors ligne (fixtures)

Python standard uniquement. Aucun ordre n'est jamais envoyé : le script ne
fait que lire des données publiques et calculer. La variable d'environnement
SEC_USER_AGENT ("Prénom Nom email") active les parties SEC (8-K, résultats).
"""
import argparse
import datetime
import gzip
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS = os.path.join(ROOT, "skills")
UA = "Mozilla/5.0 (compatible; day-trader-dashboard/1.0)"
MAX_PLANS = 10         # plafond de plans de trade détaillés par mise à jour
MAX_LIST = 20          # actions affichées en mode « tout le marché »

STEPS = []             # journal affiché en bas de la page


def step(skill, ok, detail=""):
    STEPS.append({"skill": skill, "ok": bool(ok), "detail": str(detail)[:300]})


def run(skill, script, args, cwd, timeout=600):
    """Lance un script d'un skill, renvoie (json ou None, texte d'erreur)."""
    cmd = [sys.executable, os.path.join(SKILLS, skill, script)] + [str(a) for a in args]
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return None, "délai dépassé"
    out = p.stdout.strip()
    if out:
        try:
            return json.loads(out), ""
        except ValueError:
            pass
    msg = (p.stderr.strip() or out or "aucune sortie (code %d)" % p.returncode)
    return None, msg.splitlines()[-1][:300] if msg else "erreur"


def closes_from_result(res):
    ts = res.get("timestamp") or []
    q = ((res.get("indicators") or {}).get("quote") or [{}])[0]
    cl = q.get("close") or []
    pts = []
    for t, c in zip(ts, cl):
        if c is None:
            continue
        d = datetime.datetime.fromtimestamp(t, datetime.timezone.utc).strftime("%Y-%m-%d")
        pts.append([d, round(float(c), 2)])
    return pts


def fetch_history(sym):
    last = None
    for host in ("query2", "query1"):
        url = "https://%s.finance.yahoo.com/v8/finance/chart/%s?range=3mo&interval=1d" % (
            host, sym.replace(".", "-"))
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Encoding": "gzip"})
            with urllib.request.urlopen(req, timeout=30) as r:
                raw = r.read()
                if r.headers.get("Content-Encoding") == "gzip":
                    raw = gzip.decompress(raw)
            return closes_from_result(json.loads(raw)["chart"]["result"][0])
        except Exception as e:      # réseau, format : on essaie l'autre hôte
            last = e
            time.sleep(1)
    raise RuntimeError(str(last))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "data", "dashboard.json"))
    ap.add_argument("--watchlist", default=os.path.join(ROOT, "trader", "watchlist.txt"))
    ap.add_argument("--config", default=os.path.join(ROOT, "trader", "config.json"))
    ap.add_argument("--demo", metavar="DIR", help="dossier tests/fixtures du pack (hors ligne)")
    ap.add_argument("--now", help='heure de New York simulée, ex. "2026-10-19 10:15"')
    a = ap.parse_args()

    with open(a.watchlist, encoding="utf-8") as fh:
        tickers = [l.split("#")[0].strip().upper() for l in fh]
    tickers = [t for t in tickers if t]
    with open(a.config, encoding="utf-8") as fh:
        config = json.load(fh)
    sec_ua = (os.environ.get("SEC_USER_AGENT") or "").strip()

    fx = a.demo
    now = ["--now", a.now] if a.now else []
    work = tempfile.mkdtemp(prefix="trader-")
    os.makedirs(os.path.join(work, "trader"))
    shutil.copy(a.config, os.path.join(work, "trader", "config.json"))

    # Mode « tout le marché » : la ligne ALL dans trader/watchlist.txt
    market = None
    full = "ALL" in tickers
    tickers = [t for t in tickers if t != "ALL"]
    if full:
        budget = float(config.get("budget") or 0)
        cap = min(budget * float(config.get("max_position_pct") or 100) / 100.0,
                  budget * (1 - float(config.get("cash_buffer_pct") or 0) / 100.0),
                  float(config.get("max_order_usd") or 1e12))
        sc = os.path.join(fx, "trader-scanner") if fx else None
        u, err = run("trader-scanner", "scan.py", ["universe", "--json"] + (["--offline", os.path.join(sc, "symdir")] if fx else []), work)
        nuni = 0
        try:
            with open(os.path.join(work, "trader", "universe.txt")) as fh:
                nuni = sum(1 for l in fh if l.strip())
        except OSError:
            pass
        dl, err_d = run("trader-scanner", "scan.py", ["daily", "--json", "--no-write"] + now + (
            ["--offline", os.path.join(sc, "daily-spark-2026-10-19.json")] if fx else []), work, timeout=900)
        ob, err_o = run("trader-scanner", "scan.py", ["orb", "--json", "--no-write"] + now + (
            ["--offline", os.path.join(sc, "wall5m-2026-10-19.json.gz")] if fx else []), work, timeout=900)
        dhits, ohits = (dl or {}).get("hits", []), (ob or {}).get("hits", [])
        fits = lambda h: h.get("price") is not None and h["price"] <= cap
        picked = [h["symbol"] for h in ohits if fits(h)][:MAX_LIST]
        for h in dhits:
            if fits(h) and h["symbol"] not in picked and len(picked) < MAX_LIST:
                picked.append(h["symbol"])
        tickers = picked + [t for t in tickers if t not in picked]
        market = {"universe": nuni, "position_cap": round(cap, 2),
                  "daily": {"scanned": (dl or {}).get("scanned"), "hits": len(dhits), "affordable": sum(map(fits, dhits)),
                            "as_of": (dl or {}).get("as_of"), "error": None if dl else err_d},
                  "orb": {"scanned": (ob or {}).get("scanned"), "hits": len(ohits), "affordable": sum(map(fits, ohits)),
                          "as_of": (ob or {}).get("as_of"), "unconfirmed": (ob or {}).get("unconfirmed"),
                          "error": None if ob else err_o}}
        step("marché entier", nuni and (dl or ob), "%d actions US ; scan journalier : %s ; cassures du range d'ouverture : %s" % (
            nuni, ("%d configurations sur %s graphiques" % (len(dhits), dl.get("scanned"))) if dl else err_d,
            ("%d sur %s graphiques" % (len(ohits), ob.get("scanned"))) if ob else err_o))
    out = {"watchlist": tickers, "market": market, "demo": bool(fx), "config": {
        k: config.get(k) for k in (
            "budget", "cash_buffer_pct", "max_loss_per_trade_usd", "max_daily_loss_usd",
            "max_trades_per_day", "min_reward_risk", "max_position_pct", "no_entries_before", "budget_eur",
            "no_entries_after", "flat_by", "paper", "broker")}}

    # 1. trader-alerts : horloge NYSE + cours
    d, err = run("trader-alerts", "alerts.py", ["clock", "--json"] + now, work)
    out["clock"] = d
    if not tickers:
        tickers = ["SPY"]            # rien d'abordable trouvé : on garde au moins l'indice pour vérifier la chaîne
    out["watchlist"] = tickers
    args = ["quote"] + tickers + ["--json", "--write"] + now
    if fx:
        args += ["--offline", os.path.join(fx, "trader-alerts")]
    q, err2 = run("trader-alerts", "alerts.py", args, work)
    out["quotes"] = (q or {}).get("quotes", {})
    nq = len(out["quotes"])
    step("trader-alerts", d and nq, "%d cours sur %d" % (nq, len(tickers)) if q else (err2 or err))

    # Historique 3 mois (courbes) : même source Yahoo que les skills
    hist, bad = {}, []
    if fx:
        try:
            with open(os.path.join(fx, "trader-scanner", "spark-3mo-live-2026-10-20.json")) as fh:
                for r in json.load(fh)["spark"]["result"]:
                    if r["symbol"] in tickers:
                        hist[r["symbol"]] = closes_from_result(r["response"][0])
        except Exception as e:
            bad.append(str(e))
    else:
        for t in tickers:
            try:
                hist[t] = fetch_history(t)
            except Exception as e:
                bad.append("%s: %s" % (t, e))
            time.sleep(0.4)
    out["history"] = hist
    step("historique 3 mois", hist, "%d courbes sur %d%s" % (
        len(hist), len(tickers), (" ; " + bad[0][:120]) if bad else ""))

    # 2. trader-scanner : configurations sur les clôtures journalières
    args = ["daily", "--symbols", ",".join(tickers), "--json", "--no-write", "--min-volume", "0"] + now
    if fx:
        args += ["--offline", os.path.join(fx, "trader-scanner", "daily-spark-2026-10-19.json")]
    d, err = run("trader-scanner", "scan.py", args, work)
    out["scan"] = d
    step("trader-scanner", d, "%d configuration(s) sur %d graphiques" % (
        len(d.get("hits", [])), d.get("scanned", 0)) if d else err)

    # 3. trader-news : titres (et 8-K si SEC_USER_AGENT)
    args = ["--tickers"] + tickers + ["--json", "--dry-run", "--all", "--hours", "36"]
    args += ["--user-agent", sec_ua] if sec_ua else ["--no-sec"]
    if fx:
        args += ["--offline", os.path.join(fx, "trader-news"), "--hours", "72"]
    if a.now:
        ny = datetime.datetime.strptime(a.now, "%Y-%m-%d %H:%M")
        args += ["--now", (ny + datetime.timedelta(hours=4)).strftime("%Y-%m-%dT%H:%M:00Z")]
    d, err = run("trader-news", "news.py", args, work)
    if d:
        for it in d.get("items", []):
            it.pop("summary", None)          # on ne republie que le titre et le lien
        d["items"] = d.get("items", [])[:60]
    out["news"] = d
    step("trader-news", d, ("%d titre(s)%s" % (len(d["items"]), "" if sec_ua else " ; 8-K SEC ignorés (pas de SEC_USER_AGENT)")) if d else err)

    # 4. trader-entry : cassure du range d'ouverture pour chaque action
    entries, n_trig = {}, 0
    for t in tickers:
        args = ["check", t, "--json"] + now
        if fx:
            f = os.path.join(fx, "trader-entry", "%s-2026-10-19-5m.json" % t)
            if not os.path.exists(f):
                continue
            args += ["--offline", f]
        d, err = run("trader-entry", "entry.py", args, work)
        entries[t] = d if d else {"status": "no_data", "reason": err}
        n_trig += bool(d and d.get("status") == "triggered")
        if not fx:
            time.sleep(0.4)
    out["entries"] = entries
    step("trader-entry", any(e.get("status") != "no_data" for e in entries.values()),
         "%d action(s) vérifiée(s), %d cassure(s)" % (len(entries), n_trig))

    # 5-9. Pour chaque cassure : exit -> timemachine -> budget -> risk -> broker (ticket, jamais envoyé)
    plans, notes = [], {k: [] for k in ("trader-exit", "trader-timemachine", "trader-budget", "trader-risk", "trader-broker")}
    nmax = min(MAX_PLANS, int(config.get("max_trades_per_day") or MAX_PLANS))
    trig = [t for t in tickers if entries.get(t, {}).get("status") == "triggered"][:nmax]
    for t in trig:
        w = tempfile.mkdtemp(prefix="plan-")
        os.makedirs(os.path.join(w, "trader"))
        shutil.copy(a.config, os.path.join(w, "trader", "config.json"))
        args = ["check", t, "--write", "--json"] + now      # écrit trader/entry.json pour trader-exit
        if fx:
            args += ["--offline", os.path.join(fx, "trader-entry", "%s-2026-10-19-5m.json" % t)]
        run("trader-entry", "entry.py", args, w)
        item = {"symbol": t, "entry": entries[t]}
        plan, err = run("trader-exit", "exit.py", ["plan", "--write", "--json"] + now, w)
        item["plan"] = plan
        notes["trader-exit"].append("%s: %s" % (t, "plan écrit" if plan else err))
        if plan:
            args = ["run", "--json", "--until", plan.get("flat_by") or "15:55"] + now
            if fx:
                args += ["--offline", os.path.join(fx, "trader-timemachine", "%s-60d5m.json.gz" % t)]
            tm, err = run("trader-timemachine", "timemachine.py", args, w)
            if tm:
                tm.get("mc", {}).pop("bands", None)
                tm.get("mc", {}).pop("band_times", None)
                tm.get("mc", {}).pop("paths", None)
                tm.get("history", {}).pop("trades", None)
            item["timemachine"] = tm
            notes["trader-timemachine"].append("%s: %s" % (t, "10 000 rejeux" if tm else err))
            sz, err = run("trader-budget", "size.py", ["--write", "--json"] + now, w)
            item["sizing"] = (sz or {}).get("sizing")
            notes["trader-budget"].append("%s: %s" % (t, "taille calculée" if sz else err))
            if sz and sz.get("orders"):
                rk, err = run("trader-risk", "check.py", ["--json"] + now, w)
                item["risk"] = rk
                notes["trader-risk"].append("%s: %s" % (t, ("%d PASS, %d BLOCK" % (rk.get("pass", 0), rk.get("block", 0))) if rk else err))
                tk, err = run("trader-broker", "ticket.py", ["show", "--json"] + now, w)
                item["tickets"] = tk
                notes["trader-broker"].append("%s: %s" % (t, "ticket affiché, rien n'est envoyé" if tk else err))
        plans.append(item)
        shutil.rmtree(w, ignore_errors=True)
    out["plans"] = plans
    okkey = {"trader-exit": "plan", "trader-timemachine": "timemachine", "trader-budget": "sizing",
             "trader-risk": "risk", "trader-broker": "tickets"}
    for k, v in notes.items():
        good = not plans or any(p.get(okkey[k]) for p in plans)
        step(k, good, " ; ".join(v) if v else "aucune cassure à traiter pour l'instant")

    # 10. trader-analyst : résultats trimestriels (SEC)
    if sec_ua or fx:
        args = tickers + ["--json", "--no-filings"]
        args += ["--offline", os.path.join(fx, "trader-analyst")] if fx else ["--user-agent", sec_ua]
        d, err = run("trader-analyst", "facts.py", args, work)
        rows = []
        for r in d or []:
            res = r.get("result") or {}
            if not res:
                continue
            last = (res.get("rows") or [{}])[0]
            rows.append({"ticker": r.get("ticker"), "entity": res.get("entity"), "ttm": res.get("ttm"),
                         "latest": last, "changes": (r.get("changes") or [])[:3], "note": r.get("note")})
        out["analyst"] = rows
        step("trader-analyst", rows, "%d société(s)" % len(rows) if rows else err)
    else:
        out["analyst"] = None
        step("trader-analyst", False, "ignoré : ajoute le secret SEC_USER_AGENT pour l'activer")

    # 11. trader-pelosi : déclarations récentes des élus (House Clerk)
    ref = datetime.datetime.strptime(a.now, "%Y-%m-%d %H:%M") if a.now else datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
    since = (ref - datetime.timedelta(days=60)).strftime("%Y-%m-%d")
    args = ["index", "--since", since, "--json", "--year", str(ref.year)]
    if fx:
        args += ["--offline", os.path.join(fx, "trader-pelosi", "2026FD.zip")]
    d, err = run("trader-pelosi", "ptr.py", args, work)
    if isinstance(d, list):
        d.sort(key=lambda r: r.get("filed", ""), reverse=True)
        out["congress"] = {"since": since, "total": len(d), "filings": d[:40]}
        step("trader-pelosi", True, "%d déclaration(s) depuis le %s" % (len(d), since))
    else:
        out["congress"] = None
        step("trader-pelosi", False, err)

    out["steps"] = STEPS
    out["generated_at"] = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None).strftime("%Y-%m-%dT%H:%M:%SZ")
    shutil.rmtree(work, ignore_errors=True)
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, separators=(",", ":"))
        fh.write("\n")
    for s in STEPS:
        print("%s %-20s %s" % ("OK " if s["ok"] else "-- ", s["skill"], s["detail"]))
    # Si aucun cours n'est revenu, on signale l'échec pour ne pas publier une page vide.
    return 0 if (out["quotes"] or (market and (market["daily"]["hits"] or market["orb"]["hits"]))) else 1


if __name__ == "__main__":
    sys.exit(main())
