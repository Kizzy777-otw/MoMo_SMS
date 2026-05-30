"""DSA Comparison: Linear Search vs Dictionary (Hash Map) Lookup."""
import os
import time
from xml.etree import ElementTree as ET

# Parse the XML and build the data structures
xml_path = os.path.join(os.path.dirname(__file__), "..", "database", "raw", "momo_sms.xml")
tree = ET.parse(xml_path)
root = tree.getroot()

transactions_list = []
transactions_dict = {}
for i, sms in enumerate(root.findall(".//sms"), start=1):
    tx = dict(sms.attrib)
    tx["id"] = str(i)
    transactions_list.append(tx)
    transactions_dict[i] = tx


def linear_search(target_id):
    for tx in transactions_list:
        if tx["id"] == target_id:
            return tx
    return None


def hashmap_lookup(target_id):
    return transactions_dict.get(target_id)


ids_to_test = [str(i) for i in range(1, 21)]

print(f"Dataset size: {len(transactions_list)} transactions")
print(f"Searching for {len(ids_to_test)} IDs\n")

print(f"{'ID':<8} {'Linear':<15} {'HashMap':<15} {'Speedup'}")
print("-" * 50)

total_linear = 0
total_hash = 0

for tid in ids_to_test:
    start = time.perf_counter()
    linear_search(tid)
    linear_time = time.perf_counter() - start

    start = time.perf_counter()
    hashmap_lookup(tid)
    hash_time = time.perf_counter() - start

    total_linear += linear_time
    total_hash += hash_time

    speedup = linear_time / hash_time if hash_time > 0 else 0
    print(f"{tid:<8} {linear_time*1e6:<15.4f} {hash_time*1e6:<15.4f} {speedup:.1f}x")

print("-" * 50)
avg_linear = total_linear / len(ids_to_test)
avg_hash = total_hash / len(ids_to_test)
avg_speedup = avg_linear / avg_hash if avg_hash > 0 else 0
print(f"{'Avg':<8} {avg_linear*1e6:<15.4f} {avg_hash*1e6:<15.4f} {avg_speedup:.1f}x")

