"""Take the v3 screenshots of the two demo card apps, the static (no-server) copy and the Studio screen.
Needs (with SHOP_DEMO_NOW=2026-10-24T10:30 so the demo shops act as a Saturday morning):
  8081 luxury demo server, 8082 barber demo server, 8083 static copy of the luxury demo, 8090 the Studio.
Every screen shows a real response from the running demo apps; nothing is drawn in by hand."""
import json
import sys
import urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT = Path(sys.argv[1] if len(sys.argv) > 1 else "/workspace/studio_shots_v3")
OUT.mkdir(parents=True, exist_ok=True)
LUX, BAR, STA, STU = "http://localhost:8081", "http://localhost:8082", "http://localhost:8083", "http://localhost:8090"
PW = "demo-owner-2026"
DEV = {"phone": dict(viewport={"width": 390, "height": 844}, device_scale_factor=2, is_mobile=True, has_touch=True),
       "tablet": dict(viewport={"width": 820, "height": 1180}, device_scale_factor=2, is_mobile=True, has_touch=True)}


def shot(page, name, full=False):
    page.wait_for_timeout(500)
    page.screenshot(path=str(OUT / f"{name}.png"), full_page=full)
    print("saved", name)


def to_book(page):
    page.evaluate("document.querySelector('#book').scrollIntoView()")


RUN = [0]


def booking_flow(page, base, tag, service_index=0, staff_index=1, day_index=1, time_index=2, before_send=None, shots=True):
    RUN[0] += 1
    page.goto(f"{base}/?visit={RUN[0]}#book"); page.wait_for_selector("#bk .opt")
    page.locator("#bk .opt").nth(service_index).click(); to_book(page)
    shots and shot(page, f"{tag}_book1_service")
    page.click("#bnext"); page.wait_for_selector("#bk .opt")
    page.locator("#bk .opt").nth(staff_index).click(); to_book(page)
    shots and shot(page, f"{tag}_book2_stylist")
    page.click("#bnext"); page.wait_for_selector("#bk .day")
    days = page.locator("#bk .day:not(.shut)")
    days.nth(min(day_index, days.count() - 1)).click(); to_book(page)
    shots and shot(page, f"{tag}_book3_day")
    page.click("#bnext"); page.wait_for_selector("#bk .time", timeout=8000); to_book(page)
    shots and shot(page, f"{tag}_book4_times")
    page.locator("#bk .time").nth(time_index).click()
    page.click("#bnext"); page.wait_for_selector("#bn")
    page.fill("#bn", "Test Customer (demo)"); page.fill("#bp", "07700 900111")
    if page.locator("#bpol").count():
        page.check("#bpol")
    to_book(page)
    shots and shot(page, f"{tag}_book5_details")
    if before_send:
        before_send(page)
    page.click("#bsend"); page.wait_for_timeout(1500); to_book(page)


def admin(page, base, tag, tabs, full_tabs=("modules",)):
    page.goto(base + "/admin"); page.wait_for_selector("#pw")
    page.fill("#pw", PW); page.click("#go"); page.wait_for_selector("#nav")
    for t in tabs:
        page.click(f'#nav button[data-t="{t}"]'); page.wait_for_timeout(800)
        shot(page, f"{tag}_admin_{t}", full=(t in full_tabs))


def take_time_first(page):
    """Someone else books the same time on another phone while this customer is still typing (B20)."""
    st = page.evaluate("JSON.stringify(S.bk)")
    b = json.loads(st)
    body = json.dumps({"service_id": b["service"], "staff_id": b["staff"], "date": b["date"], "time": b["time"],
                       "name": "Other customer (demo)", "phone": "07700 900222", "accept_policy": True}).encode()
    urllib.request.urlopen(urllib.request.Request(LUX + "/api/book", data=body, headers={"Content-Type": "application/json"}, method="POST"))


