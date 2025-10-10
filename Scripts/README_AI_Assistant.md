# SalesSync AI Assistant

An AI-powered question-answering system that integrates with your SalesSync database to provide intelligent insights about your sales data.

## 🚀 Features

- **Interactive Q&A**: Ask questions in natural language about your sales data
- **AI-Powered Analysis**: Uses Llama 3 model for intelligent responses
- **Database Integration**: Direct connection to your SalesSync MySQL database
- **Real-time Data**: Always up-to-date information from your database
- **Multiple Query Types**: Performance analysis, trends, customer insights, and more

## 📋 Prerequisites

- Python 3.8 or higher
- MySQL database access
- Sufficient memory for AI model (8GB+ recommended)

## 🛠️ Installation

1. **Install Dependencies**:
   ```bash
   cd /workspace/Scripts
   pip install -r requirements.txt
   ```

2. **Verify Database Connection**:
   ```bash
   python test_database_connection.py
   ```

3. **Launch AI Assistant**:
   ```bash
   python launch_ai_assistant.py
   ```

## 💬 Usage

### Starting the Assistant

```bash
python launch_ai_assistant.py
```

### Example Questions

- **Performance Questions**:
  - "Which team lead has the best performance?"
  - "What's the average visits per day?"
  - "Show me the top performing team members"

- **Customer Questions**:
  - "Who are our top 10 customers by visit count?"
  - "Which customers haven't been visited recently?"
  - "Show me customer visit patterns"

- **Trend Questions**:
  - "What are the weekly visit trends?"
  - "Show me the busiest days of the week"
  - "How has performance changed over time?"

- **General Questions**:
  - "What are the total visits this month?"
  - "How many unique customers did we visit?"
  - "What's our team performance summary?"

### Interactive Commands

- `help` - Show example questions
- `quit`, `exit`, `bye` - End the session
- `Ctrl+C` - Force quit

## 🔧 Configuration

### Database Configuration
Edit `db_config.py` to update database connection settings:
```python
DATABASE_CONFIG = {
    "host": "your_host",
    "user": "your_user", 
    "password": "your_password",
    "database": "salessync"
}
```

### AI Model Configuration
Edit `ai_config.py` to customize AI behavior:
- Model selection (primary/fallback)
- Response length and style
- Query limits and timeouts

## 📊 Supported Data Types

The system can analyze:
- **Visit Data**: Daily visits, team performance, customer interactions
- **Customer Data**: Customer profiles, visit history, engagement patterns
- **Team Data**: Team lead performance, individual statistics
- **Trend Data**: Time-based patterns, growth trends, seasonality

## 🚨 Troubleshooting

### Common Issues

1. **Database Connection Failed**:
   - Check database credentials in `db_config.py`
   - Verify network connectivity
   - Ensure MySQL server is running

2. **AI Model Loading Error**:
   - Check available memory (8GB+ recommended)
   - Verify internet connection for model download
   - Try the fallback model configuration

3. **Import Errors**:
   - Run `pip install -r requirements.txt`
   - Check Python version (3.8+ required)
   - Verify all files are in the correct location

### Performance Tips

- **Memory Usage**: The AI model requires significant RAM. Close other applications if needed.
- **Query Speed**: Large datasets may take time to process. Use specific date ranges when possible.
- **Model Loading**: First startup may take several minutes to download and load the AI model.

## 📁 File Structure

```
Scripts/
├── database_qa_system.py      # Main Q&A system
├── ai_summarizer.py          # AI model integration
├── report_processor.py       # Report data processing
├── launch_ai_assistant.py    # Simple launcher
├── test_database_connection.py # Connection tester
├── ai_config.py              # Configuration settings
├── db_config.py              # Database configuration
└── requirements.txt          # Python dependencies
```

## 🔒 Security Notes

- Database credentials are stored in `db_config.py`
- Ensure this file has appropriate permissions
- Consider using environment variables for production deployments
- The AI model may send data to external services (model hosting)

## 📈 Advanced Usage

### Custom Queries
You can extend the system by adding custom SQL patterns in `ai_config.py`:

```python
SQL_PATTERNS = {
    "custom_analysis": """
        SELECT your_custom_query_here
        FROM your_table
        WHERE your_conditions
    """
}
```

### Response Customization
Modify response formatting in `ai_config.py`:
- Change output format (markdown, plain, json)
- Adjust response length limits
- Customize timestamp and source information

## 🤝 Support

For issues or questions:
1. Check the troubleshooting section
2. Run the test script: `python test_database_connection.py`
3. Verify all dependencies are installed
4. Check database connectivity and permissions

## 📝 License

This system is designed for internal use with your SalesSync database. Ensure compliance with your organization's data policies and AI model usage terms.