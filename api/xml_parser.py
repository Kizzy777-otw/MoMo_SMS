"""XML parser and search-performance comparison utilities (api package).

This module parses the SMS XML and exposes:
- `transactions_list` (list of dicts)
- `transactions_dict` (id -> dict)
- `get_next_id()`
- `linear_search(target_id)`
- `dict_lookup(target_id)`
- `compare_search_methods(target_ids)`

Running this module directly prints a JSON sample (first 5 records)
and runs a DSA comparison across at least 20 IDs (or fewer if not available).
"""
from xml.etree import ElementTree as ET
import json
import os
import time
from typing import List, Dict, Optional

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
        tx = dict(sms.attrib)
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
    """Return the next available integer id for a new transaction."""
    if not transactions_list:
        return 1
    return max(tx["id"] for tx in transactions_list) + 1


def linear_search(target_id: int) -> Optional[Dict]:
    """Linear-scan search through `transactions_list` for `target_id`.

    Returns the transaction dict if found, otherwise `None`.
    """
    for tx in transactions_list:
        if tx.get("id") == target_id:
            return tx
    return None


def dict_lookup(target_id: int) -> Optional[Dict]:
    """Dictionary lookup in `transactions_dict` for `target_id`.

    Returns the transaction dict if found, otherwise `None`.
    """
    return transactions_dict.get(target_id)


def compare_search_methods(target_ids: List[int]):
    """Compare timings of `linear_search` vs `dict_lookup` for IDs.

    Uses time.perf_counter() to measure timings, prints per-ID times
    and average times, and prints a short reflection on complexity.
    """
    if not target_ids:
        print("No IDs provided for comparison.")
        return

    linear_times = []
    dict_times = []

    print("ID | linear_search (s) | dict_lookup (s)")
    print("---|-------------------|----------------")

    for tid in target_ids:
        t0 = time.perf_counter()
        _ = linear_search(tid)
        t1 = time.perf_counter()
        lt = t1 - t0

        t0 = time.perf_counter()
        _ = dict_lookup(tid)
        t1 = time.perf_counter()
        dt = t1 - t0

        linear_times.append(lt)
        dict_times.append(dt)

        print(f"{tid} | {lt:.9f} | {dt:.9f}")

    avg_linear = sum(linear_times) / len(linear_times)
    avg_dict = sum(dict_times) / len(dict_times)

    print()
    print(f"Average linear_search: {avg_linear:.9f} s")
    print(f"Average dict_lookup  : {avg_dict:.9f} s")
    print()
    print("Reflection:")
    print("Dictionary lookup is faster on average because it uses a hash table")
    print("with O(1) average-time complexity for key access, while linear_search")
    print("scans each element one-by-one with O(n) time complexity. For large")
    print("datasets the difference grows proportionally to n, making dict lookups")
    print("significantly faster in practice.")


if __name__ == "__main__":
    # Print a JSON sample of the first 5 records
    sample = transactions_list[:5]
    print("Parsed XML from:", xml_path)
    print(json.dumps(sample, indent=2, ensure_ascii=False))

    # Prepare at least 20 IDs for comparison: 1..20 or fewer if not available
    total = len(transactions_list)
    if total == 0:
        print("No transactions to compare.")
    else:
        count = 20 if total >= 20 else total
        ids_to_test = list(range(1, count + 1))
        print(f"\nRunning search method comparison on {len(ids_to_test)} IDs...\n")
        compare_search_methods(ids_to_test)