with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
    for dev, opts in DEV.items():
        ctx = b.new_context(**opts); page = ctx.new_page()
        page.goto(LUX + "/"); page.wait_for_selector(".hero"); shot(page, f"{dev}_luxury_home")
        page.goto(LUX + "/#services"); page.wait_for_timeout(600); page.evaluate("document.querySelector('#services').scrollIntoView()"); shot(page, f"{dev}_luxury_services")
        page.goto(BAR + "/"); page.wait_for_selector(".hero"); shot(page, f"{dev}_barber_home")
        page.goto(BAR + "/#services"); page.wait_for_timeout(600); page.evaluate("document.querySelector('#services').scrollIntoView()"); shot(page, f"{dev}_barber_services")
        if dev == "phone":
            page.goto(LUX + "/"); page.wait_for_selector(".hero"); shot(page, "phone_luxury_fullpage", full=True)
            page.goto(BAR + "/"); page.wait_for_selector(".hero"); shot(page, "phone_barber_fullpage", full=True)
            # 1. a normal instant booking (Men's restyle, no deposit) -> confirmed
            booking_flow(page, LUX, "phone_luxury", service_index=1, staff_index=3)
            shot(page, "phone_luxury_book6_confirmed")
            # 2. a service with a deposit, no payment firm connected -> an honest request
            booking_flow(page, LUX, "x", service_index=0, staff_index=2, day_index=2, time_index=4, shots=False)
            shot(page, "phone_luxury_deposit_request")
            # 3. the time goes while the customer is typing -> told, and offered other times
            booking_flow(page, LUX, "x", service_index=6, staff_index=1, day_index=3, time_index=1, before_send=take_time_first, shots=False)
            page.locator("#berr").scroll_into_view_if_needed(); shot(page, "phone_luxury_slot_taken")
            # 4. no signal when pressing Book -> saved on the phone, clearly NOT booked
            booking_flow(page, LUX, "x", service_index=6, staff_index=0, day_index=4, time_index=3,
                         before_send=lambda pg: ctx.set_offline(True), shots=False)
            shot(page, "phone_luxury_offline_not_booked"); ctx.set_offline(False); page.wait_for_timeout(1500)
            to_book(page); shot(page, "phone_luxury_back_online_sent")
            # 5. walk-in queue: join, ticket, then signal lost
            page.goto(BAR + "/#queue"); page.wait_for_selector("#qn")
            page.evaluate("document.querySelector('#queue').scrollIntoView()")
            shot(page, "phone_barber_queue_join")
            page.fill("#qn", "Test (demo)"); page.fill("#qp", "07700 900333"); page.click("#qgo"); page.wait_for_timeout(1200)
            page.evaluate("document.querySelector('#queue').scrollIntoView()")
            shot(page, "phone_barber_queue_ticket")
            ctx.set_offline(True); page.evaluate("renderQueue()"); page.wait_for_timeout(1000)
            page.evaluate("document.querySelector('#queue').scrollIntoView()")
            shot(page, "phone_barber_queue_no_signal"); ctx.set_offline(False)
            # 6. same phone tries to join twice
            page.evaluate("localStorage.removeItem('queue_ticket'); S.ticket=''; renderQueue()"); page.wait_for_selector("#qn")
            page.fill("#qn", "Test again (demo)"); page.fill("#qp", "07700 900333"); page.click("#qgo"); page.wait_for_timeout(900)
            page.evaluate("document.querySelector('#queue').scrollIntoView()")
            shot(page, "phone_barber_queue_same_phone_refused")
            # 7. Arabic (right-to-left)
            page.goto(LUX + "/"); page.wait_for_selector("#lang"); page.select_option("#lang", "ar"); page.wait_for_timeout(800)
            shot(page, "phone_luxury_arabic_rtl")
            page.evaluate("localStorage.setItem('lang','en')")
            # 8. static copy (no always-on server) -> WhatsApp request
            page.goto(STA + "/"); page.wait_for_selector(".hero"); shot(page, "phone_static_copy_home")
            booking_flow(page, STA, "x", service_index=1, staff_index=1, shots=False)
            shot(page, "phone_static_copy_whatsapp_request")
        else:
            booking_flow(page, BAR, "tablet_barber", service_index=1, staff_index=1)
            shot(page, "tablet_barber_book6_confirmed")
            page.goto(BAR + "/queue"); page.wait_for_timeout(1500); shot(page, "tablet_queue_board")
            admin(page, LUX, "tablet_luxury", ["today", "bookings", "modules", "clients"], full_tabs=("modules", "bookings"))
            admin(page, BAR, "tablet_barber", ["queue", "modules"])
        ctx.close()
    ctx = b.new_context(viewport={"width": 1280, "height": 720}); page = ctx.new_page()
    page.goto(BAR + "/queue"); page.wait_for_timeout(1500); shot(page, "tv_queue_board"); ctx.close()
    ctx = b.new_context(**DEV["phone"]); page = ctx.new_page()
    admin(page, BAR, "phone_barber", ["queue", "modules"]); admin(page, LUX, "phone_luxury", ["bookings"], full_tabs=()); ctx.close()
    ctx = b.new_context(viewport={"width": 1440, "height": 1000}); page = ctx.new_page()
    page.goto(STU + "/#/cards"); page.wait_for_selector("[data-mod]", state="attached", timeout=15000); page.wait_for_timeout(800); shot(page, "studio_card_apps")
    ctx.close()
    b.close()
