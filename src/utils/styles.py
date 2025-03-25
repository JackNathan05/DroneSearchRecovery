# src/utils/styles.py
"""Style definitions for consistent UI appearance"""

# Color scheme from config
COLORS = {
    "primary": "#4A90E2",    # Soft Blue
    "secondary": "#1E3A8A",  # Deep Navy
    "accent": "#FF7E47",     # Safety Orange
    "neutral": "#D1D5DB",    # Silver Gray
    "white": "#FFFFFF",      # White
    "light_bg": "#F9FAFB",   # Light background
    "hover_primary": "#3A80D2"  # Hover color for primary
}

# Style sheets
BUTTON_STYLES = {
    "primary": f"""
        QPushButton {{
            background-color: {COLORS['primary']};
            color: {COLORS['white']};
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: {COLORS['hover_primary']};
        }}
    """,
    
    "secondary": f"""
        QPushButton {{
            background-color: {COLORS['secondary']};
            color: {COLORS['white']};
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: #152C66;
        }}
    """,
    
    "neutral": f"""
        QPushButton {{
            background-color: {COLORS['neutral']};
            color: {COLORS['secondary']};
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: #9CA3AF;
        }}
    """,
    
    "accent": f"""
        QPushButton {{
            background-color: {COLORS['accent']};
            color: {COLORS['white']};
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: #E56A37;
        }}
    """
}

INPUT_STYLES = {
    "default": f"""
        QLineEdit, QTextEdit {{
            border: 2px solid {COLORS['neutral']};
            border-radius: 5px;
            padding: 5px 10px;
            background-color: {COLORS['white']};
        }}
        QLineEdit:focus, QTextEdit:focus {{
            border: 2px solid {COLORS['primary']};
        }}
    """
}

PANEL_STYLES = {
    "default": f"""
        QFrame {{
            background-color: {COLORS['light_bg']};
            border: 2px solid {COLORS['neutral']};
            border-radius: 10px;
        }}
    """
}

SIDEBAR_STYLE = f"""
    QWidget {{
        background-color: {COLORS['secondary']};
        color: {COLORS['white']};
    }}
"""

# Function to generate label styles with different sizes
def get_label_style(size="medium", weight="normal", color="secondary"):
    """Get label style based on size, weight and color"""
    
    size_map = {
        "small": "14px",
        "medium": "16px",
        "large": "20px",
        "xlarge": "24px"
    }
    
    weight_map = {
        "normal": "normal",
        "bold": "bold"
    }
    
    return f"""
        QLabel {{
            font-size: {size_map.get(size, "16px")};
            font-weight: {weight_map.get(weight, "normal")};
            color: {COLORS.get(color, COLORS['secondary'])};
        }}
    """