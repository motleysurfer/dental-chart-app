import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import io

# Initialize session state for form fields if not already present
if 'reset_requested' not in st.session_state:
    st.session_state.reset_requested = False

# Add this before the form fields are created
if st.session_state.reset_requested:
    # Reset the state before widgets are rendered
    for key in ['max_missing', 'max_implant', 'max_extracted', 'max_crown', 
               'max_rct', 'max_filling', 'max_bridge',
               'mand_missing', 'mand_implant', 'mand_extracted', 'mand_crown',
               'mand_rct', 'mand_filling', 'mand_bridge']:
        st.session_state[key] = ""
    # Reset the flag
    st.session_state.reset_requested = False



st.set_page_config(page_title="Dental Chart Generator", layout="wide")

# Set up the page
st.title("Dental Chart Generator")
st.markdown("""
This application generates dental charts for patient records using the Universal Numbering System.
Fill in the tooth numbers for any modifications, then click "Generate Chart".
""")

# Create tabs for upper and lower jaw
tab1, tab2 = st.tabs(["Upper Jaw (Maxillary)", "Lower Jaw (Mandibular)"])

# Define validation functions
def parse_teeth_numbers(text, jaw=None):
    if not text.strip():
        return []
    
    # Define valid ranges for teeth numbers
    valid_teeth = range(1, 33)  # Universal Numbering System: 1-32
    maxillary_teeth = range(1, 17)  # Upper teeth: 1-16
    mandibular_teeth = range(17, 33)  # Lower teeth: 17-32
    
    result = []
    errors = []
    
    # Handle missing comma case (e.g. "1234" should be "1,2,3,4")
    # Check if it's a single "number" longer than 2 digits with no commas
    if len(text.strip()) > 2 and "," not in text and not text.strip().isspace():
        # Try to interpret as individual digits
        if all(c.isdigit() for c in text.strip()):
            possible_teeth = []
            current_num = ""
            
            for char in text.strip():
                current_num += char
                # Check if we have a valid one or two-digit tooth number
                if 1 <= int(current_num) <= 32:
                    possible_teeth.append(int(current_num))
                    current_num = ""
                # If we've accumulated more than 2 digits, this approach won't work
                elif len(current_num) > 2:
                    possible_teeth = []
                    break
            
            # If we successfully parsed all characters and have no leftover digits
            if possible_teeth and current_num == "":
                st.warning(f"No commas found. Interpreted '{text}' as {possible_teeth}")
                text = ",".join(str(t) for t in possible_teeth)
    
    try:
        # Normal comma-separated case
        for tooth_str in text.split(','):
            tooth_str = tooth_str.strip()
            if not tooth_str:
                continue
                
            tooth = int(tooth_str)
            
            # Validate tooth number is in range
            if tooth not in valid_teeth:
                errors.append(f"Tooth {tooth} is not valid (must be 1-32)")
                continue
                
            # Check if tooth is in the correct jaw (if specified)
            if jaw == "maxillary" and tooth not in maxillary_teeth:
                errors.append(f"Tooth {tooth} is not an upper jaw tooth (must be 1-16)")
                continue
            elif jaw == "mandibular" and tooth not in mandibular_teeth:
                errors.append(f"Tooth {tooth} is not a lower jaw tooth (must be 17-32)")
                continue
                
            result.append(tooth)
            
        if errors:
            for error in errors:
                st.warning(error)
                
        return result
    except ValueError:
        st.warning(f"Invalid input '{text}'. Please use comma-separated numbers.")
        return []

