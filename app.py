import matplotlib.pyplot as plt
import numpy as np
import ipywidgets as widgets
from IPython.display import display, clear_output

# Create widgets for entering tooth numbers
maxillary_missing_input = widgets.Text(description='Missing:', placeholder='e.g., 1,4,7')
maxillary_implant_input = widgets.Text(description='Implant:', placeholder='e.g., 5,6')
maxillary_extracted_input = widgets.Text(description='Extracted:', placeholder='e.g., 8')
maxillary_crown_input = widgets.Text(description='Crown:', placeholder='e.g., 2,3')
maxillary_rct_input = widgets.Text(description='RCT:', placeholder='e.g., 7')
maxillary_filling_input = widgets.Text(description='Filling:', placeholder='e.g., 10,11')
maxillary_bridge_input = widgets.Text(description='Bridge:', placeholder='e.g., 7-9,14-16')

# Add help texts for each field
max_help = widgets.HTML("""<div style="font-size:0.8em; color:#666;">
<p><b>Bridge Format:</b> You can use either "10-12" (with hyphen) OR "10,12" (with comma).</p>
<p>You can mark a tooth as both missing and implant to show an implant at a missing tooth site.</p>
</div>""")

mandibular_missing_input = widgets.Text(description='Missing:', placeholder='e.g., 17,20')
mandibular_implant_input = widgets.Text(description='Implant:', placeholder='e.g., 18')
mandibular_extracted_input = widgets.Text(description='Extracted:', placeholder='e.g., 19')
mandibular_crown_input = widgets.Text(description='Crown:', placeholder='e.g., 30')
mandibular_rct_input = widgets.Text(description='RCT:', placeholder='e.g., 30')
mandibular_filling_input = widgets.Text(description='Filling:', placeholder='e.g., 22,23')
mandibular_bridge_input = widgets.Text(description='Bridge:', placeholder='e.g., 29-31 or 29,31')

# Add help text for mandibular tab too
mand_help = widgets.HTML("""<div style="font-size:0.8em; color:#666;">
<p><b>Bridge Format:</b> You can use either "29-31" (with hyphen) OR "29,31" (with comma).</p>
<p>You can mark a tooth as both missing and implant to show an implant at a missing tooth site.</p>
</div>""")

# Parse input text to lists of integers with validation
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
                print(f"Warning: No commas found. Interpreted '{text}' as {possible_teeth}")
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
            print("Validation errors:")
            for error in errors:
                print(f"- {error}")

        return result
    except ValueError:
        print(f"Warning: Invalid input '{text}'. Please use comma-separated numbers.")
        return []

# Parse bridge input with more flexible format options
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

        # Print errors if any
        if errors:
            print("Validation errors:")
            for error in errors:
                print(f"- {error}")

        # Print message when valid bridges are found
        if bridges:
            formatted_bridges = [f"{b[0]}-{b[1]}" for b in bridges]
            print(f"Bridges detected: {', '.join(formatted_bridges)}")

        return bridges
    except ValueError as e:
        print(f"Warning: Invalid bridge input '{text}'. Use format like '10-12' or '10,12'.")
        return []

# Function to generate the dental chart
def draw_dental_chart(maxillary_missing, maxillary_implant, maxillary_extracted, maxillary_bridges,
                      maxillary_crown, maxillary_rct, maxillary_filling,
                      mandibular_missing, mandibular_implant, mandibular_extracted, mandibular_bridges,
                      mandibular_crown, mandibular_rct, mandibular_filling,
                      output_pdf='Dental_Chart.pdf', output_jpg='Dental_Chart.jpg'):

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
    fig = plt.figure(figsize=(8, 8.5))

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

    def draw_filling(ax, x, y, color='darkorange'):
        fill_circle = plt.Circle((x, y + 0.9), 0.08, color=color, fill=False, linewidth=2)
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
                draw_filling(ax, x, y, color='darkorange')
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
    plt.savefig(output_pdf, format='pdf', bbox_inches='tight')
    plt.savefig(output_jpg, format='jpg', dpi=300, bbox_inches='tight')

    # Display the chart
    plt.show()

