from triadlang.adapters.base import BaseAdapter
from triadlang.adapters.headless import HeadlessAdapter
from triadlang.adapters.flask import FlaskAdapter

ADAPTERS = {
    'headless': HeadlessAdapter,
    'flask': FlaskAdapter,
}

def get_adapter(name: str):
    if name not in ADAPTERS:
        available = ', '.join(sorted(ADAPTERS.keys()))
        raise ValueError(
            f"unknown adapter '{name}'. available: {available}"
        )
    return ADAPTERS[name]
