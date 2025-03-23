from pathlib import Path

import yaml


class Translator:
    config_path = Path("locales/config.yaml")
    locales_path = Path("locales/language")
    default_language = "en"

    def __init__(self):
        self.language = self.get_language()
        self.translations = self.load_translations(self.language)

    def load_translations(self, lang_code):
        file = self.locales_path / f"{lang_code}.yaml"
        if not file.exists():
            file = self.locales_path / "en.yaml"
        with file.open("r", encoding="utf-8") as fr:
            return yaml.safe_load(fr)

    def t(self, key_path: str):
        keys = key_path.split(".")
        value = self.translations
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return f"[{key_path}]"
        return value or f"[{key_path}]"

    def set_language(self, lang_code):
        if self.config_path.exists():
            with self.config_path.open("r", encoding="utf-8") as fr:
                config = yaml.safe_load(fr) or {}
            config["language"] = lang_code
            with self.config_path.open("w", encoding="utf-8") as fw:
                yaml.safe_dump(config, fw)

        # 🧠 DODAJ TO, żeby zadziałało od razu
        self.language = lang_code
        self.translations = self.load_translations(lang_code)

    def get_language(self):
        if not self.config_path.exists():
            return "en"
        with self.config_path.open("r", encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}
            return config.get("language", "en")
