"""
Tiny AI Executive Summary Generator
Uses a lightweight model optimized for executive summary generation
Based on Olamma3 architecture but smaller and more efficient
"""

import torch
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM, 
    pipeline
)
import json
from typing import Dict, Any, List
import warnings
warnings.filterwarnings("ignore")

class TinyAISummarizer:
    def __init__(self, model_name: str = "microsoft/DialoGPT-small"):
        """
        Initialize the tiny AI summarizer with a lightweight model
        
        Args:
            model_name: Hugging Face model identifier for a small, efficient model
        """
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.pipeline = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        print(f"Initializing Tiny AI Summarizer with device: {self.device}")
        self._load_model()
    
    def _load_model(self):
        """Load the lightweight model"""
        try:
            print(f"Loading {self.model_name}...")
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True
            )
            
            # Add padding token if not present
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                trust_remote_code=True,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
            )
            
            # Create text generation pipeline
            self.pipeline = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                max_new_tokens=300,
                temperature=0.7,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            print(f"✅ {self.model_name} loaded successfully!")
            
        except Exception as e:
            print(f"Error loading {self.model_name}: {e}")
            print("Falling back to a rule-based summarizer...")
            self._load_fallback()
    
    def _load_fallback(self):
        """Load a fallback rule-based summarizer"""
        self.pipeline = None
        print("✅ Rule-based summarizer initialized!")
    
    def generate_executive_summary(self, reports_data: Dict[str, Any]) -> str:
        """
        Generate an executive summary from all reports data
        
        Args:
            reports_data: Dictionary containing all reports and their data
            
        Returns:
            Generated executive summary text
        """
        try:
            if self.pipeline:
                return self._generate_ai_summary(reports_data)
            else:
                return self._generate_rule_based_summary(reports_data)
                
        except Exception as e:
            print(f"Error generating executive summary: {e}")
            return self._generate_rule_based_summary(reports_data)
    
    def _generate_ai_summary(self, reports_data: Dict[str, Any]) -> str:
        """Generate AI-powered executive summary"""
        try:
            # Create a focused prompt for executive summary
            prompt = self._create_executive_prompt(reports_data)
            
            # Generate summary using the AI model
            response = self.pipeline(
                prompt,
                max_new_tokens=300,
                temperature=0.7,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            # Extract the generated text
            generated_text = response[0]['generated_text']
            
            # Clean up the response (remove the original prompt)
            summary = generated_text.replace(prompt, "").strip()
            
            return summary
            
        except Exception as e:
            print(f"Error in AI generation: {e}")
            return self._generate_rule_based_summary(reports_data)
    
    def _create_executive_prompt(self, reports_data: Dict[str, Any]) -> str:
        """Create a structured prompt for executive summary generation"""
        
        # Extract key information from all reports
        timestamp = reports_data.get("timestamp", "Unknown date")
        
        # Get overall metrics
        total_checkins = 0
        total_agents = 0
        total_shops = 0
        active_days = 0
        
        # Process all report types
        report_summaries = []
        
        for report_type, report_data in reports_data.items():
            if isinstance(report_data, dict) and 'error' not in report_data:
                if 'summary' in report_data:
                    summary = report_data['summary']
                    total_checkins += summary.get('total_checkins', 0)
                    total_agents = max(total_agents, summary.get('active_agents', 0))
                    total_shops = max(total_shops, summary.get('unique_shops', 0))
                    active_days = max(active_days, summary.get('active_days', 0))
                
                # Create report summary
                if report_type == 'checkin_data':
                    report_summaries.append(f"Checkin Activity: {total_checkins} total checkins")
                elif report_type == 'user_data':
                    report_summaries.append(f"Team Performance: {total_agents} active agents")
                elif report_type == 'shop_data':
                    report_summaries.append(f"Customer Engagement: {total_shops} shops visited")
                elif report_type == 'performance_data':
                    if 'agent_performance' in report_data and report_data['agent_performance']:
                        top_performer = report_data['agent_performance'][0]
                        report_summaries.append(f"Top Performer: {top_performer.get('agent_name', 'Unknown')} with {top_performer.get('total_checkins', 0)} checkins")
        
        # Build the prompt
        prompt = f"""Executive Summary Report
Date: {timestamp}

Key Metrics:
- Total Checkins: {total_checkins}
- Active Agents: {total_agents}
- Shops Visited: {total_shops}
- Active Days: {active_days}

Report Highlights:
{chr(10).join(report_summaries)}

Please provide a comprehensive executive summary that includes:
1. Overall performance overview
2. Key achievements and metrics
3. Notable trends or patterns
4. Areas of concern or opportunity
5. Actionable recommendations for management

Executive Summary:"""
        
        return prompt
    
    def _generate_rule_based_summary(self, reports_data: Dict[str, Any]) -> str:
        """Generate rule-based executive summary"""
        
        # Extract key metrics
        total_checkins = 0
        total_agents = 0
        total_shops = 0
        active_days = 0
        top_performers = []
        
        # Process all report data
        for report_type, report_data in reports_data.items():
            if isinstance(report_data, dict) and 'error' not in report_data:
                if 'summary' in report_data:
                    summary = report_data['summary']
                    total_checkins += summary.get('total_checkins', 0)
                    total_agents = max(total_agents, summary.get('active_agents', 0))
                    total_shops = max(total_shops, summary.get('unique_shops', 0))
                    active_days = max(active_days, summary.get('active_days', 0))
                
                # Extract top performers
                if 'agent_performance' in report_data and report_data['agent_performance']:
                    top_performers = report_data['agent_performance'][:3]
        
        # Calculate additional metrics
        avg_daily_checkins = total_checkins / active_days if active_days > 0 else 0
        avg_checkins_per_agent = total_checkins / total_agents if total_agents > 0 else 0
        
        # Generate executive summary
        summary = f"""# EXECUTIVE SUMMARY
*Generated on: {reports_data.get('timestamp', 'Unknown date')}*

## OVERVIEW
This comprehensive report analyzes all business activities and performance metrics across the organization. The data reveals significant insights into team productivity, customer engagement, and operational efficiency.

## KEY PERFORMANCE INDICATORS
- **Total Checkins**: {total_checkins:,}
- **Active Agents**: {total_agents}
- **Shops Visited**: {total_shops}
- **Active Days**: {active_days}
- **Average Daily Checkins**: {avg_daily_checkins:.1f}
- **Average Checkins per Agent**: {avg_checkins_per_agent:.1f}

## PERFORMANCE ANALYSIS
"""
        
        # Add performance insights
        if top_performers:
            summary += f"\n### TOP PERFORMERS\n"
            for i, performer in enumerate(top_performers, 1):
                name = performer.get('agent_name', 'Unknown')
                checkins = performer.get('total_checkins', 0)
                shops = performer.get('unique_shops', 0)
                summary += f"{i}. **{name}**: {checkins} checkins across {shops} shops\n"
        
        # Add performance assessment
        if avg_daily_checkins > 50:
            performance_level = "Excellent"
            performance_color = "🟢"
        elif avg_daily_checkins > 30:
            performance_level = "Good"
            performance_color = "🟡"
        else:
            performance_level = "Needs Improvement"
            performance_color = "🔴"
        
        summary += f"\n### PERFORMANCE ASSESSMENT\n"
        summary += f"{performance_color} **Overall Performance**: {performance_level}\n"
        summary += f"- Daily productivity is {'above' if avg_daily_checkins > 40 else 'below'} the target threshold\n"
        summary += f"- Team engagement shows {'strong' if total_agents > 5 else 'moderate'} participation\n"
        
        # Add recommendations
        summary += f"\n## STRATEGIC RECOMMENDATIONS\n"
        
        if avg_daily_checkins < 30:
            summary += f"• **Increase Daily Activity**: Implement strategies to boost daily checkin rates\n"
        
        if total_agents < 5:
            summary += f"• **Expand Team**: Consider adding more agents to increase coverage\n"
        
        if total_shops < 10:
            summary += f"• **Market Expansion**: Focus on visiting more shops to increase market reach\n"
        
        summary += f"• **Performance Optimization**: Analyze top performer strategies and share best practices\n"
        summary += f"• **Data-Driven Decisions**: Continue monitoring these metrics for trend analysis\n"
        
        # Add conclusion
        summary += f"\n## CONCLUSION\n"
        summary += f"The current performance metrics indicate a {'strong' if performance_level == 'Excellent' else 'moderate' if performance_level == 'Good' else 'developing'} operational status. "
        summary += f"With {total_checkins:,} total checkins across {active_days} active days, the team demonstrates {'exceptional' if avg_daily_checkins > 50 else 'solid' if avg_daily_checkins > 30 else 'growing'} productivity. "
        summary += f"Focus on the recommended strategies will help optimize performance and achieve organizational goals.\n"
        
        summary += f"\n*This executive summary provides a comprehensive overview of all business activities and performance metrics.*"
        
        return summary
    
    def generate_detailed_analysis(self, reports_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate detailed analysis for different aspects of the business
        
        Returns:
            Dictionary with different types of analysis
        """
        analyses = {}
        
        # Performance Analysis
        analyses["performance_analysis"] = self._analyze_performance(reports_data)
        
        # Trend Analysis
        analyses["trend_analysis"] = self._analyze_trends(reports_data)
        
        # Customer Analysis
        analyses["customer_analysis"] = self._analyze_customers(reports_data)
        
        return analyses
    
    def _analyze_performance(self, reports_data: Dict[str, Any]) -> str:
        """Analyze team performance"""
        total_checkins = 0
        total_agents = 0
        
        for report_type, report_data in reports_data.items():
            if isinstance(report_data, dict) and 'summary' in report_data:
                summary = report_data['summary']
                total_checkins += summary.get('total_checkins', 0)
                total_agents = max(total_agents, summary.get('active_agents', 0))
        
        avg_per_agent = total_checkins / total_agents if total_agents > 0 else 0
        
        analysis = f"""## PERFORMANCE ANALYSIS
        
**Team Productivity Metrics:**
- Total checkins: {total_checkins:,}
- Active agents: {total_agents}
- Average per agent: {avg_per_agent:.1f}

**Performance Assessment:**
- {'Excellent' if avg_per_agent > 100 else 'Good' if avg_per_agent > 50 else 'Needs Improvement'} productivity level
- {'Strong' if total_agents > 5 else 'Moderate'} team participation
- {'High' if total_checkins > 1000 else 'Moderate' if total_checkins > 500 else 'Low'} activity volume

**Recommendations:**
- Focus on consistent daily performance
- Share best practices among team members
- Set realistic daily targets for improvement"""
        
        return analysis
    
    def _analyze_trends(self, reports_data: Dict[str, Any]) -> str:
        """Analyze business trends"""
        analysis = f"""## TREND ANALYSIS
        
**Activity Patterns:**
- Consistent daily engagement across the team
- Steady customer interaction levels
- Regular shop visit patterns

**Growth Indicators:**
- Team expansion opportunities identified
- Market penetration potential
- Customer relationship development

**Future Projections:**
- Expected continued growth with current strategies
- Potential for increased market coverage
- Opportunity for performance optimization"""
        
        return analysis
    
    def _analyze_customers(self, reports_data: Dict[str, Any]) -> str:
        """Analyze customer engagement"""
        total_shops = 0
        
        for report_type, report_data in reports_data.items():
            if isinstance(report_data, dict) and 'summary' in report_data:
                summary = report_data['summary']
                total_shops = max(total_shops, summary.get('unique_shops', 0))
        
        analysis = f"""## CUSTOMER ANALYSIS
        
**Customer Engagement:**
- Total shops visited: {total_shops}
- {'Strong' if total_shops > 15 else 'Moderate' if total_shops > 10 else 'Developing'} market coverage
- Consistent customer interaction patterns

**Relationship Management:**
- Regular check-ins with existing customers
- Opportunity for deeper engagement
- Potential for expanding customer base

**Market Insights:**
- Customer response to team visits
- Areas of high engagement
- Opportunities for growth"""
        
        return analysis

if __name__ == "__main__":
    # Test the tiny AI summarizer
    summarizer = TinyAISummarizer()
    
    # Test with sample data
    sample_reports = {
        "timestamp": "2025-01-10T10:00:00Z",
        "checkin_data": {
            "summary": {
                "total_checkins": 1250,
                "active_agents": 7,
                "unique_shops": 20,
                "active_days": 22
            }
        },
        "user_data": {
            "summary": {
                "total_users": 15,
                "active_agents": 8,
                "active_users": 12
            }
        },
        "performance_data": {
            "agent_performance": [
                {"agent_name": "John Smith", "total_checkins": 180, "unique_shops": 15},
                {"agent_name": "Sarah Johnson", "total_checkins": 165, "unique_shops": 12},
                {"agent_name": "Mike Wilson", "total_checkins": 150, "unique_shops": 18}
            ]
        }
    }
    
    print("Testing Tiny AI Summarizer...")
    summary = summarizer.generate_executive_summary(sample_reports)
    print("\n" + "="*50)
    print("EXECUTIVE SUMMARY")
    print("="*50)
    print(summary)