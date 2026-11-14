#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🏆 بطولة مسابقات الروبوت والبرمجة الافتراضية
College Competition Management System - GUI Version
"""

import tkinter as tk
from tkinter import ttk, messagebox, font
import json

# ── الألوان والثوابت ───────────────────────────────────────────────────────────
BG_DARK      = "#0D1117"
BG_CARD      = "#161B22"
BG_SIDEBAR   = "#0D1117"
ACCENT       = "#F0A500"
ACCENT2      = "#E05C00"
TEXT_PRIMARY = "#E6EDF3"
TEXT_MUTED   = "#8B949E"
SUCCESS      = "#3FB950"
DANGER       = "#F85149"
INFO_CLR     = "#58A6FF"
BORDER       = "#30363D"
GOLD         = "#FFD700"
SILVER       = "#C0C0C0"
BRONZE       = "#CD7F32"

MAX_TEAMS       = 5
MAX_MEMBERS     = 5
MAX_INDIVIDUALS = 20

EVENTS = [
    "البرمجة الإبداعية",
    "التحدث أمام الجمهور",
    "حل المشكلات",
    "الابتكار والتصميم",
    "المعرفة العامة",
]

# ── البيانات ───────────────────────────────────────────────────────────────────
teams       = {}  # {name: {"members": [...], "scores": {ev_idx: score}}}
individuals = {}  # {name: {"scores": {ev_idx: score}}}


def total_score(scores):
    return sum(scores.values()) if scores else 0


# ══════════════════════════════════════════════════════════════════════════════
# مكوّنات UI مساعدة
# ══════════════════════════════════════════════════════════════════════════════
def styled_button(parent, text, command, color=ACCENT, fg=BG_DARK, **kw):
    btn = tk.Button(
        parent, text=text, command=command,
        bg=color, fg=fg, relief="flat", cursor="hand2",
        font=("Cairo", 11, "bold"),
        padx=20, pady=8,
        activebackground=ACCENT2, activeforeground=TEXT_PRIMARY,
        **kw
    )
    btn.bind("<Enter>", lambda e: btn.config(bg=ACCENT2, fg=TEXT_PRIMARY))
    btn.bind("<Leave>", lambda e: btn.config(bg=color, fg=fg))
    return btn


def card_frame(parent, **kw):
    return tk.Frame(parent, bg=BG_CARD, bd=0,
                    highlightbackground=BORDER, highlightthickness=1, **kw)


def lbl(parent, text, size=11, color=TEXT_PRIMARY, bold=False, **kw):
    f = ("Cairo", size, "bold") if bold else ("Cairo", size)
    return tk.Label(parent, text=text, bg=parent["bg"], fg=color, font=f, **kw)


def entry_field(parent, **kw):
    e = tk.Entry(
        parent, bg="#21262D", fg=TEXT_PRIMARY,
        insertbackground=ACCENT, relief="flat",
        font=("Cairo", 11),
        highlightbackground=BORDER, highlightthickness=1,
        **kw
    )
    e.bind("<FocusIn>",  lambda ev: e.config(highlightbackground=ACCENT))
    e.bind("<FocusOut>", lambda ev: e.config(highlightbackground=BORDER))
    return e


def spinbox_field(parent, **kw):
    s = tk.Spinbox(
        parent, from_=0, to=100,
        bg="#21262D", fg=TEXT_PRIMARY,
        buttonbackground="#21262D",
        relief="flat", font=("Cairo", 11),
        highlightbackground=BORDER, highlightthickness=1,
        insertbackground=ACCENT,
        **kw
    )
    return s


# ══════════════════════════════════════════════════════════════════════════════
# نافذة: تسجيل فريق
# ══════════════════════════════════════════════════════════════════════════════
class RegisterTeamWindow(tk.Toplevel):
    def __init__(self, master, on_done):
        super().__init__(master)
        self.on_done = on_done
        self.title("تسجيل فريق جديد")
        self.configure(bg=BG_DARK)
        self.resizable(False, False)
        self.grab_set()
        self._build()
        self._center()

    def _center(self):
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        x = (self.winfo_screenwidth()  - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"+{x}+{y}")

    def _build(self):
        pad = {"padx": 30, "pady": 10}

        header = tk.Frame(self, bg=ACCENT, height=6)
        header.pack(fill="x")

        lbl(self, "🏅 تسجيل فريق جديد", 16, ACCENT, bold=True).pack(pady=(20, 5))
        lbl(self, f"يمكن تسجيل {MAX_TEAMS - len(teams)} فريق متبقي", 10, TEXT_MUTED).pack()

        # اسم الفريق
        f1 = card_frame(self)
        f1.pack(fill="x", padx=30, pady=(15, 5))
        lbl(f1, "اسم الفريق", 10, TEXT_MUTED).pack(anchor="e", padx=12, pady=(10, 2))
        self.team_name = entry_field(f1, width=32)
        self.team_name.pack(padx=12, pady=(0, 10), fill="x")

        # أسماء الأعضاء
        f2 = card_frame(self)
        f2.pack(fill="x", padx=30, pady=5)
        lbl(f2, "أسماء الأعضاء الخمسة", 10, TEXT_MUTED).pack(anchor="e", padx=12, pady=(10, 4))
        self.member_entries = []
        for i in range(MAX_MEMBERS):
            row = tk.Frame(f2, bg=BG_CARD)
            row.pack(fill="x", padx=12, pady=2)
            lbl(row, f"العضو {i+1}", 9, TEXT_MUTED).pack(side="right", padx=(0, 6))
            e = entry_field(row, width=26)
            e.pack(side="right", fill="x", expand=True)
            self.member_entries.append(e)
        tk.Frame(f2, bg=BG_CARD, height=10).pack()

        # أزرار
        btn_row = tk.Frame(self, bg=BG_DARK)
        btn_row.pack(pady=20)
        styled_button(btn_row, "✔  تسجيل", self._save, color=SUCCESS).pack(side="right", padx=6)
        styled_button(btn_row, "✖  إلغاء", self.destroy, color=DANGER).pack(side="right", padx=6)

    def _save(self):
        name = self.team_name.get().strip()
        if not name:
            messagebox.showerror("خطأ", "أدخل اسم الفريق!", parent=self); return
        if name in teams:
            messagebox.showerror("خطأ", "هذا الاسم مستخدم بالفعل!", parent=self); return
        members = []
        for i, e in enumerate(self.member_entries):
            m = e.get().strip()
            if not m:
                messagebox.showerror("خطأ", f"أدخل اسم العضو {i+1}!", parent=self); return
            members.append(m)
        teams[name] = {"members": members, "scores": {}}
        messagebox.showinfo("نجاح", f"تم تسجيل الفريق '{name}' بنجاح! 🎉", parent=self)
        self.on_done()
        self.destroy()


# ══════════════════════════════════════════════════════════════════════════════
# نافذة: تسجيل فرد
# ══════════════════════════════════════════════════════════════════════════════
class RegisterIndividualWindow(tk.Toplevel):
    def __init__(self, master, on_done):
        super().__init__(master)
        self.on_done = on_done
        self.title("تسجيل مشارك فردي")
        self.configure(bg=BG_DARK)
        self.resizable(False, False)
        self.grab_set()
        self._build()
        self._center()

    def _center(self):
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        x = (self.winfo_screenwidth()  - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"+{x}+{y}")

    def _build(self):
        tk.Frame(self, bg=INFO_CLR, height=6).pack(fill="x")
        lbl(self, "👤 تسجيل مشارك فردي", 16, INFO_CLR, bold=True).pack(pady=(20, 5))
        lbl(self, f"{MAX_INDIVIDUALS - len(individuals)} مشارك متبقٍ", 10, TEXT_MUTED).pack()

        f = card_frame(self)
        f.pack(fill="x", padx=30, pady=20)
        lbl(f, "اسم المشارك", 10, TEXT_MUTED).pack(anchor="e", padx=12, pady=(10, 2))
        self.name_entry = entry_field(f, width=32)
        self.name_entry.pack(padx=12, pady=(0, 14), fill="x")

        btn_row = tk.Frame(self, bg=BG_DARK)
        btn_row.pack(pady=(0, 20))
        styled_button(btn_row, "✔  تسجيل", self._save, color=SUCCESS).pack(side="right", padx=6)
        styled_button(btn_row, "✖  إلغاء", self.destroy, color=DANGER).pack(side="right", padx=6)

    def _save(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("خطأ", "أدخل اسم المشارك!", parent=self); return
        if name in individuals:
            messagebox.showerror("خطأ", "هذا الاسم مستخدم بالفعل!", parent=self); return
        if len(individuals) >= MAX_INDIVIDUALS:
            messagebox.showerror("خطأ", "وصلت للحد الأقصى من المشاركين الأفراد!", parent=self); return
        individuals[name] = {"scores": {}}
        messagebox.showinfo("نجاح", f"تم تسجيل '{name}' بنجاح! 🎉", parent=self)
        self.on_done()
        self.destroy()


# ══════════════════════════════════════════════════════════════════════════════
# نافذة: تقييم الأحداث
# ══════════════════════════════════════════════════════════════════════════════
class EvaluateWindow(tk.Toplevel):
    def __init__(self, master, on_done):
        super().__init__(master)
        self.on_done = on_done
        self.title("تقييم الأحداث")
        self.configure(bg=BG_DARK)
        self.resizable(True, True)
        self.grab_set()
        self._selected_event = tk.IntVar(value=0)
        self._build()
        self._center()

    def _center(self):
        self.update_idletasks()
        self.geometry("680x600")
        x = (self.winfo_screenwidth()  - 680) // 2
        y = (self.winfo_screenheight() - 600) // 2
        self.geometry(f"680x600+{x}+{y}")

    def _build(self):
        tk.Frame(self, bg=ACCENT, height=6).pack(fill="x")
        lbl(self, "⭐ تقييم الأحداث", 16, ACCENT, bold=True).pack(pady=(16, 4))

        # اختيار الحدث
        ev_frame = card_frame(self)
        ev_frame.pack(fill="x", padx=24, pady=8)
        lbl(ev_frame, "اختر الحدث", 11, TEXT_MUTED, bold=True).pack(anchor="e", padx=14, pady=(10, 6))
        for i, ev in enumerate(EVENTS):
            row = tk.Frame(ev_frame, bg=BG_CARD)
            row.pack(fill="x", padx=14, pady=2)
            rb = tk.Radiobutton(
                row, text=f"الحدث {i+1}: {ev}",
                variable=self._selected_event, value=i,
                bg=BG_CARD, fg=TEXT_PRIMARY,
                selectcolor=BG_DARK, activebackground=BG_CARD,
                font=("Cairo", 10),
                command=self._load_scores
            )
            rb.pack(side="right")
        tk.Frame(ev_frame, bg=BG_CARD, height=8).pack()

        # منطقة الدرجات
        lbl(self, "الدرجات (0 - 100)", 11, TEXT_MUTED).pack(anchor="e", padx=24, pady=(6, 2))

        canvas_frame = tk.Frame(self, bg=BG_DARK)
        canvas_frame.pack(fill="both", expand=True, padx=24)

        self.canvas = tk.Canvas(canvas_frame, bg=BG_CARD, bd=0,
                                highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical",
                                  command=self.canvas.yview)
        self.score_frame = tk.Frame(self.canvas, bg=BG_CARD)

        self.score_frame.bind("<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.canvas.create_window((0, 0), window=self.score_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.spinboxes = {}
        self._load_scores()

        btn_row = tk.Frame(self, bg=BG_DARK)
        btn_row.pack(pady=12)
        styled_button(btn_row, "💾  حفظ التقييمات", self._save, color=SUCCESS).pack(side="right", padx=6)
        styled_button(btn_row, "✖  إغلاق", self.destroy, color=DANGER).pack(side="right", padx=6)

    def _load_scores(self):
        for w in self.score_frame.winfo_children():
            w.destroy()
        self.spinboxes.clear()

        ev_idx = self._selected_event.get()

        def add_section(title, entries, color):
            sec = tk.Frame(self.score_frame, bg=BG_CARD)
            sec.pack(fill="x", padx=10, pady=(10, 4))
            tk.Frame(sec, bg=color, height=2).pack(fill="x")
            lbl(sec, title, 10, color, bold=True).pack(anchor="e", padx=6, pady=4)
            for nm in entries:
                row = tk.Frame(sec, bg=BG_CARD)
                row.pack(fill="x", padx=6, pady=3)
                current = entries[nm]["scores"].get(ev_idx, 0)
                sp = spinbox_field(row, width=6)
                sp.delete(0, "end")
                sp.insert(0, str(current))
                sp.pack(side="left", padx=(0, 10))
                lbl(row, nm, 10, TEXT_PRIMARY).pack(side="right")
                self.spinboxes[(nm, ev_idx)] = sp

        if teams:
            add_section("🏅 الأفرقة", teams, ACCENT)
        if individuals:
            add_section("👤 الأفراد", individuals, INFO_CLR)
        if not teams and not individuals:
            lbl(self.score_frame, "لا يوجد مشاركون مسجلون بعد", 11, TEXT_MUTED).pack(pady=20)

    def _save(self):
        ev_idx = self._selected_event.get()
        try:
            for (nm, eidx), sp in self.spinboxes.items():
                val = int(sp.get())
                if not (0 <= val <= 100):
                    raise ValueError(f"درجة '{nm}' خارج النطاق")
                if nm in teams:
                    teams[nm]["scores"][eidx] = val
                elif nm in individuals:
                    individuals[nm]["scores"][eidx] = val
        except ValueError as ex:
            messagebox.showerror("خطأ", str(ex), parent=self); return

        messagebox.showinfo("نجاح", "✔  تم حفظ التقييمات بنجاح!", parent=self)
        self.on_done()


# ══════════════════════════════════════════════════════════════════════════════
# النافذة الرئيسية
# ══════════════════════════════════════════════════════════════════════════════
class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🏆 نظام إدارة مسابقة الكلية")
        self.configure(bg=BG_DARK)
        self.minsize(960, 640)
        self._center_window(960, 680)
        self._current_page = None
        self._build_layout()
        self._show_dashboard()

    def _center_window(self, w, h):
        x = (self.winfo_screenwidth()  - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    # ── هيكل التخطيط ──────────────────────────────────────────────────────────
    def _build_layout(self):
        # شريط علوي
        topbar = tk.Frame(self, bg=BG_CARD, height=56)
        topbar.pack(fill="x")
        topbar.pack_propagate(False)

        lbl(topbar, "🏆  نظام إدارة مسابقة الكلية",
            14, ACCENT, bold=True).pack(side="right", padx=24, pady=12)
        lbl(topbar, "College Competition System",
            9, TEXT_MUTED).pack(side="left", padx=16, pady=12)

        tk.Frame(self, bg=BORDER, height=1).pack(fill="x")

        body = tk.Frame(self, bg=BG_DARK)
        body.pack(fill="both", expand=True)

        # شريط جانبي
        self.sidebar = tk.Frame(body, bg=BG_SIDEBAR, width=200)
        self.sidebar.pack(side="right", fill="y")
        self.sidebar.pack_propagate(False)

        tk.Frame(self.sidebar, bg=BORDER, width=1).pack(side="left", fill="y")

        self._build_sidebar()

        # منطقة المحتوى
        self.content = tk.Frame(body, bg=BG_DARK)
        self.content.pack(side="left", fill="both", expand=True)

    def _build_sidebar(self):
        lbl(self.sidebar, "القائمة الرئيسية", 9, TEXT_MUTED).pack(pady=(20, 8), padx=16, anchor="e")

        nav_items = [
            ("🏠  لوحة التحكم",    self._show_dashboard,   ACCENT),
            ("🏅  تسجيل فريق",     self._open_reg_team,    SUCCESS),
            ("👤  تسجيل فرد",      self._open_reg_ind,     INFO_CLR),
            ("⭐  تقييم الأحداث",  self._open_evaluate,    ACCENT2),
            ("📊  عرض النتائج",    self._show_results,     "#A371F7"),
            ("👥  المشاركون",      self._show_participants, TEXT_MUTED),
        ]

        self.nav_buttons = []
        for label, cmd, color in nav_items:
            btn = tk.Button(
                self.sidebar, text=label, command=cmd,
                bg=BG_SIDEBAR, fg=color,
                relief="flat", cursor="hand2",
                font=("Cairo", 11),
                anchor="e", padx=16, pady=10,
                activebackground=BG_CARD, activeforeground=color,
                width=20
            )
            btn.pack(fill="x", pady=1, padx=8)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=BG_CARD))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=BG_SIDEBAR))
            self.nav_buttons.append(btn)

    def _clear_content(self):
        for w in self.content.winfo_children():
            w.destroy()

    # ── لوحة التحكم ───────────────────────────────────────────────────────────
    def _show_dashboard(self):
        self._clear_content()
        c = self.content

        lbl(c, "لوحة التحكم", 18, TEXT_PRIMARY, bold=True).pack(anchor="e", padx=30, pady=(24, 4))
        lbl(c, "نظرة عامة على المسابقة", 10, TEXT_MUTED).pack(anchor="e", padx=30)

        # بطاقات الإحصاء
        cards_row = tk.Frame(c, bg=BG_DARK)
        cards_row.pack(fill="x", padx=24, pady=20)

        stats = [
            ("الأفرقة",         f"{len(teams)}/{MAX_TEAMS}",        ACCENT,  "🏅"),
            ("الأفراد",         f"{len(individuals)}/{MAX_INDIVIDUALS}", INFO_CLR, "👤"),
            ("الأحداث",         f"{len(EVENTS)}",                   SUCCESS, "⭐"),
            ("التقييمات المنجزة",
             str(sum(len(d["scores"]) for d in {**teams, **individuals}.values())),
             "#A371F7", "📊"),
        ]

        for title, value, color, icon in stats:
            card = card_frame(cards_row)
            card.pack(side="right", expand=True, fill="both", padx=6, ipady=12)
            lbl(card, icon, 22, color).pack(pady=(14, 4))
            lbl(card, value, 20, color, bold=True).pack()
            lbl(card, title, 10, TEXT_MUTED).pack(pady=(2, 14))

        # قائمة الأفرقة
        if teams:
            lbl(c, "الأفرقة المسجلة", 13, TEXT_PRIMARY, bold=True).pack(
                anchor="e", padx=30, pady=(10, 6))
            for tname, tdata in teams.items():
                row = card_frame(c)
                row.pack(fill="x", padx=24, pady=3, ipady=6)
                tot = total_score(tdata["scores"])
                ev_done = len(tdata["scores"])
                lbl(row, f"مجموع: {tot} | أحداث: {ev_done}/{len(EVENTS)}",
                    9, TEXT_MUTED).pack(side="left", padx=14)
                lbl(row, f"🏅  {tname}", 11, ACCENT, bold=True).pack(
                    side="right", padx=14)

        # قائمة الأفراد
        if individuals:
            lbl(c, "المشاركون الأفراد", 13, TEXT_PRIMARY, bold=True).pack(
                anchor="e", padx=30, pady=(16, 6))
            row_wrap = tk.Frame(c, bg=BG_DARK)
            row_wrap.pack(fill="x", padx=24)
            for i, (nm, data) in enumerate(individuals.items()):
                chip = tk.Label(
                    row_wrap, text=f"👤 {nm}",
                    bg=BG_CARD, fg=INFO_CLR,
                    font=("Cairo", 10),
                    padx=10, pady=6, relief="flat",
                    highlightbackground=BORDER, highlightthickness=1
                )
                chip.grid(row=i // 4, column=i % 4, padx=4, pady=3, sticky="e")

    # ── عرض النتائج ───────────────────────────────────────────────────────────
    def _show_results(self):
        self._clear_content()
        c = self.content

        lbl(c, "📊 النتائج والترتيب", 18, TEXT_PRIMARY, bold=True).pack(
            anchor="e", padx=30, pady=(24, 4))

        # Notebook للأحداث
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Custom.TNotebook",           background=BG_DARK,   borderwidth=0)
        style.configure("Custom.TNotebook.Tab",
                        background=BG_CARD, foreground=TEXT_MUTED,
                        font=("Cairo", 10), padding=[12, 6])
        style.map("Custom.TNotebook.Tab",
                  background=[("selected", ACCENT)],
                  foreground=[("selected", BG_DARK)])

        nb = ttk.Notebook(c, style="Custom.TNotebook")
        nb.pack(fill="both", expand=True, padx=20, pady=10)

        # --- تبويب لكل حدث ---
        for ev_idx, ev_name in enumerate(EVENTS):
            tab = tk.Frame(nb, bg=BG_DARK)
            nb.add(tab, text=f" {ev_idx+1}. {ev_name} ")

            team_rows = [(n, d["scores"].get(ev_idx)) for n, d in teams.items()
                         if d["scores"].get(ev_idx) is not None]
            ind_rows  = [(n, d["scores"].get(ev_idx)) for n, d in individuals.items()
                         if d["scores"].get(ev_idx) is not None]

            if not team_rows and not ind_rows:
                lbl(tab, "لم يتم تقييم هذا الحدث بعد", 12, TEXT_MUTED).pack(pady=40)
                continue

            def make_rank_widget(parent, rows, title, color):
                frame = card_frame(parent)
                frame.pack(fill="x", padx=16, pady=8, ipady=6)
                tk.Frame(frame, bg=color, height=3).pack(fill="x")
                lbl(frame, title, 11, color, bold=True).pack(anchor="e", padx=14, pady=8)
                for rank, (nm, sc) in enumerate(
                        sorted(rows, key=lambda x: x[1], reverse=True), 1):
                    row = tk.Frame(frame, bg=BG_CARD)
                    row.pack(fill="x", padx=14, pady=2)
                    medals = {1: ("🥇", GOLD), 2: ("🥈", SILVER), 3: ("🥉", BRONZE)}
                    med_txt, med_clr = medals.get(rank, (str(rank), TEXT_MUTED))

                    # شريط التقدم
                    bar_w = int(sc * 1.4)
                    bar = tk.Frame(row, bg=color, width=bar_w, height=8)
                    bar.pack(side="left", padx=(0, 10), pady=4)

                    lbl(row, f"{sc} نقطة", 10, color).pack(side="left")
                    lbl(row, nm, 10, TEXT_PRIMARY).pack(side="right")
                    lbl(row, f"{med_txt} #{rank}", 10, med_clr).pack(side="right", padx=8)

            if team_rows:
                make_rank_widget(tab, team_rows, "🏅 ترتيب الأفرقة", ACCENT)
            if ind_rows:
                make_rank_widget(tab, ind_rows, "👤 ترتيب الأفراد", INFO_CLR)

        # --- تبويب الترتيب العام ---
        overall_tab = tk.Frame(nb, bg=BG_DARK)
        nb.add(overall_tab, text=" 🏆 الترتيب العام ")

        all_entries = []
        for nm, data in teams.items():
            all_entries.append((nm, "فريق", total_score(data["scores"]),
                                len(data["scores"]), ACCENT))
        for nm, data in individuals.items():
            all_entries.append((nm, "فرد", total_score(data["scores"]),
                                len(data["scores"]), INFO_CLR))
        all_entries.sort(key=lambda x: x[2], reverse=True)

        if not all_entries:
            lbl(overall_tab, "لا توجد نتائج بعد", 13, TEXT_MUTED).pack(pady=40)
        else:
            # جدول
            cols_frame = tk.Frame(overall_tab, bg=BG_CARD)
            cols_frame.pack(fill="x", padx=20, pady=(16, 4), ipady=6)
            for col, width in [("المجموع", 8), ("الأحداث", 8), ("النوع", 8),
                                ("الاسم", 20), ("المركز", 6)]:
                lbl(cols_frame, col, 10, TEXT_MUTED, bold=True).pack(
                    side="right", padx=width)

            medals = {1: ("🥇", GOLD), 2: ("🥈", SILVER), 3: ("🥉", BRONZE)}
            for rank, (nm, kind, tot, ev_cnt, color) in enumerate(all_entries, 1):
                row = card_frame(overall_tab)
                row.pack(fill="x", padx=20, pady=2, ipady=6)

                if rank == 1:
                    tk.Frame(row, bg=GOLD, width=4).pack(side="left", fill="y")

                med_txt, med_clr = medals.get(rank, (f"#{rank}", TEXT_MUTED))
                lbl(row, str(tot), 11, color, bold=True).pack(side="left", padx=14)
                lbl(row, f"{ev_cnt}/{len(EVENTS)}", 10, TEXT_MUTED).pack(side="left", padx=8)
                lbl(row, kind, 10, TEXT_MUTED).pack(side="left", padx=8)
                lbl(row, nm, 11, TEXT_PRIMARY).pack(side="right", padx=14)
                lbl(row, med_txt, 12, med_clr).pack(side="right", padx=10)

    # ── عرض المشاركين ─────────────────────────────────────────────────────────
    def _show_participants(self):
        self._clear_content()
        c = self.content

        lbl(c, "👥 المشاركون المسجلون", 18, TEXT_PRIMARY, bold=True).pack(
            anchor="e", padx=30, pady=(24, 4))

        # الأفرقة
        lbl(c, f"الأفرقة ({len(teams)}/{MAX_TEAMS})", 12, ACCENT, bold=True).pack(
            anchor="e", padx=30, pady=(12, 6))

        if teams:
            wrap = tk.Frame(c, bg=BG_DARK)
            wrap.pack(fill="x", padx=24)
            for col, (tname, tdata) in enumerate(teams.items()):
                card = card_frame(wrap)
                card.grid(row=0, column=col, padx=6, pady=4, sticky="nsew")
                wrap.columnconfigure(col, weight=1)
                tk.Frame(card, bg=ACCENT, height=3).pack(fill="x")
                lbl(card, f"🏅 {tname}", 11, ACCENT, bold=True).pack(
                    anchor="e", padx=10, pady=(8, 4))
                tk.Frame(card, bg=BORDER, height=1).pack(fill="x", padx=10)
                for m in tdata["members"]:
                    lbl(card, f"• {m}", 10, TEXT_PRIMARY).pack(
                        anchor="e", padx=14, pady=2)
                tk.Frame(card, bg=BG_CARD, height=8).pack()
        else:
            lbl(c, "لا توجد أفرقة مسجلة", 11, TEXT_MUTED).pack(anchor="e", padx=30, pady=4)

        # الأفراد
        lbl(c, f"المشاركون الأفراد ({len(individuals)}/{MAX_INDIVIDUALS})",
            12, INFO_CLR, bold=True).pack(anchor="e", padx=30, pady=(20, 6))

        if individuals:
            wrap2 = tk.Frame(c, bg=BG_DARK)
            wrap2.pack(fill="x", padx=24)
            for i, nm in enumerate(individuals):
                chip = tk.Label(
                    wrap2, text=f"👤 {nm}",
                    bg=BG_CARD, fg=INFO_CLR,
                    font=("Cairo", 10),
                    padx=12, pady=8, relief="flat",
                    highlightbackground=INFO_CLR, highlightthickness=1
                )
                chip.grid(row=i // 5, column=i % 5, padx=4, pady=4, sticky="e")
        else:
            lbl(c, "لا يوجد مشاركون أفراد", 11, TEXT_MUTED).pack(anchor="e", padx=30)

    # ── فتح نوافذ التسجيل والتقييم ────────────────────────────────────────────
    def _open_reg_team(self):
        if len(teams) >= MAX_TEAMS:
            messagebox.showwarning("تحذير", f"وصلت للحد الأقصى ({MAX_TEAMS}) أفرقة!"); return
        RegisterTeamWindow(self, self._show_dashboard)

    def _open_reg_ind(self):
        if len(individuals) >= MAX_INDIVIDUALS:
            messagebox.showwarning("تحذير", f"وصلت للحد الأقصى ({MAX_INDIVIDUALS}) مشاركاً!"); return
        RegisterIndividualWindow(self, self._show_dashboard)

    def _open_evaluate(self):
        if not teams and not individuals:
            messagebox.showwarning("تحذير", "سجّل مشاركين أولاً!"); return
        EvaluateWindow(self, self._show_results)


# ══════════════════════════════════════════════════════════════════════════════
# نقطة البداية
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
