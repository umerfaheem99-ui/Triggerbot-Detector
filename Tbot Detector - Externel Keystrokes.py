import tkinter as tk
from pynput import mouse, keyboard
import time
from collections import deque
import os
import threading
import pystray
from PIL import Image, ImageDraw

WINDOW_MS = 600
UPDATE_MS = 50
MAX_CPS   = 20

BG        = "#09090b"
CARD      = "#111114"
BORDER    = "#23232b"

WHITE     = "#f4f4f5"
DIM       = "#8b8b95"

FONT      = "Segoe UI"

TRANS_KEY = "#010101"

def lerp_hex(c1, c2, t):

    t = max(0.0, min(1.0, t))

    def ch(s, e):
        return int(
            int(s, 16) +
            (int(e, 16) - int(s, 16)) * t
        )

    r = ch(c1[1:3], c2[1:3])
    g = ch(c1[3:5], c2[3:5])
    b = ch(c1[5:7], c2[5:7])

    return f"#{r:02x}{g:02x}{b:02x}"

def rounded_rect(canvas, x1, y1, x2, y2, r=20, **kwargs):

    points = [
        x1+r, y1,
        x2-r, y1,

        x2, y1,
        x2, y1+r,

        x2, y2-r,
        x2, y2,

        x2-r, y2,
        x1+r, y2,

        x1, y2,
        x1, y2-r,

        x1, y1+r,
        x1, y1
    ]

    return canvas.create_polygon(
        points,
        smooth=True,
        splinesteps=36,
        **kwargs
    )

