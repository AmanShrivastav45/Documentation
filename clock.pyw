"""
Session Tracker - a tiny always-on-top work/break timer.

Uses only the Python standard library (tkinter) - no pip install needed.
Run by double-clicking this file (requires pythonw.exe on PATH so no
console window appears), or with: pythonw session_tracker.pyw

Logs:
  - session_log.csv     -> one row per work/break segment
  - daily_summary.csv   -> one row per day (total work / break hours)

Both files are created next to this script.
"""

import csv
import os
import time
import tkinter as tk
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "session_log.csv")
SUMMARY_FILE = os.path.join(BASE_DIR, "daily_summary.csv")

IDLE, WORKING, BREAK = "IDLE", "WORKING", "ON BREAK"

STATUS_COLORS = {
    IDLE: "#555555",
    WORKING: "#1a7f37",
    BREAK: "#b8860b",
}


def today_str():
    return datetime.now().strftime("%Y-%m-%d")


def fmt_hms(seconds):
    seconds = int(seconds)
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def fmt_hm(seconds):
    seconds = int(seconds)
    h, rem = divmod(seconds, 3600)
    m = rem // 60
    return f"{h}h {m:02d}m"


def ensure_log_file():
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", newline="") as f:
            csv.writer(f).writerow(["date", "type", "start_time", "end_time", "duration_seconds"])


def ensure_summary_file():
    if not os.path.exists(SUMMARY_FILE):
        with open(SUMMARY_FILE, "w", newline="") as f:
            csv.writer(f).writerow(
                ["date", "first_start", "last_end", "total_work_seconds", "total_break_seconds"]
            )


def load_today_totals():
    """Read today's existing segments so reopening the app resumes correctly."""
    work_total, break_total = 0, 0
    first_start, last_end = None, None
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, newline="") as f:
            for row in csv.DictReader(f):
                if row["date"] != today_str():
                    continue
                dur = float(row["duration_seconds"])
                if row["type"] == "work":
                    work_total += dur
                else:
                    break_total += dur
                if first_start is None:
                    first_start = row["start_time"]
                last_end = row["end_time"]
    return work_total, break_total, first_start, last_end


def append_segment(seg_type, start_dt, end_dt):
    ensure_log_file()
    duration = (end_dt - start_dt).total_seconds()
    with open(LOG_FILE, "a", newline="") as f:
        csv.writer(f).writerow(
            [today_str(), seg_type, start_dt.strftime("%H:%M:%S"), end_dt.strftime("%H:%M:%S"), f"{duration:.0f}"]
        )
    return duration


class App:
    def __init__(self, root):
        self.root = root
        root.title("Session Tracker")
        root.attributes("-topmost", True)
        root.resizable(False, False)
        root.geometry("270x190")
        root.configure(bg="#1e1e1e")

        self.state = IDLE
        self.segment_start = None
        self.work_total, self.break_total, self.first_start, self.last_end = load_today_totals()

        self.status_var = tk.StringVar(value=IDLE)
        self.timer_var = tk.StringVar(value="00:00:00")
        self.totals_var = tk.StringVar(value=self._totals_text())

        self.status_label = tk.Label(root, textvariable=self.status_var, font=("Segoe UI", 12, "bold"),
                                      fg=STATUS_COLORS[IDLE], bg="#1e1e1e")
        self.status_label.pack(pady=(12, 0))

        tk.Label(root, textvariable=self.timer_var, font=("Consolas", 26),
                 fg="white", bg="#1e1e1e").pack(pady=(0, 6))

        tk.Label(root, textvariable=self.totals_var, font=("Segoe UI", 9),
                 fg="#aaaaaa", bg="#1e1e1e", justify="center").pack(pady=(0, 8))

        btn_frame = tk.Frame(root, bg="#1e1e1e")
        btn_frame.pack()

        self.primary_btn = tk.Button(btn_frame, text="Start Work", width=12,
                                      command=self.on_primary, bg="#2d2d2d", fg="white",
                                      relief="flat", activebackground="#3d3d3d")
        self.primary_btn.grid(row=0, column=0, padx=4, pady=4)

        self.end_btn = tk.Button(btn_frame, text="End Day", width=12,
                                  command=self.on_end_day, bg="#2d2d2d", fg="white",
                                  relief="flat", activebackground="#3d3d3d")
        self.end_btn.grid(row=0, column=1, padx=4, pady=4)

        root.protocol("WM_DELETE_WINDOW", self.on_close)
        self._tick()

    def _totals_text(self):
        return f"Today  -  Work: {fmt_hm(self.work_total)}   Break: {fmt_hm(self.break_total)}"

    def _set_status(self, state):
        self.state = state
        self.status_var.set(state)
        self.status_label.config(fg=STATUS_COLORS[state])

    def on_primary(self):
        now = datetime.now()
        if self.state == IDLE:
            self.segment_start = now
            self._set_status(WORKING)
            self.primary_btn.config(text="Take Break")
            if self.first_start is None:
                self.first_start = now.strftime("%H:%M:%S")

        elif self.state == WORKING:
            dur = append_segment("work", self.segment_start, now)
            self.work_total += dur
            self.segment_start = now
            self._set_status(BREAK)
            self.primary_btn.config(text="Resume Work")

        elif self.state == BREAK:
            dur = append_segment("break", self.segment_start, now)
            self.break_total += dur
            self.segment_start = now
            self._set_status(WORKING)
            self.primary_btn.config(text="Take Break")

        self.last_end = now.strftime("%H:%M:%S")
        self.totals_var.set(self._totals_text())

    def on_end_day(self):
        now = datetime.now()
        if self.state in (WORKING, BREAK):
            seg_type = "work" if self.state == WORKING else "break"
            dur = append_segment(seg_type, self.segment_start, now)
            if seg_type == "work":
                self.work_total += dur
            else:
                self.break_total += dur
            self.last_end = now.strftime("%H:%M:%S")

        ensure_summary_file()
        with open(SUMMARY_FILE, "a", newline="") as f:
            csv.writer(f).writerow([
                today_str(),
                self.first_start or "",
                self.last_end or "",
                f"{self.work_total:.0f}",
                f"{self.break_total:.0f}",
            ])

        self._set_status(IDLE)
        self.primary_btn.config(text="Start Work")
        self.segment_start = None
        self.totals_var.set(self._totals_text())

    def on_close(self):
        # Auto-save an in-progress segment so nothing is lost on close.
        if self.state in (WORKING, BREAK):
            now = datetime.now()
            seg_type = "work" if self.state == WORKING else "break"
            append_segment(seg_type, self.segment_start, now)
        self.root.destroy()

    def _tick(self):
        if self.state != IDLE and self.segment_start:
            elapsed = (datetime.now() - self.segment_start).total_seconds()
            self.timer_var.set(fmt_hms(elapsed))
        else:
            self.timer_var.set("00:00:00")
        self.root.after(1000, self._tick)


if __name__ == "__main__":
    ensure_log_file()
    root = tk.Tk()
    app = App(root)
    root.mainloop()
