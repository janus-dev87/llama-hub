from typing import List
import re
from llama_hub.sec_filings.sec_filings_extractor import SECExtractor
import concurrent.futures
from functools import partial
from llama_hub.sec_filings.prepline_sec_filings.fetch import get_cik_by_ticker
import requests
from llama_hub.sec_filings.prepline_sec_filings.fetch import get_filing
import pandas as pd
from datetime import datetime


def sec_main(
    ticker: str,
    year: str,
    filing_types: List[str] = ["10-K", "10-Q"],
    include_amends=True,
):
    cik = get_cik_by_ticker(ticker)
    rgld_cik = int(cik.strip("0"))
    forms = []
    if include_amends:
        for form in filing_types:
            forms.append(form)
            forms.append(form + "/A")
    else:
        forms = filing_types
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    # Send a GET request to the URL with headers
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        json_data = response.json()
    else:
        print(f"Error: Unable to fetch data. Status code: {response.status_code}")

    form_lists = []
    filings = json_data["filings"]
    recent_filings = filings["recent"]
    for acc_num, form_name, filing_date, report_date in zip(
        recent_filings["accessionNumber"],
        recent_filings["form"],
        recent_filings["filingDate"],
        recent_filings["reportDate"],
    ):
        if form_name in forms and report_date.startswith(str(year)):
            if form_name == "10-Q":
                datetime_obj = datetime.strptime(report_date, "%Y-%m-%d")
                quarter = pd.Timestamp(datetime_obj).quarter
                form_name += str(quarter)
            no_dashes_acc_num = re.sub("-", "", acc_num)
            form_lists.append([no_dashes_acc_num, form_name, filing_date, report_date])

    acc_nums_list = [fl[0] for fl in form_lists]

    get_filing_partial = partial(
        get_filing,
        cik=rgld_cik,
        company="Unstructured Technologies",
        email="support@unstructured.io",
    )

    sec_extractor = SECExtractor(ticker=ticker)

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        results = executor.map(get_filing_partial, acc_nums_list)
    results_texts = []
    for res in results:
        results_texts.append(res)
    assert len(results_texts) == len(
        acc_nums_list
    ), f"The scraped text {len(results_texts)} is not matching with accession number texts {len(acc_nums_list)}"

    with concurrent.futures.ProcessPoolExecutor(max_workers=4) as executor:
        results = executor.map(sec_extractor.get_section_texts_from_text, results_texts)
    section_texts = []
    for res in results:
        section_texts.append(res)
    assert len(section_texts) == len(
        acc_nums_list
    ), f"The section text {len(section_texts)} is not matching with accession number texts {len(acc_nums_list)}"

    for idx, val in enumerate(form_lists):
        val.append(section_texts[idx])
    return form_lists
