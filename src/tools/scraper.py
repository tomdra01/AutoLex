import os
import requests
import datetime
import xml.etree.ElementTree as ET
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# Constants
BASE_STATIC_PDF_URL = "https://static.slov-lex.sk/pdf/SK/ZZ"
BASE_XML_URL = "https://static.slov-lex.sk/static/xml/SK/ZZ"
# User Agent is critical for Slov-Lex
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.5481.100 Safari/537.36"
}
NAMESPACES = {'ml': 'http://www.metalex.eu/metalex/1.0'}


def get_project_root():
    """Helper to find the project root from src/tools/scraper.py"""
    current_file = os.path.abspath(__file__)
    # Go up 3 levels: src/tools/scraper.py -> src/tools -> src -> Root
    return os.path.dirname(os.path.dirname(os.path.dirname(current_file)))


def fetch_specific_law(year: int, law_id: int) -> str:
    """
    Downloads the XML and PDF for a specific Slov-Lex law.
    Returns the text content of the law or a status message.
    """
    print(f"\n[Tool] Attempting to fetch Slov-Lex Law: {year}/{law_id}...")

    # 1. Setup Folder (Fixed to use Project Root)
    project_root = get_project_root()
    base_dir = os.path.join(project_root, "downloads", str(year), str(law_id))

    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    # 2. Download XML (Vyhlasene Znenie)
    xml_filename = f"law_{year}_{law_id}.xml"
    xml_path = os.path.join(base_dir, xml_filename)
    xml_url = f"{BASE_XML_URL}/{year}/{law_id}/vyhlasene_znenie.xml"

    xml_content = download_file(xml_url, xml_path)
    if not xml_content:
        return f"Failed to find XML for Law {year}/{law_id}. It might not exist."

    # 3. Parse XML to get Dates
    candidate_dates = extract_candidate_dates(xml_content)

    # 4. Try to find the PDF using the date guessing logic
    pdf_found = False
    pdf_name = "N/A"

    if candidate_dates:
        # Generate range +/- 2 days for each date
        date_attempts = set()
        for date_obj in candidate_dates:
            for offset in range(-2, 3):
                attempt_date = date_obj + datetime.timedelta(days=offset)
                date_attempts.add(attempt_date.strftime("%Y%m%d"))

        # Sort and try downloading
        for date_str in sorted(date_attempts):
            pdf_filename = f"ZZ_{year}_{law_id}_{date_str}.pdf"
            pdf_url = f"{BASE_STATIC_PDF_URL}/{year}/{law_id}/{pdf_filename}"
            pdf_save_path = os.path.join(base_dir, pdf_filename)

            if download_file(pdf_url, pdf_save_path):
                print(f"✅ PDF Found: {pdf_filename}")
                pdf_found = True
                pdf_name = pdf_filename
                break
    else:
        print("⚠️ No dates found in XML to guess PDF url.")

    # 5. Extract Text for the Agent
    law_info = parse_law_details(xml_content)

    result = (
        f"SUCCESS. Law {year}/{law_id} downloaded.\n"
        f"Title: {law_info['title']}\n"
        f"Articles Count: {law_info['article_count']}\n"
        f"PDF Status: {'Downloaded' if pdf_found else 'Not Found'} ({pdf_name})\n"
        f"Local Path: {base_dir}"
    )
    return result


def scan_laws_for_keyword(year: int, keyword: str, limit: int = 600) -> str:
    """
    Scans laws in parallel to find matches.
    - limit: Increased to 600 to cover a full year.
    - Uses ThreadPoolExecutor for speed.
    """
    print(f"\n[Tool] Scanning first {limit} laws of {year} for keyword: '{keyword}' (Parallel)...")

    matches = []

    # Helper function for a single thread
    def check_law(law_id):
        xml_url = f"{BASE_XML_URL}/{year}/{law_id}/vyhlasene_znenie.xml"
        try:
            response = requests.get(xml_url, headers=HEADERS, timeout=5)
            if response.status_code == 200:
                details = parse_law_details(response.content)
                title = details.get("title", "").lower()

                if keyword.lower() in title:
                    return f"ID {law_id}: {details['title']}"
        except Exception:
            pass
        return None

    # Run in parallel threads (20 workers = 20 checks at once)
    with ThreadPoolExecutor(max_workers=20) as executor:
        # Create all tasks
        futures = {executor.submit(check_law, i): i for i in range(1, limit + 1)}

        # Collect results as they finish
        for future in as_completed(futures):
            result = future.result()
            if result:
                matches.append(result)
                print(f"  FOUND: {result}")

    if not matches:
        return f"No laws found in the first {limit} containing '{keyword}'."

    # Sort matches by ID so they look nice
    matches.sort(key=lambda x: int(x.split(':')[0].replace("ID ", "")))

    return f"Found {len(matches)} matches:\n" + "\n".join(matches)


def download_file(url, path):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            with open(path, "wb") as f:
                f.write(response.content)
            return response.content
    except Exception as e:
        print(f"Error downloading {url}: {e}")
    return None


def extract_candidate_dates(xml_bytes):
    try:
        root = ET.fromstring(xml_bytes)
        dates = set()

        for meta in root.findall(".//ml:meta", NAMESPACES):
            prop = meta.get("property")
            content = meta.get("content")

            if not prop or not content:
                continue

            if prop in ["slovlex-owl:platny", "slovlex-owl:ucinny", "slovlex-owl:vyhlaseny"]:
                if "zaciatok=" in content:
                    content = content.split("zaciatok=")[-1].split(";")[0].strip()

                try:
                    dt = datetime.datetime.strptime(content.strip(), "%Y-%m-%d")
                    dates.add(dt)
                except ValueError:
                    pass
        return list(dates)
    except Exception as e:
        print(f"Date extract error: {e}")
        return []


def parse_law_details(xml_bytes):
    try:
        root = ET.fromstring(xml_bytes)

        def get_text(xpath):
            node = root.find(xpath, NAMESPACES)
            return node.text.strip() if node is not None and node.text else "Unknown"

        return {
            "title": get_text(".//ml:htitle[@name='predpisNadpis']"),
            "article_count": len(root.findall(".//ml:hcontainer[@name='clanok']", NAMESPACES))
        }
    except:
        return {"title": "Parse Error", "article_count": 0}