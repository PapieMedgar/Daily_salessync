import csv
import os
import sys
import glob
from datetime import date, timedelta
from typing import Dict, List
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment

# Mapping from Team Lead -> List of direct reports (user display names)
TEAM_LEAD_TO_USERS: Dict[str, List[str]] = {
    "Moses Thulare Moshwane": [
        "Thabo Caiphas Mosa",
        "Katlego Mofokeng",
        "Maithobo Motshabi",
        "Lebo Ramano",
        "Refilwe Prudence Mgidi",
    ],
    "Nkosingiphile Ntombikayise Ntombi Khumalo": [
        "Phamela Z Mayisela",
        "Akhona Tshiamo Ngqukavana",
        "Goodness Luyanda Sthandiwe Ndwandwe",
        "Nolwazi Natasha Adams",
        "Nolwazi Mthethwa",
    ],
    "Ntombizodwa Zodwa Dubazana": [
        "Saziso Veli Nhlozi",
        "Ayanda Kekana",
        "Perseverance G Merafe",
        "Lebogang Karabo Radebe",
        "Onalenna Maisa",
    ],
    "Gilda Katarina Mashele": [
        "Karyn Moloi",
        "Mothipane Mary Mpuru (Keneiloe)",
        "Dineo Sophie Semase",
        "Mojo Godi",
    ],
}

# Desired output column order
LEAD_ORDER: List[str] = [
    "Moses Thulare Moshwane",
    "Nkosingiphile Ntombikayise Ntombi Khumalo",
    "Ntombizodwa Zodwa Dubazana",
    "Gilda Katarina Mashele",
]


def find_latest_daily_visits_file(reports_dir: str = "reports") -> str:
    """Find the most recent daily visits CSV file."""
    # Look for files matching the pattern: daily_visits_YYYY-MM-DD.csv
    pattern = os.path.join(reports_dir, "daily_visits_*.csv")
    files = glob.glob(pattern)
    
    if not files:
        # Fallback to the old naming convention
        old_file = os.path.join(reports_dir, "daily_visits.csv")
        if os.path.exists(old_file):
            return old_file
        return None
    
    # Sort by modification time (most recent first)
    files.sort(key=os.path.getmtime, reverse=True)
    return files[0]


def generate_daily_visits_if_needed(reports_dir: str = "reports") -> str:
    """Generate daily visits report if it doesn't exist."""
    # Check if we have a recent file (within last 7 days)
    latest_file = find_latest_daily_visits_file(reports_dir)
    if latest_file and os.path.exists(latest_file):
        # Check if file is recent (within last 7 days)
        file_time = os.path.getmtime(latest_file)
        current_time = os.path.getmtime(__file__)  # Use script modification time as reference
        if current_time - file_time < 7 * 24 * 3600:  # 7 days in seconds
            return latest_file
    
    # Generate new daily visits report
    print("Generating daily visits report...")
    try:
        from daily_visits_report import main as generate_daily_visits
        # Generate for yesterday (most recent complete day)
        yesterday = date.today() - timedelta(days=1)
        date_str = yesterday.strftime('%Y-%m-%d')
        output_file = os.path.join(reports_dir, f"daily_visits_{date_str}.csv")
        
        # Temporarily modify sys.argv to pass arguments to the daily visits script
        original_argv = sys.argv
        sys.argv = ['daily_visits_report.py', date_str, date_str, output_file]
        
        try:
            generate_daily_visits()
            return output_file
        finally:
            sys.argv = original_argv
            
    except Exception as e:
        print(f"Warning: Could not auto-generate daily visits report: {e}")
        return None