def parse_bridges(text, jaw=None):
    if not text.strip():
        return []
    
    # Define valid ranges for teeth numbers
    maxillary_teeth = range(1, 17)  # Upper teeth: 1-16
    mandibular_teeth = range(17, 33)  # Lower teeth: 17-32
    
    bridges = []
    errors = []
    
    try:
        # First check if we have multiple bridge pairs (comma separated)
        for bridge_pair in text.split(','):
            bridge_pair = bridge_pair.strip()
            
            # Skip empty parts
            if not bridge_pair:
                continue
                
            start_tooth = None
            end_tooth = None
            
            # Check for hyphen format (e.g. "10-12")
            if '-' in bridge_pair:
                start, end = bridge_pair.split('-')
                start_tooth = int(start.strip())
                end_tooth = int(end.strip())
            
            # If there's no hyphen but there are two numbers, assume it's a bridge (space format)
            elif ' ' in bridge_pair:
                # Space-separated format (e.g. "10 12")
                parts = bridge_pair.split()
                if len(parts) == 2:
                    start_tooth = int(parts[0].strip())
                    end_tooth = int(parts[1].strip())
            
            # Check if it's a simple pair of numbers without a separator (e.g. "10,12")
            elif ',' in text and len(text.split(',')) == 2 and ',' not in bridge_pair:
                # This is a special case for a single bridge with comma format
                all_parts = [p.strip() for p in text.split(',')]
                if len(all_parts) == 2 and all(p.isdigit() for p in all_parts):
                    start_tooth = int(all_parts[0])
                    end_tooth = int(all_parts[1])
                    # Exit early since we've parsed the whole text as one bridge
                    bridges = [(start_tooth, end_tooth)]
                    break
                    
            # If we've extracted the start and end teeth, validate them
            if start_tooth and end_tooth:
                # Check if teeth are in range 1-32
                if not (1 <= start_tooth <= 32 and 1 <= end_tooth <= 32):
                    errors.append(f"Bridge teeth ({start_tooth}-{end_tooth}) must be in range 1-32")
                    continue
                
                # Check if both teeth are in the same jaw
                if (start_tooth in maxillary_teeth and end_tooth not in maxillary_teeth) or \
                   (start_tooth in mandibular_teeth and end_tooth not in mandibular_teeth):
                    errors.append(f"Bridge teeth ({start_tooth}-{end_tooth}) must be in the same jaw")
                    continue
                
                # Check if teeth are in the specified jaw (if provided)
                if jaw == "maxillary" and (start_tooth not in maxillary_teeth or end_tooth not in maxillary_teeth):
                    errors.append(f"Bridge teeth ({start_tooth}-{end_tooth}) must be in upper jaw (1-16)")
                    continue
                elif jaw == "mandibular" and (start_tooth not in mandibular_teeth or end_tooth not in mandibular_teeth):
                    errors.append(f"Bridge teeth ({start_tooth}-{end_tooth}) must be in lower jaw (17-32)")
                    continue
                
                bridges.append((start_tooth, end_tooth))
        
        # Show errors if any
        if errors:
            for error in errors:
                st.warning(error)
        
        # Show message when valid bridges are found
        if bridges:
            formatted_bridges = [f"{b[0]}-{b[1]}" for b in bridges]
            st.success(f"Bridges detected: {', '.join(formatted_bridges)}")
        
        return bridges
    except ValueError as e:
        st.warning(f"Invalid bridge input '{text}'. Use format like '10-12' or '10,12'.")
        return []

