"""
CSS customizado para o Dashboard v2
Estilos que complementam o Bootstrap e definem comportamentos interativos
"""

from dashboard_v2.config import COLORS, FONTS, SPACING

# CSS inline que será injetado no app
CUSTOM_CSS = f"""
/* ===== RESET E BASE ===== */
* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

body {{
    font-family: {FONTS['family']};
    background-color: {COLORS['bg_primary']};
    color: {COLORS['text_primary']};
    overflow-x: hidden;
}}

/* ===== SIDEBAR NAVIGATION ===== */
.nav-item:hover {{
    background-color: {COLORS['sidebar_hover']};
    color: {COLORS['text_primary']} !important;
    border-left-color: {COLORS['primary']} !important;
}}

.nav-item.active {{
    background-color: {COLORS['sidebar_hover']};
    color: {COLORS['primary']} !important;
    border-left-color: {COLORS['primary']} !important;
    font-weight: {FONTS['weight']['semibold']};
}}

/* ===== DROPDOWN CUSTOMIZATION ===== */
.Select-control {{
    background-color: {COLORS['bg_card']} !important;
    border: 1px solid {COLORS['border']} !important;
    border-radius: 8px !important;
    color: {COLORS['text_primary']} !important;
}}

.Select-menu-outer {{
    background-color: {COLORS['bg_secondary']} !important;
    border: 1px solid {COLORS['border']} !important;
    border-radius: 8px !important;
    margin-top: 4px !important;
    z-index: 9999 !important;
}}

.Select-option {{
    background-color: transparent !important;
    color: {COLORS['text_primary']} !important;
    padding: {SPACING['sm']}px {SPACING['md']}px !important;
}}

.Select-option:hover {{
    background-color: {COLORS['bg_hover']} !important;
}}

.Select-option.is-selected {{
    background-color: {COLORS['primary']} !important;
}}

.Select-placeholder {{
    color: {COLORS['text_muted']} !important;
}}

.Select-value-label {{
    color: {COLORS['text_primary']} !important;
}}

/* ===== DROPDOWN COM TEXTO BRANCO (para modais) ===== */
.dropdown-white-text .Select-control {{
    background-color: {COLORS['bg_card']} !important;
    color: {COLORS['text_primary']} !important;
}}

.dropdown-white-text .Select-value-label {{
    color: {COLORS['text_primary']} !important;
}}

.dropdown-white-text .Select-placeholder {{
    color: {COLORS['text_secondary']} !important;
}}

.dropdown-white-text .Select-menu-outer {{
    background-color: {COLORS['bg_secondary']} !important;
}}

.dropdown-white-text .Select-option {{
    color: {COLORS['text_primary']} !important;
    background-color: transparent !important;
}}

.dropdown-white-text .Select-option:hover {{
    background-color: {COLORS['bg_hover']} !important;
}}

.dropdown-white-text .Select-option.is-selected {{
    background-color: {COLORS['primary']} !important;
    color: white !important;
}}

/* ===== DATE PICKER CUSTOMIZATION ===== */
.DateInput_input {{
    background-color: {COLORS['bg_card']} !important;
    border: 1px solid {COLORS['border']} !important;
    color: {COLORS['text_primary']} !important;
    font-family: {FONTS['family']} !important;
    font-size: {FONTS['size']['sm']} !important;
    padding: 8px 12px !important;
}}

.DateInput_input::placeholder {{
    color: {COLORS['text_muted']} !important;
}}

.DateRangePickerInput {{
    background-color: {COLORS['bg_card']} !important;
    border: 1px solid {COLORS['border']} !important;
    border-radius: 8px !important;
}}

.DateRangePicker_picker {{
    z-index: 9999 !important;
    background-color: {COLORS['bg_secondary']} !important;
    border: 1px solid {COLORS['border']} !important;
    border-radius: 8px !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5) !important;
}}

.CalendarDay {{
    background-color: {COLORS['bg_card']} !important;
    color: {COLORS['text_primary']} !important;
    border: 1px solid {COLORS['border']} !important;
}}

.CalendarDay:hover {{
    background-color: {COLORS['bg_hover']} !important;
    border: 1px solid {COLORS['primary']} !important;
}}

.CalendarDay__selected, .CalendarDay__selected:active, .CalendarDay__selected:hover {{
    background-color: {COLORS['primary']} !important;
    border: 1px solid {COLORS['primary']} !important;
    color: white !important;
}}

.CalendarDay__selected_span {{
    background-color: {COLORS['bg_hover']} !important;
    border: 1px solid {COLORS['border']} !important;
}}

.CalendarMonth_caption {{
    color: {COLORS['text_primary']} !important;
    font-weight: {FONTS['weight']['semibold']} !important;
}}

.DayPickerNavigation_button {{
    background-color: {COLORS['bg_card']} !important;
    border: 1px solid {COLORS['border']} !important;
}}

.DayPickerNavigation_button:hover {{
    background-color: {COLORS['bg_hover']} !important;
    border: 1px solid {COLORS['primary']} !important;
}}

.DayPickerNavigation_svg__horizontal {{
    fill: {COLORS['text_primary']} !important;
}}

.DayPicker_weekHeader {{
    color: {COLORS['text_secondary']} !important;
}}

.CalendarDay__blocked_out_of_range {{
    background-color: {COLORS['bg_primary']} !important;
    color: {COLORS['text_muted']} !important;
    border: 1px solid {COLORS['border']} !important;
}}

/* ===== CARDS ===== */
.custom-card {{
    background-color: {COLORS['bg_card']};
    border-radius: 10px;
    padding: {SPACING['md']}px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}}

.custom-card:hover {{
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
}}

.card-value {{
    font-size: {FONTS['size']['4xl']};
    font-weight: {FONTS['weight']['bold']};
    margin: {SPACING['sm']}px 0;
    line-height: 1.2;
}}

.card-label {{
    font-size: {FONTS['size']['sm']};
    color: {COLORS['text_secondary']};
    text-transform: uppercase;
    letter-spacing: 0.5px;
    font-weight: {FONTS['weight']['semibold']};
}}

.card-subtitle {{
    font-size: {FONTS['size']['xs']};
    color: {COLORS['text_muted']};
    margin-top: {SPACING['xs']}px;
}}

/* ===== BADGES ===== */
.badge-success {{
    background-color: {COLORS['success']};
    color: white;
    padding: 4px 12px;
    border-radius: 12px;
    font-size: {FONTS['size']['xs']};
    font-weight: {FONTS['weight']['semibold']};
}}

.badge-danger {{
    background-color: {COLORS['danger']};
    color: white;
    padding: 4px 12px;
    border-radius: 12px;
    font-size: {FONTS['size']['xs']};
    font-weight: {FONTS['weight']['semibold']};
}}

.badge-warning {{
    background-color: {COLORS['warning']};
    color: {COLORS['bg_primary']};
    padding: 4px 12px;
    border-radius: 12px;
    font-size: {FONTS['size']['xs']};
    font-weight: {FONTS['weight']['semibold']};
}}

/* ===== GRÁFICOS ===== */
.graph-container {{
    background-color: {COLORS['bg_card']};
    border-radius: 10px;
    padding: {SPACING['md']}px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}}

.graph-title {{
    color: {COLORS['text_primary']};
    font-size: {FONTS['size']['lg']};
    font-weight: {FONTS['weight']['semibold']};
    margin-bottom: {SPACING['md']}px;
}}

/* ===== SCROLLBAR CUSTOMIZADA ===== */
::-webkit-scrollbar {{
    width: 8px;
    height: 8px;
}}

::-webkit-scrollbar-track {{
    background-color: {COLORS['bg_primary']};
}}

::-webkit-scrollbar-thumb {{
    background-color: {COLORS['border']};
    border-radius: 4px;
}}

::-webkit-scrollbar-thumb:hover {{
    background-color: {COLORS['text_muted']};
}}

/* ===== ANIMAÇÕES ===== */
@keyframes fadeIn {{
    from {{
        opacity: 0;
        transform: translateY(10px);
    }}
    to {{
        opacity: 1;
        transform: translateY(0);
    }}
}}

.animate-fade-in {{
    animation: fadeIn 0.4s ease-out;
}}

/* ===== RESPONSIVIDADE ===== */
@media (max-width: 1920px) {{
    /* Full HD - ajustes sutis */
    .card-value {{
        font-size: {FONTS['size']['3xl']};
    }}
}}

@media (max-width: 1366px) {{
    /* HD - reduzir ainda mais */
    .card-value {{
        font-size: {FONTS['size']['2xl']};
    }}
    
    .custom-card {{
        padding: {SPACING['md']}px;
    }}
}}

@media (max-width: 768px) {{
    /* Mobile/Tablet */
    .card-value {{
        font-size: {FONTS['size']['xl']};
    }}
    
    /* Sidebar some em mobile */
    .sidebar {{
        display: none;
    }}
}}
"""

def get_custom_css():
    """Retorna o CSS customizado como string"""
    return CUSTOM_CSS
