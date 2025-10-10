"""
Optimized AI Executive Summary Generator
Uses open-source models that work without authentication
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

class OptimizedAISummarizer:
    def __init__(self, model_name: str = "microsoft/DialoGPT-large"):
        """
        Initialize the optimized AI summarizer with an open-source model
        
        Args:
            model_name: Hugging Face model identifier for open-source model
        """
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.pipeline = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        print(f"Initializing Optimized AI Summarizer with device: {self.device}")
        self._load_model()
    
    def _load_model(self):
        """Load the optimized model"""
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
                max_new_tokens=400,
                temperature=0.7,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            print(f"✅ {self.model_name} loaded successfully!")
            
        except Exception as e:
            print(f"Error loading {self.model_name}: {e}")
            print("Falling back to a smaller model...")
            self._load_fallback_model()
    
    def _load_fallback_model(self):
        """Load a smaller fallback model"""
        try:
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
                max_new_tokens=300,
                temperature=0.7,
                do_sample=True
            )
            
            print("✅ Fallback model loaded successfully!")
            
        except Exception as e:
            print(f"Error loading fallback model: {e}")
            raise RuntimeError("Could not load any AI model")
    
    def answer_question(self, question: str, context_data: Dict[str, Any] = None) -> str:
        """
        Answer user questions with enhanced context understanding
        
        Args:
            question: User's question
            context_data: Additional context data
            
        Returns:
            AI-generated answer
        """
        try:
            # Create a focused prompt for the question
            prompt = self._create_question_prompt(question, context_data)
            
            # Generate response
            response = self.pipeline(
                prompt,
                max_new_tokens=300,
                temperature=0.7,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            # Extract and clean the response
            answer = response[0]['generated_text'].replace(prompt, "").strip()
            
            # Enhance the response with context if available
            if context_data:
                answer = self._enhance_response_with_context(answer, context_data)
            
            return answer
            
        except Exception as e:
            print(f"Error generating answer: {e}")
            return self._create_contextual_answer(question, context_data)
    
    def _create_question_prompt(self, question: str, context_data: Dict[str, Any] = None) -> str:
        """Create a prompt for answering specific questions"""
        
        prompt = f"""You are a business intelligence assistant for a sales team. Answer the following question about sales data with specific, actionable insights.

Question: {question}

