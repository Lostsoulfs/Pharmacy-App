"""UI layer — Tkinter, Pydroid 3 target.

PharmacyApp: login, auth + lockout, nav shell, and all feature panels
(home, quiz, tools, calculators, law, admin, tpr, hotkeys, partials,
vaccines, sig, lookup). Phone-oriented: vertical scroll, large touch
targets. Clinical/law entries show the UNVERIFIED tag (ADR-C05).
"""

import time
import random
import difflib
import sqlite3
from datetime import datetime
import tkinter as tk
from tkinter import simpledialog, messagebox

from .config import (LOCKOUT_THRESHOLD, LOCKOUT_SECONDS,
                     is_unverified, verified_on)
from .theme import (BG, PANEL, TEXT, ACCENT, DIM, GREEN, RED,
                    FONT_HEADING, FONT_BODY, FONT_BUTTON)
from .clinical_data import (RED_FLAGS, LASA_PAIRS, SIG_ABBREVIATIONS,
                            COMMON_RX_FLAGS, BRAND_GENERIC, VACCINES,
                            LAW_BULLETS, TPR_CODES)
from .logic import (calc_insulin_logic, calc_days_supply_logic,
                    verify_dea_logic, dea_registrant_type,
                    calc_crcl_cockcroft_gault, calc_bsa_mosteller,
                    calc_peds_dose, answer_matches, is_strong_pin,
                    calculate_weight, sm2_update)
from .validation import (validate_filter_text, validate_inventory_entry,
                         validate_lookup_query, validate_partial_fill,
                         validate_sig_tokens)
from .data import (get_db_connection, init_db, db_log_audit, db_add_user,
                    db_remove_user, db_verify_pin, db_user_has_pin,
                    db_list_users,
                    db_get_state, db_set_state, db_perf, db_record_score,
                    db_list_backups,
                    db_restore, db_open_partials_count,
                    db_expired_inventory, db_backup, db_export_inventory,
                    db_export_audit_log, db_mastered_brands,
                    db_recent_scores, db_weak_spots, ptcb_readiness,
                    db_inventory_expiring, db_inventory_list,
                    db_audit_log, db_open_partials,
                    db_mark_mastered, db_get_mastery_stats,
                    db_upsert_mastery_stats, db_add_inventory,
                    db_remove_inventory, db_add_partial, db_update_partial,
                    db_resolve_partial)


