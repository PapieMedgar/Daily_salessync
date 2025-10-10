"""
Report Data Processor for AI Executive Summary
Processes various report formats and prepares data for AI analysis
"""

import pandas as pd
import os
from datetime import datetime
from typing import Dict, List, Any
import json

class ReportProcessor:
    def __init__(self, reports_dir: str = "/workspace/reports"):
        self.reports_dir = reports_dir
        
    def load_daily_visits_report(self) -> Dict[str, Any]:
        """Load and process daily visits report"""
        try:
            df = pd.read_csv(os.path.join(self.reports_dir, "daily_visits.csv"))
            
            # Calculate summary statistics
            summary = {
                "report_type": "Daily Visits",
                "date_range": f"{df['Date'].iloc[1]} to {df['Date'].iloc[-1]}" if len(df) > 1 else df['Date'].iloc[0],
                "total_days": len(df) - 1,  # Exclude header
                "team_members": list(df.columns[1:]),  # All columns except Date
                "total_visits_by_member": {},
                "daily_totals": [],
                "top_performers": [],
                "insights": []
            }
            
            # Calculate visits per team member
            for member in summary["team_members"]:
                total_visits = df[member].sum()
                summary["total_visits_by_member"][member] = int(total_visits)
            
            # Calculate daily totals
            for _, row in df.iterrows():
                if row['Date'] != 'Date':  # Skip header
                    daily_total = sum([row[member] for member in summary["team_members"]])
                    summary["daily_totals"].append({
                        "date": row['Date'],
                        "total_visits": int(daily_total)
                    })
            
            # Find top performers
            sorted_members = sorted(summary["total_visits_by_member"].items(), 
                                  key=lambda x: x[1], reverse=True)
            summary["top_performers"] = sorted_members[:5]
            
            # Generate insights
            total_visits = sum(summary["total_visits_by_member"].values())
            avg_daily = total_visits / summary["total_days"] if summary["total_days"] > 0 else 0
            
            summary["insights"] = [
                f"Total visits across all team members: {total_visits}",
                f"Average daily visits: {avg_daily:.1f}",
                f"Top performer: {summary['top_performers'][0][0]} with {summary['top_performers'][0][1]} visits",
                f"Team size: {len(summary['team_members'])} members"
            ]
            
            return summary
            
        except Exception as e:
            return {"error": f"Failed to process daily visits report: {str(e)}"}
    
    def load_team_lead_visits_report(self) -> Dict[str, Any]:
        """Load and process team lead visits report"""
        try:
            df = pd.read_csv(os.path.join(self.reports_dir, "team_lead_daily_visits.csv"))
            
            summary = {
                "report_type": "Team Lead Visits",
                "date_range": f"{df['Date'].iloc[1]} to {df['Date'].iloc[-1]}" if len(df) > 1 else df['Date'].iloc[0],
                "total_days": len(df) - 1,
                "team_leads": list(df.columns[1:-1]),  # Exclude Date and Total
                "total_visits_by_lead": {},
                "daily_totals": [],
                "insights": []
            }
            
            # Calculate visits per team lead
            for lead in summary["team_leads"]:
                total_visits = df[lead].sum()
                summary["total_visits_by_lead"][lead] = int(total_visits)
            
            # Calculate daily totals
            for _, row in df.iterrows():
                if row['Date'] != 'Date':  # Skip header
                    daily_total = row['Total'] if 'Total' in row else sum([row[lead] for lead in summary["team_leads"]])
                    summary["daily_totals"].append({
                        "date": row['Date'],
                        "total_visits": int(daily_total)
                    })
            
            # Generate insights
            total_visits = sum(summary["total_visits_by_lead"].values())
            avg_daily = total_visits / summary["total_days"] if summary["total_days"] > 0 else 0
            
            summary["insights"] = [
                f"Total visits across all team leads: {total_visits}",
                f"Average daily visits: {avg_daily:.1f}",
                f"Number of team leads: {len(summary['team_leads'])}",
                f"Best performing team lead: {max(summary['total_visits_by_lead'].items(), key=lambda x: x[1])[0]}"
            ]
            
            return summary
            
        except Exception as e:
            return {"error": f"Failed to process team lead visits report: {str(e)}"}
    
    def load_visit_details_reports(self) -> Dict[str, Any]:
        """Load and process all visit details reports"""
        try:
            visit_details_dir = os.path.join(self.reports_dir, "visit_details")
            all_visits = []
            team_lead_stats = {}
            
            for filename in os.listdir(visit_details_dir):
                if filename.endswith('.csv'):
                    filepath = os.path.join(visit_details_dir, filename)
                    df = pd.read_csv(filepath)
                    
                    # Extract team lead name from filename
                    team_lead = filename.replace('visit_details_', '').replace('.csv', '').replace('-', ' ')
                    
                    # Process visits
                    visits = []
                    for _, row in df.iterrows():
                        if row['Team Lead'] != 'Team Lead':  # Skip header
                            visit = {
                                "team_lead": row['Team Lead'],
                                "date": row['Date'],
                                "goldrush_id": row['Goldrush ID'],
                                "customer_name": row['Cust Name']
                            }
                            visits.append(visit)
                            all_visits.append(visit)
                    
                    # Calculate stats for this team lead
                    team_lead_stats[team_lead] = {
                        "total_visits": len(visits),
                        "unique_customers": len(set([v['customer_name'] for v in visits])),
                        "date_range": f"{visits[0]['date']} to {visits[-1]['date']}" if visits else "No visits"
                    }
            
            summary = {
                "report_type": "Visit Details",
                "total_visits": len(all_visits),
                "team_lead_stats": team_lead_stats,
                "insights": [
                    f"Total individual visits: {len(all_visits)}",
                    f"Number of team leads with visits: {len(team_lead_stats)}",
                    f"Average visits per team lead: {len(all_visits) / len(team_lead_stats) if team_lead_stats else 0:.1f}"
                ]
            }
            
            return summary
            
        except Exception as e:
            return {"error": f"Failed to process visit details reports: {str(e)}"}
    
    def process_all_reports(self) -> Dict[str, Any]:
        """Process all available reports and return combined data"""
        print("Processing all reports...")
        
        all_data = {
            "timestamp": datetime.now().isoformat(),
            "reports": {}
        }
        
        # Process each report type
        all_data["reports"]["daily_visits"] = self.load_daily_visits_report()
        all_data["reports"]["team_lead_visits"] = self.load_team_lead_visits_report()
        all_data["reports"]["visit_details"] = self.load_visit_details_reports()
        
        # Create combined summary
        all_data["combined_summary"] = self._create_combined_summary(all_data["reports"])
        
        return all_data
    
    def _create_combined_summary(self, reports: Dict[str, Any]) -> Dict[str, Any]:
        """Create a high-level summary of all reports"""
        summary = {
            "total_reports_processed": len([r for r in reports.values() if "error" not in r]),
            "key_metrics": {},
            "recommendations": []
        }
        
        # Extract key metrics
        if "daily_visits" in reports and "error" not in reports["daily_visits"]:
            daily_data = reports["daily_visits"]
            summary["key_metrics"]["total_team_visits"] = sum(daily_data["total_visits_by_member"].values())
            summary["key_metrics"]["team_size"] = len(daily_data["team_members"])
            summary["key_metrics"]["reporting_period_days"] = daily_data["total_days"]
        
        if "visit_details" in reports and "error" not in reports["visit_details"]:
            details_data = reports["visit_details"]
            summary["key_metrics"]["total_individual_visits"] = details_data["total_visits"]
            summary["key_metrics"]["active_team_leads"] = len(details_data["team_lead_stats"])
        
        # Generate recommendations
        if summary["key_metrics"].get("total_team_visits", 0) > 0:
            avg_daily = summary["key_metrics"]["total_team_visits"] / summary["key_metrics"]["reporting_period_days"]
            summary["recommendations"].append(f"Average daily performance: {avg_daily:.1f} visits per day")
        
        return summary

if __name__ == "__main__":
    processor = ReportProcessor()
    data = processor.process_all_reports()
    
    # Save processed data
    with open("/workspace/processed_reports.json", "w") as f:
        json.dump(data, f, indent=2)
    
    print("Reports processed and saved to processed_reports.json")
    print(f"Processed {data['combined_summary']['total_reports_processed']} reports successfully")