# Create the dental chart function
def draw_dental_chart(maxillary_missing, maxillary_implant, maxillary_extracted, maxillary_bridges,
                      maxillary_crown, maxillary_rct, maxillary_filling,
                      mandibular_missing, mandibular_implant, mandibular_extracted, mandibular_bridges,
                      mandibular_crown, mandibular_rct, mandibular_filling):
    
    # Create the dental_modifications dictionary
    dental_modifications = {
        "maxillary": {
            "missing": set(maxillary_missing),
            "implant": set(maxillary_implant),
            "extracted": set(maxillary_extracted),
            "bridges": maxillary_bridges,
            "crown": set(maxillary_crown),
            "rct": set(maxillary_rct),
            "filling": set(maxillary_filling)
        },
        "mandibular": {
            "missing": set(mandibular_missing),
            "implant": set(mandibular_implant),
            "extracted": set(mandibular_extracted),
            "bridges": mandibular_bridges,
            "crown": set(mandibular_crown),
            "rct": set(mandibular_rct),
            "filling": set(mandibular_filling)
        }
    }

    # Create a taller figure with room for signature
    fig = plt.figure(figsize=(10, 8.5))
    
    # Create subplot grid with custom heights: dental charts on top, signature area on bottom
    gs = fig.add_gridspec(3, 1, height_ratios=[1, 1, 0.7])
    
    # Create the maxillary and mandibular axes
    axs = [fig.add_subplot(gs[0]), fig.add_subplot(gs[1])]
    
    # Create a third axes for the signature area
    signature_ax = fig.add_subplot(gs[2])

    maxillary_positions = {1: (-7, 0), 2: (-6, 0), 3: (-5, 0), 4: (-4, 0), 5: (-3, 0), 6: (-2, 0), 7: (-1, 0), 8: (0, 0),
                           9: (1, 0), 10: (2, 0), 11: (3, 0), 12: (4, 0), 13: (5, 0), 14: (6, 0), 15: (7, 0), 16: (8, 0)}

    mandibular_positions = {32: (-7.5, 0), 31: (-6.5, 0), 30: (-5.5, 0), 29: (-4.5, 0), 28: (-3.5, 0), 27: (-2.5, 0), 26: (-1.5, 0), 25: (-0.5, 0),
                            24: (0.5, 0), 23: (1.5, 0), 22: (2.5, 0), 21: (3.5, 0), 20: (4.5, 0), 19: (5.5, 0), 18: (6.5, 0), 17: (7.5, 0)}

    def draw_crown(ax, x, y, is_maxillary=True, color='purple'):
        # Draw crown at the top for maxillary teeth, bottom for mandibular teeth
        if is_maxillary:
            ax.plot([x - 0.3, x + 0.3], [y + 0.8, y + 0.8], color=color, linewidth=3)
        else:
            ax.plot([x - 0.3, x + 0.3], [y - 0.3, y - 0.3], color=color, linewidth=3)

    def draw_tooth(ax, x, y, color='black', linestyle='solid', linewidth=2):
        tooth_shape = np.array([[-0.3, 0], [-0.2, 0.5], [0, 0.7], [0.2, 0.5], [0.3, 0], [0, -0.2], [-0.3, 0]])
        ax.plot(tooth_shape[:, 0] + x, tooth_shape[:, 1] + y, color=color, linewidth=linewidth, linestyle=linestyle)

    def draw_implant(ax, x, y, color='blue', linewidth=4):
        ax.plot([x, x], [y - 0.2, y + 0.7], color=color, linewidth=linewidth)

    def draw_root_canal(ax, x, y, color='saddlebrown'):
        ax.plot([x, x], [y - 0.15, y + 0.6], color=color, linewidth=3)

     def draw_filling(ax, x, y, is_maxillary=True, color='darkorange'):
        # For maxillary teeth, draw the filling at the top
        # For mandibular teeth, draw the filling at the bottom
        if is_maxillary:
            fill_circle = plt.Circle((x, y + 0.9), 0.08, color=color, fill=False, linewidth=2)
        else:
            fill_circle = plt.Circle((x, y - 0.4), 0.08, color=color, fill=False, linewidth=2)
        ax.add_patch(fill_circle)

    for arch, positions in zip(["maxillary", "mandibular"], [maxillary_positions, mandibular_positions]):
        ax = axs[0] if arch == "maxillary" else axs[1]
        is_maxillary = arch == "maxillary"
        
        for num, (x, y) in positions.items():
            # First, draw all teeth that need a visible outline
            if num in dental_modifications[arch]["extracted"]:
                draw_tooth(ax, x, y, color='red', linestyle='dashed')
            elif num not in dental_modifications[arch]["missing"]:
                # Only draw normal tooth if not missing
                draw_tooth(ax, x, y, color='black')
                
            # Now handle special cases that can coexist with missing status
            if num in dental_modifications[arch]["missing"]:
                ax.text(x, y, "X", fontsize=14, ha='center', va='center', color='red', fontweight='bold')
                
            # Implant can be shown even if tooth is marked missing
            if num in dental_modifications[arch]["implant"]:
                draw_implant(ax, x, y, color='blue')
                
            if num in dental_modifications[arch]["rct"]:
                draw_root_canal(ax, x, y, color='saddlebrown')
                
            if num in dental_modifications[arch]["filling"]:
                draw_filling(ax, x, y, is_maxillary=is_maxillary, color='darkorange')
                
            if num in dental_modifications[arch]["crown"]:
                draw_crown(ax, x, y, is_maxillary=is_maxillary, color='purple')
            ax.text(x, y - 1.0 if arch == "maxillary" else y + 1.0, str(num), fontsize=12, ha='center', va='center', color='black')

        # Draw multiple bridges if they exist
        for bridge in dental_modifications[arch]["bridges"]:
            if len(bridge) == 2:  # Ensure the bridge tuple has exactly 2 elements
                bridge_start, bridge_end = bridge
                # Get x positions from positions dictionary
                if bridge_start in positions and bridge_end in positions:
                    start_x = positions[bridge_start][0]
                    end_x = positions[bridge_end][0]
                    # Draw bridge at appropriate y position for arch
                    bridge_y = 0.8 if is_maxillary else -0.3
                    ax.plot([start_x, end_x], [bridge_y, bridge_y], color='purple', linewidth=3)

    axs[0].set_title("Maxillary Arch (Upper Jaw) - Universal Numbering System")
    axs[1].set_title("Mandibular Arch (Lower Jaw) - Universal Numbering System")

    for ax in axs:
        ax.set_xlim(-8.5, 8.5)
        ax.set_ylim(-1.5, 1.5)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_frame_on(False)
    
    # Configure the signature area
    signature_ax.set_frame_on(False)
    signature_ax.set_xticks([])
    signature_ax.set_yticks([])
    
    # Add text and signature lines
    signature_ax.text(0.05, 0.85, "TREATMENT PLAN UNDERSTANDING & CONSENT:", fontweight='bold')
    signature_ax.text(0.05, 0.65, "I understand the proposed treatment plan including any modifications to my teeth as shown above.")
    signature_ax.text(0.05, 0.5, "I have had all my questions answered and consent to proceed with treatment.")
    
    # Add signature line
    signature_ax.axhline(y=0.25, xmin=0.05, xmax=0.45, color='black', linestyle='-')
    signature_ax.text(0.25, 0.15, "Patient Signature", ha='center')
    
    # Add date line
    signature_ax.axhline(y=0.25, xmin=0.55, xmax=0.95, color='black', linestyle='-')
    signature_ax.text(0.75, 0.15, "Date", ha='center')

    plt.tight_layout()
    
    # Save the figure to a buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
    buf.seek(0)
    
    return fig, buf

