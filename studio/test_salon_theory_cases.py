"""
The Hair Salon & Barber theory test (26 Sept 2026, /workspace/salon_theory) as automated tests.

The theory test ran 29 cases on paper-code: B1-B21 (bookings, deposits, safety, reminders, offline)
and Q1-Q8 (walk-in queue). Q8 was "not run" there (it needs a real phone); here it is checked
by the server's checked_at time and by the phone code that keeps the last answer.
Every case below uses the REAL engines that ship in the shop app (studio/engines), with the
same shops, times and expected results as the theory test. Times are London wall-clock.

    python3 -m pytest studio/test_salon_theory_cases.py -q
"""
import json
import sys
import threading
from datetime import datetime, timedelta
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "card_template"))
from engines.booking import BookingEngine, SlotTaken  # noqa: E402
from engines.store import EngineError, to_utc, uk_offset_hours  # noqa: E402
from engines.walkin import WalkInQueue  # noqa: E402
from engines import messages  # noqa: E402

SAT, MON = "2026-10-03", "2026-10-05"
DAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
THEORY = Path("/workspace/salon_theory/sim_results.json")


class Clock:
    def __init__(self, t):
        self.t = t

    def __call__(self):
        return self.t

    def add(self, minutes):
        self.t += timedelta(minutes=minutes)


def hours(o, c):
    return [{"day": d, "open": o, "close": c, "closed": d == "sun"} for d in DAYS]


def staff(sid, start="09:00", end="18:00", lunch="13:00-13:30"):
    s, e = lunch.split("-")
    days = {d: {"start": start, "end": end} for d in DAYS[:6]}
    return {"id": sid, "name": sid.title(), "days": days, "breaks": [{"start": s, "end": e, "flexible": True}]}


def luxury_shop(buffer=10, **booking):
    return {"hours": hours("09:00", "18:00"),
            "services": [{"id": "cut", "name": "Cut & finish", "duration_min": 60, "price_from": "65"},
                         {"id": "colour", "name": "Full colour", "duration_min": 120, "price_from": "140", "deposit": "30",
                          "needs_patch_test": True, "segments": "45 active, 45 processing, 30 active"},
                         {"id": "blow", "name": "Blow-dry", "duration_min": 45, "price_from": "40"},
                         {"id": "trim", "name": "Fringe trim", "duration_min": 15, "price_from": "12"}],
            "staff": [staff(s) for s in ("amara", "bea", "cleo", "dina")],
            "booking": dict({"buffer_minutes": buffer}, **booking)}


def textured_shop():
    return {"hours": hours("09:00", "19:00"),
            "services": [{"id": "braids", "name": "Knotless braids (long)", "duration_min": 360, "deposit": "40"},
                         {"id": "locs", "name": "Loc retwist", "duration_min": 180, "deposit": "20"},
                         {"id": "consult", "name": "Consultation", "duration_min": 20}],
            "staff": [staff("zara", "09:00", "18:00", "13:00-13:30"), staff("yemi", "10:00", "19:00", "14:00-14:30")],
            "booking": {"buffer_minutes": 15}}


def barber_shop():
    return {"hours": hours("09:00", "19:00"),
            "services": [{"id": "cut", "name": "Cut", "duration_min": 25}, {"id": "fade", "name": "Skin fade + beard", "duration_min": 45}],
            "staff": [{"id": b, "name": b.title()} for b in ("ash", "ben", "cal")], "booking": {"buffer_minutes": 0},
            "walkin": {"max_waiting": 25, "default_minutes": 25}}


def engine(tmp_path, shop, clock, tests=None, deposits=True, name="b.json"):
    tests = {} if tests is None else tests
    return BookingEngine(tmp_path / name, lambda: shop, now=clock,
                         patch_tests=lambda phone: tests.get(phone, []), deposits_on=lambda: deposits)


def req(phone, svc, day, time, who="any", name="Client"):
    return {"service_id": svc, "date": day, "time": time, "staff_id": who, "name": name, "phone": phone}