class PharmacyApp:
    def __init__(self, root):
        self.root = root
        self.user = None
        self.is_admin = False
        # Lockout window persists in AppState (survives app restart);
        # fail counter is in-memory (fresh count per launch is fine —
        # the lockout timestamp is the security-relevant part).
        self._admin_fails = 0
        # T7.7 — audit log filter persists across re-renders of
        # panel_admin. Empty string = no filter.
        self._audit_filter = ""
        # T7.12 — inventory drug-name filter, same persistence pattern.
        self._inv_filter = ""

        root.title("Pharmacy OS")
        try:
            root.geometry("420x860")  # Pydroid fullscreens; hint only
        except Exception:
            pass
        root.configure(bg=BG)
        self.container = tk.Frame(root, bg=BG)
        self.container.pack(fill="both", expand=True)

        init_db()
        self.login_screen()

    # ---- helpers ----
    def _clear(self):
        # Drop the application-wide wheel handler the outgoing view
        # may have bound (make_scrollable uses bind_all).
        self.container.unbind_all("<MouseWheel>")
        for w in self.container.winfo_children():
            w.destroy()

    def make_scrollable(self, parent):
        """Vertical scroll area; inner width synced to canvas so content
        fills a narrow phone screen."""
        canvas = tk.Canvas(parent, bg=BG, highlightthickness=0)
        sb = tk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        inner = tk.Frame(canvas, bg=BG)
        win = canvas.create_window((0, 0), window=inner, anchor="nw")
        inner.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas.bind(
            "<Configure>",
            lambda e: canvas.itemconfigure(win, width=e.width),
        )
        canvas.configure(yscrollcommand=sb.set)
        canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        # Desktop wheel; on-device touch-drag is Scott's to verify.
        # bind_all is application-wide, so drop any handler a previous
        # panel left bound before adding this canvas's own — otherwise
        # handlers stack and fire yview_scroll on destroyed canvases.
        canvas.unbind_all("<MouseWheel>")
        canvas.bind_all(
            "<MouseWheel>",
            lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"),
        )
        return inner

    # ---- auth ----
    def login_screen(self):
        self._clear()
        f = tk.Frame(self.container, bg=BG)
        f.pack(fill="both", expand=True)
        tk.Label(f, text="Pharmacy OS", bg=BG, fg=ACCENT,
                 font=("Segoe UI", 26, "bold")).pack(pady=28)
        admins, techs = db_list_users()
        for a in admins:
            tk.Button(f, text="%s (Admin)" % a, font=FONT_BUTTON, bg=PANEL,
                      fg=TEXT, height=2, bd=0,
                      command=lambda n=a: self._admin_login(n)
                      ).pack(fill="x", padx=24, pady=8)
        tk.Label(f, text="--- Technicians ---", bg=BG, fg=DIM,
                 font=FONT_BODY).pack(pady=12)
        for t in techs:
            tk.Button(f, text=t, font=FONT_BUTTON, bg=PANEL, fg=TEXT,
                      height=2, bd=0,
                      command=lambda n=t: self._tech_login(n)
                      ).pack(fill="x", padx=24, pady=6)
        if not techs:
            tk.Label(f, text="(no technicians yet — add in Admin Control)",
                     bg=BG, fg=DIM, font=FONT_BODY).pack(pady=6)

    def _admin_login(self, name):
        now = time.time()
        lock_until = float(db_get_state("admin_lock_until", "0") or "0")
        if now < lock_until:
            secs = int(lock_until - now)
            messagebox.showerror(
                "Locked", "Admin access locked for %d seconds." % secs)
            return
        pin = simpledialog.askstring(
            "Admin", "Enter PIN:", show="*", parent=self.root)
        if pin is None:
            return
        if db_verify_pin(name, pin):
            self._admin_fails = 0
            db_set_state("admin_lock_until", "0")
            if pin == "1234":
                self._force_pin_change(name)
            self._enter(name, admin=True)
        else:
            self._admin_fails += 1
            remaining = LOCKOUT_THRESHOLD - self._admin_fails
            if remaining <= 0:
                db_set_state("admin_lock_until", str(now + LOCKOUT_SECONDS))
                self._admin_fails = 0
                messagebox.showerror(
                    "Locked",
                    "Admin access locked for %d seconds." % LOCKOUT_SECONDS)
            else:
                messagebox.showerror(
                    "Denied",
                    "Invalid PIN. %d attempt(s) before lockout." % remaining)

    def _force_pin_change(self, name):
        messagebox.showinfo(
            "Security", "Default PIN in use. Set a new admin PIN.")
        while True:
            new = simpledialog.askstring(
                "Set PIN", "New admin PIN (min 4 chars):",
                show="*", parent=self.root)
            if new is None:
                continue  # forced — cannot cancel out
            # old_pin='1234': forced change only triggers on default
            # login, so this also blocks reverting to the default.
            ok, reason = is_strong_pin(new, old_pin="1234")
            if not ok:
                messagebox.showerror("Invalid", reason)
                continue
            # Confirmation re-entry: masked field gives no echo, so a
            # silent typo here would lock the admin out of a PIN they
            # cannot reproduce. Require an exact second entry.
            confirm = simpledialog.askstring(
                "Set PIN", "Re-enter new PIN to confirm:",
                show="*", parent=self.root)
            if confirm != new:
                messagebox.showerror(
                    "Mismatch", "PINs did not match. Set it again.")
                continue
            db_add_user(name, "admin", new)
            messagebox.showinfo("Security", "Admin PIN updated.")
            return

    def _tech_login(self, name):
        # Technicians may carry an optional PIN (set via Add Tech).
        # When one is set it must be entered — otherwise a
        # PIN-protected tech account opens for anyone who taps it.
        if db_user_has_pin(name):
            pin = simpledialog.askstring(
                "Technician", "Enter PIN:", show="*", parent=self.root)
            if pin is None:
                return
            if not db_verify_pin(name, pin):
                messagebox.showerror("Denied", "Invalid PIN.")
                return
        self._enter(name, admin=False)

    def _enter(self, name, admin):
        self.user = name
        self.is_admin = admin
        db_log_audit(name, "Logged In")
        self._build_shell()
        self.navigate_to("home")
        # T7.11 + T7.15 — Login briefing. Combines expired-stock alert
        # with open-partials count into one popup so users get the
        # full shift-start picture in one place, not two popups.
        expired = db_expired_inventory()
        open_partials = db_open_partials_count()
        sections = []
        if expired:
            lines = ["%s  —  expired %s" % (d, e) for d, e in expired]
            shown = lines[:10]
            if len(lines) > len(shown):
                shown.append("...and %d more." % (len(lines) - len(shown)))
            sections.append(
                "EXPIRED STOCK — do not dispense:\n" + "\n".join(shown))
        if open_partials > 0:
            sections.append(
                "OPEN PARTIALS: %d unresolved on the ledger."
                % open_partials)
        if sections:
            messagebox.showwarning(
                "Shift Briefing",
                "\n\n".join(sections))

    def logout(self):
        if self.user:
            db_log_audit(self.user, "Logged Out")
        self.user = None
        self.is_admin = False
        # A2 fix: clear UI filter state so it doesn't leak across
        # users. Otherwise admin A's filter persists into admin B's
        # next session — confusing at best, security signal at worst.
        self._audit_filter = ""
        self._inv_filter = ""
        self.login_screen()

    # ---- shell + routing ----
    def _build_shell(self):
        self._clear()
        self.shell = tk.Frame(self.container, bg=BG)
        self.shell.pack(fill="both", expand=True)
        top = tk.Frame(self.shell, bg=PANEL)
        top.pack(fill="x")
        tk.Label(top, text="User: %s" % self.user, bg=PANEL, fg=ACCENT,
                 font=FONT_BUTTON).pack(side="left", padx=8, pady=6)
        tk.Button(top, text="Logout", bg=RED, fg=BG, font=FONT_BUTTON,
                  bd=0, command=self.logout).pack(side="right", padx=8, pady=4)
        nav = tk.Frame(self.shell, bg=BG)
        nav.pack(fill="x")
        items = [("Home", "home"), ("Training", "quiz"),
                 ("Tools", "tools"), ("Calc", "calculators"),
                 ("Law", "law")]
        if self.is_admin:
            items.append(("Admin", "admin"))
        for label, route in items:
            tk.Button(nav, text=label, bg=PANEL, fg=TEXT, font=FONT_BUTTON,
                      bd=0, command=lambda r=route: self.navigate_to(r)
                      ).pack(side="left", expand=True, fill="x",
                             padx=2, pady=4)
        self.content_host = tk.Frame(self.shell, bg=BG)
        self.content_host.pack(fill="both", expand=True)

    def navigate_to(self, target):
        for w in self.content_host.winfo_children():
            w.destroy()
        routes = {
            "home": self.panel_home,
            "quiz": self.panel_quiz,
            "tools": self.panel_tools,
            "calculators": self.panel_calculators,
            "law": self.panel_law,
            "admin": self.panel_admin,
            "tpr": self.panel_tpr,
            "hotkeys": self.panel_hotkeys,
            "partials": self.panel_partials,
            "vaccines": self.panel_vaccines,
            "sig": self.panel_sig,
            "lookup": self.panel_lookup,
        }
        fn = routes.get(target)
        if fn:
            fn()

    # ---- panels ----
    def _unverified_banner(self, host, domains, text=None, pady=(0, 8)):
        """Render the ADR-C05 data-status line. `domains` is a list of
        config.DATA_VERIFIED keys this panel renders. Shows a red
        UNVERIFIED warning until every listed domain is verified, then
        a small dated confirmation."""
        if is_unverified(domains):
            if text is None:
                text = ("⚠ UNVERIFIED DATA — not externally "
                        "validated.")
            tk.Label(host, text=text, bg=BG, fg=RED, font=FONT_BODY,
                     wraplength=360, justify="left").pack(
                         padx=14, pady=pady)
            return
        tk.Label(host, text="✓ Verified data (%s)" % verified_on(domains),
                 bg=BG, fg=GREEN, font=FONT_BODY, wraplength=360,
                 justify="left").pack(padx=14, pady=pady)

    def panel_home(self):
        host = self.make_scrollable(self.content_host)
        title = "Home Dashboard" if self.is_admin else "Station Dashboard"
        tk.Label(host, text=title, bg=BG, fg=TEXT,
                 font=FONT_HEADING).pack(pady=14)

        # Shift Notes
        sn = tk.Frame(host, bg=PANEL)
        sn.pack(fill="x", padx=16, pady=8)
        tk.Label(sn, text="Shift Notes", bg=PANEL, fg=ACCENT,
                 font=FONT_BUTTON).pack(anchor="w", padx=10, pady=(8, 2))
        tk.Label(sn, text=db_get_state("shift_notes",
                                       "Welcome to your shift."),
                 bg=PANEL, fg=TEXT, font=FONT_BODY, wraplength=340,
                 justify="left").pack(anchor="w", padx=10, pady=(0, 10))

        # T7.1 — Expiration alerts. Inventory rows expiring within the
        # next 30 days (or already expired). ISO date strings sort
        # lexicographically, so SQLite string compare is correct here.
        today = datetime.now().strftime("%Y-%m-%d")
        expiring = db_inventory_expiring(within_days=30)

        ef = tk.Frame(host, bg=PANEL)
        ef.pack(fill="x", padx=16, pady=8)
        tk.Label(ef, text="Expiration Alerts (≤ 30 days)",
                 bg=PANEL, fg=ACCENT, font=FONT_BUTTON).pack(
                     anchor="w", padx=10, pady=(8, 2))
        if not expiring:
            tk.Label(ef, text="No upcoming expirations.",
                     bg=PANEL, fg=DIM, font=FONT_BODY).pack(
                         anchor="w", padx=10, pady=(0, 10))
        else:
            for drug_name, exp_date in expiring:
                is_expired = exp_date <= today
                color = RED if is_expired else ACCENT
                tag = "EXPIRED" if is_expired else "expires"
                tk.Label(
                    ef,
                    text="%s  —  %s %s" % (drug_name, tag, exp_date),
                    bg=PANEL, fg=color, font=FONT_BODY,
                    anchor="w", wraplength=320, justify="left"
                ).pack(anchor="w", padx=14, pady=2)
            tk.Frame(ef, bg=PANEL, height=6).pack()

        # Tech performance card
        if not self.is_admin:
            q, avg = db_perf(self.user)
            pf = tk.Frame(host, bg=PANEL)
            pf.pack(fill="x", padx=16, pady=8)
            tk.Label(pf, text="My Performance", bg=PANEL, fg=ACCENT,
                     font=FONT_BUTTON).pack(anchor="w", padx=10, pady=(8, 2))
            tk.Label(pf, text="Quizzes Completed: %d" % q, bg=PANEL,
                     fg=TEXT, font=FONT_BODY).pack(anchor="w", padx=10)
            tk.Label(pf, text="Average Score: %d%%" % avg, bg=PANEL,
                     fg=TEXT, font=FONT_BODY).pack(anchor="w", padx=10,
                                                   pady=(0, 10))

            # T7.3 — PTCB readiness. Counts distinct mastered drugs
            # from PTCBMastery for this tech, against BRAND_GENERIC pool.
            mastered, total, pct = ptcb_readiness(self.user)
            rf = tk.Frame(host, bg=PANEL)
            rf.pack(fill="x", padx=16, pady=8)
            tk.Label(rf, text="PTCB Readiness", bg=PANEL, fg=ACCENT,
                     font=FONT_BUTTON).pack(anchor="w", padx=10,
                                            pady=(8, 2))
            tk.Label(rf,
                     text="Mastered: %d / %d  (%d%%)" % (
                         mastered, total, pct),
                     bg=PANEL, fg=GREEN if pct >= 80 else TEXT,
                     font=FONT_BODY).pack(anchor="w", padx=10)
            tk.Label(rf,
                     text=("Ready for exam." if pct >= 80
                           else "Keep drilling Top 200 quiz."),
                     bg=PANEL, fg=DIM, font=FONT_BODY).pack(
                         anchor="w", padx=10, pady=(0, 10))

            # T7.5 — Weak Spots: top 5 drugs this tech misses most.
            weak = db_weak_spots(self.user, limit=5)
            wf = tk.Frame(host, bg=PANEL)
            wf.pack(fill="x", padx=16, pady=8)
            tk.Label(wf, text="Weak Spots — Drill These",
                     bg=PANEL, fg=ACCENT, font=FONT_BUTTON).pack(
                         anchor="w", padx=10, pady=(8, 4))
            if not weak:
                tk.Label(wf,
                         text="No miss data yet. Run a quiz to "
                              "see weak spots.",
                         bg=PANEL, fg=DIM, font=FONT_BODY,
                         wraplength=320, justify="left").pack(
                             anchor="w", padx=14, pady=(0, 10))
            else:
                for drug, missed, total, miss_pct in weak:
                    tk.Label(
                        wf,
                        text="%s  —  missed %d/%d  (%d%%)" % (
                            drug, missed, total, miss_pct),
                        bg=PANEL, fg=RED if miss_pct >= 50 else TEXT,
                        font=FONT_BODY, anchor="w",
                        wraplength=320, justify="left"
                    ).pack(anchor="w", padx=14, pady=2)
                tk.Frame(wf, bg=PANEL, height=6).pack()

            # T7.6 — Recent Quizzes: last 10 sessions, newest first.
            recent = db_recent_scores(self.user, limit=10)
            rqf = tk.Frame(host, bg=PANEL)
            rqf.pack(fill="x", padx=16, pady=8)
            tk.Label(rqf, text="Recent Quizzes",
                     bg=PANEL, fg=ACCENT, font=FONT_BUTTON).pack(
                         anchor="w", padx=10, pady=(8, 4))
            if not recent:
                tk.Label(rqf,
                         text="No quizzes recorded yet.",
                         bg=PANEL, fg=DIM, font=FONT_BODY).pack(
                             anchor="w", padx=14, pady=(0, 10))
            else:
                for date, correct, total, pct in recent:
                    if pct >= 80:
                        col = GREEN
                    elif pct >= 50:
                        col = TEXT
                    else:
                        col = RED
                    tk.Label(
                        rqf,
                        text="%s  —  %d / %d  (%d%%)" % (
                            date, correct, total, pct),
                        bg=PANEL, fg=col, font=FONT_BODY,
                        anchor="w", wraplength=320, justify="left"
                    ).pack(anchor="w", padx=14, pady=1)
                tk.Frame(rqf, bg=PANEL, height=6).pack()

    def panel_tools(self):
        host = self.make_scrollable(self.content_host)
        tk.Label(host, text="Clinical Tools", bg=BG, fg=TEXT,
                 font=FONT_HEADING).pack(pady=14)
        for label, route in [("SIG Decoder", "sig"),
                             ("Drug Lookup", "lookup"),
                             ("Vaccine Eligibility", "vaccines"),
                             ("Partial Fill Ledger", "partials"),
                             ("TPR Insurance Guide", "tpr"),
                             ("IC+ Hotkeys", "hotkeys")]:
            tk.Button(host, text=label, bg=PANEL, fg=TEXT, font=FONT_BUTTON,
                      height=2, bd=0,
                      command=lambda r=route: self.navigate_to(r)
                      ).pack(fill="x", padx=24, pady=6)

    # ---- T5.1: panel_quiz (Training Center) ----
    # C06-EARS: Carried from v13 methods panel_quiz_picker, launch_quiz,
    # show_question, check_answer. Per-user mastery tracking + adaptive
    # hard mode. Quiz modes: b2g (brand->generic), g2b (generic->brand),
    # hard (weighted by missed), redflag (clinical red flags), lasa
    # (look-alike/sound-alike). Session = 10 questions; score saved to DB.
    # All quiz data (RED_FLAGS, LASA_PAIRS, BRAND_GENERIC) marked
    # UNVERIFIED per ADR-C05; UI renders visible warning.

    def panel_quiz(self):
        """Mode selection for quiz. Routes to launch_quiz(mode)."""
        host = self.make_scrollable(self.content_host)
        tk.Label(host, text="Training Center", bg=BG, fg=TEXT,
                 font=FONT_HEADING).pack(pady=12)
        self._unverified_banner(
            host, ["red_flags", "lasa_pairs", "brand_generic"])

        modes = [
            ("Top 200: Brand → Generic", "b2g"),
            ("Top 200: Generic → Brand", "g2b"),
            ("Smart Hard Mode (Focus Drugs)", "hard"),
            ("Red Flags & Scenarios", "redflag"),
            ("LASA (Look-Alike Sound-Alike)", "lasa")
        ]
        for label, mode_key in modes:
            tk.Button(host, text=label, font=FONT_BODY, bg=PANEL, fg=TEXT,
                      height=2, bd=0,
                      command=lambda m=mode_key: self.launch_quiz(m)
                      ).pack(fill="x", padx=14, pady=5)

    def launch_quiz(self, mode):
        """Initialize quiz state. Called by panel_quiz mode buttons."""
        self.quiz_mode = mode
        self.quiz_score = 0
        self.quiz_total = 0
        self.show_question()

    def show_question(self):
        """Render next quiz question. Clears content_host, draws question
        + entry field + submit button. Binds Return to check_answer."""
        for widget in self.content_host.winfo_children():
            widget.destroy()
        # The quiz question view is not scrollable; drop the wheel
        # handler the previous panel bound via make_scrollable.
        self.content_host.unbind_all("<MouseWheel>")

        main_f = tk.Frame(self.content_host, bg=BG)
        main_f.pack(fill="both", expand=True, padx=14, pady=12)

        # Select question based on mode
        if self.quiz_mode == "redflag":
            self.current_q = random.choice(RED_FLAGS)
            q_text = self.current_q["q"]
            self.correct_ans = self.current_q["a"]
        elif self.quiz_mode == "lasa":
            self.current_q = random.choice(LASA_PAIRS)
            q_text = self.current_q["q"]
            self.correct_ans = self.current_q["a"]
        else:
            # Drug-based quiz modes (b2g, g2b, hard)
            drugs = BRAND_GENERIC
            if self.quiz_mode == "hard":
                conn = None
                try:
                    conn = get_db_connection()
                    weights = [
                        calculate_weight(self.user, d["brand"], conn)
                        for d in drugs
                    ]
                    self.current_drug = random.choices(drugs, weights=weights, k=1)[0]
                except sqlite3.Error:
                    # DB unavailable -> uniform random fallback; a
                    # non-DB error is a real bug and now propagates.
                    self.current_drug = random.choice(drugs)
                finally:
                    if conn:
                        conn.close()
            else:
                self.current_drug = random.choice(drugs)

            if self.quiz_mode == "b2g":
                q_text = "What is the GENERIC for: %s?" % self.current_drug["brand"]
                self.correct_ans = self.current_drug["generic"]
            else:  # g2b
                q_text = "What is the BRAND for: %s?" % self.current_drug["generic"]
                self.correct_ans = self.current_drug["brand"]

        # Render question
        tk.Label(main_f, text="Question %d" % (self.quiz_total + 1),
                 font=FONT_BODY, bg=BG, fg=DIM).pack(pady=(0, 12))
        tk.Label(main_f, text=q_text, font=FONT_HEADING, bg=BG, fg=TEXT,
                 wraplength=500, justify="center").pack(pady=20)

        # Entry field
        self.ans_entry = tk.Entry(main_f, font=FONT_HEADING, bg=PANEL,
                                   fg=TEXT, insertbackground=TEXT,
                                   justify="center")
        self.ans_entry.pack(pady=10, ipady=10, fill="x")
        self.ans_entry.focus()
        self.ans_entry.bind("<Return>", lambda e: self.check_answer())

        # Submit button
        tk.Button(main_f, text="Submit Answer", font=FONT_BUTTON,
                  bg=ACCENT, fg=BG, bd=0, command=self.check_answer
                  ).pack(pady=20, fill="x")

    def check_answer(self):
        """Validate answer, update mastery stats, save score after 10 Qs.
        Fuzzy matching for scenarios (80%+ similarity via difflib);
        exact matching for drugs (answer_matches). Feedback via messagebox."""
        user_val = self.ans_entry.get().strip().lower()
        self.quiz_total += 1
        is_scenario = self.quiz_mode in ["redflag", "lasa"]
        is_correct = False

        # Validate answer
        if is_scenario:
            similarity = difflib.SequenceMatcher(None, user_val,
                                                 self.correct_ans.lower()).ratio()
            is_correct = similarity >= 0.8
        else:
            is_correct = answer_matches(user_val, self.correct_ans)

        # Track mastery stats (drug modes only). Persistence runs
        # through data.py helpers; this stays orchestration-only.
        if not is_scenario:
            drug_name = self.current_drug["brand"]
            try:
                if is_correct:
                    db_mark_mastered(self.user, drug_name)
                row = db_get_mastery_stats(self.user, drug_name)
                now_iso = datetime.now().isoformat(timespec="seconds")
                if row:
                    ease, interval, reps = sm2_update(
                        row["ease_factor"], row["interval_days"],
                        row["repetitions"], is_correct)
                    new_total = row["total"] + 1
                    new_correct = row["correct"] + (1 if is_correct else 0)
                else:
                    ease, interval, reps = sm2_update(
                        None, None, None, is_correct)
                    new_total = 1
                    new_correct = 1 if is_correct else 0
                db_upsert_mastery_stats(
                    self.user, drug_name, new_total, new_correct,
                    ease, interval, reps, now_iso)
            except sqlite3.Error:
                # Swallow DB errors only (mastery tracking is
                # non-critical); a real bug now propagates instead.
                pass

        # Feedback
        if is_correct:
            self.quiz_score += 1
            rat = self.current_q.get("rationale", "") if is_scenario else ""
            feedback = "Correct! %s" % self.correct_ans
            if rat:
                feedback += "\n%s" % rat
            messagebox.showinfo("Correct!", feedback)
        else:
            rat = self.current_q.get("rationale", "") if is_scenario else ""
            feedback = "Not quite. The answer was: %s" % self.correct_ans
            if rat:
                feedback += "\n%s" % rat
            messagebox.showerror("Incorrect", feedback)

        # End quiz or continue
        if self.quiz_total >= 10:
            try:
                db_record_score(self.user, self.quiz_score, 10)
            except sqlite3.Error:
                # Swallow DB errors only (score save is non-critical);
                # a real bug now propagates instead.
                pass
            self.navigate_to("home")
        else:
            self.show_question()

    def panel_calculators(self):
        host = self.make_scrollable(self.content_host)
        tk.Label(host, text="Calculators", bg=BG, fg=TEXT,
                 font=FONT_HEADING).pack(pady=12)

        def section(title):
            f = tk.Frame(host, bg=PANEL)
            f.pack(fill="x", padx=14, pady=8)
            tk.Label(f, text=title, bg=PANEL, fg=ACCENT,
                     font=FONT_BUTTON).pack(anchor="w", padx=10, pady=(8, 4))
            return f

        def field(parent, label):
            r = tk.Frame(parent, bg=PANEL)
            r.pack(fill="x", padx=10, pady=3)
            tk.Label(r, text=label, bg=PANEL, fg=TEXT, font=FONT_BODY,
                     width=16, anchor="w").pack(side="left")
            e = tk.Entry(r, font=FONT_BODY, bg=BG, fg=TEXT,
                         insertbackground=TEXT)
            e.pack(side="left", fill="x", expand=True, ipady=4)
            return e

        # --- Insulin days supply (calls calc_insulin_logic) ---
        ins = section("Insulin Days Supply")
        i_daily = field(ins, "Units/day")
        i_ml = field(ins, "Total mL")
        i_conc = field(ins, "Concentration")
        # T7.17 — F-06 fix. Priming units/day. Pens waste ~2u per
        # injection on priming; pharmacist enters
        # priming_per_injection * injections_per_day. Default 0 = vial.
        i_prime = field(ins, "Priming u/day")
        i_prime.insert(0, "0")
        i_res = tk.Label(ins, text="--", bg=PANEL, fg=DIM,
                         font=FONT_BUTTON)
        i_res.pack(pady=8)

        def run_insulin():
            try:
                days = calc_insulin_logic(
                    i_daily.get(), i_ml.get(), i_conc.get(),
                    i_prime.get() or "0")
                i_res.config(text="%d days supply" % days, fg=GREEN)
            except ValueError as e:
                i_res.config(text=str(e), fg=RED)

        tk.Button(ins, text="Calculate", bg=ACCENT, fg=BG,
                  font=FONT_BUTTON, bd=0, command=run_insulin
                  ).pack(fill="x", padx=10, pady=(0, 10))

        # --- Days supply (calls calc_days_supply_logic) ---
        ds = section("Days Supply")
        d_qty = field(ds, "Quantity")
        d_day = field(ds, "Units/day")
        d_res = tk.Label(ds, text="--", bg=PANEL, fg=DIM,
                         font=FONT_BUTTON)
        d_res.pack(pady=8)

        def run_days():
            try:
                days = calc_days_supply_logic(d_qty.get(), d_day.get())
                d_res.config(text="%d days supply" % days, fg=GREEN)
            except ValueError as e:
                d_res.config(text=str(e), fg=RED)

        tk.Button(ds, text="Calculate", bg=ACCENT, fg=BG,
                  font=FONT_BUTTON, bd=0, command=run_days
                  ).pack(fill="x", padx=10, pady=(0, 10))

        # --- DEA checksum (calls verify_dea_logic) ---
        dea = section("DEA Checksum")
        dea_e = field(dea, "DEA number")
        dea_res = tk.Label(dea, text="--", bg=PANEL, fg=DIM,
                           font=FONT_BUTTON)
        dea_res.pack(pady=8)

        def run_dea():
            raw = dea_e.get()
            checksum_ok = verify_dea_logic(raw)
            type_label, is_prescriber = dea_registrant_type(raw)
            if not checksum_ok:
                dea_res.config(text="INVALID / forgery flag", fg=RED)
                return
            # T7.20 — registrant-type flag. Non-prescriber prefix on a
            # dispensing prescription is itself a forgery signal.
            if type_label and not is_prescriber:
                dea_res.config(
                    text="Checksum OK — but %s — NOT a prescriber, "
                         "VERIFY before dispensing" % type_label,
                    fg=RED)
            elif type_label:
                dea_res.config(
                    text="VALID — %s" % type_label, fg=GREEN)
            else:
                dea_res.config(text="VALID checksum", fg=GREEN)

        tk.Button(dea, text="Verify", bg=ACCENT, fg=BG,
                  font=FONT_BUTTON, bd=0, command=run_dea
                  ).pack(fill="x", padx=10, pady=(0, 10))

        # --- T7.21: Cockcroft-Gault CrCl (renal dosing) ---
        cg = section("CrCl (Cockcroft-Gault)")
        cg_age = field(cg, "Age (years)")
        cg_wt = field(cg, "Weight (kg)")
        cg_scr = field(cg, "Serum Cr (mg/dL)")
        cg_sex_var = tk.StringVar(value="male")
        sex_row = tk.Frame(cg, bg=PANEL)
        sex_row.pack(fill="x", padx=10, pady=3)
        tk.Label(sex_row, text="Sex", bg=PANEL, fg=TEXT, font=FONT_BODY,
                 width=16, anchor="w").pack(side="left")
        tk.Radiobutton(sex_row, text="Male", variable=cg_sex_var,
                       value="male", bg=PANEL, fg=TEXT,
                       selectcolor=BG, font=FONT_BODY,
                       activebackground=PANEL).pack(side="left")
        tk.Radiobutton(sex_row, text="Female", variable=cg_sex_var,
                       value="female", bg=PANEL, fg=TEXT,
                       selectcolor=BG, font=FONT_BODY,
                       activebackground=PANEL).pack(side="left",
                                                     padx=(8, 0))
        cg_res = tk.Label(cg, text="--", bg=PANEL, fg=DIM,
                          font=FONT_BUTTON)
        cg_res.pack(pady=8)

        def run_cg():
            try:
                crcl = calc_crcl_cockcroft_gault(
                    cg_age.get(), cg_wt.get(), cg_scr.get(),
                    is_female=(cg_sex_var.get() == "female"))
                # Severity coloring per common renal-dosing bands.
                # Not a substitute for FDA package-insert dose
                # adjustment thresholds.
                if crcl < 30:
                    col = RED
                elif crcl < 60:
                    col = ACCENT
                else:
                    col = GREEN
                cg_res.config(
                    text="CrCl = %s mL/min" % crcl, fg=col)
            except ValueError as e:
                cg_res.config(text=str(e), fg=RED)

        tk.Button(cg, text="Estimate", bg=ACCENT, fg=BG,
                  font=FONT_BUTTON, bd=0, command=run_cg
                  ).pack(fill="x", padx=10, pady=(0, 4))
        tk.Label(cg,
                 text="Estimate only. Not for pediatrics, extremes "
                      "of weight, or unstable renal function. "
                      "Source: Cockcroft & Gault, Nephron 1976.",
                 bg=PANEL, fg=DIM, font=FONT_BODY,
                 wraplength=320, justify="left").pack(
                     anchor="w", padx=10, pady=(0, 10))

        # --- T7.22: BSA (Mosteller) for chemo / pediatric dosing ---
        bsa = section("BSA (Mosteller)")
        bsa_h = field(bsa, "Height (cm)")
        bsa_w = field(bsa, "Weight (kg)")
        bsa_res = tk.Label(bsa, text="--", bg=PANEL, fg=DIM,
                           font=FONT_BUTTON)
        bsa_res.pack(pady=8)

        def run_bsa():
            try:
                val = calc_bsa_mosteller(bsa_h.get(), bsa_w.get())
                bsa_res.config(text="BSA = %s m²" % val, fg=GREEN)
            except ValueError as e:
                bsa_res.config(text=str(e), fg=RED)

        tk.Button(bsa, text="Calculate", bg=ACCENT, fg=BG,
                  font=FONT_BUTTON, bd=0, command=run_bsa
                  ).pack(fill="x", padx=10, pady=(0, 4))
        tk.Label(bsa,
                 text="Source: Mosteller, NEJM 1987. FDA-cited for "
                      "chemo and pediatric weight-based dosing.",
                 bg=PANEL, fg=DIM, font=FONT_BODY,
                 wraplength=320, justify="left").pack(
                     anchor="w", padx=10, pady=(0, 10))

        # --- T7.23: Pediatric weight-based dose ---
        pd = section("Pediatric Dose (weight-based)")
        pd_wt = field(pd, "Weight (kg)")
        pd_mkd = field(pd, "mg/kg/day")
        pd_dpd = field(pd, "Doses/day")
        pd_conc = field(pd, "Conc (mg/mL)")
        pd_res = tk.Label(pd, text="--", bg=PANEL, fg=DIM,
                          font=FONT_BUTTON, justify="left",
                          wraplength=320)
        pd_res.pack(pady=8)

        def run_pd():
            try:
                mgd, mld = calc_peds_dose(
                    pd_wt.get(), pd_mkd.get(),
                    pd_dpd.get(), pd_conc.get())
                pd_res.config(
                    text="Per dose: %s mg  /  %s mL" % (mgd, mld),
                    fg=GREEN)
            except ValueError as e:
                pd_res.config(text=str(e), fg=RED)

        tk.Button(pd, text="Calculate", bg=ACCENT, fg=BG,
                  font=FONT_BUTTON, bd=0, command=run_pd
                  ).pack(fill="x", padx=10, pady=(0, 4))
        tk.Label(pd,
                 text="Concentration: enter as mg/mL "
                      "(250 mg/5 mL suspension = 50 mg/mL). "
                      "Pharmacist verifies max-daily-dose and "
                      "appropriateness independently.",
                 bg=PANEL, fg=DIM, font=FONT_BODY,
                 wraplength=320, justify="left").pack(
                     anchor="w", padx=10, pady=(0, 10))

    def panel_law(self):
        # T5.2 + T7.19 — panel_law. Renders clinical_data.LAW_BULLETS
        # (verified 2026-05-20 against MS Board of Pharmacy
        # regulations) grouped by category.
        host = self.make_scrollable(self.content_host)
        tk.Label(host, text="Mississippi Pharmacy Law & Safety",
                 bg=BG, fg=TEXT, font=FONT_HEADING).pack(pady=12)
        self._unverified_banner(host, ["law"])
        tk.Label(host,
                 text=("Source of truth: Mississippi Board of "
                       "Pharmacy regulations — Miss. Admin. Code "
                       "Title 30, Part 3001 (mbp.ms.gov). Re-verify "
                       "against the current regulations; state law "
                       "changes."),
                 bg=BG, fg=DIM, font=FONT_BODY, wraplength=360,
                 justify="left").pack(padx=14, pady=(0, 8))

        last_cat = None
        for entry in LAW_BULLETS:
            if entry["category"] != last_cat:
                last_cat = entry["category"]
                tk.Label(host, text=last_cat, bg=BG, fg=ACCENT,
                         font=FONT_BUTTON, anchor="w").pack(
                             fill="x", padx=14, pady=(10, 2))
            row = tk.Frame(host, bg=PANEL)
            row.pack(fill="x", padx=14, pady=2)
            tk.Label(row, text="•", bg=PANEL, fg=ACCENT,
                     font=FONT_BUTTON).pack(side="left", anchor="n",
                                            padx=(8, 6), pady=4)
            tk.Label(row, text=entry["rule"], bg=PANEL, fg=TEXT,
                     font=FONT_BODY, wraplength=300, justify="left",
                     anchor="w").pack(side="left", fill="x",
                                      expand=True, pady=4)

    def panel_admin(self):
        # T5.3 — admin control. DB-backed. Admin-only guard.
        # Reuses db_add_user / db_remove_user / db_list_users / db_log_audit /
        # is_strong_pin. Inventory + AuditLog read inline (no helper churn).
        host = self.make_scrollable(self.content_host)
        tk.Label(host, text="Admin Control", bg=BG, fg=TEXT,
                 font=FONT_HEADING).pack(pady=12)
        if not self.is_admin:
            tk.Label(host, text="Admin only.", bg=BG, fg=RED,
                     font=FONT_BUTTON).pack(pady=20)
            return

        # ---- Shift Notes Editor (T7.2) ----
        notes_card = tk.Frame(host, bg=PANEL)
        notes_card.pack(fill="x", padx=14, pady=8)
        tk.Label(notes_card, text="Shift Notes Editor", bg=PANEL,
                 fg=ACCENT, font=FONT_BUTTON).pack(
                     anchor="w", padx=10, pady=(8, 4))
        notes_txt = tk.Text(notes_card, bg=BG, fg=TEXT, font=FONT_BODY,
                            height=4, bd=0, wrap="word",
                            insertbackground=TEXT, padx=8, pady=6)
        notes_txt.pack(fill="x", padx=10, pady=2)
        notes_txt.insert(
            "1.0",
            db_get_state("shift_notes", "Welcome to your shift."))
        tk.Button(notes_card, text="Save Notes", bg=ACCENT, fg=BG,
                  font=FONT_BUTTON, bd=0,
                  command=lambda: self._admin_save_notes(
                      notes_txt.get("1.0", "end"))
                  ).pack(fill="x", padx=10, pady=(6, 10))

        # ---- Staff Roster ----
        roster = tk.Frame(host, bg=PANEL)
        roster.pack(fill="x", padx=14, pady=8)
        tk.Label(roster, text="Staff Roster", bg=PANEL, fg=ACCENT,
                 font=FONT_BUTTON).pack(anchor="w", padx=10, pady=(8, 4))
        admins, techs = db_list_users()
        for a in admins:
            tk.Label(roster, text="%s  (admin)" % a, bg=PANEL, fg=DIM,
                     font=FONT_BODY, anchor="w").pack(
                         anchor="w", padx=14, pady=2)
        for t in techs:
            row = tk.Frame(roster, bg=PANEL)
            row.pack(fill="x", padx=10, pady=2)
            tk.Label(row, text=t, bg=PANEL, fg=TEXT, font=FONT_BODY,
                     anchor="w").pack(side="left", fill="x", expand=True,
                                       padx=4)
            # T7.13 — Audit shortcut: sets audit filter to this tech
            # and redraws. Compounds with T7.7's filter mechanism.
            tk.Button(row, text="Audit", bg=DIM, fg=BG,
                      font=FONT_BUTTON, bd=0,
                      command=lambda n=t: self._admin_audit_filter(n)
                      ).pack(side="right", padx=4)
            tk.Button(row, text="Remove", bg=RED, fg=BG,
                      font=FONT_BUTTON, bd=0,
                      command=lambda n=t: self._admin_remove_tech(n)
                      ).pack(side="right", padx=4)
        if not techs:
            tk.Label(roster, text="(no technicians)", bg=PANEL, fg=DIM,
                     font=FONT_BODY).pack(anchor="w", padx=14, pady=2)

        add_f = tk.Frame(roster, bg=PANEL)
        add_f.pack(fill="x", padx=10, pady=(8, 10))
        tk.Label(add_f, text="Add Technician:", bg=PANEL, fg=TEXT,
                 font=FONT_BODY).pack(anchor="w")
        name_e = tk.Entry(add_f, font=FONT_BODY, bg=BG, fg=TEXT,
                          insertbackground=TEXT)
        name_e.pack(fill="x", pady=2, ipady=4)
        tk.Label(add_f, text="Optional PIN (min 4):", bg=PANEL, fg=DIM,
                 font=FONT_BODY).pack(anchor="w", pady=(4, 0))
        pin_e = tk.Entry(add_f, font=FONT_BODY, bg=BG, fg=TEXT,
                         insertbackground=TEXT, show="*")
        pin_e.pack(fill="x", pady=2, ipady=4)
        tk.Button(add_f, text="Add Tech", bg=ACCENT, fg=BG,
                  font=FONT_BUTTON, bd=0,
                  command=lambda: self._admin_add_tech(
                      name_e.get(), pin_e.get())
                  ).pack(fill="x", pady=(6, 0))

        # ---- Class PTCB Readiness (T7.4) ----
        # Per-tech mastery against the BRAND_GENERIC pool. Color bands:
        # >=80 GREEN, >=50 ACCENT, <50 RED. Empty roster shows hint.
        cr = tk.Frame(host, bg=PANEL)
        cr.pack(fill="x", padx=14, pady=8)
        tk.Label(cr, text="Class PTCB Readiness", bg=PANEL, fg=ACCENT,
                 font=FONT_BUTTON).pack(anchor="w", padx=10, pady=(8, 4))
        if not techs:
            tk.Label(cr, text="(no technicians on roster)",
                     bg=PANEL, fg=DIM, font=FONT_BODY).pack(
                         anchor="w", padx=14, pady=(2, 10))
        else:
            for t in techs:
                m_count, m_total, m_pct = ptcb_readiness(t)
                if m_pct >= 80:
                    col = GREEN
                elif m_pct >= 50:
                    col = ACCENT
                else:
                    col = RED
                tk.Label(
                    cr,
                    text="%s  —  %d / %d  (%d%%)" % (
                        t, m_count, m_total, m_pct),
                    bg=PANEL, fg=col, font=FONT_BODY,
                    anchor="w", wraplength=320, justify="left"
                ).pack(anchor="w", padx=14, pady=2)
            tk.Frame(cr, bg=PANEL, height=6).pack()

        # ---- Inventory / Expiration (T5.3 + T7.12 filter) ----
        inv = tk.Frame(host, bg=PANEL)
        inv.pack(fill="x", padx=14, pady=8)
        inv_header = ("Inventory / Expiration (filter: '%s')"
                      % self._inv_filter
                      if self._inv_filter
                      else "Inventory / Expiration")
        tk.Label(inv, text=inv_header, bg=PANEL, fg=ACCENT,
                 font=FONT_BUTTON).pack(anchor="w", padx=10, pady=(8, 4))

        # T7.12 — drug-name filter. Parameterized LIKE; case-insensitive
        # via SQLite default for ASCII.
        ifilt = tk.Frame(inv, bg=PANEL)
        ifilt.pack(fill="x", padx=10, pady=(2, 6))
        ifilt_e = tk.Entry(ifilt, font=FONT_BODY, bg=BG, fg=TEXT,
                           insertbackground=TEXT)
        ifilt_e.insert(0, self._inv_filter)
        ifilt_e.pack(side="left", fill="x", expand=True, ipady=4)
        tk.Button(ifilt, text="Find", bg=ACCENT, fg=BG,
                  font=FONT_BUTTON, bd=0,
                  command=lambda: self._admin_inv_filter(ifilt_e.get())
                  ).pack(side="left", padx=(6, 0))
        if self._inv_filter:
            tk.Button(ifilt, text="Clear", bg=DIM, fg=BG,
                      font=FONT_BUTTON, bd=0,
                      command=lambda: self._admin_inv_filter("")
                      ).pack(side="left", padx=(6, 0))

        # A5 fix (LIKE-wildcard escaping) now lives in db_inventory_list.
        inv_rows = db_inventory_list(self._inv_filter)
        if not inv_rows:
            empty_msg = ("(no matches)" if self._inv_filter
                         else "(no inventory)")
            tk.Label(inv, text=empty_msg, bg=PANEL, fg=DIM,
                     font=FONT_BODY).pack(anchor="w", padx=14, pady=2)
        for drug_name, exp_date in inv_rows:
            row = tk.Frame(inv, bg=PANEL)
            row.pack(fill="x", padx=10, pady=2)
            tk.Label(row,
                     text="%s — exp %s" % (drug_name, exp_date),
                     bg=PANEL, fg=TEXT, font=FONT_BODY,
                     anchor="w").pack(side="left", fill="x", expand=True,
                                       padx=4)
            tk.Button(row, text="Remove", bg=RED, fg=BG,
                      font=FONT_BUTTON, bd=0,
                      command=lambda d=drug_name:
                          self._admin_remove_inv(d)
                      ).pack(side="right", padx=4)

        add_inv = tk.Frame(inv, bg=PANEL)
        add_inv.pack(fill="x", padx=10, pady=(8, 10))
        tk.Label(add_inv, text="Add Drug:", bg=PANEL, fg=TEXT,
                 font=FONT_BODY).pack(anchor="w")
        drug_e = tk.Entry(add_inv, font=FONT_BODY, bg=BG, fg=TEXT,
                          insertbackground=TEXT)
        drug_e.pack(fill="x", pady=2, ipady=4)
        tk.Label(add_inv, text="Expiration date (YYYY-MM-DD):",
                 bg=PANEL, fg=DIM, font=FONT_BODY).pack(
                     anchor="w", pady=(4, 0))
        exp_e = tk.Entry(add_inv, font=FONT_BODY, bg=BG, fg=TEXT,
                         insertbackground=TEXT)
        exp_e.pack(fill="x", pady=2, ipady=4)
        tk.Button(add_inv, text="Add", bg=ACCENT, fg=BG,
                  font=FONT_BUTTON, bd=0,
                  command=lambda: self._admin_add_inv(
                      drug_e.get(), exp_e.get())
                  ).pack(fill="x", pady=(6, 0))

        # T7.16 — Inventory export (stock-count audit use).
        tk.Button(inv, text="Export Inventory",
                  bg=ACCENT, fg=BG, font=FONT_BUTTON, bd=0,
                  command=self._admin_export_inventory
                  ).pack(fill="x", padx=10, pady=(4, 10))

        # ---- Audit Log Viewer (T5.3 + T7.7 filter) ----
        log_f = tk.Frame(host, bg=PANEL)
        log_f.pack(fill="x", padx=14, pady=8)
        header = ("Audit Log (latest 50, filter: '%s')" % self._audit_filter
                  if self._audit_filter
                  else "Audit Log (latest 50)")
        tk.Label(log_f, text=header, bg=PANEL, fg=ACCENT,
                 font=FONT_BUTTON).pack(anchor="w", padx=10, pady=(8, 4))

        # T7.7 filter form. Matches user OR action via parameterized LIKE.
        filt_row = tk.Frame(log_f, bg=PANEL)
        filt_row.pack(fill="x", padx=10, pady=(2, 6))
        filt_e = tk.Entry(filt_row, font=FONT_BODY, bg=BG, fg=TEXT,
                          insertbackground=TEXT)
        filt_e.insert(0, self._audit_filter)
        filt_e.pack(side="left", fill="x", expand=True, ipady=4)
        tk.Button(filt_row, text="Filter", bg=ACCENT, fg=BG,
                  font=FONT_BUTTON, bd=0,
                  command=lambda: self._admin_audit_filter(filt_e.get())
                  ).pack(side="left", padx=(6, 0))
        if self._audit_filter:
            tk.Button(filt_row, text="Clear", bg=DIM, fg=BG,
                      font=FONT_BUTTON, bd=0,
                      command=lambda: self._admin_audit_filter("")
                      ).pack(side="left", padx=(6, 0))

        # A5 fix (LIKE-wildcard escaping) now lives in db_audit_log.
        entries = db_audit_log(self._audit_filter, limit=50)
        if not entries:
            empty_msg = ("(no matches)" if self._audit_filter
                         else "(empty)")
            tk.Label(log_f, text=empty_msg, bg=PANEL, fg=DIM,
                     font=FONT_BODY).pack(anchor="w", padx=14, pady=(2, 10))
        for timestamp, user, action in entries:
            tk.Label(log_f,
                     text="%s  %s  —  %s" % (timestamp, user, action),
                     bg=PANEL, fg=TEXT, font=FONT_BODY, wraplength=340,
                     justify="left",
                     anchor="w").pack(anchor="w", padx=14, pady=1)

        # T7.9 — Export. Always exports the FULL AuditLog table, not
        # just the latest-50 view or the current filter.
        tk.Button(log_f, text="Export Full Audit Log",
                  bg=ACCENT, fg=BG, font=FONT_BUTTON, bd=0,
                  command=self._admin_export_audit
                  ).pack(fill="x", padx=10, pady=(10, 4))

        # T7.10 — DB backup. Full snapshot via online backup API.
        tk.Button(log_f, text="Backup Database",
                  bg=ACCENT, fg=BG, font=FONT_BUTTON, bd=0,
                  command=self._admin_backup_db
                  ).pack(fill="x", padx=10, pady=(0, 10))

        # ---- Backups (T7.14) ----
        # Lists pharmacy_backup_*.db files in home dir, newest first,
        # each with a Restore button. Restore is destructive: prompts
        # before overwriting live DB, then forces logout.
        bk = tk.Frame(host, bg=PANEL)
        bk.pack(fill="x", padx=14, pady=8)
        tk.Label(bk, text="Backups (Restore)", bg=PANEL, fg=ACCENT,
                 font=FONT_BUTTON).pack(anchor="w", padx=10, pady=(8, 4))
        backups = db_list_backups()
        if not backups:
            tk.Label(bk,
                     text="(no backups — use 'Backup Database' above)",
                     bg=PANEL, fg=DIM, font=FONT_BODY).pack(
                         anchor="w", padx=14, pady=(2, 10))
        for fname, fpath, _ in backups:
            row = tk.Frame(bk, bg=PANEL)
            row.pack(fill="x", padx=10, pady=2)
            tk.Label(row, text=fname, bg=PANEL, fg=TEXT,
                     font=FONT_BODY, anchor="w",
                     wraplength=240, justify="left").pack(
                         side="left", fill="x", expand=True, padx=4)
            tk.Button(row, text="Restore", bg=RED, fg=BG,
                      font=FONT_BUTTON, bd=0,
                      command=lambda p=fpath, n=fname:
                          self._admin_restore_db(p, n)
                      ).pack(side="right", padx=4)
        if backups:
            tk.Frame(bk, bg=PANEL, height=6).pack()

    # ---- admin mutation handlers (T5.3) ----
    def _admin_add_tech(self, name, pin):
        name = (name or "").strip()
        pin = (pin or "").strip()
        if not name:
            messagebox.showerror("Add Tech", "Name required.")
            return
        if pin:
            ok, reason = is_strong_pin(pin)
            if not ok:
                messagebox.showerror("Add Tech", reason)
                return
        if not db_add_user(name, "tech", pin if pin else None):
            messagebox.showerror(
                "Add Tech",
                "Name is reserved, blank, or already taken by an admin.")
            return
        db_log_audit(self.user, "Added tech: %s" % name)
        self.navigate_to("admin")

    def _admin_remove_tech(self, name):
        if not messagebox.askyesno(
                "Remove Tech",
                "Remove '%s' and their scores/mastery?" % name):
            return
        # A3 fix: db_remove_user now returns False if the removal
        # would leave zero admins. Surface that to the user.
        if not db_remove_user(name):
            messagebox.showerror(
                "Remove Tech",
                "Cannot remove '%s': would leave zero admins.\n"
                "Add another admin first." % name)
            return
        db_log_audit(self.user, "Removed tech: %s" % name)
        self.navigate_to("admin")

    def _admin_add_inv(self, drug, exp):
        result = validate_inventory_entry(drug, exp)
        if not result.ok:
            messagebox.showerror("Inventory", result.error)
            return
        payload = result.value
        db_add_inventory(payload["drug"], payload["exp_date"])
        db_log_audit(
            self.user,
            "Inventory add: %s exp %s" % (
                payload["drug"], payload["exp_date"]))
        self.navigate_to("admin")

    def _admin_remove_inv(self, drug):
        db_remove_inventory(drug)
        db_log_audit(self.user, "Inventory remove: %s" % drug)
        self.navigate_to("admin")

    def _admin_save_notes(self, text):
        # T7.2 — persist shift notes via db_set_state. Strip the
        # trailing newline the Tk Text widget appends.
        cleaned = (text or "").strip()
        db_set_state("shift_notes", cleaned)
        db_log_audit(self.user, "Updated shift notes")
        messagebox.showinfo("Shift Notes", "Saved.")

    def _admin_audit_filter(self, text):
        # T7.7 — set the audit log filter (or clear if empty) and
        # re-render. SQL LIKE % wildcards are added at query time, not
        # stored, so user-typed % is treated as literal-ish through the
        # parameterized binding. No filter audit-log entry (would spam).
        result = validate_filter_text(text, "Audit filter")
        if not result.ok:
            messagebox.showerror("Audit Filter", result.error)
            return
        self._audit_filter = result.value
        self.navigate_to("admin")

    def _admin_inv_filter(self, text):
        # T7.12 — inventory drug-name filter. Same pattern as audit
        # filter: state attribute + redraw.
        result = validate_filter_text(text, "Inventory filter")
        if not result.ok:
            messagebox.showerror("Inventory Filter", result.error)
            return
        self._inv_filter = result.value
        self.navigate_to("admin")

    def _admin_export_inventory(self):
        # T7.16 — export inventory to tab-separated text. Audit-logs
        # the export. Same OSError handling pattern as T7.9.
        try:
            path = db_export_inventory()
        except OSError as exc:
            messagebox.showerror(
                "Export Failed", "Could not write file:\n%s" % exc)
            return
        db_log_audit(self.user, "Exported inventory to %s" % path)
        messagebox.showinfo(
            "Export Complete",
            "Inventory written to:\n%s" % path)
        self.navigate_to("admin")

    def _admin_export_audit(self):
        # T7.9 — export to plain text. Audit-logs the export action
        # itself (and the destination path) so the export is itself
        # traceable. messagebox confirms the path Scott / inspector
        # can find via Pydroid 3 Files browser.
        try:
            path = db_export_audit_log()
        except OSError as exc:
            messagebox.showerror(
                "Export Failed", "Could not write file:\n%s" % exc)
            return
        db_log_audit(self.user, "Exported audit log to %s" % path)
        messagebox.showinfo(
            "Export Complete",
            "Audit log written to:\n%s" % path)
        self.navigate_to("admin")

    def _admin_backup_db(self):
        # T7.10 — full SQLite online backup. Audit-logs the backup
        # action so the snapshot is itself traceable. sqlite3.Error
        # (db locked, disk full, perms) is the failure mode.
        try:
            path = db_backup()
        except (sqlite3.Error, OSError) as exc:
            messagebox.showerror(
                "Backup Failed", "Could not back up DB:\n%s" % exc)
            return
        db_log_audit(self.user, "Backed up DB to %s" % path)
        messagebox.showinfo(
            "Backup Complete",
            "Database snapshot written to:\n%s" % path)
        self.navigate_to("admin")

    def _admin_restore_db(self, backup_path, backup_name):
        # T7.14 — restore from snapshot. Destructive: overwrites the
        # live DB. Strong confirmation. Audit-logs the intent BEFORE
        # the restore (because the restored DB may not contain this
        # entry afterward). Forces logout — in-app state may not
        # match the new DB (different users, different lockout, etc).
        if not messagebox.askyesno(
                "Restore Database",
                "OVERWRITE the live database with:\n"
                "  %s\n\n"
                "Current data will be REPLACED with the snapshot. "
                "This cannot be undone (unless you have a newer "
                "backup). You will be logged out.\n\n"
                "Proceed?" % backup_name):
            return
        db_log_audit(self.user,
                     "Restoring DB from %s (pre-restore mark)"
                     % backup_name)
        try:
            db_restore(backup_path)
        except (sqlite3.Error, OSError) as exc:
            messagebox.showerror(
                "Restore Failed",
                "Live DB unchanged.\nError: %s" % exc)
            return
        messagebox.showinfo(
            "Restore Complete",
            "Database restored from:\n%s\n\nLogging out." % backup_name)
        self.logout()

    def panel_tpr(self):
        # T5.4 — TPR Insurance Guide. Static panel; verbatim 5 rows from
        # v13 (panel_tpr_resolver lines 1190-1196). ADR-C05: UNVERIFIED.
        host = self.make_scrollable(self.content_host)
        tk.Label(host, text="TPR (Third Party Rejection) Guide",
                 bg=BG, fg=TEXT, font=FONT_HEADING).pack(pady=12)
        self._unverified_banner(host, ["tpr"])
        tk.Label(host,
                 text=("Common NCPDP claim reject codes. The "
                       "technician resolves these unless the action "
                       "names the pharmacist."),
                 bg=BG, fg=DIM, font=FONT_BODY, wraplength=360,
                 justify="left").pack(padx=14, pady=(0, 8))

        for entry in TPR_CODES:
            row = tk.Frame(host, bg=PANEL)
            row.pack(fill="x", padx=14, pady=4)
            tk.Label(row, text=entry["code"], bg=PANEL, fg=ACCENT,
                     font=FONT_BUTTON, anchor="w", wraplength=320,
                     justify="left").pack(anchor="w", padx=10,
                                          pady=(6, 0))
            tk.Label(row, text=entry["meaning"], bg=PANEL, fg=DIM,
                     font=FONT_BODY, wraplength=320, justify="left",
                     anchor="w").pack(anchor="w", padx=10, pady=(2, 0))
            tk.Label(row, text="→ " + entry["action"], bg=PANEL,
                     fg=TEXT, font=FONT_BODY, wraplength=320,
                     justify="left", anchor="w").pack(
                         anchor="w", padx=10, pady=(2, 6))

    def panel_hotkeys(self):
        # T5.5 — IC+ Hotkeys. Static panel; verbatim 8 key/description
        # pairs from v13 (panel_hotkeys lines 1208-1213). Software workflow
        # reference, not clinical/law data — no UNVERIFIED banner per
        # ADR-C05 scope.
        host = self.make_scrollable(self.content_host)
        tk.Label(host, text="Intercom Plus (IC+) Hotkeys",
                 bg=BG, fg=TEXT, font=FONT_HEADING).pack(pady=12)

        keys = [
            ("F9", "Patient Search"),
            ("F12", "Release to POS / Finish"),
            ("ALT + O", "Options Menu"),
            ("ALT + P", "Product Detail"),
            ("CTRL + X", "Exception Queue"),
            ("CTRL + S", "Scan Rx / Document"),
            ("Shift + F1", "TeamRx / Help"),
            ("ALT + R", "Ready Status Check"),
        ]
        card = tk.Frame(host, bg=PANEL)
        card.pack(fill="x", padx=14, pady=8)
        for k, desc in keys:
            row = tk.Frame(card, bg=PANEL)
            row.pack(fill="x", padx=10, pady=4)
            tk.Label(row, text=k, bg=PANEL, fg=GREEN,
                     font=FONT_BUTTON, width=12, anchor="w").pack(
                         side="left")
            tk.Label(row, text=desc, bg=PANEL, fg=TEXT,
                     font=FONT_BODY, wraplength=240, justify="left",
                     anchor="w").pack(side="left", fill="x", expand=True)

    def panel_partials(self):
        # T5.6 — Partial Fill Ledger. DB-backed. Lists open partials
        # (resolved=0), add new partial (drug, qty_owed, patient, date),
        # resolve button per row. Uses PartialFills table (schema in
        # init_db). Parametrized writes. Audit-logged.
        host = self.make_scrollable(self.content_host)
        tk.Label(host, text="Partial Fill Ledger", bg=BG, fg=TEXT,
                 font=FONT_HEADING).pack(pady=12)

        # ---- open partials list ----
        list_card = tk.Frame(host, bg=PANEL)
        list_card.pack(fill="x", padx=14, pady=8)
        tk.Label(list_card, text="Open Partials", bg=PANEL, fg=ACCENT,
                 font=FONT_BUTTON).pack(anchor="w", padx=10, pady=(8, 4))
        rows = db_open_partials()
        if not rows:
            tk.Label(list_card,
                     text="All partials resolved. Inventory is clear.",
                     bg=PANEL, fg=DIM, font=FONT_BODY).pack(
                         anchor="w", padx=14, pady=(2, 10))
        for pid, drug, qty_owed, patient, date in rows:
            row = tk.Frame(list_card, bg=PANEL)
            row.pack(fill="x", padx=10, pady=4)
            tk.Label(
                row,
                text="%s  —  qty owed: %s\n%s  (%s)" % (
                    drug, qty_owed, patient, date),
                bg=PANEL, fg=TEXT, font=FONT_BODY, justify="left",
                anchor="w", wraplength=240).pack(
                    side="left", fill="x", expand=True, padx=4)
            actions = tk.Frame(row, bg=PANEL)
            actions.pack(side="right", padx=4)
            tk.Button(actions, text="Edit", bg=ACCENT, fg=BG,
                      font=FONT_BUTTON, bd=0,
                      command=lambda item=(
                          pid, drug, qty_owed, patient, date):
                          self._partial_prepare_edit(item)
                      ).pack(fill="x", pady=(0, 3))
            tk.Button(actions, text="Resolve", bg=GREEN, fg=BG,
                      font=FONT_BUTTON, bd=0,
                      command=lambda rid=pid:
                          self._partial_resolve(rid)
                      ).pack(fill="x")

        # ---- add new partial ----
        edit_row = getattr(self, "_partial_edit", None)
        add_card = tk.Frame(host, bg=PANEL)
        add_card.pack(fill="x", padx=14, pady=8)
        tk.Label(add_card,
                 text="Edit Partial" if edit_row else "Add Partial",
                 bg=PANEL, fg=ACCENT,
                 font=FONT_BUTTON).pack(anchor="w", padx=10, pady=(8, 4))

        def fld(label):
            r = tk.Frame(add_card, bg=PANEL)
            r.pack(fill="x", padx=10, pady=3)
            tk.Label(r, text=label, bg=PANEL, fg=TEXT, font=FONT_BODY,
                     width=12, anchor="w").pack(side="left")
            e = tk.Entry(r, font=FONT_BODY, bg=BG, fg=TEXT,
                         insertbackground=TEXT)
            e.pack(side="left", fill="x", expand=True, ipady=4)
            return e

        e_drug = fld("Drug")
        e_qty = fld("Qty owed")
        e_pat = fld("Patient")
        e_date = fld("Date")
        if edit_row:
            _, edit_drug, edit_qty, edit_patient, edit_date = edit_row
            e_drug.insert(0, edit_drug)
            e_qty.insert(0, str(edit_qty))
            e_pat.insert(0, edit_patient)
            e_date.insert(0, edit_date)
            tk.Button(add_card, text="Save Changes", bg=ACCENT, fg=BG,
                      font=FONT_BUTTON, bd=0,
                      command=lambda rid=edit_row[0]: self._partial_update(
                          rid, e_drug.get(), e_qty.get(),
                          e_pat.get(), e_date.get())
                      ).pack(fill="x", padx=10, pady=(6, 4))
            tk.Button(add_card, text="Cancel Edit", bg=BG, fg=TEXT,
                      font=FONT_BUTTON, bd=0,
                      command=self._partial_cancel_edit
                      ).pack(fill="x", padx=10, pady=(0, 10))
        else:
            e_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
            tk.Button(add_card, text="Add to Ledger", bg=ACCENT, fg=BG,
                      font=FONT_BUTTON, bd=0,
                      command=lambda: self._partial_add(
                          e_drug.get(), e_qty.get(),
                          e_pat.get(), e_date.get())
                      ).pack(fill="x", padx=10, pady=(6, 10))

    def _partial_add(self, drug, qty, patient, date):
        result = validate_partial_fill(drug, qty, patient, date)
        if not result.ok:
            messagebox.showerror("Partial", result.error)
            return
        payload = result.value
        db_add_partial(
            payload["drug"],
            payload["qty_owed"],
            payload["patient"],
            payload["date"],
        )
        db_log_audit(self.user,
                     "Logged partial: %s for %s" % (
                         payload["drug"], payload["patient"]))
        self.navigate_to("partials")

    def _partial_prepare_edit(self, row):
        self._partial_edit = row
        self.navigate_to("partials")

    def _partial_cancel_edit(self):
        self._partial_edit = None
        self.navigate_to("partials")

    def _partial_update(self, pid, drug, qty, patient, date):
        result = validate_partial_fill(drug, qty, patient, date)
        if not result.ok:
            messagebox.showerror("Partial", result.error)
            return
        payload = result.value
        affected = db_update_partial(
            pid,
            payload["drug"],
            payload["qty_owed"],
            payload["patient"],
            payload["date"],
        )
        if affected:
            self._partial_edit = None
            db_log_audit(
                self.user,
                "Edited partial (ID: %s): %s for %s" % (
                    pid, payload["drug"], payload["patient"]),
            )
        else:
            self._partial_edit = None
            messagebox.showinfo(
                "Partial",
                "Already resolved or no longer in ledger.")
        self.navigate_to("partials")

    def _partial_resolve(self, pid):
        affected = db_resolve_partial(pid)
        # A6 fix: only audit-log when a row was actually changed.
        # Prevents misleading 'Resolved partial (ID:X)' entry when
        # the pid was already resolved or no longer exists.
        if affected:
            db_log_audit(self.user, "Resolved partial (ID: %s)" % pid)
        else:
            messagebox.showinfo(
                "Partial",
                "Already resolved or no longer in ledger.")
        self.navigate_to("partials")

    def panel_vaccines(self):
        # T5 scope item resolved 2026-05-20: the empty-placeholder panel
        # is replaced with structured eligibility data from
        # clinical_data.VACCINES. That data is GENERATED, NOT externally
        # verified — UNVERIFIED banner per ADR-C05, plus a CDC/ACIP
        # source-of-truth citation.
        host = self.make_scrollable(self.content_host)
        tk.Label(host, text="Vaccine Eligibility", bg=BG, fg=TEXT,
                 font=FONT_HEADING).pack(pady=12)
        self._unverified_banner(
            host, ["vaccines"],
            text=("⚠ UNVERIFIED DATA — generated quick-reference, "
                  "NOT cross-checked against the current schedule. "
                  "Verify every age, dose count and interval before "
                  "clinical use. Pharmacist administration scope "
                  "varies by state and patient age."),
            pady=(0, 4))
        tk.Label(host,
                 text=("Source of truth: CDC/ACIP Immunization "
                       "Schedules\ncdc.gov/vaccines/schedules"),
                 bg=BG, fg=DIM, font=FONT_BODY, wraplength=360,
                 justify="left").pack(padx=14, pady=(0, 8))

        for v in VACCINES:
            card = tk.Frame(host, bg=PANEL)
            card.pack(fill="x", padx=14, pady=6)
            tk.Label(card, text=v["vaccine"], bg=PANEL, fg=ACCENT,
                     font=FONT_BUTTON, anchor="w", wraplength=320,
                     justify="left").pack(anchor="w", padx=10,
                                          pady=(8, 2))
            for label, key in (("Eligible ages", "ages"),
                                ("Schedule", "schedule"),
                                ("Notes", "notes")):
                tk.Label(card, text="%s: %s" % (label, v[key]),
                         bg=PANEL, fg=TEXT, font=FONT_BODY,
                         wraplength=320, justify="left",
                         anchor="w").pack(anchor="w", padx=14,
                                          pady=(0, 2))
            tk.Frame(card, bg=PANEL, height=4).pack()

    def panel_sig(self):
        host = self.make_scrollable(self.content_host)
        tk.Label(host, text="SIG Decoder", bg=BG, fg=TEXT,
                 font=FONT_HEADING).pack(pady=12)
        self._unverified_banner(host, ["sig_abbreviations"])

        inp_f = tk.Frame(host, bg=PANEL)
        inp_f.pack(fill="x", padx=14, pady=6)
        tk.Label(inp_f, text="SIG string:", bg=PANEL, fg=TEXT,
                 font=FONT_BODY).pack(anchor="w", padx=10, pady=(8, 2))
        entry = tk.Entry(inp_f, font=FONT_BODY, bg=BG, fg=TEXT,
                         insertbackground=TEXT)
        entry.pack(fill="x", padx=10, ipady=6, pady=(0, 4))

        res_box = tk.Text(host, bg=PANEL, fg=TEXT, font=FONT_BODY,
                          height=6, bd=0, state="disabled",
                          wrap="word", padx=8, pady=6)
        res_box.pack(fill="x", padx=14, pady=4)

        def decode():
            result = validate_sig_tokens(entry.get())
            if not result.ok:
                messagebox.showerror("SIG Decoder", result.error)
                return
            tokens = result.value
            lines = []
            for tok in tokens:
                meaning = SIG_ABBREVIATIONS.get(tok)
                if meaning:
                    lines.append("%s  →  %s" % (tok, meaning))
                else:
                    lines.append(
                        "%s  →  not in reference; verify manually" % tok)
            res_box.config(state="normal")
            res_box.delete("1.0", "end")
            res_box.insert("end", "\n".join(lines))
            res_box.config(state="disabled")

        tk.Button(inp_f, text="Decode", bg=ACCENT, fg=BG,
                  font=FONT_BUTTON, bd=0, command=decode
                  ).pack(fill="x", padx=10, pady=(0, 10))

        # Full reference list
        ref = tk.Frame(host, bg=PANEL)
        ref.pack(fill="x", padx=14, pady=8)
        tk.Label(ref, text="Full Reference", bg=PANEL, fg=ACCENT,
                 font=FONT_BUTTON).pack(anchor="w", padx=10, pady=(8, 4))
        for abbr, meaning in sorted(SIG_ABBREVIATIONS.items()):
            tk.Label(ref, text="%s  —  %s" % (abbr, meaning),
                     bg=PANEL, fg=TEXT, font=FONT_BODY,
                     anchor="w").pack(anchor="w", padx=14, pady=1)

    def panel_lookup(self):
        host = self.make_scrollable(self.content_host)
        tk.Label(host, text="Drug Lookup", bg=BG, fg=TEXT,
                 font=FONT_HEADING).pack(pady=12)
        self._unverified_banner(host, ["brand_generic", "common_rx_flags"])

        inp_f = tk.Frame(host, bg=PANEL)
        inp_f.pack(fill="x", padx=14, pady=6)
        tk.Label(inp_f, text="Brand or generic name:", bg=PANEL, fg=TEXT,
                 font=FONT_BODY).pack(anchor="w", padx=10, pady=(8, 2))
        entry = tk.Entry(inp_f, font=FONT_BODY, bg=BG, fg=TEXT,
                         insertbackground=TEXT)
        entry.pack(fill="x", padx=10, ipady=6, pady=(0, 4))

        res_box = tk.Text(host, bg=PANEL, fg=TEXT, font=FONT_BODY,
                          height=8, bd=0, state="disabled",
                          wrap="word", padx=8, pady=6)
        res_box.pack(fill="x", padx=14, pady=4)

        def search():
            result = validate_lookup_query(entry.get())
            if not result.ok:
                messagebox.showerror("Drug Lookup", result.error)
                return
            q = result.value.lower()
            hits = [
                d for d in BRAND_GENERIC
                if q in d["brand"].lower() or q in d["generic"].lower()
            ]
            # T7.8 — mastery indicator (tech only). One bulk query for
            # all hit brands, build a set, decorate each result line.
            mastered = set()
            if hits and not self.is_admin:
                mastered = db_mastered_brands(
                    self.user, [d["brand"] for d in hits])
            lines = []
            if hits:
                for d in hits:
                    lines.append("Brand: %s  |  Generic: %s" % (
                        d["brand"], d["generic"]))
                    if not self.is_admin:
                        if d["brand"] in mastered:
                            lines.append("  ✓ Mastered")
                        else:
                            lines.append("  · Not yet mastered")
                    # check COMMON_RX_FLAGS against generic name
                    for drug, flag in COMMON_RX_FLAGS:
                        if drug in d["generic"].lower():
                            lines.append("  ⚠ RX FLAG: %s" % flag)
            else:
                lines.append("No match found for \"%s\"." % entry.get().strip())
            res_box.config(state="normal")
            res_box.delete("1.0", "end")
            res_box.insert("end", "\n".join(lines))
            res_box.config(state="disabled")

        tk.Button(inp_f, text="Search", bg=ACCENT, fg=BG,
                  font=FONT_BUTTON, bd=0, command=search
                  ).pack(fill="x", padx=10, pady=(0, 10))

        # Full list
        ref = tk.Frame(host, bg=PANEL)
        ref.pack(fill="x", padx=14, pady=8)
        tk.Label(ref, text="Full List (Brand → Generic)", bg=PANEL, fg=ACCENT,
                 font=FONT_BUTTON).pack(anchor="w", padx=10, pady=(8, 4))
        for d in sorted(BRAND_GENERIC, key=lambda x: x["brand"]):
            tk.Label(ref, text="%s  →  %s" % (d["brand"], d["generic"]),
                     bg=PANEL, fg=TEXT, font=FONT_BODY,
                     anchor="w").pack(anchor="w", padx=14, pady=1)
