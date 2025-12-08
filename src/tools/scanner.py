import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from src.config import BASE_XML_URL, HEADERS
from src.tools.utils import parse_law_details


def scan_laws_for_keyword(year: int, keyword: str, limit: int = 600) -> str:
    """Scans law titles in parallel to find keyword matches."""
    print(f"\n[Tool] Scanning first {limit} laws of {year} for '{keyword}' (Parallel)...")

    matches = []

    def check_single_law(law_id):
        url = f"{BASE_XML_URL}/{year}/{law_id}/vyhlasene_znenie.xml"
        try:
            resp = requests.get(url, headers=HEADERS, timeout=5)
            if resp.status_code == 200:
                details = parse_law_details(resp.content)
                if keyword.lower() in details.get("title", "").lower():
                    return f"ID {law_id}: {details['title']}"
        except Exception:
            pass
        return None

    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(check_single_law, i): i for i in range(1, limit + 1)}
        for future in as_completed(futures):
            res = future.result()
            if res:
                matches.append(res)
                print(f"  FOUND: {res}")

    if not matches:
        return f"No laws found in first {limit} for '{keyword}'."

    matches.sort(key=lambda x: int(x.split(':')[0].replace("ID ", "")))
    return f"Found {len(matches)} matches:\n" + "\n".join(matches)