def ok(e, *a, **k):
    try:
        return e.create(req(*a, **k), "instant")
    except EngineError:
        return None


def free(e, svc, day, time, who):
    return any(s["time"] == time and who in s["staff"] for s in e.slots(svc, day, who)["slots"])


def clear_test(day):
    return [{"tested_on": day, "result": "clear"}]


@pytest.fixture
def clock():
    return Clock(datetime(2026, 10, 1, 9, 0))


# ------------------------------------------------------------------ bookings
def test_B1_same_time_different_stylists(tmp_path, clock):
    e = engine(tmp_path, luxury_shop(), clock)
    assert ok(e, "07700900001", "cut", SAT, "10:00", "amara") and ok(e, "07700900002", "cut", SAT, "10:00", "bea")


def test_B2_same_stylist_same_time_refused(tmp_path, clock):
    e = engine(tmp_path, luxury_shop(), clock)
    ok(e, "07700900001", "cut", SAT, "10:00", "amara")
    with pytest.raises(SlotTaken):
        e.create(req("07700900003", "cut", SAT, "10:00", "amara"), "instant")


def test_B3_partial_overlap_refused(tmp_path, clock):
    e = engine(tmp_path, luxury_shop(), clock)
    ok(e, "07700900001", "cut", SAT, "10:00", "amara")
    assert ok(e, "07700900004", "blow", SAT, "10:30", "amara") is None


def test_B4_buffer_after_every_booking(tmp_path, clock):
    e = engine(tmp_path, luxury_shop(buffer=10), clock)
    ok(e, "07700900001", "cut", SAT, "10:00", "amara")
    assert ok(e, "07700900005", "blow", SAT, "11:00", "amara") is None
    assert ok(e, "07700900006", "blow", SAT, "11:10", "amara")


def test_B5_FIX1_buffer_may_run_past_closing(tmp_path, clock):
    e = engine(tmp_path, luxury_shop(buffer=10), clock)
    assert ok(e, "07700900007", "cut", SAT, "17:00", "amara")            # last slot of the day kept
    strict = engine(tmp_path, luxury_shop(buffer=10, buffer_may_pass_closing=0), clock, name="strict.json")
    assert ok(strict, "07700900007", "cut", SAT, "17:00", "amara") is None   # the owner can switch it back


def test_B6_long_service_never_crosses_the_stylists_day(tmp_path, clock):
    e = engine(tmp_path, textured_shop(), clock)
    assert ok(e, "07700900008", "braids", SAT, "14:00", "yemi") is None
    starts = [s["time"] for s in e.slots("braids", SAT, "yemi")["slots"]]
    assert starts and max(starts) <= "13:00"                              # 13:00 + 6 hrs = 19:00 finish


def test_B7_FIX2_flexible_break_for_long_services(tmp_path, clock):
    e = engine(tmp_path, textured_shop(), clock)
    starts = [s["time"] for s in e.slots("braids", SAT, "zara")["slots"]]
    assert starts and starts[0] == "09:00"
    shop = textured_shop()
    shop["staff"][0]["breaks"][0]["flexible"] = False                     # a fixed lunch blocks every 6-hr start
    e2 = engine(tmp_path, shop, clock, name="fixed.json")
    assert e2.slots("braids", SAT, "zara")["slots"] == []
    # a short service still respects the break
    assert not free(e, "consult", SAT, "13:00", "zara")


def test_B8_FIX3_processing_time_frees_the_stylist(tmp_path, clock):
    tests = {"07700900009": clear_test("2026-09-28")}
    e = engine(tmp_path, luxury_shop(), clock, tests)
    col = e.create(req("07700900009", "colour", SAT, "10:00", "bea"), "instant")
    assert col["status"] == "held" and col["busy"] == [[600, 645], [690, 720]]
    e.payment_result(col["id"], True)
    assert ok(e, "07700900010", "trim", SAT, "11:00", "bea")              # during 10:45-11:30 processing
    assert ok(e, "07700900011", "trim", SAT, "11:30", "bea") is None      # back to active part
    assert e.clashes() == []


