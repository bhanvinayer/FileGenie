# 🧞‍♂️ FileGenie - AI-Powered File Management Wizard

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://python.org)
[![AI Powered](https://img.shields.io/badge/AI-Powered-purple.svg)](https://openai.com)

> *"Your wish is my command! Grant me access to your files, and I shall bring order to digital chaos!"* ✨

FileGenie is a conversational, AI-powered file management tool that transforms chaotic workspaces into organized digital realms. With both **offline** and **online** modes, it provides intelligent file operations, semantic search, and automated organization.

**Engineering Constraints**: Built with maximum **8 variables** and **≤500 lines of code** - proving that powerful AI-enhanced file management can be achieved through elegant, minimalist design.  
This constraint-driven architecture demonstrates efficient coding practices while delivering comprehensive file organization, semantic analysis, and intelligent automation capabilities.

## 🌟 Key Features

### 🤖 Dual Mode Operation
- **🚀 FAST Mode (Offline)**: Lightning-fast responses with basic file operations
- **🧠 SMART Mode (Online)**: AI-powered analysis with OpenAI integration

### 🔮 Intelligent File Management
- **Conversational Commands**: Natural language file operations
- **Semantic Search**: Find files by meaning, not just names
- **Smart Organization**: Auto-categorize files by type and content
- **Duplicate Detection**: Find and remove duplicate files intelligently
- **Content Analysis**: AI-powered file content understanding

### 🛠️ Core Operations
- **File Operations**: Move, rename, copy, delete with confirmation
- **Smart Cleanup**: Identify temp files, large files, and old files
- **Auto-Tagging**: Semantic categorization of files
- **Relationship Detection**: Discover connections between files
- **Smart Rename**: Auto-fix messy filenames

## 🚀 Quick Start

### Prerequisites
- Python 3.7 or higher
- Optional: OpenAI API key for AI features

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/bhanvinayer/FileGenie.git
cd FileGenie
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set up environment (Optional - for AI features):**
```bash
# Create .env file
echo "OPENAI_API_KEY=your_api_key_here" > .env
```

4. **Run FileGenie:**
```bash
python filegenie.py
```

## 📖 Usage Guide

### Basic Commands

**Natural Language Operations:**
```
"organize python files"
"delete temp files"  
"find all images"
"move documents to archive folder"
"rename draft.txt to final.txt"
```

**Interactive Menu Options:**
1. 💬 Conversational Commands
2. 🧠 Semantic Content Analysis  
3. 🗂️ Smart Auto-Organization
4. 🔗 Duplicate Detection & Removal
5. 🧹 Smart Workspace Cleanup
6. 🔍 Semantic Search
7. 🔗 File Relationship Analysis
8. 📊 Workspace Analytics

### Example Workflows

#### Organize a Messy Downloads Folder
```python
# 1. Scan workspace
> python filegenie.py
> Enter workspace: /Users/username/Downloads

# 2. Smart organization
> Choice: 3
# FileGenie will auto-categorize files into:
# - code/ (Python, JavaScript, etc.)
# - docs/ (PDFs, Word docs, etc.)  
# - data/ (CSV, JSON files)
# - misc/ (Other files)
```

#### Find Related Project Files
```python
# 1. Enable AI mode with OPENAI_API_KEY
# 2. Analyze content
> Choice: 2

# 3. Search semantically  
> Choice: 6
> Search query: machine learning model
# Returns files related to ML even without "machine learning" in filename
```

#### Clean Up Workspace
```python
# 1. Smart cleanup suggestions
> Choice: 5
# Identifies:
# - Temporary files (temp*, backup*, copy*)
# - Large files (>5MB)
# - Old files (>30 days)

# 2. Remove duplicates
> Choice: 4
# Groups similar files and lets you choose which to keep
```

## 🏗️ Technical Architecture

### Design Constraints
- **Maximum 8 Variables**: Optimized memory usage with strategic variable reuse
- **≤500 Lines of Code**: Compact, efficient implementation
- **Dual Mode Support**: Seamless offline/online operation switching

### Core Components

```python
# Global State Management (8 variables max)
files = []      # Tracked file paths
meta = {}       # File metadata and settings  
sem = {}        # Semantic analysis results
rel = {}        # File relationships
q = ""          # Query/operation string
res = ""        # Response/result string  
ai = None       # AI agent instance
cmd = {}        # Command parsing and temp data
```

### File Type Support
- **Code Files**: `.py`, `.js`, `.html`, `.css`, `.json`
- **Documents**: `.txt`, `.md`, `.pdf`, `.docx`  
- **Data Files**: `.csv`, `.xlsx`, `.yaml`
- **Logs**: `.log`, `.cfg`

## 🔧 Configuration

### Environment Variables
```bash
# .env file
OPENAI_API_KEY=your_openai_api_key_here  # Optional: Enables AI features
```

### Safe Mode
FileGenie runs in **safe mode** by default, requiring confirmation for destructive operations:
- File deletion
- File moving/renaming  
- Bulk operations

## 🎯 Advanced Features

### Semantic Search (AI Mode)
```python
# Example: Find configuration files
semantic_search("application settings and configuration")
# Returns files containing config data, even if not named "config"
```

### Smart Organization Categories
- **Code**: Python, JavaScript, Java files
- **Docs**: Text files, PDFs, documentation
- **Data**: CSV, JSON, Excel files  
- **Misc**: Logs, temporary files

### Relationship Detection
FileGenie can discover semantic relationships between files:
- Similar content structure
- Related project files
- Documentation-code pairs

## 📊 Analytics & Insights

FileGenie provides comprehensive workspace analytics:
- File count and size distribution
- Duplicate file analysis  
- File type breakdown
- Large file identification
- Workspace organization score

## 🔒 Safety Features

- **Confirmation Prompts**: All destructive operations require confirmation
- **Safe Mode**: Enabled by default
- **Operation History**: Track all file operations
- **Backup Suggestions**: Recommends backing up before major changes
- **Reversible Operations**: Where possible, operations can be undone

## 🌐 Online vs Offline Mode

### Online Mode (AI-Powered) 🧠
**Requirements**: OpenAI API key
**Features**:
- Advanced semantic analysis
- Intelligent content summarization  
- Context-aware file relationships
- Natural language command parsing
- Smart organization suggestions

### Offline Mode (Fast) 🚀  
**Requirements**: None
**Features**:
- Basic file operations
- Pattern-based search
- Rule-based organization
- File type analysis
- Manual duplicate detection

### Development Guidelines
- Maintain the 8-variable constraint
- Keep total code under 500 lines


## 🎉 Examples & Demo

The `demo/` folder contains sample files to test FileGenie:
- Mixed file types (Python, CSV, text, images)
- Duplicate files for testing detection  
- Messy filenames for smart rename testing
- Various content types for semantic analysis

Try running FileGenie on the demo folder to see it in action!


*"In the realm of digital chaos, FileGenie brings order, one file at a time!"* 🧞‍♂️
