"""
AI Executive Summary Generator using Llama 3
Uses a smaller, quantized Llama 3 model for efficient executive summary generation
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

class AISummarizer:
    def __init__(self, model_name: str = "meta-llama/Llama-3.1-8B-Instruct"):
        """
        Initialize the AI summarizer with a quantized Llama 3 model
        
        Args:
            model_name: Hugging Face model identifier for Llama 3
        """
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.pipeline = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        print(f"Initializing AI Summarizer with device: {self.device}")
        self._load_model()
    
    def _load_model(self):
        """Load the quantized Llama 3 model"""
        try:
            # Configure quantization for memory efficiency
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4"
            )
            
            print("Loading tokenizer...")
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True
            )
            
            # Add padding token if not present
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            print("Loading model with quantization...")
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
            
            print("Model loaded successfully!")
            
        except Exception as e:
            print(f"Error loading model: {e}")
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
            
            print("Fallback model loaded successfully!")
            
        except Exception as e:
            print(f"Error loading fallback model: {e}")
            raise RuntimeError("Could not load any AI model")
    
    def create_executive_summary(self, report_data: Dict[str, Any]) -> str:
        """
        Generate an executive summary from processed report data
        
        Args:
            report_data: Processed report data from ReportProcessor
            
        Returns:
            Generated executive summary text
        """
        try:
            # Prepare the prompt for the AI model
            prompt = self._create_prompt(report_data)
            
            # Generate summary using the AI model
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
            print(f"Error generating summary: {e}")
            return self._create_fallback_summary(report_data)
    
    def _create_prompt(self, report_data: Dict[str, Any]) -> str:
        """Create a structured prompt for the AI model"""
        
        # Extract key information
        timestamp = report_data.get("timestamp", "Unknown date")
        reports = report_data.get("reports", {})
        combined = report_data.get("combined_summary", {})
        
        # Build the prompt
        prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are an expert business analyst creating executive summaries for management reports. Create a concise, professional executive summary that highlights key performance indicators, trends, and actionable insights.

<|eot_id|><|start_header_id|>user<|end_header_id|>

Please create an executive summary for the following business reports data:

REPORT TIMESTAMP: {timestamp}

SUMMARY OF REPORTS PROCESSED:
- Total reports processed: {combined.get('total_reports_processed', 0)}

KEY METRICS:
"""
        
        # Add key metrics
        key_metrics = combined.get('key_metrics', {})
        for metric, value in key_metrics.items():
            prompt += f"- {metric.replace('_', ' ').title()}: {value}\n"
        
        # Add report-specific insights
        for report_name, report_data in reports.items():
            if "error" not in report_data:
                prompt += f"\n{report_name.upper().replace('_', ' ')} REPORT:\n"
                insights = report_data.get('insights', [])
                for insight in insights:
                    prompt += f"- {insight}\n"
        
        prompt += """

Please provide a professional executive summary that includes:
1. Overall performance overview
2. Key achievements and metrics
3. Notable trends or patterns
4. Areas of concern or opportunity
5. Actionable recommendations for management

<|eot_id|><|start_header_id|>assistant<|end_header_id|>

EXECUTIVE SUMMARY:

"""
        
        return prompt
    
    def _create_fallback_summary(self, report_data: Dict[str, Any]) -> str:
        """Create a basic summary if AI generation fails"""
        
        combined = report_data.get("combined_summary", {})
        reports = report_data.get("reports", {})
        
        summary = f"""EXECUTIVE SUMMARY
Generated on: {report_data.get('timestamp', 'Unknown date')}

OVERVIEW:
This summary covers {combined.get('total_reports_processed', 0)} business reports processed successfully.

KEY METRICS:
"""
        
        # Add key metrics
        key_metrics = combined.get('key_metrics', {})
        for metric, value in key_metrics.items():
            summary += f"• {metric.replace('_', ' ').title()}: {value}\n"
        
        summary += "\nREPORT HIGHLIGHTS:\n"
        
        # Add insights from each report
        for report_name, report_data in reports.items():
            if "error" not in report_data:
                summary += f"\n{report_name.upper().replace('_', ' ')}:\n"
                insights = report_data.get('insights', [])
                for insight in insights:
                    summary += f"• {insight}\n"
        
        summary += """
RECOMMENDATIONS:
• Review individual team member performance for optimization opportunities
• Monitor daily visit trends to identify patterns
• Consider expanding successful strategies across the team
• Regular review of customer visit details for quality assurance

This summary provides a high-level overview of the business performance based on the available data.
"""
        
        return summary
    
    def generate_detailed_analysis(self, report_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate detailed analysis for different aspects of the business
        
        Returns:
            Dictionary with different types of analysis
        """
        analyses = {}
        
        # Performance Analysis
        performance_prompt = self._create_performance_analysis_prompt(report_data)
        try:
            response = self.pipeline(performance_prompt, max_new_tokens=300, temperature=0.7)
            analyses["performance_analysis"] = response[0]['generated_text'].replace(performance_prompt, "").strip()
        except:
            analyses["performance_analysis"] = "Performance analysis could not be generated at this time."
        
        # Trend Analysis
        trend_prompt = self._create_trend_analysis_prompt(report_data)
        try:
            response = self.pipeline(trend_prompt, max_new_tokens=300, temperature=0.7)
            analyses["trend_analysis"] = response[0]['generated_text'].replace(trend_prompt, "").strip()
        except:
            analyses["trend_analysis"] = "Trend analysis could not be generated at this time."
        
        return analyses
    
    def _create_performance_analysis_prompt(self, report_data: Dict[str, Any]) -> str:
        """Create prompt for performance analysis"""
        return f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are a business performance analyst. Analyze the team performance data and provide insights on individual and team productivity.

<|eot_id|><|start_header_id|>user<|end_header_id|>

Analyze the performance data and provide insights on:
1. Top performing team members
2. Performance consistency
3. Areas for improvement
4. Team dynamics

Data: {json.dumps(report_data, indent=2)}

<|eot_id|><|start_header_id|>assistant<|end_header_id|>

PERFORMANCE ANALYSIS:

"""
    
    def _create_trend_analysis_prompt(self, report_data: Dict[str, Any]) -> str:
        """Create prompt for trend analysis"""
        return f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are a business trend analyst. Analyze the data patterns and identify trends, seasonality, and future projections.

<|eot_id|><|start_header_id|>user<|end_header_id|>

Analyze the trends in the data and provide insights on:
1. Daily/weekly patterns
2. Growth trends
3. Seasonal variations
4. Future projections

Data: {json.dumps(report_data, indent=2)}

<|eot_id|><|start_header_id|>assistant<|end_header_id|>

TREND ANALYSIS:

"""

if __name__ == "__main__":
    # Test the AI summarizer
    summarizer = AISummarizer()
    
    # Load sample data
    try:
        with open("/workspace/processed_reports.json", "r") as f:
            sample_data = json.load(f)
        
        print("Generating executive summary...")
        summary = summarizer.create_executive_summary(sample_data)
        print("\n" + "="*50)
        print("EXECUTIVE SUMMARY")
        print("="*50)
        print(summary)
        
    except FileNotFoundError:
        print("No processed reports found. Please run report_processor.py first.")
    except Exception as e:
        print(f"Error: {e}")