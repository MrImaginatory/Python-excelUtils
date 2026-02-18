
import streamlit as st
import pandas as pd
import json
import time
import io
import re

# -----------------------------------------------------------------------------
# Page Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Excel to JSON & SQL Pro",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------------
# Custom CSS for Enhanced UI
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #4a4e69;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: 700;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #6c757d;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton>button {
        background-color: #4a4e69;
        color: white;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #22223b;
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .benefit-card {
        background-color: #26272f;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        text-align: center;
        margin-bottom: 1rem;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
        color: #22223b;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------
@st.cache_data
def get_sheet_names(file):
    """Get all sheet names from the Excel file."""
    try:
        xls = pd.ExcelFile(file)
        return xls.sheet_names
    except Exception as e:
        st.error(f"Error reading sheet names: {e}")
        return None

@st.cache_data
def load_data(file, sheet_name=0):
    """Load a specific sheet from an Excel file into DataFrame."""
    try:
        return pd.read_excel(file, sheet_name=sheet_name)
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return None

def clean_data(df, selected_cols):
    """Clean DataFrame based on selected columns."""
    df_clean = df.copy()
    
    
    # Convert various "null" strings to actual NA
    if selected_cols:
        for col in selected_cols:
            if col in df_clean.columns:
                # Convert to string, strip whitespace, then replace known "bad" values
                # Added 'ns', 'none', 'nan' (case insensitive) per request
                df_clean[col] = df_clean[col].astype(str).str.strip().replace({
                    r'(?i)^NA$': pd.NA,
                    r'(?i)^null$': pd.NA,
                    r'(?i)^not available$': pd.NA,
                    r'(?i)^nan$': pd.NA,
                    r'(?i)^None$': pd.NA,
                    r'(?i)^ns$': pd.NA,
                    r'^\s*$': pd.NA
                }, regex=True)
        
        # Drop rows where selected columns are NA
        df_clean = df_clean.dropna(subset=[col for col in selected_cols if col in df_clean.columns])
    
    return df_clean

def sanitize_name(name):
    """Sanitize a column/table name for SQL."""
    name = re.sub(r'[^\w]', '_', str(name).strip())
    name = re.sub(r'_+', '_', name).strip('_')
    if not name or name[0].isdigit():
        name = f'col_{name}'
    return name.lower()

def map_dtype_to_sql(dtype, dialect='mysql'):
    """Map pandas dtype to SQL column type."""
    dtype_str = str(dtype)
    if 'int' in dtype_str:
        return 'INT' if dialect != 'postgresql' else 'INTEGER'
    elif 'float' in dtype_str:
        return 'DOUBLE' if dialect == 'mysql' else 'REAL' if dialect == 'sqlite' else 'DOUBLE PRECISION'
    elif 'bool' in dtype_str:
        return 'BOOLEAN'
    elif 'datetime' in dtype_str:
        return 'DATETIME' if dialect != 'postgresql' else 'TIMESTAMP'
    else:
        return 'VARCHAR(255)' if dialect == 'mysql' else 'TEXT'

def generate_sql(df, table_name, dialect='mysql'):
    """Generate CREATE TABLE and INSERT INTO SQL statements from a DataFrame."""
    table_name = sanitize_name(table_name)
    col_map = {col: sanitize_name(col) for col in df.columns}
    
    # --- CREATE TABLE ---
    col_defs = []
    for col in df.columns:
        sql_type = map_dtype_to_sql(df[col].dtype, dialect)
        col_defs.append(f"    {col_map[col]} {sql_type}")
    
    create_stmt = f"CREATE TABLE IF NOT EXISTS {table_name} (\n"
    create_stmt += ",\n".join(col_defs)
    create_stmt += "\n);\n"
    
    # --- INSERT INTO ---
    insert_stmts = []
    col_names = ", ".join(col_map[col] for col in df.columns)
    
    for _, row in df.iterrows():
        values = []
        for col in df.columns:
            val = row[col]
            if pd.isna(val):
                values.append("NULL")
            elif isinstance(val, (int, float)):
                values.append(str(val))
            else:
                escaped = str(val).replace("'", "''")
                values.append(f"'{escaped}'")
        vals_str = ", ".join(values)
        insert_stmts.append(f"INSERT INTO {table_name} ({col_names}) VALUES ({vals_str});")
    
    return create_stmt, "\n".join(insert_stmts)

# -----------------------------------------------------------------------------
# Sidebar Configuration
# -----------------------------------------------------------------------------
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/8297/8297437.png", width=100)
    st.title("⚙️ Settings")
    st.markdown("---")
    
    st.subheader("Cleaning Options")
    
    st.markdown("### JSON Options")
    json_orient = st.selectbox(
        "Orientation",
        options=['records', 'columns', 'index', 'values', 'table'],
        index=0,
        help="Format of the JSON output. 'records' is standard list of objects."
    )
    
    indent_level = st.slider("Indent Level", min_value=0, max_value=4, value=2, step=1)
    
    st.markdown("### SQL Options")
    sql_table_name = st.text_input("Table Name", value="my_table", help="Name for the SQL table.")
    sql_dialect = st.selectbox(
        "SQL Dialect",
        options=['mysql', 'postgresql', 'sqlite'],
        index=0,
        help="Target database dialect for type mapping."
    )
    
    st.markdown("---")
    st.markdown("Made with ❤️ for efficiency.")

# -----------------------------------------------------------------------------
# Main Content
# -----------------------------------------------------------------------------
col1, col2, col3 = st.columns([1, 6, 1])
with col2:
    st.markdown('<div class="main-header">✨ Excel to JSON & SQL Pro</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Transform your spreadsheets into clean JSON data and SQL queries in seconds.</div>', unsafe_allow_html=True)

# File Uploader Section
st.markdown("### 1. Upload Your Data")
uploaded_file = st.file_uploader("Drop your Excel file here", type=['xlsx', 'xls'], help="Supported formats: .xlsx, .xls")

if uploaded_file:
    # Read sheet names first
    sheet_names = get_sheet_names(uploaded_file)

    if sheet_names is not None:
        # Sheet Selection
        st.markdown("### 📄 Sheet Selection")
        if len(sheet_names) > 1:
            selected_sheet = st.selectbox(
                "This workbook has multiple sheets. Select one to convert:",
                options=sheet_names,
                index=0,
                help="Choose which sheet to load and convert to JSON."
            )
        else:
            selected_sheet = sheet_names[0]
            st.info(f"📄 Single sheet detected: **{selected_sheet}**")

        # Start Process Button
        st.markdown("---")
        if st.button("🚀 Start Process", type="primary", use_container_width=True):
            st.session_state['process_started'] = True
            st.session_state['process_sheet'] = selected_sheet

        # Only proceed if the user clicked Start Process
        if st.session_state.get('process_started') and st.session_state.get('process_sheet') == selected_sheet:
            # Load Data for the selected sheet
            with st.spinner(f"Loading sheet '{selected_sheet}'..."):
                original_df = load_data(uploaded_file, sheet_name=selected_sheet)
                time.sleep(0.5)  # UX pause

            if original_df is not None:
                # Data Overview
                st.markdown("### 2. Data Overview")
                col_metrics1, col_metrics2, col_metrics3 = st.columns(3)
                with col_metrics1:
                    st.metric("Total Rows", original_df.shape[0])
                with col_metrics2:
                    st.metric("Total Columns", original_df.shape[1])
                with col_metrics3:
                    st.metric("Data Size", f"{uploaded_file.size / 1024:.1f} KB")

                with st.expander("🔍 Preview Raw Data", expanded=False):
                    st.dataframe(original_df.head(10), width='stretch')

                # Cleaning Configuration
                st.markdown("### 3. Data Cleaning")
                
                available_cols = original_df.columns.tolist()
                
                # Default to ALL columns for cleaning now
                selected_cleaning_cols = st.multiselect(
                    "Select columns to filter for invalid values (NA/null/empty/ns):",
                    options=available_cols,
                    default=available_cols,
                    help="Rows with invalid values in ANY of these selected columns will be removed."
                )
                
                # Apply Cleaning
                cleaned_df = clean_data(original_df, selected_cleaning_cols)
                
                # Calculate stats
                rows_dropped = len(original_df) - len(cleaned_df)
                percent_dropped = (rows_dropped / len(original_df) * 100) if len(original_df) > 0 else 0
                
                # Show Cleaning Results
                st.success(f"Processing Complete! Kept {len(cleaned_df)} rows.")
                
                m1, m2, m3 = st.columns(3)
                m1.metric("Retained Rows", len(cleaned_df))
                m2.metric("Dropped Rows", rows_dropped, delta=-rows_dropped, delta_color="inverse")
                m3.metric("Retention Rate", f"{100-percent_dropped:.1f}%")

                if rows_dropped > 0:
                    st.warning(f"⚠️ Removed {rows_dropped} rows containing invalid data (NA, null, empty, ns).")
                
                with st.expander("✅ Preview Cleaned Data"):
                    st.dataframe(cleaned_df.head(), width='stretch')

                # JSON Conversion
                st.markdown("### 4. JSON Output")
                
                full_json_str = cleaned_df.to_json(orient=json_orient, indent=indent_level if indent_level > 0 else None)
                
                # Convert only top 10 for preview
                preview_df = cleaned_df.head(10)
                preview_json_str = preview_df.to_json(orient=json_orient, indent=indent_level if indent_level > 0 else None)

                # Download Button
                file_label = uploaded_file.name.rsplit('.', 1)[0]
                sheet_suffix = f"_{selected_sheet}" if len(sheet_names) > 1 else ""
                st.download_button(
                    label="⬇️ Download Full JSON",
                    data=full_json_str,
                    file_name=f"{file_label}{sheet_suffix}_cleaned.json",
                    mime="application/json",
                    key='download-btn'
                )

                # SQL Output
                st.markdown("### 5. SQL Output")
                
                create_stmt, insert_stmts = generate_sql(cleaned_df, sql_table_name, sql_dialect)
                full_sql = create_stmt + "\n" + insert_stmts
                
                # Preview SQL (CREATE + first 10 inserts)
                preview_create, preview_inserts = generate_sql(preview_df, sql_table_name, sql_dialect)
                preview_sql = preview_create + "\n" + preview_inserts

                st.download_button(
                    label="⬇️ Download Full SQL",
                    data=full_sql,
                    file_name=f"{file_label}{sheet_suffix}.sql",
                    mime="text/plain",
                    key='download-sql-btn'
                )

                st.caption("Previewing CREATE TABLE + first 10 INSERT statements:")
                tab_create, tab_insert, tab_full = st.tabs(["CREATE TABLE", "INSERT INTO", "Full SQL"])
                
                with tab_create:
                    st.code(preview_create, language='sql')
                    
                with tab_insert:
                    st.code(preview_inserts, language='sql')
                    
                with tab_full:
                    st.text_area("SQL Preview", preview_sql, height=300)

else:
    # Empty State / Landing Page
    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div class="benefit-card">
            <h3>🚀 Fast</h3>
            <p>Instant conversion with optimized Pandas processing.</p>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="benefit-card">
            <h3>🧹 Clean</h3>
            <p>Intelligent filtering of null and missing values.</p>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class="benefit-card">
            <h3>🔒 Secure</h3>
            <p>Your data is processed locally in your session.</p>
        </div>
        """, unsafe_allow_html=True)

