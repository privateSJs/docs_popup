import sys
from pathlib import Path

import yaml

from popup import ParameterPopup
from translator import Translator


class Configurator:
    CONFIG_DIRECTORY_PATH: str = "config"


class YamlReader(Configurator):
    def __init__(self):
        super().__init__()
        self.path = Path(self.CONFIG_DIRECTORY_PATH)
        self.yaml_data = self.read_configuration()

    def read_configuration(self):
        solution = {}
        for file in self.path.glob("*.yaml"):
            with file.open("r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                if isinstance(data, dict):
                    solution.update(data)
        return solution


class TextBuilder(YamlReader):
    def __init__(self, address=None, parameter=None, value=None, translator=None):
        super().__init__()
        self.address = address
        self.parameter = parameter
        self.value = value
        self.translator = translator

    def build_text(self):
        text = ""

        if not self.address:
            text += self.translator.t("no_object") + "\n\n"
            text += self.translator.t("available_objects") + "\n"
            text += "\n".join(f"• {addr}" for addr in self.yaml_data) + "\n\n"

        if self.parameter and not self.address:
            text += f"{self.translator.t('parameter_label')} {self.parameter}\n"
            text += self.translator.t("found_in") + "\n"
            found = []
            for addr, params in self.yaml_data.items():
                if self.parameter in params:
                    found.append(
                        f"• {addr} (ID: {params[self.parameter].get('id', '-')})"
                    )
            if found:
                text += "\n".join(found) + "\n\n"
            else:
                text += self.translator.t("parameter_not_found") + "\n\n"

        if self.address and self.parameter:
            group = self.yaml_data.get(self.address)
            if not group:
                text += f"{self.translator.t('object_not_exist')}\n"
                return text

            param = group.get(self.parameter)
            if not param:
                text += f"{self.translator.t('param_not_exist')}\n"
                return text

            text += f"{self.translator.t('object_label')} {self.address}\n"
            text += f"{self.translator.t('parameter')} {self.parameter}\n"
            text += f"{self.translator.t('id_label')} {param.get('id', '-')}\n\n"

            values = param.get("possible_values", {})

            if self.value is not None:
                description = values.get(
                    self.value, f"{self.translator.t('unknown_value')}"
                )
                text += f"{self.translator.t('value_label')}\n    • {self.value} → {description}\n\n"

            text += f"{self.translator.t('possible_values')}\n"
            for k, v in values.items():
                text += f"    • {k} – {v}\n"

        elif self.address and not self.parameter:
            text += f"{self.translator.t('object_only_label')} {self.address}:\n"
            for key, param in self.yaml_data[self.address].items():
                text += f"• {key} (ID: {param.get('id', '-')})\n"

        return text

    @classmethod
    def from_line(cls, line: str, translator=None):
        yaml_data = YamlReader().yaml_data
        words = line.strip().replace(":", " ").replace(",", " ").split()

        address = None
        parameter = None
        value = None

        for addr in yaml_data:
            if addr in words:
                address = addr
                break

        if address and address not in yaml_data:
            return cls(None, None, None)

        if address:
            for key in yaml_data.get(address, {}):
                if key in words:
                    parameter = key
                    break

        if not address and not parameter:
            for addr, params in yaml_data.items():
                for key in params:
                    if key in words:
                        parameter = key
                        break
                if parameter:
                    break

        if parameter and address:
            possible_vals = yaml_data[address][parameter].get("possible_values", {})
            for word in reversed(words):
                if word.isdigit() and int(word) in possible_vals:
                    value = int(word)
                    break

        return cls(address, parameter, value, translator=translator)


def main():
    if len(sys.argv) < 3:
        print("❌ Need FilePath and LineNumber as arguments.")
        return

    file_path = sys.argv[1]
    line_num = int(sys.argv[2])

    try:
        with open(file_path, encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
        return

    if line_num < 1 or line_num > len(lines):
        print("❌ Invalid line number.")
        return

    line = lines[line_num - 1].strip()
    translator = Translator()
    builder = TextBuilder().from_line(line, translator=translator)
    popup = ParameterPopup(builder=builder, translator=translator)
    popup.mainloop()


if __name__ == "__main__":
    main()