def test_B9_cancel_frees_the_slot_straight_away(tmp_path, clock):
    e = engine(tmp_path, luxury_shop(), clock)
    a = ok(e, "07700900011", "cut", SAT, "15:00", "cleo")
    assert not free(e, "cut", SAT, "15:00", "cleo")
    e.set_status(a["id"], "cancelled")
    assert free(e, "cut", SAT, "15:00", "cleo")
    assert ok(e, "07700900012", "cut", SAT, "15:00", "cleo")


def test_B10_late_cancel_is_flagged(tmp_path, clock):
    clock.t = datetime(2026, 10, 2, 16, 0)
    e = engine(tmp_path, luxury_shop(), clock)
    a = ok(e, "07700900013", "cut", SAT, "10:00", "dina")
    b = e.cancel_by_customer(a["ref"], "07700900013")
    assert b["status"] == "cancelled" and "late cancel - policy applies" in b["flags"]


def test_B11_no_show_grace_count_and_deposit_next_time(tmp_path, clock):
    e = engine(tmp_path, luxury_shop(), clock)
    a = ok(e, "07700900014", "cut", SAT, "10:00", "dina")
    clock.t = datetime(2026, 10, 3, 10, 5)
    with pytest.raises(EngineError):
        e.set_status(a["id"], "no_show")
    clock.t = datetime(2026, 10, 3, 10, 20)
    assert e.set_status(a["id"], "no_show")["status"] == "no_show"
    assert e.no_show_count("07700 900014") == 1
    clock.t = datetime(2026, 10, 3, 10, 30)
    nxt = e.create(req("07700900014", "cut", MON, "10:00", "dina"), "instant")
    assert nxt["status"] == "held" and nxt["deposit"]["amount"] == "10"


def test_B12_deposit_paid_in_time_confirms(tmp_path, clock):
    e = engine(tmp_path, luxury_shop(), clock, {"07700900015": clear_test("2026-09-20")})
    a = e.create(req("07700900015", "colour", SAT, "09:00", "amara"), "instant")
    assert a["status"] == "held" and a["hold_until"] == "2026-10-01T09:10:00"
    assert not free(e, "cut", SAT, "09:00", "amara")                      # the hold blocks others
    clock.add(3)
    assert e.payment_result(a["id"], True)["booking"]["status"] == "confirmed"


def test_B13_card_declined_releases_the_slot(tmp_path, clock):
    e = engine(tmp_path, luxury_shop(), clock, {"07700900016": clear_test("2026-09-20")})
    a = e.create(req("07700900016", "colour", SAT, "09:00", "amara"), "instant")
    r = e.payment_result(a["id"], False)
    assert r["booking"]["status"] == "cancelled" and free(e, "colour", SAT, "09:00", "amara")


def test_B14_abandoned_payment_hold_expires(tmp_path, clock):
    e = engine(tmp_path, luxury_shop(), clock, {"07700900017": clear_test("2026-09-20")})
    a = e.create(req("07700900017", "colour", SAT, "09:00", "amara"), "instant")
    clock.add(11)
    assert free(e, "colour", SAT, "09:00", "amara")
    assert e.expire_holds() == 1 and e.get(a["id"])["status"] == "expired"
    assert e.public_status(a["ref"])["status"] == "expired"


def test_B15_FIX4_late_payment_rechecked_refund_and_alert(tmp_path, clock):
    tests = {"07700900018": clear_test("2026-09-20"), "07700900019": clear_test("2026-09-20")}
    e = engine(tmp_path, luxury_shop(), clock, tests)
    a = e.create(req("07700900018", "colour", SAT, "09:00", "amara"), "instant")
    clock.add(12)
    b = e.create(req("07700900019", "cut", SAT, "09:30", "amara"), "instant")
    assert b["status"] == "confirmed"
    r = e.payment_result(a["id"], True, source="stripe", event_id="evt_1")
    assert r["booking"]["status"] == "refund_due" and r["result"] == "refund due - owner alerted"
    assert e.clashes() == [] and len(e.alerts()) == 1 and "Refund needed" in e.alerts()[0]["text"]
    assert e.payment_result(a["id"], True, event_id="evt_1")["result"] == "already handled"   # same message twice
    # late payment when the time is STILL free: confirmed, not refunded
    e2 = engine(tmp_path, luxury_shop(), Clock(datetime(2026, 10, 1, 9, 0)), tests, name="b2.json")
    c = e2.create(req("07700900018", "colour", SAT, "09:00", "amara"), "instant")
    e2.now.add(12)
    assert e2.payment_result(c["id"], True)["booking"]["status"] == "confirmed"


