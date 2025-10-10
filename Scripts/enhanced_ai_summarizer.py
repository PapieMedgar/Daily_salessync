"""
Enhanced AI Executive Summary Generator using Llama 3
Optimized for better performance and smaller memory footprint
"""

import torch
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM, 
    BitsAndBytesConfig,
    pipeline
)
import json
from typing import Dict, Any, List
import warnings
warnings.filterwarnings("ignore")

class EnhancedAISummarizer:
    def __init__(self, model_name: str = "meta-llama/Llama-3.1-8B-Instruct"):
        """
        Initialize the enhanced AI summarizer with a smaller, more efficient Llama 3 model
        
        Args:
            model_name: Hugging Face model identifier for Llama 3 (using 1B for efficiency)
        """
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.pipeline = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        print(f"Initializing Enhanced AI Summarizer with device: {self.device}")
        self._load_model()
    
    def _load_model(self):
        """Load the optimized Llama 3 model"""
        try:
            # Configure quantization for memory efficiency
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4"
            )
            
            print("Loading Llama 3 tokenizer...")
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True
            )
            
            # Add padding token if not present
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            print("Loading Llama 3 model with quantization...")
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                quantization_config=quantization_config,
                device_map="auto",
                trust_remote_code=True,
                torch_dtype=torch.float16
            )
            
            # Create text generation pipeline
            self.pipeline = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                max_new_tokens=512,
                temperature=0.7,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            print("✅ Llama 3 model loaded successfully!")
            
        except Exception as e:
            print(f"Error loading Llama 3 model: {e}")
            print("Falling back to a smaller model...")
            self._load_fallback_model()
    
    def _load_fallback_model(self):
        """Load a smaller fallback model if the main model fails"""
        try:
            # Use a smaller, more accessible model
            fallback_model = "microsoft/DialoGPT-medium"
            
            print(f"Loading fallback model: {fallback_model}")
            self.tokenizer = AutoTokenizer.from_pretrained(fallback_model)
            self.model = AutoModelForCausalLM.from_pretrained(fallback_model)
            
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            self.pipeline = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                max_new_tokens=256,
                temperature=0.7,
                do_sample=True
            )
            
            print("✅ Fallback model loaded successfully!")
            
        except Exception as e:
            print(f"Error loading fallback model: {e}")
            raise RuntimeError("Could not load any AI model")
    
    def create_executive_summary(self, report_data: Dict[str, Any]) -> str:
        """
        Generate an executive summary from processed report data using Llama 3
        
        Args:
            report_data: Processed report data from ReportProcessor
            
        Returns:
            Generated executive summary text
        """
        try:
            # Prepare the prompt for Llama 3
            prompt = self._create_llama_prompt(report_data)
            
            # Generate summary using Llama 3
            response = self.pipeline(
                prompt,
                max_new_tokens=512,
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
            print(f"Error generating summary with Llama 3: {e}")
            return self._create_fallback_summary(report_data)
    
    def _create_llama_prompt(self, report_data: Dict[str, Any]) -> str:
        """Create a structured prompt optimized for Llama 3"""
        
        # Extract key information
        timestamp = report_data.get("timestamp", "Unknown date")
        reports = report_data.get("reports", {})
        combined = report_data.get("combined_summary", {})
        
        # Build the prompt in Llama 3 format
        prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are an expert business intelligence analyst for a sales team. Create professional, actionable executive summaries that help management make data-driven decisions. Focus on key insights, trends, and recommendations.

<|eot_id|><|start_header_id|>user<|end_header_id|>

Please analyze the following sales data and create an executive summary:

TIMESTAMP: {timestamp}
REPORTS PROCESSED: {combined.get('total_reports_processed', 0)}

KEY METRICS:
"""
        
        # Add key metrics
        key_metrics = combined.get('key_metrics', {})
        for metric, value in key_metrics.items():
            prompt += f"• {metric.replace('_', ' ').title()}: {value}\n"
        
        # Add report-specific insights
        for report_name, report_data in reports.items():
            if "error" not in report_data:
                prompt += f"\n{report_name.upper().replace('_', ' ')} INSIGHTS:\n"
                insights = report_data.get('insights', [])
                for insight in insights:
                    prompt += f"• {insight}\n"
        
        prompt += """

Please provide a comprehensive executive summary that includes:
1. **Executive Overview**: High-level performance summary
2. **Key Achievements**: Notable accomplishments and metrics
3. **Performance Analysis**: Team and individual performance insights
4. **Trends & Patterns**: Important trends and patterns identified
5. **Areas of Concern**: Any issues or challenges
6. **Strategic Recommendations**: Actionable next steps for management

Format the response professionally with clear sections and bullet points.

<|eot_id|><|start_header_id|>assistant<|end_header_id|>

# EXECUTIVE SUMMARY

"""
        
        return prompt
    
    def answer_question(self, question: str, context_data: Dict[str, Any] = None) -> str:
        """
        Answer user questions using Llama 3 with enhanced context understanding
        
        Args:
            question: User's question
            context_data: Additional context data
            
        Returns:
            AI-generated answer
        """
        try:
            # Create a focused prompt for the question
            prompt = self._create_question_prompt(question, context_data)
            
            # Generate response using Llama 3
            response = self.pipeline(
                prompt,
                max_new_tokens=400,
                temperature=0.7,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            # Extract and clean the response
            answer = response[0]['generated_text'].replace(prompt, "").strip()
            
            return answer
            
        except Exception as e:
            print(f"Error generating answer with Llama 3: {e}")
            return self._create_basic_answer(question, context_data)
    
    def _create_question_prompt(self, question: str, context_data: Dict[str, Any] = None) -> str:
        """Create a prompt for answering specific questions"""
        
        prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are a business intelligence assistant for a sales team. Answer questions about sales data with specific, actionable insights. Use the provided data to give accurate, professional responses.

<|eot_id|><|start_header_id|>user<|end_header_id|>

Question: {question}

"""
        
        if context_data:
            prompt += f"Data Context: {json.dumps(context_data, indent=2, default=str)}\n\n"
        
        prompt += """Please provide a comprehensive answer based on the data. Include specific numbers, trends, and actionable insights where possible.

<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""
        
        return prompt
    
    def _create_fallback_summary(self, report_data: Dict[str, Any]) -> str:
        """Create a basic summary if Llama 3 generation fails"""
        
        combined = report_data.get("combined_summary", {})
        reports = report_data.get("reports", {})
        
        summary = f"""# EXECUTIVE SUMMARY
*Generated on: {report_data.get('timestamp', 'Unknown date')}*

## OVERVIEW
This summary covers {combined.get('total_reports_processed', 0)} business reports processed successfully.

## KEY METRICS
"""
        
        # Add key metrics
        key_metrics = combined.get('key_metrics', {})
        for metric, value in key_metrics.items():
            summary += f"• **{metric.replace('_', ' ').title()}**: {value}\n"
        
        summary += "\n## REPORT HIGHLIGHTS\n"
        
        # Add insights from each report
        for report_name, report_data in reports.items():
            if "error" not in report_data:
                summary += f"\n### {report_name.upper().replace('_', ' ')}\n"
                insights = report_data.get('insights', [])
                for insight in insights:
                    summary += f"• {insight}\n"
        
        summary += """
## RECOMMENDATIONS
• Review individual team member performance for optimization opportunities
• Monitor daily visit trends to identify patterns
• Consider expanding successful strategies across the team
• Regular review of customer visit details for quality assurance

*This summary provides a high-level overview of the business performance based on the available data.*
"""
        
        return summary
    
    def _create_basic_answer(self, question: str, context_data: Dict[str, Any] = None) -> str:
        """Create a basic answer without AI generation"""
        
        if context_data:
            return f"Based on the available data: {json.dumps(context_data, indent=2, default=str)}"
        else:
            return f"I understand you're asking: '{question}'. However, I need more context data to provide a comprehensive answer. Please ensure the database connection is working properly."

if __name__ == "__main__":
    # Test the enhanced AI summarizer
    summarizer = EnhancedAISummarizer()
    
    # Test with sample data
    sample_data = {
        "timestamp": "2025-10-10T10:00:00Z",
        "combined_summary": {
            "total_reports_processed": 3,
            "key_metrics": {
                "total_checkins": 810,
                "active_agents": 17,
                "unique_shops": 4
            }
        },
        "reports": {
            "checkins": {
                "insights": [
                    "Total checkins this month: 810",
                    "Average daily checkins: 135.0",
                    "Top performer: Ayanda Kekana with 99 checkins"
                ]
            }
        }
    }
    
    print("Testing enhanced AI summarizer...")
    summary = summarizer.create_executive_summary(sample_data)
    print("\n" + "="*50)
    print("ENHANCED EXECUTIVE SUMMARY")
    print("="*50)
    print(summary)