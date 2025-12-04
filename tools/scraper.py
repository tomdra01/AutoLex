import os
import requests
import datetime
import xml.etree.ElementTree as ET
import time

# Constants
BASE_STATIC_PDF_URL = "https://static.slov-lex.sk/pdf/SK/ZZ"
BASE_XML_URL = "https://static.slov-lex.sk/static/xml/SK/ZZ"
# User Agent is critical for Slov-Lex
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.5481.100 Safari/537.36"
}
NAMESPACES = {'ml': 'http://www.metalex.eu/metalex/1.0'}


def fetch_specific_law(year: int, law_id: int) -> str:
    """
    Downloads the XML and PDF for a specific Slov-Lex law.
    Returns the text content of the law or a status message.
    """
    print(f"\n[Tool] Attempting to fetch Slov-Lex Law: {year}/{law_id}...")

    # 1. Setup Folder
    # path/to/project/downloads/2023/123/
    base_dir = os.path.join("downloads", str(year), str(law_id))
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    # 2. Download XML (Vyhlasene Znenie)
    xml_filename = f"law_{year}_{law_id}.xml"
    xml_path = os.path.join(base_dir, xml_filename)
    xml_url = f"{BASE_XML_URL}/{year}/{law_id}/vyhlasene_znenie.xml"

    xml_content = download_file(xml_url, xml_path)
    if not xml_content:
        return f"Failed to find XML for Law {year}/{law_id}. It might not exist."

    # 3. Parse XML to get Dates (Ported from your C# Logic)
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
    # We return the Title and some text so the agent knows what it found
    law_info = parse_law_details(xml_content)

    result = (
        f"SUCCESS. Law {year}/{law_id} downloaded.\n"
        f"Title: {law_info['title']}\n"
        f"Articles Count: {law_info['article_count']}\n"
        f"PDF Status: {'Downloaded' if pdf_found else 'Not Found'} ({pdf_name})\n"
        f"Local Path: {base_dir}"
    )
    return result


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
    """
    Parses XML metadata to find 'platny', 'ucinny', 'vyhlaseny' dates.
    Matches your C# ExtractCandidateDates logic.
    """
    try:
        root = ET.fromstring(xml_bytes)
        dates = set()

        # Find all <ml:meta> tags
        for meta in root.findall(".//ml:meta", NAMESPACES):
            prop = meta.get("property")
            content = meta.get("content")

            if not prop or not content:
                continue

            # Check specific properties
            if prop in ["slovlex-owl:platny", "slovlex-owl:ucinny", "slovlex-owl:vyhlaseny"]:
                # Clean up "zaciatok=" if present
                if "zaciatok=" in content:
                    content = content.split("zaciatok=")[-1].split(";")[0].strip()

                # Parse YYYY-MM-DD
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
    root = ET.fromstring(xml_bytes)

    def get_text(xpath):
        node = root.find(xpath, NAMESPACES)
        return node.text.strip() if node is not None and node.text else "Unknown"

    return {
        "title": get_text(".//ml:htitle[@name='predpisNadpis']"),
        "article_count": len(root.findall(".//ml:hcontainer[@name='clanok']", NAMESPACES))
    }


def scan_laws_for_keyword(year: int, keyword: str, limit: int = 50) -> str:
    """
    Scans the titles of the first 'limit' laws of a year to find matches.
    Does NOT download files, just checks metadata. Fast search.
    """
    print(f"\n[Tool] Scanning first {limit} laws of {year} for keyword: '{keyword}'...")

    matches = []

    # Check laws 1 to 'limit'
    for law_id in range(1, limit + 1):
        xml_url = f"{BASE_XML_URL}/{year}/{law_id}/vyhlasene_znenie.xml"

        try:
            # We use a short timeout because we are doing many requests
            response = requests.get(xml_url, headers=HEADERS, timeout=2)

            if response.status_code == 200:
                # Reuse the helper we already wrote!
                details = parse_law_details(response.content)
                title = details.get("title", "").lower()

                # Check if keyword is in title
                if keyword.lower() in title:
                    match_info = f"ID {law_id}: {details['title']}"
                    matches.append(match_info)
                    print(f"  FOUND: {match_info}")

            # Be polite to the server
            time.sleep(0.05)

        except Exception:
            continue

    if not matches:
        return f"No laws found in the first {limit} containing '{keyword}'."

    return f"Found {len(matches)} matches:\n" + "\n".join(matches)