def test_B16_eight_phones_same_instant_exactly_one_wins(tmp_path, clock):
    e = engine(tmp_path, luxury_shop(), clock)
    out, go = [], threading.Barrier(8)

    def run(i):
        go.wait()
        out.append(ok(e, f"0770090010{i}", "cut", SAT, "16:00", "cleo"))
    ths = [threading.Thread(target=run, args=(i,)) for i in range(8)]
    [t.start() for t in ths]
    [t.join() for t in ths]
    assert sum(1 for o in out if o) == 1 and e.clashes() == []


def test_B17_any_stylist_tries_each_in_turn(tmp_path, clock):
    e = engine(tmp_path, luxury_shop(), clock)
    r = [ok(e, f"0770090020{i}", "cut", SAT, "12:00", "any") for i in range(5)]
    got = [x["staff_id"] for x in r if x]
    assert len(got) == 4 and len(set(got)) == 4 and r[4] is None


def test_B18_patch_test_rule(tmp_path, clock):
    tests = {"07700900301": clear_test("2026-10-02"), "07700900302": clear_test("2026-09-29"),
             "07700900303": [{"tested_on": "2026-09-29", "result": "reaction"}]}
    e = engine(tmp_path, luxury_shop(), clock, tests)
    with pytest.raises(EngineError, match="patch test first"):
        e.create(req("07700900300", "colour", SAT, "09:00", "amara"), "instant")
    with pytest.raises(EngineError, match="48 hours"):
        e.create(req("07700900301", "colour", SAT, "09:00", "amara"), "instant")
    assert e.create(req("07700900302", "colour", SAT, "09:00", "bea"), "instant")["status"] == "held"
    with pytest.raises(EngineError):
        e.create(req("07700900303", "colour", SAT, "09:00", "cleo"), "instant")
    # client records switched off: can't check, so it can only be a request, flagged for the salon
    off = BookingEngine(tmp_path / "off.json", lambda: luxury_shop(), now=clock, patch_tests=None, deposits_on=lambda: True)
    r = off.create(req("07700900300", "colour", SAT, "09:00", "amara"), "instant")
    assert r["status"] == "requested" and "patch test needed - salon to check" in r["flags"]


def test_B19_reminder_uses_london_time_across_the_clock_change():
    due = messages.reminder_due({"date": "2026-10-26", "start": "09:00"}, 24)
    assert due["local"] == "2026-10-25T09:00" and due["label"].startswith("Sun 25 Oct 09:00")
    assert due["utc"] == "2026-10-25T09:00Z"                                # GMT after the change; a fixed +1 says 08:00
    assert messages.reminder_due({"date": "2026-10-24", "start": "09:00"})["utc"] == "2026-10-23T08:00Z"   # still BST
    # the stdlib-only fallback (for PCs without the zone database) agrees with the zone database all year
    from zoneinfo import ZoneInfo
    from datetime import timezone
    t = datetime(2026, 1, 1, 0, 30)
    while t.year == 2026:
        if not (t.month in (3, 10) and t.day >= 25 and 0 <= t.hour <= 2):   # skip the ambiguous/missing hour
            zone = t.replace(tzinfo=ZoneInfo("Europe/London")).utcoffset().total_seconds() / 3600
            assert uk_offset_hours(t) == zone, t
        t += timedelta(hours=7)
    assert to_utc(datetime(2026, 7, 1, 12, 0)) == datetime(2026, 7, 1, 11, 0)


