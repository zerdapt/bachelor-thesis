import requests
import pandas as pd
from time import sleep

# --- Configuration ---
EVENT_BASE_URL = "https://api.fda.gov/drug/event.json"
LABEL_BASE_URL = "https://api.fda.gov/drug/label.json"

# Using a synonym dictionary for robust status lookups
DRUG_SYNONYMS = {
    "PARACETAMOL": ["ACETAMINOPHEN", "PARACETAMOL"],
    "DIPYRONE": ["DIPYRONE", "METAMIZOLE"],
    "ASPIRIN": ["ASPIRIN"],
    "NAPROXEN": ["NAPROXEN"],
    "IBUPROFEN": ["IBUPROFEN"],
    "DICLOFENAC": ["DICLOFENAC"]
}
PAINKILLERS = list(DRUG_SYNONYMS.keys())

# --- Output Filenames ---
FILE_SUMMARY = "drug_risk_summary.csv"
FILE_FATAL_DETAILS = "fatal_report_details.csv"

# --- Analysis Parameters ---
FATAL_EXAMPLES_TO_FIND = 10
IDS_TO_CHECK = 50
AGE_UPPER_BOUND = 140

# ==============================================================================
# PART 1: Create the High-Level Summary CSV
# ==============================================================================
print(f"--- Part 1 of 2: Generating '{FILE_SUMMARY}' ---")
summary_data = []

for drug in PAINKILLERS:
    print(f"\nProcessing summary for: {drug}...")
    
    # Get the US marketing status for the drug
    marketing_status = "Not Approved in US"
    for term in DRUG_SYNONYMS[drug]:
        params = {'search': f'openfda.generic_name.exact:"{term}"', 'limit': 1}
        try:
            response = requests.get(LABEL_BASE_URL, params=params)
            if response.status_code == 200 and response.json().get('results'):
                product_type = response.json()['results'][0].get('openfda', {}).get('product_type', ['Unknown'])[0]
                marketing_status = "Over-the-Counter" if "OTC" in product_type else "Prescription" if "PRESCRIPTION" in product_type else "Other"
                break
        except requests.exceptions.RequestException:
            continue
    print(f"  - Status: {marketing_status}")

    # Get the key counts using reliable 'count' queries
    total_reports, serious_reports, fatal_reports = 0, 0, 0
    try:
        url_total = f'{EVENT_BASE_URL}?search=patient.drug.medicinalproduct.exact:"{drug}"&limit=0'
        total_reports = requests.get(url_total).json()["meta"]["results"]["total"]
        
        url_serious = f'{EVENT_BASE_URL}?search=patient.drug.medicinalproduct.exact:"{drug}"+AND+serious:1&limit=0'
        serious_reports = requests.get(url_serious).json()["meta"]["results"]["total"]
        
        url_fatal = f'{EVENT_BASE_URL}?search=patient.drug.medicinalproduct.exact:"{drug}"+AND+seriousnessdeath:1&limit=0'
        fatal_reports = requests.get(url_fatal).json()["meta"]["results"]["total"]
    except Exception:
        pass
    print(f"  - Counts -> Total: {total_reports:,}, Serious: {serious_reports:,}, Fatal: {fatal_reports:,}")
    
    summary_data.append({
        'painkiller_id': drug,
        'us_regulatory_status': marketing_status,
        'total_reports': total_reports,
        'serious_reports': serious_reports,
        'fatal_reports': fatal_reports
    })
    sleep(1)

# Save the summary data to its CSV file
df_summary = pd.DataFrame(summary_data)
df_summary.to_csv(FILE_SUMMARY, index=False, sep=';')
print(f"\n Successfully saved the risk summary to '{FILE_SUMMARY}'")

# ==============================================================================
# PART 2: Create the Detailed Fatal Reports CSV
# ==============================================================================
print(f"\n--- Part 2 of 2: Generating '{FILE_FATAL_DETAILS}' ---")
fatal_details_data = []

for drug in PAINKILLERS:
    print(f"\nProcessing fatal details for: {drug}...")
    
    # Step A: FIND a list of potential fatal report IDs
    print(f"  - Finding up to {IDS_TO_CHECK} potential fatal report IDs...")
    potential_ids = []
    try:
        find_url = (f'{EVENT_BASE_URL}?search=patient.drug.medicinalproduct.exact:"{drug}"'
                    f'+AND+seriousnessdeath:1&count=safetyreportid.exact&limit={IDS_TO_CHECK}')
        response = requests.get(find_url)
        response.raise_for_status()
        results = response.json().get('results', [])
        
        # Step B: FILTER for single-drug reports only (count == 1)
        potential_ids = [item['term'] for item in results if item['count'] == 1]
        print(f"    - Found {len(potential_ids)} single-drug fatal report IDs.")
        
    except Exception as e:
        print(f"    - Could not find fatal report IDs for {drug}: {e}")
        continue

    if not potential_ids:
        continue

    # Step C: FETCH, VALIDATE, and EXTRACT details for each clean ID
    print(f"  - Fetching details to find {FATAL_EXAMPLES_TO_FIND} complete examples...")
    found_complete_examples = 0
    for report_id in potential_ids:
        if found_complete_examples >= FATAL_EXAMPLES_TO_FIND:
            break
        try:
            params_fetch = {'search': f'safetyreportid:"{report_id}"'}
            response = requests.get(EVENT_BASE_URL, params=params_fetch)
            report = response.json().get('results', [{}])[0]
            
            # VALIDATION STEP: Check for complete data and valid age
            patient_info = report.get('patient', {})
            age_str = patient_info.get('patientonsetage')
            if age_str and age_str.isdigit() and (0 <= int(age_str) <= AGE_UPPER_BOUND) and 'patientsex' in patient_info and 'occurcountry' in report:
                # EXTRACTION STEP: If data is valid, extract it
                for reaction in patient_info.get('reaction', []):
                    fatal_details_data.append({
                        'painkiller_id': drug,
                        'report_id': report.get('safetyreportid', 'N/A'),
                        'is_fatal': 'true',
                        'report_date': report.get('receiptdate', 'N/A'),
                        'side_effect': reaction.get('reactionmeddrapt', 'N/A'),
                        'patient_age': patient_info.get('patientonsetage'),
                        'patient_sex': "Female" if patient_info.get('patientsex') == '2' else "Male",
                        'report_country_code': report.get('occurcountry')
                    })
                found_complete_examples += 1
            sleep(0.3)
        except Exception:
            continue
    print(f"    - Successfully collected {found_complete_examples} complete examples.")

# Save the detailed fatal reports to their CSV file
df_fatal_details = pd.DataFrame(fatal_details_data)
if not df_fatal_details.empty:
    final_headers = ['painkiller_id', 'report_id', 'is_fatal', 'report_date', 'side_effect', 'patient_age', 'patient_sex', 'report_country_code']
    df_fatal_details = df_fatal_details.reindex(columns=final_headers)
df_fatal_details.to_csv(FILE_FATAL_DETAILS, index=False, sep=';')
print(f"\n Successfully saved the fatal report details to '{FILE_FATAL_DETAILS}'")

print("\n--- All tasks complete! ---")