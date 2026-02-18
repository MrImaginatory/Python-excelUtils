# Cell to Set ✨

A powerful, user-friendly Streamlit web application that transforms Excel spreadsheets into clean JSON data and SQL queries in seconds.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.0%2B-orange)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 📋 Table of Contents

- [Features](#features)
- [Demo](#demo)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration Options](#configuration-options)
- [Technical Details](#technical-details)
- [API Reference](#api-reference)
- [Contributing](#contributing)
- [License](#license)

---

## ✨ Features

### Core Functionality

- **Excel File Upload**: Support for both `.xlsx` and `.xls` file formats
- **Multi-Sheet Support**: Automatically detects and allows selection from multiple sheets within a workbook
- **JSON Conversion**: Convert Excel data to JSON with multiple orientation options
- **SQL Generation**: Generate `CREATE TABLE` and `INSERT INTO` statements for MySQL, PostgreSQL, and SQLite

### Data Cleaning

- **Intelligent Null Handling**: Automatically detects and filters various null representations:
  - `NA`, `null`, `None`
  - `nan`, `ns`
  - `not available`
  - Empty strings and whitespace-only values
- **Column-Selective Cleaning**: Choose specific columns for null filtering
- **Real-time Statistics**: View retained rows, dropped rows, and retention rate

### User Interface

- **Modern UI**: Clean, professional interface with custom CSS styling
- **Data Preview**: Preview raw and cleaned data before downloading
- **SQL Preview Tabs**: View `CREATE TABLE`, `INSERT INTO`, and full SQL separately
- **Download Options**: One-click download for both JSON and SQL outputs

---

## 🎬 Demo

#### Link to Project [https://cell-to-set.streamlit.app/](https://cell-to-set.streamlit.app/)

### Demo Video

[![Watch the Demo]](https://github.com/MrImaginatory/Python-excelUtils/blob/main/Demo_Video.mp4)


### Workflow

1. Upload your Excel file (.xlsx or .xls)
2. Select the sheet to convert (if multiple sheets exist)
3. Click "🚀 Start Process"
4. Review data overview and cleaning results
5. Configure JSON/SQL options in the sidebar
6. Download your converted JSON or SQL file

---

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/MrImaginatory/Cell_to_Set.git
   cd Excel_to_Json
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   streamlit run excelJson.py
   ```

5. Open your browser and navigate to `http://localhost:8501`

---

## 📖 Usage

### Basic Usage

1. **Upload File**: Drag and drop or click to upload an Excel file
2. **Select Sheet**: If the workbook contains multiple sheets, select the desired one
3. **Start Process**: Click the "🚀 Start Process" button to begin conversion
4. **Review Results**: Check the data overview and cleaning statistics
5. **Download**: Use the download buttons to save your JSON or SQL output

### Data Cleaning

The application automatically cleans your data by:

1. Converting various null representations to proper `NA` values
2. Removing rows with invalid data in selected columns
3. Preserving all valid data rows

### JSON Output Options

Configure JSON output format in the sidebar:

| Orientation | Description |
|-------------|-------------|
| `records` | List of dictionaries (default, most common) |
| `columns` | Dictionary with column names as keys |
| `index` | Dictionary with row indices as keys |
| `values` | Nested array of values |
| `table` | Table schema format |

### SQL Output Options

| Option | Description |
|--------|-------------|
| **Table Name** | Custom name for the generated SQL table |
| **SQL Dialect** | Choose between MySQL, PostgreSQL, or SQLite |

---

## ⚙️ Configuration Options

### Sidebar Settings

#### JSON Options

- **Orientation**: Select the JSON structure format
- **Indent Level**: Control formatting indentation (0-4 spaces)

#### SQL Options

- **Table Name**: Specify the target table name (default: `my_table`)
- **SQL Dialect**: Choose target database:
  - MySQL
  - PostgreSQL
  - SQLite

---

## 🔧 Technical Details

### Dependencies

| Package | Purpose |
|---------|---------|
| `streamlit` | Web application framework |
| `pandas` | Data manipulation and Excel reading |
| `openpyxl` | Excel file format support |

### Data Type Mapping (SQL)

| Pandas dtype | MySQL | PostgreSQL | SQLite |
|--------------|-------|------------|--------|
| `int*` | INT | INTEGER | INT |
| `float*` | DOUBLE | DOUBLE PRECISION | REAL |
| `bool` | BOOLEAN | BOOLEAN | BOOLEAN |
| `datetime` | DATETIME | TIMESTAMP | DATETIME |
| `object/string` | VARCHAR(255) | TEXT | TEXT |

### Caching

The application uses Streamlit's `@st.cache_data` decorator for:
- [`get_sheet_names()`](excelJson.py:68) - Caches sheet names for performance
- [`load_data()`](excelJson.py:78) - Caches loaded DataFrames

---

## 📚 API Reference

### Functions

#### `get_sheet_names(file)`

Retrieves all sheet names from an Excel file.

**Parameters:**
- `file`: Uploaded Excel file object

**Returns:**
- `list`: List of sheet names or `None` on error

---

#### `load_data(file, sheet_name=0)`

Loads a specific sheet from an Excel file into a pandas DataFrame.

**Parameters:**
- `file`: Uploaded Excel file object
- `sheet_name`: Sheet name or index (default: 0)

**Returns:**
- `DataFrame`: Loaded data or `None` on error

---

#### `clean_data(df, selected_cols)`

Cleans a DataFrame by converting null-like values and dropping invalid rows.

**Parameters:**
- `df`: Input DataFrame
- `selected_cols`: List of columns to clean

**Returns:**
- `DataFrame`: Cleaned DataFrame

**Null Values Detected:**
- `NA`, `null`, `None` (case insensitive)
- `nan`, `ns` (case insensitive)
- `not available` (case insensitive)
- Empty strings and whitespace

---

#### `sanitize_name(name)`

Sanitizes a column or table name for SQL compatibility.

**Parameters:**
- `name`: Original name string

**Returns:**
- `str`: Sanitized, lowercase name with underscores

---

#### `map_dtype_to_sql(dtype, dialect='mysql')`

Maps pandas data types to SQL column types.

**Parameters:**
- `dtype`: pandas dtype object
- `dialect`: Target SQL dialect ('mysql', 'postgresql', 'sqlite')

**Returns:**
- `str`: SQL column type string

---

#### `generate_sql(df, table_name, dialect='mysql')`

Generates CREATE TABLE and INSERT INTO SQL statements.

**Parameters:**
- `df`: Input DataFrame
- `table_name`: Target table name
- `dialect`: SQL dialect for type mapping

**Returns:**
- `tuple`: (create_statement, insert_statements)

---

## 🎨 UI Components

### Page Configuration

- **Page Title**: "Cell to Set"
- **Page Icon**: ✨
- **Layout**: Wide
- **Initial Sidebar State**: Expanded

### Custom Styling

The application includes custom CSS for:
- Header styling (`.main-header`, `.sub-header`)
- Button hover effects
- Benefit cards for the landing page
- Metric value formatting

---

## 📁 Project Structure

```
Excel_to_Json/
├── excelJson.py        # Main application file
├── requirements.txt    # Python dependencies
├── README.md           # Documentation
└── .gitignore          # Git ignore rules
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style

- Follow PEP 8 guidelines
- Add docstrings to all functions
- Include type hints where appropriate

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Data processing powered by [pandas](https://pandas.pydata.org/)
- Excel file support via [openpyxl](https://openpyxl.readthedocs.io/)

---

## 📧 Support

For issues, questions, or suggestions, please open an issue in the repository.

---

*Made with ❤️ for efficiency.*