def test_B20_offline_request_is_never_shown_as_booked(tmp_path, clock):
    e = engine(tmp_path, luxury_shop(), clock)
    ok(e, "07700900401", "cut", SAT, "14:00", "dina")                    # someone else books while the phone is offline
    with pytest.raises(SlotTaken) as x:
        e.create(req("07700900400", "cut", SAT, "14:00", "dina"), "instant")   # the replay
    assert x.value.alternatives and "14:00" not in x.value.alternatives
    js = (HERE / "card_template" / "site" / "app.js").read_text()
    words = (HERE / "card_template" / "site" / "i18n.js").read_text()
    assert "booking_outbox" in js and "flushOutbox" in js and "you are NOT booked" in words


def test_B21_no_server_falls_back_to_a_whatsapp_request(tmp_path):
    import card_app
    import cardbuild
    import cards
    import demo_content
    card = cards.load_card("CARD-HAIR-01")
    shop = demo_content.sample_shop(card, cards.preset(card, "luxury"), {"auto_booking": True, "walkin_queue": True, "loyalty": True})
    shop["whatsapp"] = "07700900123"
    card_app.generate("CARD-HAIR-01", shop, tmp_path / "app", password="test-pass-1")
    r = cardbuild.write_static_site(tmp_path / "app", tmp_path / "static")
    c = json.loads((tmp_path / "static" / "content.json").read_text())
    assert r["booking_mode"] == c["booking_mode"] == "whatsapp_request"
    assert c["static_copy"] and "only booked when the shop replies" in c["static_note"]
    assert "auto_booking" not in c["modules"] and "walkin_queue" not in c["modules"] and "loyalty" not in c["modules"]
    assert not (tmp_path / "static" / "queue.html").exists() and not (tmp_path / "static" / "admin").exists()
    assert "password_hash" not in (tmp_path / "static" / "content.json").read_text()
    assert "waRequest" in (tmp_path / "static" / "app.js").read_text()


# --------------------------------------------------------------------- queue
@pytest.fixture
def barber(tmp_path):
    clock = Clock(datetime(2026, 10, 3, 10, 0))
    shop = barber_shop()
    q = WalkInQueue(tmp_path / "q.json", lambda: shop, now=clock)
    return q, clock, shop


def test_Q1_waits_from_service_times_and_free_chairs(barber):
    q, clock, _ = barber
    js = [q.join(n, "cut", "any", p) for n, p in (("Tom", "07000000001"), ("Ali", "07000000002"), ("Sam", "07000000003"),
                                                    ("Kofi", "07000000004"), ("Dan", "07000000005"))]
    assert [j["position"] for j in js] == [1, 2, 3, 4, 5]
    assert [j["wait_minutes"] for j in js] == [0, 0, 0, 25, 25]


def test_Q1b_FIX6_each_persons_own_service_length_counts(tmp_path):
    clock = Clock(datetime(2026, 10, 3, 10, 0))
    shop = dict(barber_shop(), staff=[{"id": "ash", "name": "Ash"}])
    q = WalkInQueue(tmp_path / "q1.json", lambda: shop, now=clock)
    q.join("Fade", "fade", "any", "07000000011")
    q.join("Cut", "cut", "any", "07000000012")
    third = q.join("Next", "cut", "any", "07000000013")
    assert third["wait_minutes"] == 45 + 25                                # not 2 x an average
    c = q.call_next("ash")
    q.set_status(c["no"], "in_chair")
    clock.add(30)                                                         # fade started 30 min ago: 15 min left
    assert q.ticket(third["token"])["wait_minutes"] == 15 + 25


def test_Q2_leaving_moves_everyone_up(barber):
    q, _, _ = barber
    t = {n: q.join(n, "cut", "any", f"0700000000{i}") for i, n in enumerate(("Tom", "Ali", "Sam", "Kofi", "Dan"))}
    q.leave(t["Ali"]["token"])
    assert [x["name"] for x in q.admin_list() if x["status"] == "waiting"] == ["Tom", "Sam", "Kofi", "Dan"]
    assert q.ticket(t["Sam"]["token"])["position"] == 2