# Add help text for input formats
with st.expander("Help & Instructions"):
    st.markdown("""
    ### Instructions
    - Enter tooth numbers as comma-separated values (e.g., "1,2,5")
    - For bridges, you can use either:
      - Two teeth separated by a hyphen (e.g., "10-12")
      - Two teeth separated by a comma (e.g., "10,12")
    - You can mark a tooth as both missing and implant to show an implant at a missing tooth site
    
    ### Legend
    - **X** (red) = Missing tooth
    - **Dashed outline** (red) = Extracted tooth
    - **Vertical line** (blue) = Implant
    - **Horizontal line** (purple) = Crown or Bridge
    - **Vertical line in tooth** (brown) = Root Canal Treatment (RCT)
    - **Circle** (orange) = Filling
    """)

# Maxillary (Upper Jaw) tab
with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Tooth Conditions")
        maxillary_missing = st.text_input("Missing", placeholder="e.g., 1,4,7", key="max_missing")
        maxillary_implant = st.text_input("Implant", placeholder="e.g., 2,5", key="max_implant")
        maxillary_extracted = st.text_input("Extracted", placeholder="e.g., 8", key="max_extracted")
        maxillary_crown = st.text_input("Crown", placeholder="e.g., 13", key="max_crown")
    
    with col2:
        st.subheader("Procedures")
        maxillary_rct = st.text_input("Root Canal Treatment", placeholder="e.g., 12", key="max_rct")
        maxillary_filling = st.text_input("Filling", placeholder="e.g., 10", key="max_filling")
        maxillary_bridge = st.text_input("Bridge", placeholder="e.g., 10-12 or 10,12", key="max_bridge")
        st.markdown("<p style='font-size:0.8em; color:#666;'>For bridges: Use either format '10-12' or '10,12'.</p>", unsafe_allow_html=True)

