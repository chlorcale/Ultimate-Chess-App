from __future__ import annotations

import tkinter as tk


# ============================================================
# COLORS
# ============================================================

BG = "#1E2024"
PANEL = "#292C31"
PANEL_DARK = "#24262A"

TEXT = "#F3F4F6"
TEXT_MUTED = "#9CA3AF"

BORDER = "#3A3F46"

# Stockfish information
BLUE_LIGHT = "#DDF3FF"
BLUE_LIGHT_TEXT = "#123B4A"
BLUE_MUTED = "#5D7E8C"

# Best move
BLUE_DARK = "#075985"
BLUE_DARK_TEXT = "#E8F7FF"

# Last move highlight
MOVE_HIGHLIGHT = "#DFF3FF"
MOVE_HIGHLIGHT_TEXT = "#075985"


# ============================================================
# FIXED WINDOW
# ============================================================

WINDOW_WIDTH = 470
WINDOW_HEIGHT = 390

WINDOW_TITLE = "Ultimate Stockfish Reader"


class ChessReaderUI:

    def __init__(
        self,
        on_mode_change,
        on_close,
    ):

        self.on_mode_change = on_mode_change
        self.on_close = on_close


        # ====================================================
        # ROOT
        # ====================================================

        self.root = tk.Tk()

        self.root.title(
            WINDOW_TITLE
        )

        # CỐ ĐỊNH kích thước
        self.root.geometry(
            f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}"
        )

        self.root.resizable(
            False,
            False,
        )

        self.root.configure(
            bg=BG
        )

        self.root.protocol(
            "WM_DELETE_WINDOW",
            self._close,
        )


        # ====================================================
        # ALWAYS ON TOP
        # ====================================================

        self.topmost_var = tk.BooleanVar(
            value=True
        )

        self.root.attributes(
            "-topmost",
            True
        )


        # ====================================================
        # MAIN
        #
        # Grid:
        #
        # row 0 = header
        # row 1 = controls
        # row 2 = move list -> expandable
        # row 3 = engine -> FIXED
        #
        # Chỉ row 2 được phép co giãn.
        # ====================================================

        self.root.grid_rowconfigure(
            0,
            weight=0,
        )

        self.root.grid_rowconfigure(
            1,
            weight=0,
        )

        self.root.grid_rowconfigure(
            2,
            weight=1,
        )

        self.root.grid_rowconfigure(
            3,
            weight=0,
        )

        self.root.grid_columnconfigure(
            0,
            weight=1,
        )


        self.main = tk.Frame(
            self.root,
            bg=BG,
        )

        self.main.grid(
            row=0,
            column=0,
            rowspan=4,
            sticky="nsew",
            padx=10,
            pady=8,
        )


        # ====================================================
        # HEADER
        # ====================================================

        self._build_header()


        # ====================================================
        # CONTROLS
        # ====================================================

        self._build_controls()


        # ====================================================
        # MOVE LIST
        # ====================================================

        self._build_move_list()


        # ====================================================
        # ENGINE
        # ====================================================

        self._build_engine_area()


    # ========================================================
    # HEADER
    # ========================================================

    def _build_header(self):

        self.header = tk.Frame(
            self.main,
            bg=BG,
        )

        self.header.pack(
            fill="x",
            pady=(0, 4),
        )


        # ----------------------------------------------------
        # Title
        # ----------------------------------------------------

        title = tk.Label(
            self.header,
            text="♟ STOCKFISH READER",
            bg=BG,
            fg=TEXT,
            font=(
                "Segoe UI",
                11,
                "bold",
            ),
        )

        title.pack(
            side="left"
        )


        # ----------------------------------------------------
        # Status
        # ----------------------------------------------------

        self.status_label = tk.Label(
            self.header,
            text="Connecting...",
            bg=BG,
            fg=TEXT_MUTED,
            font=(
                "Segoe UI",
                8,
            ),
        )

        self.status_label.pack(
            side="right"
        )


    # ========================================================
    # CONTROLS
    # ========================================================

    def _build_controls(self):

        self.controls = tk.Frame(
            self.main,
            bg=BG,
            height=28,
        )

        self.controls.pack(
            fill="x",
            pady=(0, 6),
        )

        self.controls.pack_propagate(
            False
        )


        # ----------------------------------------------------
        # Always on top
        # ----------------------------------------------------

        topmost = tk.Checkbutton(
            self.controls,
            text="Always on top",
            variable=self.topmost_var,
            command=self._toggle_topmost,

            bg=BG,
            fg=TEXT,

            activebackground=BG,
            activeforeground=TEXT,

            selectcolor=PANEL_DARK,

            highlightthickness=0,
            bd=0,

            font=(
                "Segoe UI",
                8,
            ),
        )

        topmost.pack(
            side="left",
            padx=(0, 12),
        )


        # ----------------------------------------------------
        # Analysis
        # ----------------------------------------------------

        tk.Label(
            self.controls,
            text="Phân tích:",
            bg=BG,
            fg=TEXT,
            font=(
                "Segoe UI",
                8,
                "bold",
            ),
        ).pack(
            side="left",
            padx=(0, 4),
        )


        self.mode_var = tk.StringVar(
            value="both"
        )


        for text, value in (
            ("Trắng", "white"),
            ("Đen", "black"),
            ("Cả hai", "both"),
        ):

            button = tk.Radiobutton(
                self.controls,

                text=text,
                value=value,

                variable=self.mode_var,
                command=self._mode_changed,

                bg=BG,
                fg=TEXT,

                activebackground=BG,
                activeforeground=TEXT,

                selectcolor=PANEL_DARK,

                highlightthickness=0,
                bd=0,

                font=(
                    "Segoe UI",
                    8,
                ),
            )

            button.pack(
                side="left"
            )


    # ========================================================
    # MOVE LIST
    # ========================================================

    def _build_move_list(self):

        self.move_outer = tk.Frame(
            self.main,
            bg=PANEL,

            highlightbackground=BORDER,
            highlightthickness=1,
        )

        self.move_outer.pack(
            fill="both",
            expand=True,
            pady=(0, 8),
        )


        # ----------------------------------------------------
        # Header
        # ----------------------------------------------------

        move_header = tk.Frame(
            self.move_outer,
            bg=PANEL_DARK,
            height=25,
        )

        move_header.pack(
            fill="x"
        )

        move_header.pack_propagate(
            False
        )


        tk.Label(
            move_header,
            text="MOVE LIST",
            bg=PANEL_DARK,
            fg=TEXT_MUTED,
            font=(
                "Segoe UI",
                7,
                "bold",
            ),
        ).pack(
            side="left",
            padx=9,
        )


        # ----------------------------------------------------
        # Text frame
        # ----------------------------------------------------

        text_frame = tk.Frame(
            self.move_outer,
            bg=PANEL,
        )

        text_frame.pack(
            fill="both",
            expand=True,
        )


        # ----------------------------------------------------
        # Scrollbar
        # ----------------------------------------------------

        scrollbar = tk.Scrollbar(
            text_frame,
            orient="vertical",
            width=12,
        )

        scrollbar.pack(
            side="right",
            fill="y",
        )


        # ----------------------------------------------------
        # Move text
        #
        # 7 dòng là mục tiêu hiển thị tối thiểu.
        #
        # height=7
        # ====================================================

        self.move_text = tk.Text(
            text_frame,

            bg=PANEL,
            fg=TEXT,

            insertbackground=TEXT,

            selectbackground="#3B82F6",
            selectforeground="white",

            relief="flat",
            bd=0,

            padx=10,
            pady=7,

            font=(
                "Consolas",
                10,
            ),

            wrap="none",

            height=7,

            yscrollcommand=scrollbar.set,

            state="disabled",
        )

        self.move_text.pack(
            side="left",
            fill="both",
            expand=True,
        )


        scrollbar.config(
            command=self.move_text.yview
        )


        # ----------------------------------------------------
        # Last move highlight
        # ----------------------------------------------------

        self.move_text.tag_configure(
            "last_move",

            background=MOVE_HIGHLIGHT,
            foreground=MOVE_HIGHLIGHT_TEXT,
        )


    # ========================================================
    # ENGINE AREA
    # ========================================================

    def _build_engine_area(self):

        # ====================================================
        # Outer engine area
        # ====================================================

        self.engine_area = tk.Frame(
            self.main,
            bg=BG,

            height=78,
        )

        self.engine_area.pack(
            fill="x",
        )

        # Bắt buộc giữ chiều cao
        self.engine_area.pack_propagate(
            False
        )


        # ====================================================
        # STOCKFISH CARD
        # ====================================================

        self.engine_frame = tk.Frame(
            self.engine_area,
            bg=BLUE_LIGHT,

            width=220,

            highlightbackground=BLUE_LIGHT,
            highlightthickness=1,
        )

        self.engine_frame.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 4),
        )


        # ====================================================
        # STOCKFISH TITLE
        # ====================================================

        tk.Label(
            self.engine_frame,

            text="STOCKFISH",

            bg=BLUE_LIGHT,
            fg=BLUE_LIGHT_TEXT,

            font=(
                "Segoe UI",
                8,
                "bold",
            ),

            anchor="w",
        ).pack(
            fill="x",
            padx=10,
            pady=(6, 0),
        )


        # ====================================================
        # EVALUATION
        # ====================================================

        self.eval_label = tk.Label(
            self.engine_frame,

            text="Đánh giá: --",

            bg=BLUE_LIGHT,
            fg=BLUE_LIGHT_TEXT,

            font=(
                "Consolas",
                10,
                "bold",
            ),

            anchor="w",
        )

        self.eval_label.pack(
            fill="x",
            padx=10,
            pady=(4, 0),
        )


        # ====================================================
        # DEPTH
        # ====================================================

        self.depth_label = tk.Label(
            self.engine_frame,

            text="Depth: --",

            bg=BLUE_LIGHT,
            fg=BLUE_MUTED,

            font=(
                "Segoe UI",
                8,
            ),

            anchor="w",
        )

        self.depth_label.pack(
            fill="x",
            padx=10,
            pady=(1, 5),
        )


        # ====================================================
        # BEST MOVE CARD
        # ====================================================

        self.best_move_frame = tk.Frame(
            self.engine_area,

            bg=BLUE_DARK,

            width=220,

            highlightbackground=BLUE_DARK,
            highlightthickness=1,
        )

        self.best_move_frame.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(4, 0),
        )


        # ====================================================
        # BEST MOVE TITLE
        # ====================================================

        tk.Label(
            self.best_move_frame,

            text="BEST MOVE",

            bg=BLUE_DARK,
            fg=BLUE_DARK_TEXT,

            font=(
                "Segoe UI",
                8,
                "bold",
            ),

            anchor="w",
        ).pack(
            fill="x",
            padx=10,
            pady=(6, 0),
        )


        # ====================================================
        # MOVE
        # ====================================================

        self.best_move_label = tk.Label(
            self.best_move_frame,

            text="--",

            bg=BLUE_DARK,
            fg="white",

            font=(
                "Consolas",
                18,
                "bold",
            ),

            anchor="w",
        )

        self.best_move_label.pack(
            fill="x",
            padx=10,
            pady=(0, 0),
        )


        # ====================================================
        # HINT
        # ====================================================

        self.best_move_hint = tk.Label(
            self.best_move_frame,

            text="NƯỚC TIẾP THEO",

            bg=BLUE_DARK,
            fg="#B9E6FF",

            font=(
                "Segoe UI",
                7,
                "bold",
            ),

            anchor="w",
        )

        self.best_move_hint.pack(
            fill="x",
            padx=10,
            pady=(0, 5),
        )


    # ========================================================
    # TOPMOST
    # ========================================================

    def _toggle_topmost(self):

        self.root.attributes(
            "-topmost",
            self.topmost_var.get(),
        )


    # ========================================================
    # MODE
    # ========================================================

    def _mode_changed(self):

        self.on_mode_change(
            self.mode_var.get()
        )


    # ========================================================
    # CLOSE
    # ========================================================

    def _close(self):

        self.on_close()


    # ========================================================
    # MOVE LIST
    # ========================================================

    def set_moves(
        self,
        text: str,
    ):

        self.move_text.config(
            state="normal"
        )

        self.move_text.delete(
            "1.0",
            "end",
        )


        if text:

            lines = text.splitlines()

            for index, line in enumerate(lines):

                # Chèn line
                start = self.move_text.index(
                    "end-1c"
                )

                self.move_text.insert(
                    "end",
                    line,
                )


                # Highlight dòng cuối
                if index == len(lines) - 1:

                    end = self.move_text.index(
                        "end-1c"
                    )

                    self.move_text.tag_add(
                        "last_move",
                        start,
                        end,
                    )


                self.move_text.insert(
                    "end",
                    "\n",
                )


        self.move_text.config(
            state="disabled"
        )


        # Cuộn xuống move mới nhất
        self.move_text.see(
            "end"
        )


    # ========================================================
    # ENGINE RESULT
    # ========================================================

    def set_engine_result(
        self,
        move: str,
        evaluation: str,
        depth: int,
    ):

        # ----------------------------------------------------
        # Không có kết quả
        # ----------------------------------------------------

        if not move:

            self.best_move_label.config(
                text="--"
            )

            self.eval_label.config(
                text="Đánh giá: --"
            )

            self.depth_label.config(
                text="Depth: --"
            )

            return


        # ----------------------------------------------------
        # Best move
        # ----------------------------------------------------

        self.best_move_label.config(
            text=move
        )


        # ----------------------------------------------------
        # Evaluation
        # ----------------------------------------------------

        self.eval_label.config(
            text=f"Đánh giá: {evaluation}"
        )


        # ----------------------------------------------------
        # Depth
        # ----------------------------------------------------

        self.depth_label.config(
            text=f"Depth: {depth}"
        )


    # ========================================================
    # THINKING
    # ========================================================

    def set_thinking(self):

        self.best_move_label.config(
            text="..."
        )

        self.eval_label.config(
            text="Đánh giá: ..."
        )

        self.depth_label.config(
            text="Stockfish đang phân tích"
        )


    # ========================================================
    # STATUS
    # ========================================================

    def set_status(
        self,
        text: str,
    ):

        self.status_label.config(
            text=text
        )


    # ========================================================
    # RUN
    # ========================================================

    def run(self):

        self.root.mainloop()