"""
        
        if context_data:
            # Format context data nicely
            context_str = self._format_context_data(context_data)
            prompt += f"Data Context:\n{context_str}\n\n"
        
        prompt += "Please provide a comprehensive answer based on the data. Include specific numbers, trends, and actionable insights where possible.\n\nAnswer:"
        
        return prompt
    
    def _format_context_data(self, context_data: Dict[str, Any]) -> str:
        """Format context data for better AI understanding"""
        formatted = []
        
        for key, value in context_data.items():
            if isinstance(value, dict):
                formatted.append(f"{key.replace('_', ' ').title()}:")
                for sub_key, sub_value in value.items():
                    if isinstance(sub_value, list) and sub_value:
                        formatted.append(f"  {sub_key.replace('_', ' ').title()}: {len(sub_value)} items")
                        # Show first few items
                        for item in sub_value[:3]:
                            if isinstance(item, dict):
                                formatted.append(f"    - {item}")
                            else:
                                formatted.append(f"    - {item}")
                    else:
                        formatted.append(f"  {sub_key.replace('_', ' ').title()}: {sub_value}")
            else:
                formatted.append(f"{key.replace('_', ' ').title()}: {value}")
        
        return "\n".join(formatted)
    
    def _enhance_response_with_context(self, answer: str, context_data: Dict[str, Any]) -> str:
        """Enhance the AI response with specific context data"""
        
        # Add specific data points to the response
        enhanced_parts = [answer]
        
        # Add specific metrics if available
        if 'today_data' in context_data and 'summary' in context_data['today_data']:
            summary = context_data['today_data']['summary']
            if 'total_checkins_today' in summary:
                enhanced_parts.append(f"\n📊 Today's Activity: {summary['total_checkins_today']} checkins by {summary.get('agents_working_today', 0)} agents")
        
        if 'monthly_data' in context_data and 'summary' in context_data['monthly_data']:
            summary = context_data['monthly_data']['summary']
            if 'total_checkins_month' in summary:
                enhanced_parts.append(f"\n📈 Monthly Total: {summary['total_checkins_month']} checkins")
        
        if 'performance_data' in context_data and 'top_performer' in context_data['performance_data']:
            top_performer = context_data['performance_data']['top_performer']
            if top_performer:
                enhanced_parts.append(f"\n🏆 Top Performer: {top_performer.get('agent_name', 'Unknown')} with {top_performer.get('total_checkins', 0)} checkins")
        
        return "\n".join(enhanced_parts)
    
    def _create_contextual_answer(self, question: str, context_data: Dict[str, Any] = None) -> str:
        """Create a contextual answer without AI generation"""
        
        if not context_data:
            return f"I understand you're asking: '{question}'. However, I need more context data to provide a comprehensive answer."
        
        # Create a natural, human-like response
        question_lower = question.lower()
        
        # Handle "how many people worked today" type questions
        if any(word in question_lower for word in ['people', 'agents', 'workers', 'staff']) and 'today' in question_lower:
            if 'today_data' in context_data and 'summary' in context_data['today_data']:
                summary = context_data['today_data']['summary']
                agents_count = summary.get('agents_working_today', 0)
                checkins_count = summary.get('total_checkins_today', 0)
                return f"📊 **{agents_count} people worked today!**\n\nThey completed a total of {checkins_count} checkins, which shows great productivity from your team."
        
        # Handle performance questions
        if 'performance' in question_lower or 'best' in question_lower:
            if 'performance_data' in context_data and 'top_performer' in context_data['performance_data']:
                top_performer = context_data['performance_data']['top_performer']
                if top_performer:
                    name = top_performer.get('agent_name', 'Unknown')
                    checkins = top_performer.get('total_checkins', 0)
                    return f"🏆 **{name} is your top performer!**\n\nThey have completed {checkins} total checkins, making them the most productive agent on your team."
        
        # Handle monthly questions
        if 'month' in question_lower or 'monthly' in question_lower:
            if 'monthly_data' in context_data and 'summary' in context_data['monthly_data']:
                summary = context_data['monthly_data']['summary']
                total_checkins = summary.get('total_checkins_month', 0)
                active_agents = summary.get('active_agents_month', 0)
                active_days = summary.get('active_days_month', 0)
                avg_daily = total_checkins / active_days if active_days > 0 else 0
                return f"📈 **Monthly Performance Summary:**\n\n• Total checkins this month: {total_checkins}\n• Active agents: {active_agents}\n• Active days: {active_days}\n• Average daily checkins: {avg_daily:.1f}\n\nYour team is performing very well this month!"
        
        # Handle shop/customer questions
        if any(word in question_lower for word in ['shop', 'customer', 'store']):
            if 'customer_data' in context_data and 'top_shops' in context_data['customer_data']:
                shops = context_data['customer_data']['top_shops']
                if shops:
                    top_shop = shops[0]
                    shop_name = top_shop.get('shop_name', 'Unknown')
                    checkin_count = top_shop.get('checkin_count', 0)
                    return f"🏪 **{shop_name} is your top shop!**\n\nThey have received {checkin_count} checkins, making them the most visited location in your network."
        
        # Default response with structured data
        response_parts = []
        
        if 'today_data' in context_data and 'summary' in context_data['today_data']:
            summary = context_data['today_data']['summary']
            response_parts.append(f"📊 **Today's Activity:**")
            response_parts.append(f"• Total checkins: {summary.get('total_checkins_today', 0)}")
            response_parts.append(f"• Active agents: {summary.get('agents_working_today', 0)}")
            response_parts.append(f"• Shops visited: {summary.get('shops_visited_today', 0)}")
        
        if 'monthly_data' in context_data and 'summary' in context_data['monthly_data']:
            summary = context_data['monthly_data']['summary']
            response_parts.append(f"\n📈 **Monthly Performance:**")
            response_parts.append(f"• Total checkins: {summary.get('total_checkins_month', 0)}")
            response_parts.append(f"• Active agents: {summary.get('active_agents_month', 0)}")
            response_parts.append(f"• Unique shops: {summary.get('unique_shops_month', 0)}")
            response_parts.append(f"• Active days: {summary.get('active_days_month', 0)}")
        
        if 'performance_data' in context_data and 'agent_performance' in context_data['performance_data']:
            agents = context_data['performance_data']['agent_performance']
            if agents:
                response_parts.append(f"\n👥 **Top Performers:**")
                for i, agent in enumerate(agents[:5], 1):
                    response_parts.append(f"{i}. {agent.get('agent_name', 'Unknown')}: {agent.get('total_checkins', 0)} checkins")
        
        if 'customer_data' in context_data and 'top_shops' in context_data['customer_data']:
            shops = context_data['customer_data']['top_shops']
            if shops:
                response_parts.append(f"\n🏪 **Top Shops:**")
                for i, shop in enumerate(shops[:5], 1):
                    response_parts.append(f"{i}. {shop.get('shop_name', 'Unknown')}: {shop.get('checkin_count', 0)} checkins")
        
        if response_parts:
            return "\n".join(response_parts)
        else:
            return f"I understand you're asking: '{question}'. Let me analyze the data and provide you with the most relevant information."

if __name__ == "__main__":
    # Test the optimized AI summarizer
    summarizer = OptimizedAISummarizer()
    
    # Test with sample data
    sample_context = {
        "today_data": {
            "summary": {
                "total_checkins_today": 81,
                "agents_working_today": 12,
                "shops_visited_today": 4
            }
        },
        "monthly_data": {
            "summary": {
                "total_checkins_month": 810,
                "active_agents_month": 17,
                "unique_shops_month": 4,
                "active_days_month": 6
            }
        }
    }
    
    print("Testing optimized AI summarizer...")
    answer = summarizer.answer_question("How many agents have worked today?", sample_context)
    print("\n" + "="*50)
    print("AI RESPONSE:")
    print("="*50)
    print(answer)