# Mandibular (Lower Jaw) tab
with tab2:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Tooth Conditions")
        mandibular_missing = st.text_input("Missing", placeholder="e.g., 17,20", key="mand_missing")
        mandibular_implant = st.text_input("Implant", placeholder="e.g., 18", key="mand_implant")
        mandibular_extracted = st.text_input("Extracted", placeholder="e.g., 19", key="mand_extracted")
        mandibular_crown = st.text_input("Crown", placeholder="e.g., 30", key="mand_crown")
    
    with col2:
        st.subheader("Procedures")
        mandibular_rct = st.text_input("Root Canal Treatment", placeholder="e.g., 30", key="mand_rct")
        mandibular_filling = st.text_input("Filling", placeholder="e.g., 22,23", key="mand_filling")
        mandibular_bridge = st.text_input("Bridge", placeholder="e.g., 29-31 or 29,31", key="mand_bridge")
        st.markdown("<p style='font-size:0.8em; color:#666;'>For bridges: Use either format '29-31' or '29,31'.</p>", unsafe_allow_html=True)

# Action buttons
col1, col2 = st.columns(2)
with col1:
    generate_button = st.button("Generate Chart", type="primary")
with col2:
    reset_button = st.button("Reset All Fields")

# Handle reset button
if reset_button:
    st.session_state.reset_requested = True
    st.rerun()

# Generate chart when button is clicked
if generate_button:
    # Parse inputs with jaw validation
    max_missing = parse_teeth_numbers(st.session_state.max_missing, "maxillary")
    max_implant = parse_teeth_numbers(st.session_state.max_implant, "maxillary")
    max_extracted = parse_teeth_numbers(st.session_state.max_extracted, "maxillary")
    max_crown = parse_teeth_numbers(st.session_state.max_crown, "maxillary")
    max_rct = parse_teeth_numbers(st.session_state.max_rct, "maxillary")
    max_filling = parse_teeth_numbers(st.session_state.max_filling, "maxillary")
    max_bridges = parse_bridges(st.session_state.max_bridge, "maxillary")
    
    mand_missing = parse_teeth_numbers(st.session_state.mand_missing, "mandibular")
    mand_implant = parse_teeth_numbers(st.session_state.mand_implant, "mandibular")
    mand_extracted = parse_teeth_numbers(st.session_state.mand_extracted, "mandibular")
    mand_crown = parse_teeth_numbers(st.session_state.mand_crown, "mandibular")
    mand_rct = parse_teeth_numbers(st.session_state.mand_rct, "mandibular")
    mand_filling = parse_teeth_numbers(st.session_state.mand_filling, "mandibular")
    mand_bridges = parse_bridges(st.session_state.mand_bridge, "mandibular")

    # Generate the chart
    fig, buf = draw_dental_chart(
        max_missing, max_implant, max_extracted, max_bridges,
        max_crown, max_rct, max_filling,
        mand_missing, mand_implant, mand_extracted, mand_bridges,
        mand_crown, mand_rct, mand_filling
    )
    
    # Display the chart
    st.pyplot(fig)
    
    # Add download buttons
    col1, col2 = st.columns(2)
    
    # PNG download
    with col1:
        btn = st.download_button(
            label="Download PNG",
            data=buf,
            file_name="Dental_Chart.png",
            mime="image/png"
        )
    
    # PDF download (generate a new PDF version)
    with col2:
        pdf_buf = io.BytesIO()
        fig.savefig(pdf_buf, format='pdf', bbox_inches='tight')
        pdf_buf.seek(0)
        
        btn = st.download_button(
            label="Download PDF",
            data=pdf_buf,
            file_name="Dental_Chart.pdf",
            mime="application/pdf"
        )