class App:

    def __init__(self):

        self.ltimes = deque()
        self.rtimes = deque()

        self.lmb = False
        self.rmb = False

        self.keys = {
            k: False for k in (
                "w", "a", "s", "d", "space"
            )
        }

        self.kalpha = {
            k: 0.0 for k in (
                "w", "a", "s", "d",
                "space", "lmb", "rmb"
            )
        }

        self.theme_color = "#00ff9c"
        self.overlay_scale = 1.0

        self.root = tk.Tk()

        self.root.title("Triggerbot Detector")

        self.root.overrideredirect(True)

        self.root.attributes("-topmost", True)

        self.root.configure(bg=BG)

        self.root.attributes("-alpha", 0.0)

        self._listeners()

        self._start_tray()

        self._setup_ui()

        self.root.mainloop()

    # ====================================
    # TRAY ICON
    # ====================================

    def _make_tray_icon(self):
        img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
        d   = ImageDraw.Draw(img)
        d.ellipse((4, 4, 60, 60), fill="#00ff9c")
        d.text((18, 18), "CPS", fill="#09090b")
        return img

    def _start_tray(self):

        def on_show_hide(icon, item):
            if self.root.state() == "withdrawn":
                self.root.after(0, self.root.deiconify)
            else:
                self.root.after(0, self.root.withdraw)

        def on_exit(icon, item):
            icon.stop()
            self.root.after(0, self._safe_close)

        menu = pystray.Menu(
            pystray.MenuItem("Show / Hide", on_show_hide, default=True),
            pystray.MenuItem("Exit", on_exit)
        )

        self._tray = pystray.Icon(
            "Triggerbot Detector",
            self._make_tray_icon(),
            "Triggerbot Detector",
            menu
        )

        t = threading.Thread(target=self._tray.run, daemon=True)
        t.start()

    # ====================================
    # SAFE CLOSE
    # ====================================

    def _safe_close(self):

        try:
            self.root.quit()
        except:
            pass

        try:
            self.root.destroy()
        except:
            pass

        os._exit(0)

    # ====================================
    # FADE
    # ====================================

    def _fi(self, a=0.0, target=1.0):

        a = min(a + 0.08, target)

        self.root.attributes("-alpha", a)

        if a < target:

            self.root.after(
                12,
                lambda: self._fi(a, target)
            )

    # ====================================
    # HELPERS
    # ====================================

    def _clear(self):

        for w in self.root.winfo_children():
            w.destroy()

    def _center(self, w, h):

        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()

        self.root.geometry(
            f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}"
        )

    def _drag_press(self, e):

        self._ox = (
            e.x_root -
            self.root.winfo_x()
        )

        self._oy = (
            e.y_root -
            self.root.winfo_y()
        )

    def _drag_move(self, e):

        self.root.geometry(
            f"+{e.x_root-self._ox}+{e.y_root-self._oy}"
        )

    def _bind_drag(self, *widgets):

        for t in (list(widgets) or [self.root]):

            t.bind(
                "<ButtonPress-1>",
                self._drag_press
            )

            t.bind(
                "<B1-Motion>",
                self._drag_move
            )

    def _get_cps(self, times):

        now = time.time() * 1000

        while times and now - times[0] > WINDOW_MS:
            times.popleft()

        return len(times)

    # ====================================
    # UI
    # ====================================

    def _setup_ui(self):

        W = 430
        H = 530

        self._center(W, H)

        self._clear()

        self.root.attributes("-alpha", 0.0)

        self._fi()

        cv = tk.Canvas(
            self.root,
            width=W,
            height=H,
            bg=BG,
            highlightthickness=0
        )

        cv.place(x=0, y=0)

        self._bind_drag(cv)

        rounded_rect(
            cv,
            10, 10,
            W-10, H-10,
            r=28,
            fill=CARD,
            outline=BORDER,
            width=2
        )

        cv.create_text(
            W//2,
            55,
            text="Triggerbot Detector",
            font=(FONT, 22, "bold"),
            fill=WHITE
        )

        cv.create_text(
            W//2,
            88,
            text="End Of Triggerbot Users Works On Every Game",
            font=(FONT, 11),
            fill="#00ff9c"
        )

        # ====================================
        # SIZE
        # ====================================

        cv.create_text(
            40,
            145,
            text="Overlay Size",
            anchor="w",
            font=(FONT, 12, "bold"),
            fill=WHITE
        )

        self.size_var = tk.StringVar(value="Medium")

        self.size_buttons = {}

        sizes = [
            ("Small", 55),
            ("Medium", 165),
            ("Large", 295)
        ]

        for txt, x in sizes:

            b = tk.Label(
                self.root,
                text=txt,
                bg="#17171c",
                fg=WHITE,
                font=(FONT, 10, "bold"),
                padx=18,
                pady=9,
                cursor="hand2",
                relief="flat"
            )

            b.place(x=x, y=165)

            self.size_buttons[txt] = b

            b.bind(
                "<Button-1>",
                lambda e, t=txt: self._select_size(t)
            )

        self._refresh_size_buttons()

        # ====================================
        # COLORS
        # ====================================

        cv.create_text(
            40,
            255,
            text="Accent Color",
            anchor="w",
            font=(FONT, 12, "bold"),
            fill=WHITE
        )

        self.color_var = tk.StringVar(value="green")

        self.color_widgets = {}

        colors = [
            ("#00ff9c", "green"),
            ("#3ea6ff", "blue"),
            ("#ff4d6d", "red"),
            ("#a855f7", "purple"),
            ("#ffaa00", "orange")
        ]

        xpos = 45

        for clr, name in colors:

            holder = tk.Frame(
                self.root,
                bg=BG,
                highlightthickness=2,
                highlightbackground=BG
            )

            holder.place(x=xpos, y=275)

            c = tk.Canvas(
                holder,
                width=34,
                height=34,
                bg=BG,
                highlightthickness=0,
                cursor="hand2"
            )

            c.pack()

            c.create_oval(
                2, 2,
                32, 32,
                fill=clr,
                outline=""
            )

            self.color_widgets[name] = holder

            c.bind(
                "<Button-1>",
                lambda e, n=name: self._select_color(n)
            )

            xpos += 60

        self._refresh_color_buttons()

        # ====================================
        # START BUTTON
        # ====================================

        self.start_btn = tk.Label(
            self.root,
            text="START",
            bg=self.theme_color,
            fg=BG,
            font=(FONT, 13, "bold"),
            padx=40,
            pady=14,
            cursor="hand2"
        )

        self.start_btn.place(
            relx=0.5,
            y=390,
            anchor="center"
        )

        self.start_btn.bind(
            "<Button-1>",
            lambda e: self._launch_overlay()
        )

        # ====================================
        # CLOSE
        # ====================================

        close_btn = tk.Label(
            self.root,
            text="✕",
            bg=CARD,
            fg=DIM,
            font=(FONT, 14, "bold"),
            cursor="hand2"
        )

        close_btn.place(x=W-42, y=22)

        close_btn.bind(
            "<Button-1>",
            lambda e: self._safe_close()
        )

        # ====================================
        # FOOTER
        # ====================================

        cv.create_text(
            W//2,
            H-35,
            text="MADE BY R3MU",
            font=(FONT, 10),
            fill=DIM
        )

    # ====================================
    # SELECT SIZE
    # ====================================

    def _select_size(self, size):

        self.size_var.set(size)

        self._refresh_size_buttons()

    def _refresh_size_buttons(self):

        for name, btn in self.size_buttons.items():

            if self.size_var.get() == name:

                btn.config(
                    bg=self.theme_color,
                    fg=BG
                )

            else:

                btn.config(
                    bg="#17171c",
                    fg=WHITE
                )

    # ====================================
    # SELECT COLOR
    # ====================================

    def _select_color(self, color):

        self.color_var.set(color)

        if color == "blue":
            self.theme_color = "#3ea6ff"

        elif color == "red":
            self.theme_color = "#ff4d6d"

        elif color == "purple":
            self.theme_color = "#a855f7"

        elif color == "orange":
            self.theme_color = "#ffaa00"

        else:
            self.theme_color = "#00ff9c"

        self.start_btn.config(
            bg=self.theme_color
        )

        self._refresh_color_buttons()
        self._refresh_size_buttons()

    def _refresh_color_buttons(self):

        for name, widget in self.color_widgets.items():

            if self.color_var.get() == name:

                widget.config(
                    highlightbackground=WHITE
                )

            else:

                widget.config(
                    highlightbackground=BG
                )

    # ====================================
    # LAUNCH
    # ====================================

    def _launch_overlay(self):

        size = self.size_var.get()

        if size == "Small":
            self.overlay_scale = 0.85

        elif size == "Large":
            self.overlay_scale = 1.25

        else:
            self.overlay_scale = 1.0

        self._compact_ui()

    # ====================================
    # OVERLAY
    # ====================================

    def _compact_ui(self):

        BS = int(46 * self.overlay_scale)

        G  = 5
        P  = 7

        W = P*2 + BS*3 + G*2
        H = P*2 + BS*5 + G*4

        self.root.geometry(f"{W}x{H}+80+80")

        self.root.configure(bg=TRANS_KEY)

        self.root.attributes(
            "-transparentcolor",
            TRANS_KEY
        )

        self.root.attributes("-alpha", 1.0)

        # Windows API se HWND_TOPMOST force — fullscreen games ke upar bhi rahega
        try:
            import ctypes
            HWND_TOPMOST   = -1
            SWP_NOMOVE     = 0x0002
            SWP_NOSIZE     = 0x0001
            SWP_NOACTIVATE = 0x0010
            hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
            ctypes.windll.user32.SetWindowPos(
                hwnd, HWND_TOPMOST, 0, 0, 0, 0,
                SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE
            )
        except Exception:
            pass

        self._clear()

        cv = tk.Canvas(
            self.root,
            width=W,
            height=H,
            bg=TRANS_KEY,
            highlightthickness=0
        )

        cv.place(x=0, y=0)

        self._bind_drag(cv)

        self._ccv = cv
        self._ck  = (BS, G, P, W, H)

        self._update_loop()

    # ====================================
    # REDRAW
    # ====================================

    def _redraw(self):

        cv = self._ccv

        BS, G, P, W, H = self._ck

        cv.delete("all")

        lc = self._get_cps(self.ltimes)
        rc = self._get_cps(self.rtimes)

        def bg_c(key):

            return lerp_hex(
                "#1a1a1a",
                self.theme_color,
                self.kalpha.get(key, 0.0)
            )

        def txt_c(key):

            return lerp_hex(
                "#777777",
                WHITE,
                self.kalpha.get(key, 0.0)
            )

        def key(col, row, wc, label, k):

            x1 = P + col * (BS + G)
            y1 = P + row * (BS + G)

            x2 = x1 + wc * BS + (wc - 1) * G
            y2 = y1 + BS

            rounded_rect(
                cv,
                x1,
                y1,
                x2,
                y2,
                r=12,
                fill=bg_c(k),
                outline=""
            )

            cv.create_text(
                (x1+x2)//2,
                (y1+y2)//2,
                text=label,
                font=(FONT, 10, "bold"),
                fill=txt_c(k)
            )

        key(1,0,1,"W","w")
        key(0,1,1,"A","a")
        key(1,1,1,"S","s")
        key(2,1,1,"D","d")

        key(0,3,3,"SPACE","space")

        hw = (W-P*2-G)//2

        yr = P + 2*(BS+G)

        rounded_rect(
            cv,
            P,
            yr,
            P+hw,
            yr+BS,
            r=12,
            fill=bg_c("lmb"),
            outline=""
        )

        cv.create_text(
            (P+P+hw)//2,
            (yr+yr+BS)//2,
            text="LMB",
            font=(FONT, 10, "bold"),
            fill=txt_c("lmb")
        )

        rounded_rect(
            cv,
            P+hw+G,
            yr,
            W-P,
            yr+BS,
            r=12,
            fill=bg_c("rmb"),
            outline=""
        )

        cv.create_text(
            (P+hw+G+W-P)//2,
            (yr+yr+BS)//2,
            text="RMB",
            font=(FONT, 10, "bold"),
            fill=txt_c("rmb")
        )

        y1 = P + 4*(BS+G)
        y2 = y1 + BS

        mid = W//2

        rounded_rect(
            cv,
            P,
            y1,
            mid-2,
            y2,
            r=12,
            fill="#161616",
            outline=""
        )

        lfw = int(
            min(lc, MAX_CPS)
            / MAX_CPS
            * (mid-2-P)
        )

        if lfw:

            rounded_rect(
                cv,
                P,
                y2-5,
                P+lfw,
                y2,
                r=4,
                fill=self.theme_color,
                outline=""
            )

        cv.create_text(
            (P+mid-2)//2,
            (y1+y2)//2,
            text=f"{lc} CPS",
            font=(FONT, 10, "bold"),
            fill=self.theme_color
        )

        rounded_rect(
            cv,
            mid+2,
            y1,
            W-P,
            y2,
            r=12,
            fill="#161616",
            outline=""
        )

        rfw = int(
            min(rc, MAX_CPS)
            / MAX_CPS
            * (W-P-mid-2)
        )

        if rfw:

            rounded_rect(
                cv,
                mid+2,
                y2-5,
                mid+2+rfw,
                y2,
                r=4,
                fill=self.theme_color,
                outline=""
            )

        cv.create_text(
            (mid+2+W-P)//2,
            (y1+y2)//2,
            text=f"{rc} CPS",
            font=(FONT, 10, "bold"),
            fill=self.theme_color
        )

    # ====================================
    # ANIMATION
    # ====================================

    def _animate_keys(self):

        for k in self.kalpha:

            pressed = (
                self.lmb if k == "lmb"
                else self.rmb if k == "rmb"
                else self.keys.get(k, False)
            )

            if pressed:

                self.kalpha[k] = min(
                    self.kalpha[k] + 0.30,
                    1.0
                )

            else:

                self.kalpha[k] = max(
                    self.kalpha[k] - 0.18,
                    0.0
                )

    # ====================================
    # LOOP
    # ====================================

    def _update_loop(self):

        try:

            self._animate_keys()

            self._redraw()

            # Fullscreen windows ke upar rehne ke liye topmost re-apply
            self.root.attributes("-topmost", True)
            self.root.lift()

        except:
            pass

        self.root.after(
            UPDATE_MS,
            self._update_loop
        )

    # ====================================
    # LISTENERS
    # ====================================

    def _listeners(self):

        def on_click(x, y, btn, pressed):

            if btn == mouse.Button.left:

                self.lmb = pressed

                if pressed:

                    self.ltimes.append(
                        time.time() * 1000
                    )

            elif btn == mouse.Button.right:

                self.rmb = pressed

                if pressed:

                    self.rtimes.append(
                        time.time() * 1000
                    )

        def on_press(key):

            try:

                k = (
                    key.char.lower()
                    if hasattr(key, "char")
                    and key.char
                    else None
                )

                if k in self.keys:
                    self.keys[k] = True

            except:
                pass

            if key == keyboard.Key.space:
                self.keys["space"] = True

        def on_release(key):

            try:

                k = (
                    key.char.lower()
                    if hasattr(key, "char")
                    and key.char
                    else None
                )

                if k in self.keys:
                    self.keys[k] = False

            except:
                pass

            if key == keyboard.Key.space:
                self.keys["space"] = False

        ml = mouse.Listener(
            on_click=on_click
        )

        ml.daemon = True

        ml.start()

        kl = keyboard.Listener(
            on_press=on_press,
            on_release=on_release
        )

        kl.daemon = True

        kl.start()

if __name__ == "__main__":
    App()