def test_Q3_skip_once_back_two_places_twice_removed(barber):
    q, _, _ = barber
    t = {n: q.join(n, "cut", "any", f"0700000000{i}") for i, n in enumerate(("Tom", "Ali", "Sam", "Kofi", "Dan"))}
    q.leave(t["Ali"]["token"])
    r1 = q.skip(t["Sam"]["no"])
    assert r1 == {"no": t["Sam"]["no"], "removed": False, "new_position": 4}
    r2 = q.skip(t["Sam"]["no"])
    assert r2["removed"] and t["Sam"]["no"] not in [x["no"] for x in q.admin_list() if x["status"] == "waiting"]


def test_Q4_FIX5_free_barber_calls_first_person_he_can_serve(barber):
    q, clock, _ = barber
    clock.t = datetime(2026, 10, 3, 11, 0)
    q.join("Wants Ash", "cut", "ash", "07000000010")
    q.join("Anyone", "cut", "any", "07000000011")
    assert q.call_next("ben")["name"] == "Anyone"
    with pytest.raises(EngineError):
        q.call_next("cal")                                               # only the Ash-only client left


def test_Q5_FIX6_queue_counts_booked_appointments(tmp_path):
    clock = Clock(datetime(2026, 10, 3, 9, 0))
    shop = barber_shop()
    bk = BookingEngine(tmp_path / "b.json", lambda: shop, now=clock)
    for b in ("ash", "ben", "cal"):
        bk.create(req(f"0711100000{len(b)}{b[0]}1", "fade", SAT, "12:00", b), "instant")
        bk.create(req(f"0711100000{len(b)}{b[0]}2", "fade", SAT, "12:45", b), "instant")
    q = WalkInQueue(tmp_path / "q.json", lambda: shop, now=clock, booked=bk.busy_blocks)
    clock.t = datetime(2026, 10, 3, 11, 55)
    j = q.join("Walk-in", "cut", "any", "07000000020")
    assert j["wait_minutes"] == 95 and j["about"] == "13:30"


def test_Q6_joining_stops_when_it_would_finish_after_closing(barber):
    q, clock, _ = barber
    clock.t = datetime(2026, 10, 3, 18, 20)
    for i in range(3):
        q.join(f"P{i}", "cut", "any", f"0730000000{i}")
    with pytest.raises(EngineError, match="closed for today"):
        q.join("Late", "cut", "any", "07300000009")


def test_Q7_one_place_per_phone(barber):
    q, _, _ = barber
    q.join("P0", "cut", "any", "07300 000000")
    with pytest.raises(EngineError, match="already has a place"):
        q.join("P0 again", "cut", "any", "+447300000000")


def test_Q8_ticket_says_when_it_was_checked_and_phone_keeps_last_answer(barber):
    q, clock, _ = barber
    t = q.join("Tom", "cut", "any", "07000000001")
    assert q.ticket(t["token"])["checked_at"] == "2026-10-03T10:00"
    assert q.board()["checked_at"] == "2026-10-03T10:00"
    js = (HERE / "card_template" / "site" / "app.js").read_text()
    assert "queue_last" in js and 't("no_signal")' in js and 't("last_checked")' in js
    assert "last checked" in (HERE / "card_template" / "site" / "queue.html").read_text()


def test_board_shows_first_names_only(barber):
    q, _, _ = barber
    q.join("Sam Smith", "cut", "any", "07000000001")
    b = q.board()
    assert b["next"][0]["name"] == "Sam" and "07000000001" not in json.dumps(b)


# ------------------------------------------------------------- coverage
def test_every_theory_case_is_ported():
    ids = [f"B{i}" for i in range(1, 22)] + [f"Q{i}" for i in range(1, 9)]
    if THEORY.exists():                                   # the original theory-test output, when it is on this computer
        assert sorted(r["id"] for r in json.loads(THEORY.read_text())["tests"]) == sorted(ids)
    names = [n for n in globals() if n.startswith("test_")]
    missing = [i for i in ids if not any(n.startswith(f"test_{i}_") for n in names)]
    assert len(ids) == 29 and missing == []
