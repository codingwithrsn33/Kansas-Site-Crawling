# Kansas SOS Business Crawler 🏢

A sophisticated automation solution for comprehensive business intelligence gathering from the Kansas Secretary of State website. This enterprise-grade tool systematically extracts and structures business entity data with robust error handling and professional output management.

## 🚀 Overview

The Kansas SOS Business Crawler is designed to automate the extraction of business entity information through intelligent web navigation, multi-layered data extraction, and comprehensive error management. It transforms unstructured web data into structured, analyzable business intelligence.

## ✨ Key Features

### 🤖 Intelligent Automation
- **Smart Navigation**: Natural browsing pattern from homepage to business search
- **Form Automation**: Automated search parameter configuration
- **Dynamic Element Detection**: Adaptive element identification with multiple fallback strategies

### 📊 Comprehensive Data Extraction
- **Business Identification**: Entity names, IDs, and registration details
- **Entity Classification**: Business types, status, and jurisdiction information
- **Contact Information**: Resident agents and office addresses
- **Compliance Data**: Reporting requirements and filing deadlines

### 🛡️ Enterprise Reliability
- **Multi-layer Error Handling**: Primary, secondary, and tertiary extraction methods
- **CAPTCHA Management**: Automated detection with manual intervention protocol
- **Session Persistence**: Robust recovery from interruptions and timeouts

### 💾 Professional Output
- **Structured JSON**: Clean, normalized business data
- **Hierarchical Storage**: Organized by extraction status and data type
- **Audit Trail**: Comprehensive logging and activity monitoring

## 🏗️ Architecture

### Navigation Flow
```
Homepage (sos.ks.gov) → Business Search → Automated Setup → Search Execution → Data Extraction → Structured Storage
```

### Extraction Strategy
1. **Primary Method**: Direct element targeting using known CSS selectors
2. **Secondary Method**: Table-based parsing and pattern recognition
3. **Tertiary Method**: Text analysis and regular expression matching

## 🚀 Getting Started

### Installation

```bash
# Clone repository
git clone https://github.com/codingwithrsn33/Kansas-Site-Crawling.git
cd Kansas-Site-Crawling

# Install dependencies
pip install playwright
playwright install chromium
```

### Execution

```bash
python sos_crawler.py
```

## 📋 Default Search Configuration

The system automatically processes these business entity types:

| Category | Search Terms | Target Entities |
|----------|--------------|-----------------|
| **Test Samples** | `AA`, `AAB`, `AAC` | Validation and testing |
| **Corporate Entities** | `LLC`, `INC`, `CORP` | Business structures |
| **Industry Focus** | `SERVICE`, `KANSAS` | Regional and service businesses |

## 📁 Output Structure

```
kansas_business_data/
├── 📊 json/                           # Successful extractions
│   └── business_{name}_{timestamp}.json
├── 🔧 html_fallback/                  # Source preservation
│   └── {context}_{timestamp}.html
├── 📝 errors/                         # Diagnostic information
│   ├── error_{term}_{timestamp}.json
│   └── diagnostic_data/
└── 📋 crawler.log                     # System activity
```

## 📊 Data Schema

### Business Entity Record

```json
{
  "identification": {
    "business_id": "1234567",
    "business_name": "Example Company LLC",
    "entity_type": "Limited Liability Company"
  },
  "registration": {
    "formation_date": "2020-01-15",
    "jurisdiction": "Kansas",
    "entity_status": "Active"
  },
  "compliance": {
    "last_reporting_year": "2023",
    "next_report_due_date": "2024-04-15"
  },
  "contact_information": {
    "resident_agent": "John Doe",
    "principal_office_address": "123 Main St, Kansas City, KS 66101"
  },
  "metadata": {
    "extraction_timestamp": "2024-01-15T10:30:00Z",
    "search_term": "LLC",
    "processing_status": "success"
  }
}
```

## ⚙️ Configuration

### Search Parameters
Modify the search terms in the main execution method:

```python
search_terms = [
    "LLC", "INC", "CORP", 
    "SERVICE", "CONSTRUCTION",
    "CONSULTING", "TECHNOLOGY"
]
```

### Processing Limits
Adjust the number of entities processed per search term:

```python
# Process first 5 businesses per search term
for business in businesses[:5]:
    process_business(business)
```

## 🎯 Performance Features

### Rate Management
- Configurable delays between requests
- Respectful crawling practices
- Adaptive timing based on response patterns

### Quality Assurance
- Data validation at extraction points
- Cross-reference verification
- Completeness scoring

### Monitoring
- Real-time progress tracking
- Success rate analytics
- Performance metrics collection

## 🔧 Technical Specifications

### Requirements
- **Python**: 3.7+
- **Browser Automation**: Playwright with Chromium
- **Memory**: 2GB+ RAM recommended
- **Storage**: 1GB+ for output data

### Supported Data Elements
- Business identification numbers
- Entity names and types
- Registration dates and status
- Geographic information
- Compliance timelines
- Contact details

## 📈 Enterprise Integration

### Data Export
- Structured JSON format
- Batch processing capabilities
- Incremental extraction support
- Metadata enrichment

### Monitoring & Analytics
- Extraction success rates
- Processing efficiency metrics
- Error pattern analysis
- Performance trend tracking

## 🛠️ Operational Excellence

### Error Recovery
- Automatic retry mechanisms
- Session state preservation
- Graceful degradation
- Comprehensive diagnostics

### Maintenance
- Regular dependency updates
- Extraction rule validation
- Performance optimization
- Storage management

---

## 👨‍💻 Developer Information

**Rohan Subhash Darekar**  
Python Developer  
📞 +91 9075237180  
📧 rohandarekar307@gmail.com  
🔗 [GitHub Profile](https://github.com/codingwithrsn33)

---

**Transform web data into business intelligence with professional-grade automation.**