def read_daily_visits_pivot(input_csv_path: str) -> List[Dict[str, int]]:
    """Read the existing per-user daily visits pivot CSV.

    Returns a list of dictionaries where each dict has keys:
      - "Date": date string as-is from the CSV (e.g., 01-Oct-25)
      - other keys are user display names with integer visit counts
    """
    if not os.path.exists(input_csv_path):
        print(f"Error: Input file not found: {input_csv_path}")
        print("This script requires a daily visits report as input.")
        print("Please run one of the following commands first:")
        print("  python Scripts/daily_visits_report.py")
        print("  python Scripts/daily_visits_report.py 2024-01-15 2024-01-15 reports/daily_visits_2024-01-15.csv")
        print("Or specify the correct input file as an argument:")
        print("  python Scripts/team_lead_visits_report.py path/to/daily_visits.csv")
        raise SystemExit(1)

    rows: List[Dict[str, int]] = []
    with open(input_csv_path, mode="r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for raw in reader:
            parsed: Dict[str, int] = {"Date": raw.get("Date", "")}
            for key, val in raw.items():
                if key == "Date":
                    continue
                try:
                    parsed[key] = int(val) if val not in (None, "", " ") else 0
                except Exception:
                    parsed[key] = 0
            rows.append(parsed)
    return rows


essential_users: List[str] = sorted({u for users in TEAM_LEAD_TO_USERS.values() for u in users})


def compute_team_lead_sums(
    per_user_rows: List[Dict[str, int]], mapping: Dict[str, List[str]]
) -> List[Dict[str, int]]:
    """Aggregate per-user counts to per-team-lead sums per date.

    Missing users are treated as 0.
    """
    aggregated: List[Dict[str, int]] = []
    for row in per_user_rows:
        out_row: Dict[str, int] = {"Date": row["Date"]}
        for lead, users in mapping.items():
            total = 0
            for user in users:
                total += int(row.get(user, 0) or 0)
            out_row[lead] = total
        aggregated.append(out_row)
    return aggregated


def write_team_lead_csv(rows: List[Dict[str, int]], output_csv_path: str) -> None:
    os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)
    headers = ["Date"] + LEAD_ORDER + ["Total"]
    with open(output_csv_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for r in rows:
            lead_values = [int(r.get(lead, 0) or 0) for lead in LEAD_ORDER]
            total_value = sum(lead_values)
            row_out = {"Date": r.get("Date", "")}
            for lead, value in zip(LEAD_ORDER, lead_values):
                row_out[lead] = value
            row_out["Total"] = total_value
            writer.writerow(row_out)


def write_team_lead_xlsx(rows: List[Dict[str, int]], output_csv_path: str) -> str:
    wb = Workbook()
    ws = wb.active
    ws.title = "Daily Visits by Team Lead"

    headers = ["Date"] + LEAD_ORDER + ["Total"]
    ws.append(headers)
    for cell in ws[1]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center")

    for r in rows:
        lead_values = [int(r.get(lead, 0) or 0) for lead in LEAD_ORDER]
        total_value = sum(lead_values)
        ws.append([r.get("Date", "")] + lead_values + [total_value])

    # Autosize columns
    for col in ws.columns:
        max_length = max(len(str(cell.value)) if cell.value is not None else 0 for cell in col)
        ws.column_dimensions[col[0].column_letter].width = max_length + 2

    xlsx_path = output_csv_path.replace(".csv", ".xlsx")
    wb.save(xlsx_path)
    return xlsx_path


def main() -> None:
    # Usage: python Scripts/team_lead_visits_report.py [input_csv] [output_csv]
    reports_dir = "reports"
    
    # Determine input file
    if len(sys.argv) > 1:
        input_csv = sys.argv[1]
    else:
        # Try to find the most recent daily visits file
        input_csv = find_latest_daily_visits_file(reports_dir)
        
        if not input_csv or not os.path.exists(input_csv):
            # Try to generate it automatically
            print("No daily visits file found. Attempting to generate one...")
            input_csv = generate_daily_visits_if_needed(reports_dir)
            
            if not input_csv or not os.path.exists(input_csv):
                print("Error: Could not find or generate daily visits file.")
                print("Please run the following command first:")
                print("  python Scripts/daily_visits_report.py")
                print("Or specify the input file as an argument:")
                print("  python Scripts/team_lead_visits_report.py path/to/daily_visits.csv")
                sys.exit(1)
    
    # Determine output file
    if len(sys.argv) > 2:
        output_csv = sys.argv[2]
    else:
        # Generate output filename based on input filename
        if "daily_visits_" in input_csv:
            # Extract date from input filename
            date_part = input_csv.split("daily_visits_")[1].replace(".csv", "")
            output_csv = os.path.join(reports_dir, f"team_lead_daily_visits_{date_part}.csv")
        else:
            output_csv = os.path.join(reports_dir, "team_lead_daily_visits.csv")

    print(f"Using input file: {input_csv}")
    print(f"Output file: {output_csv}")

    per_user_rows = read_daily_visits_pivot(input_csv)
    aggregated_rows = compute_team_lead_sums(per_user_rows, TEAM_LEAD_TO_USERS)

    write_team_lead_csv(aggregated_rows, output_csv)
    xlsx_path = write_team_lead_xlsx(aggregated_rows, output_csv)

    print(f"Wrote team-lead CSV: {output_csv}")
    print(f"Wrote team-lead Excel: {xlsx_path}")


if __name__ == "__main__":
    main()
