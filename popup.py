from pathlib import Path

import ttkbootstrap as ttk
import yaml


class ParameterPopup(ttk.Window):
    container = None
    top_frame = None
    canvas = None
    mid_frame = None
    bot_frame = None
    scrollbar = None
    scroll_frame = None
    project_name = Path().resolve().name
    lang_path = Path("locales/language")
    theme_path = "locales/config.yaml"
    themes = {
        "Light": [
            "cosmo",
            "flatly",
            "journal",
            "litera",
            "lumen",
            "minty",
            "pulse",
            "sandstone",
            "yeti",
            "morph",
            "simplex",
            "cerculean",
        ],
        "Dark": ["solar", "superhero", "darkly", "cyborg", "vapor"],
    }

    def __init__(self, builder=None, translator=None):
        super().__init__(
            title="Info Window",
            themename=self.load_theme(),
            iconphoto="",
            size=(400, 200),
            position=None,
            minsize=(200, 200),
            maxsize=(800, 400),
            resizable=(False, False),
            hdpi=True,
            scaling=0.0,
            transient=None,
            overrideredirect=True,
            alpha=0.0,
        )
        #
        self.builder = builder
        self.translator = translator
        self.title = self.translator.t("title")

        #
        self.text = self.builder.build_text()

        #
        self.window_position()

        #
        self.create_top_section()

        #
        self.create_footer()

        #
        self.create_container()

        #
        self.create_scrollable_area()

        #
        self.label_content()

        #
        self.enable_drag()

        #
        self.bind_scroll()

        #
        # self.bind_discard()

        #
        self.fade_in()

    def window_position(self):
        x = self.winfo_pointerx() + 20
        y = self.winfo_pointery() + 20
        self.geometry(f"480x300+{x}+{y}")

    def load_theme(self):
        try:
            with open(self.theme_path, "r") as f:
                config = yaml.safe_load(f)
                theme = config.get("theme", "darkly")
        except FileNotFoundError as e:
            theme = "darkly"
            raise FileNotFoundError(f"Path: {self.theme_path} does not exist")
        return theme

    def save_theme(self, theme_name):
        self.style.theme_use(theme_name)
        with open(self.theme_path, "w") as f:
            yaml.safe_dump({"theme": theme_name}, f)

    def label_content(self):
        self.mid_frame = ttk.Frame(self.scroll_frame)
        self.mid_frame.pack(fill="both", expand=True, padx=(10, 20), pady=(10, 10))

        content = ttk.Text(
            self.mid_frame,
            wrap="word",
            border=0,  # dopasowanie do motywu
            font=("Segoe UI", 11),
            relief="ridge",
            cursor="arrow",
            height=10,
            width=52,
        )
        content.insert("end", self.text)
        content.configure(
            state="disabled",
            padx=10,  # ⬅️ wewnętrzny margines z lewej
            pady=5,  # ⬅️ góra-dół
        )
        content.pack(expand=True, fill="both")

    def enable_drag(self):
        def start_move(event):
            self._offset_x = event.x_root
            self._offset_y = event.y_root

        def do_move(event):
            dx = event.x_root - self._offset_x
            dy = event.y_root - self._offset_y

            x = self.winfo_x() + dx
            y = self.winfo_y() + dy

            self.geometry(f"+{x}+{y}")

            self._offset_x = event.x_root
            self._offset_y = event.y_root

        self.top_frame.bind("<ButtonPress-1>", start_move)
        self.top_frame.bind("<B1-Motion>", do_move)

    def bind_scroll(self):
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)
        self.canvas.bind_all(
            "<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units")
        )
        self.canvas.bind_all(
            "<Button-5>", lambda e: self.canvas.yview_scroll(1, "units")
        )

    def bind_discard(self):
        self.bind("<Button-1>", lambda e: self.fade_out())

    def create_container(self):
        self.container = ttk.Frame(self)
        self.container.pack(expand=True, fill="both")

    def create_top_section(self):
        self.top_frame = ttk.Frame(self, height=60)
        self.top_frame.pack(side="top", fill="x")

        ttk.Separator(self.top_frame, orient="horizontal").pack(fill="x", side="bottom")

        # ---- Menu button ----
        menu_btn = ttk.Menubutton(self.top_frame, text="☰", bootstyle="outline")
        menu = ttk.Menu(menu_btn, tearoff=0)

        # ---- Themes submenu ----
        themes_menu = ttk.Menu(menu, tearoff=0)
        light_menu = ttk.Menu(themes_menu, tearoff=0)
        dark_menu = ttk.Menu(themes_menu, tearoff=0)

        for theme in self.themes["Light"]:
            light_menu.add_command(
                label=theme.capitalize(), command=lambda t=theme: self.save_theme(t)
            )

        for theme in self.themes["Dark"]:
            dark_menu.add_command(
                label=theme.capitalize(), command=lambda t=theme: self.save_theme(t)
            )

        themes_menu.add_cascade(
            label=f"{self.translator.t('menu.themeslight')}", menu=light_menu
        )
        themes_menu.add_cascade(
            label=f"{self.translator.t('menu.themesdark')}", menu=dark_menu
        )
        menu.add_cascade(label=f"{self.translator.t('menu.themes')}", menu=themes_menu)

        # ---- Language menu ----
        lang_menu = ttk.Menu(menu, tearoff=0)
        languages = [lang.stem for lang in self.lang_path.glob("*.yaml")]
        for lang in languages:
            lang_menu.add_command(
                label=lang.upper(),
                command=lambda l=lang: self.set_language(l),
            )
        menu.add_cascade(label=f"{self.translator.t('menu.language')}", menu=lang_menu)

        # ---- Close button ----
        menu.add_command(label=f"{self.translator.t('discard')}", command=self.fade_out)

        menu_btn["menu"] = menu
        menu_btn.pack(side="left", padx=10, pady=10)

        ttk.Label(
            self.top_frame,
            text=f"📘 {self.project_name}",
            font=("Segoe UI", 12, "bold"),
        ).pack(side="left", padx=10, pady=10)

        ttk.Button(
            self.top_frame,
            text="❌",
            bootstyle="danger-link",
            command=self.fade_out,
            width=2,
        ).pack(side="right", padx=5, pady=0)

    def create_scrollable_area(self):
        # 🎨 Canvas
        self.canvas = ttk.Canvas(self.container, highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)

        self.scrollbar = ttk.Scrollbar(
            self.container, orient="vertical", command=self.canvas.yview
        )
        self.scrollbar.pack(side="right", fill="y")

        self.scroll_frame = ttk.Frame(self.canvas)

        self.scroll_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )

        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

    def create_footer(self):
        self.bot_frame = ttk.Frame(self, padding=(10, 10))
        self.bot_frame.pack(fill="x", side="bottom")

        ttk.Separator(self.bot_frame, orient="horizontal").pack(fill="x", pady=(0, 5))

        ttk.Label(
            self.bot_frame,
            text="© 2025 privateSJs – LookAtMe for ExternalTools Python",
            font=("Terminal", 9, "italic"),
            anchor="ne",
            justify="center",
        ).pack(fill="x")

    def add_separator(self):
        sep = ttk.Separator(self.scroll_frame, orient="horizontal")
        sep.pack(fill="x", pady=(0, 10))

    def on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def fade_in(self, step=0.05):
        alpha = self.attributes("-alpha")
        if alpha < 1.0:
            alpha = min(alpha + step, 1.0)
            self.attributes("-alpha", alpha)
            self.after(10, self.fade_in)

    def fade_out(self, step=0.05):
        alpha = self.attributes("-alpha")
        if alpha > 0.0:
            alpha = max(alpha - step, 0.0)
            self.attributes("-alpha", alpha)
            self.after(10, self.fade_out)
        else:
            self.destroy()

    def rebuild_ui(self):
        self.top_frame.destroy()
        self.container.destroy()
        self.bot_frame.destroy()

        self.text = self.builder.build_text()

        self.create_top_section()
        self.create_footer()
        self.create_container()
        self.create_scrollable_area()
        self.label_content()
        self.enable_drag()
        self.bind_scroll()

    def set_language(self, lang_code):
        self.translator.set_language(lang_code)
        self.builder.translator = self.translator
        self.rebuild_ui()
