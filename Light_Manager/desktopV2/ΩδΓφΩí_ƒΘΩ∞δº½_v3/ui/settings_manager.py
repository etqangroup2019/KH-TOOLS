# -*- coding: utf-8 -*-
"""
مدير إعدادات التخصيص (يحفظ/يقرأ تخصيص الواجهة لكل وحدة)
"""
from __future__ import annotations
from pathlib import Path
import json
from typing import Any, Dict

DEFAULT_SETTINGS: Dict[str, Any] = {
    "ui": {
        "rtl": True,
        "dark_mode": True,
        "sidebar_collapsed": False,
        "font_family": "Tajawal",
        "font_size": 11,
    },
    "modules": {}
}

class SettingsManager:
    def __init__(self, base_dir: Path):
        self.base_dir = Path(base_dir)
        self.file = self.base_dir / 'config' / 'ui_settings.json'
        self.file.parent.mkdir(parents=True, exist_ok=True)
        if not self.file.exists():
            self.save(DEFAULT_SETTINGS)

    def load(self) -> Dict[str, Any]:
        try:
            with open(self.file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return DEFAULT_SETTINGS.copy()

    def save(self, data: Dict[str, Any]) -> None:
        with open(self.file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def get_module_settings(self, module_key: str) -> Dict[str, Any]:
        data = self.load()
        return data.setdefault('modules', {}).setdefault(module_key, {})

    def update_ui(self, **kwargs) -> None:
        data = self.load()
        data['ui'].update(kwargs)
        self.save(data)

    def update_module(self, module_key: str, **kwargs) -> None:
        data = self.load()
        data.setdefault('modules', {}).setdefault(module_key, {}).update(kwargs)
        self.save(data)