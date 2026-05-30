"""XML parser and search-performance comparison utilities (api package).

This module parses the SMS XML and exposes:
- `transactions_list` (list of dicts)
- `transactions_dict` (id -> dict)
- `get_next_id()`

Running this module directly prints a JSON sample (first 5 records)
"""
from xml.etree import ElementTree as ET
import os
from typing import List, Dict

# Candidate XML paths (tries in order)
DEFAULT_XML_PATHS = [
    os.path.join("database", "raw", "momo_sms.xml"),
    os.path.join("database", "raw", "modified_sms_v2.xml"),
    "modified_sms_v2.xml",
]


def find_xml_path() -> str:
    """Return the first existing XML path, or raise FileNotFoundError."""
    for p in DEFAULT_XML_PATHS:
        if os.path.exists(p):
            return p
    raise FileNotFoundError("No XML file found in default locations.")


def parse_xml(path: str) -> List[Dict]:
    """Parse the XML at `path` and return list of transaction dicts.

    Each `<sms ... />` element's attributes are preserved. An integer
    `id` (starting at 1) is added to each record.
    """
    tree = ET.parse(path)
    root = tree.getroot()

    transactions: List[Dict] = []
    next_id = 1
    for sms in root.findall('.//sms'):
        tx: Dict = dict(sms.attrib)
        tx["id"] = next_id
        transactions.append(tx)
        next_id += 1

    return transactions


# Build data structures at import time
xml_path = None
try:
    xml_path = find_xml_path()
    _transactions_list = parse_xml(xml_path)
except FileNotFoundError:
    _transactions_list = []

transactions_list: List[Dict] = _transactions_list
transactions_dict: Dict[int, Dict] = {tx["id"]: tx for tx in transactions_list}


def get_next_id() -> int:
    if not transactions_list:
        return 1
    return max(tx["id"] for tx in transactions_list) + 1