def on_generate_button_clicked(b):
    # Clear any previous output
    clear_output(wait=True)

    # Parse all inputs with jaw validation
    max_missing = parse_teeth_numbers(maxillary_missing_input.value, "maxillary")
    max_implant = parse_teeth_numbers(maxillary_implant_input.value, "maxillary")
    max_extracted = parse_teeth_numbers(maxillary_extracted_input.value, "maxillary")
    max_crown = parse_teeth_numbers(maxillary_crown_input.value, "maxillary")
    max_rct = parse_teeth_numbers(maxillary_rct_input.value, "maxillary")
    max_filling = parse_teeth_numbers(maxillary_filling_input.value, "maxillary")
    max_bridges = parse_bridges(maxillary_bridge_input.value, "maxillary")

    mand_missing = parse_teeth_numbers(mandibular_missing_input.value, "mandibular")
    mand_implant = parse_teeth_numbers(mandibular_implant_input.value, "mandibular")
    mand_extracted = parse_teeth_numbers(mandibular_extracted_input.value, "mandibular")
    mand_crown = parse_teeth_numbers(mandibular_crown_input.value, "mandibular")
    mand_rct = parse_teeth_numbers(mandibular_rct_input.value, "mandibular")
    mand_filling = parse_teeth_numbers(mandibular_filling_input.value, "mandibular")
    mand_bridges = parse_bridges(mandibular_bridge_input.value, "mandibular")

    # Display the form again
    display_form()

    # Generate the chart
    draw_dental_chart(
        max_missing, max_implant, max_extracted, max_bridges,
        max_crown, max_rct, max_filling,
        mand_missing, mand_implant, mand_extracted, mand_bridges,
        mand_crown, mand_rct, mand_filling
    )

    # Display the form again
    display_form()

    # Generate the chart
    draw_dental_chart(
        max_missing, max_implant, max_extracted, max_bridges,
        max_crown, max_rct, max_filling,
        mand_missing, mand_implant, mand_extracted, mand_bridges,
        mand_crown, mand_rct, mand_filling
    )

def on_reset_button_clicked(b):
    # Clear all input fields
    maxillary_missing_input.value = ''
    maxillary_implant_input.value = ''
    maxillary_extracted_input.value = ''
    maxillary_crown_input.value = ''
    maxillary_rct_input.value = ''
    maxillary_filling_input.value = ''
    maxillary_bridge_input.value = ''

    mandibular_missing_input.value = ''
    mandibular_implant_input.value = ''
    mandibular_extracted_input.value = ''
    mandibular_crown_input.value = ''
    mandibular_rct_input.value = ''
    mandibular_filling_input.value = ''
    mandibular_bridge_input.value = ''

    # Clear any previous output
    clear_output(wait=True)

    # Display the form again
    display_form()
    print("All fields have been reset.")

# Create buttons for actions
generate_button = widgets.Button(description="Generate Chart", button_style='success')
generate_button.on_click(on_generate_button_clicked)

reset_button = widgets.Button(description="Reset All Fields", button_style='danger')
reset_button.on_click(on_reset_button_clicked)

def display_form():
    # Create tabs for maxillary and mandibular
    maxillary_tab = widgets.VBox([
        widgets.HTML("<h3>Maxillary (Upper Jaw) Modifications</h3>"),
        maxillary_missing_input,
        maxillary_implant_input,
        maxillary_extracted_input,
        maxillary_crown_input,
        maxillary_rct_input,
        maxillary_filling_input,
        maxillary_bridge_input,
        max_help
    ])

    mandibular_tab = widgets.VBox([
        widgets.HTML("<h3>Mandibular (Lower Jaw) Modifications</h3>"),
        mandibular_missing_input,
        mandibular_implant_input,
        mandibular_extracted_input,
        mandibular_crown_input,
        mandibular_rct_input,
        mandibular_filling_input,
        mandibular_bridge_input,
        mand_help
    ])

    tabs = widgets.Tab(children=[maxillary_tab, mandibular_tab])
    tabs.set_title(0, 'Upper Jaw')
    tabs.set_title(1, 'Lower Jaw')

    button_row = widgets.HBox([generate_button, reset_button])

    # Display the input form
    instructions = widgets.HTML("""
    <h2>Dental Chart Generator</h2>
    <p><b>Instructions:</b></p>
    <ul>
        <li>Enter tooth numbers as comma-separated values (e.g., "1,2,5")</li>
        <li>For bridges, you can enter either:<br>
       - Two teeth separated by a hyphen (e.g., "10-12")<br>
       - Two teeth separated by a comma (e.g., "10,12")</li>
    <li>You can mark a tooth as both missing and implant to show an implant at a missing tooth site</li>
        <li>Click "Generate Chart" to create the dental chart</li>
        <li>Click "Reset All Fields" to clear all inputs</li>
    </ul>
    """)

    legend = widgets.HTML("""
    <h3>Legend:</h3>
    <ul>
        <li><span style="color:red;font-weight:bold">X</span> = Missing tooth</li>
        <li><span style="color:red;font-style:italic">Dashed outline</span> = Extracted tooth</li>
        <li><span style="color:blue">Vertical line</span> = Implant</li>
        <li><span style="color:purple">Horizontal line</span> = Crown or Bridge</li>
        <li><span style="color:saddlebrown">Vertical line in tooth</span> = Root Canal Treatment (RCT)</li>
        <li><span style="color:darkorange">Circle</span> = Filling</li>
    </ul>
    """)

    form = widgets.VBox([instructions, tabs, legend, button_row])
    display(form)

# Display the interface
display_form()
