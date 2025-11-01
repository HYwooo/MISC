import textwrap
import pandas as pd # Add pandas import

# Define the path to the Excel file
EXCEL_FILE_PATH = 'reg.xlsx'

# Function to load register definitions from Excel
def load_registers_from_excel(file_path):
    """Loads register definitions from the specified Excel file."""
    try:
        # Read the entire sheet first to get register info from row 1
        df_full = pd.read_excel(file_path, sheet_name=0, header=None, dtype=str)
        df_full.fillna('', inplace=True)

        # --- Extract Register Info from Row 1 (adjust indices based on actual Excel) ---
        # Assuming: Col B (index 1) = Full Name, Col C (index 2) = Abbreviation (used as name), Col D (index 3) = Offset
        reg_full_name = df_full.iloc[0, 1] if df_full.shape[1] > 1 else 'Unknown Register'
        reg_name = df_full.iloc[0, 2] if df_full.shape[1] > 2 else 'REG_NAME_MISSING'
        reg_offset = df_full.iloc[0, 3] if df_full.shape[1] > 3 else '0x0000'
        reg_description = f"{reg_full_name} ({reg_name})"

        # Read the sheet again, this time using row 2 (index 1) as header for fields
        df_fields = pd.read_excel(file_path, sheet_name=0, header=1, dtype=str) # Header is row 2 (0-indexed 1)
        print("Excel Field Columns:", df_fields.columns.tolist()) # Print column names for debugging
        df_fields.fillna('', inplace=True)

    except FileNotFoundError:
        print(f"Error: Excel file not found at {file_path}")
        return []
    except Exception as e:
        print(f"Error reading Excel file {file_path}: {e}")
        return []

    registers_dict = {}
    if reg_name and reg_name != 'REG_NAME_MISSING':
        registers_dict[reg_name] = {
            "name": reg_name,
            "offset": reg_offset,
            "description": reg_description,
            "fields": []
        }

        # Map Chinese headers to expected keys (adjust if needed based on print output)
        header_map = {
            '位': 'bits',
            '字段名': 'name',
            '默认值': 'default',
            # '访问类型': 'access', # Assuming RW if not present or using hardcoded value later
            '描述': 'description'
        }

        # Iterate through field rows
        for index, row in df_fields.iterrows():
            # Check if the row seems valid (e.g., has a field name)
            field_name = row.get(header_map.get('字段名', '字段名'), '') # Use mapped key or original if map fails
            if not field_name or field_name.lower() == 'reserved': # Skip empty or reserved rows
                continue

            # Extract field data using mapped headers
            bits = row.get(header_map.get('位', '位'), '')
            default_val = row.get(header_map.get('默认值', '默认值'), '0') # Default to '0' if missing
            description = row.get(header_map.get('描述', '描述'), '')
            access = row.get(header_map.get('访问类型', '访问类型'), 'RW') # Default to RW if missing

            # Handle bit range format difference (e.g., '7:6' vs '[7:6]')
            if ':' in bits and not bits.startswith('['):
                bits = f"[{bits}]"
            elif bits.isdigit() and not bits.startswith('['):
                 bits = f"[{bits}]"

            # Convert default to string, handling potential float conversion by pandas
            if isinstance(default_val, float):
                 if default_val.is_integer():
                     default_val = str(int(default_val))
                 else:
                     default_val = str(default_val)
            elif not isinstance(default_val, str):
                 default_val = str(default_val)
            # Ensure default is a valid integer representation if possible, else keep as string
            try:
                # Attempt to convert to handle hex/binary if needed, but store as string
                int(default_val, 0)
            except ValueError:
                 # If conversion fails (e.g., 'N/A'), keep original string or default to '0'
                 if default_val.strip() == '' or default_val.upper() == 'N/A':
                     default_val = '0'
                 # Keep original string if it's not empty/NA but not a number

            registers_dict[reg_name]['fields'].append({
                "name": field_name.replace(' ', '_').upper(), # Convert to standard Verilog name format
                "bits": bits,
                "access": access if access else 'RW', # Ensure access is set, default RW
                "default": default_val,
                "description": description
            })
    else:
        print("Could not determine register name from Excel file.")


    return list(registers_dict.values())

# --- REMOVE HARDCODED LIST ---
# registers = [
#     {
#         "name": "BCR",
#         "offset": "0x0000",
#         "description": "Bus Characteristics Register",
#         "fields": [
#             # ... fields ...
#         ]
#     }
# ]
# --- END REMOVE HARDCODED LIST ---

# Define the register structure (inferred from reg.sv)
# In a real scenario, this would ideally come from a more structured source like a CSV, JSON, or YAML file.
# registers = [
#     {
#         "name": "BCR",
#         "offset": "0x0000",
#         "description": "Bus Characteristics Register",
#         "fields": [
#             # name: Field name (used for output port)
#             # bits: Bit range string (e.g., "[7:6]" or "[5]")
#             # access: Access type (RW, RO, WO) - Assuming RW based on example
#             # default: Default value for the field (as string)
#             # description: Field description (optional, for comments)
#             {"name": "DEVICE_ROLE",             "bits": "[7:6]", "access": "RW", "default": "0", "description": "Device Role"},
#             {"name": "ADVANCED_CAPABILITIES",   "bits": "[5]",   "access": "RW", "default": "0", "description": "Advanced Capabilities support"},
#             {"name": "VIRTUAL_TARGET_SUPPORT",  "bits": "[4]",   "access": "RW", "default": "0", "description": "Virtual Target support"},
#             {"name": "OFFLINE_CAPABLE",         "bits": "[3]",   "access": "RW", "default": "0", "description": "Offline Capable"},
#             {"name": "IBI_PAYLOAD",             "bits": "[2]",   "access": "RW", "default": "0", "description": "Has IBI Payload"},
#             {"name": "IBI_REQUEST_CAPABLE",     "bits": "[1]",   "access": "RW", "default": "0", "description": "IBI Request Capable"},
#             {"name": "MAX_DATA_SPEED_LIMITATION", "bits": "[0]", "access": "RW", "default": "0", "description": "Max Data Speed Limitation"}
#             # Bits 31:8 are reserved
#         ]
#     }
#     # Add more register definitions here if needed
# ]

def parse_bits(bit_str):
    """Parses bit string like '[7:6]' or '[5]' into (msb, lsb)."""
    bit_str = bit_str.strip('[]')
    if ':' in bit_str:
        msb, lsb = map(int, bit_str.split(':'))
        return msb, lsb
    else:
        bit = int(bit_str)
        return bit, bit

def get_bit_width(msb, lsb):
    """Calculates the width from msb and lsb."""
    return msb - lsb + 1

def generate_sv_code(register_list):
    """Generates the SystemVerilog code based on the register list."""
    sv_code = []

    # --- Module Definition ---
    sv_code.append("module reg (")
    sv_code.append("    // Clock and Reset")
    sv_code.append("    input  logic        i_clk,")
    sv_code.append("    input  logic        i_rst_n,")
    sv_code.append("")
    sv_code.append("    // Bus Interface")
    sv_code.append("    input  logic        i_write,")
    sv_code.append("    input  logic        i_read,")
    sv_code.append("    input  logic [31:0] i_addr,")
    sv_code.append("    input  logic [31:0] i_wdata,")
    sv_code.append("    output logic [31:0] o_rdata,")
    sv_code.append("")

    # --- Register Field Outputs ---
    output_ports = []
    for reg in register_list:
        reg_name_upper = reg['name'].upper()
        output_ports.append(f"    // Register Field Outputs ({reg_name_upper} - {reg['description']})")
        for field in reg['fields']:
            field_name_lower = field['name'].lower()
            access_prefix = field['access'].lower() # e.g., 'rw'
            port_name = f"o_{access_prefix}_{field_name_lower}"
            msb, lsb = parse_bits(field['bits'])
            width = get_bit_width(msb, lsb)
            type_str = f"logic [{width-1}:0]" if width > 1 else "logic       "
            output_ports.append(f"    output {type_str}  {port_name},")

    # Remove comma from the last port
    if output_ports:
        last_port_line = output_ports.pop()
        output_ports.append(last_port_line.rstrip(','))

    sv_code.extend(output_ports)
    sv_code.append(");")
    sv_code.append("")

    # --- Register Definitions ---
    sv_code.append("//--------------------------------------------------------------------------")
    sv_code.append("// Register Definitions")
    sv_code.append("//--------------------------------------------------------------------------")
    sv_code.append("")

    internal_regs = []
    write_enables = []
    for reg in register_list:
        reg_name_upper = reg['name'].upper()
        reg_name_lower = reg['name'].lower()
        sv_code.append(f"// {reg['description']} ({reg_name_upper}) @ {reg['offset']}")
        sv_code.append(f"localparam {reg_name_upper}_ADDR       = 32'h{reg['offset'].lstrip('0x')};")

        # Calculate VALID_BIT and DEFAULT based on fields
        valid_mask = 0
        default_val = 0
        max_bit = 0
        for field in reg['fields']:
            msb, lsb = parse_bits(field['bits'])
            max_bit = max(max_bit, msb)
            width = get_bit_width(msb, lsb)
            # Create mask for this field
            field_mask = ((1 << width) - 1) << lsb
            valid_mask |= field_mask
            # Add default value for this field
            field_default = int(field['default'], 0) # Handles '0', '0x...', '0b...'
            default_val |= (field_default << lsb)

        sv_code.append(f"localparam {reg_name_upper}_VALID_BIT  = 32'h{valid_mask:08x};  // [{max_bit}:0] valid bits") # Assuming max bit defines range
        sv_code.append(f"localparam {reg_name_upper}_DEFAULT    = 32'h{default_val:08x};")
        sv_code.append("")
        internal_regs.append(f"logic [31:0] r_{reg_name_lower};")
        write_enables.append(f"logic        w_{reg_name_lower}_wr;")

    sv_code.extend(internal_regs)
    sv_code.extend(write_enables)
    sv_code.append("")

    # --- Register Write Logic ---
    sv_code.append("//--------------------------------------------------------------------------")
    sv_code.append("// Register Write Logic")
    sv_code.append("//--------------------------------------------------------------------------")
    sv_code.append("")
    sv_code.append("always_ff @(posedge i_clk or negedge i_rst_n) begin")
    sv_code.append("    if (~i_rst_n) begin")
    for reg in register_list:
        reg_name_upper = reg['name'].upper()
        reg_name_lower = reg['name'].lower()
        sv_code.append(f"        // {reg['description']} ({reg_name_upper})")
        sv_code.append(f"        r_{reg_name_lower} <= {reg_name_upper}_DEFAULT;")
    sv_code.append("    end else begin")
    for reg in register_list:
        reg_name_upper = reg['name'].upper()
        reg_name_lower = reg['name'].lower()
        sv_code.append(f"        // {reg['description']} ({reg_name_upper})")
        sv_code.append(f"        if (w_{reg_name_lower}_wr) begin")
        sv_code.append(f"            r_{reg_name_lower} <= i_wdata & {reg_name_upper}_VALID_BIT;")
        sv_code.append(f"        end")
        # Add 'else if' for other registers if implementing write priority
        # Add 'else begin r_xxx <= r_xxx; end' if registers should retain value when not written
    sv_code.append("    end")
    sv_code.append("end")
    sv_code.append("")

    # --- Combinational Logic ---
    sv_code.append("//--------------------------------------------------------------------------")
    sv_code.append("// Combinational Logic (Write Enables and Output Assignments)")
    sv_code.append("//--------------------------------------------------------------------------")
    sv_code.append("")
    sv_code.append("always_comb begin : REG_REGION")
    sv_code.append("    // Default assignments")
    for reg in register_list:
        reg_name_lower = reg['name'].lower()
        sv_code.append(f"    w_{reg_name_lower}_wr = 1'b0;")
    sv_code.append("")

    # Write enable generation
    for reg in register_list:
        reg_name_upper = reg['name'].upper()
        reg_name_lower = reg['name'].lower()
        sv_code.append(f"    // {reg['description']} ({reg_name_upper})")
        sv_code.append(f"    w_{reg_name_lower}_wr = i_write & (i_addr == {reg_name_upper}_ADDR);")
        sv_code.append("")

    # Output assignments from internal registers
    for reg in register_list:
        reg_name_lower = reg['name'].lower()
        for field in reg['fields']:
            field_name_lower = field['name'].lower()
            access_prefix = field['access'].lower()
            port_name = f"o_{access_prefix}_{field_name_lower}"
            bits = field['bits']
            # Adjust spacing for alignment
            port_name_padded = port_name.ljust(30)
            sv_code.append(f"    {port_name_padded} = r_{reg_name_lower}{bits};")

    sv_code.append("")
    sv_code.append("end")
    sv_code.append("")

    # --- Register Read Logic ---
    sv_code.append("//--------------------------------------------------------------------------")
    sv_code.append("// Register Read Logic")
    sv_code.append("//--------------------------------------------------------------------------")
    sv_code.append("")
    sv_code.append("always_ff @(posedge i_clk or negedge i_rst_n) begin : READ_REG")
    sv_code.append("    if (~i_rst_n) begin")
    sv_code.append("        o_rdata <= 32'd0;")
    sv_code.append("    end else if (i_read) begin")
    sv_code.append("        case (i_addr)")
    for reg in register_list:
        reg_name_upper = reg['name'].upper()
        reg_name_lower = reg['name'].lower()
        sv_code.append(f"            {reg_name_upper}_ADDR: o_rdata <= r_{reg_name_lower};")
    sv_code.append("            default:  o_rdata <= 32'd0; // Default read value for undefined addresses")
    sv_code.append("        endcase")
    sv_code.append("    end else begin")
    sv_code.append("        // Keep the last read value if not reading")
    sv_code.append("        // Alternatively, could assign 0: o_rdata <= 32'd0;")
    sv_code.append("        o_rdata <= o_rdata;")
    sv_code.append("    end")
    sv_code.append("end")
    sv_code.append("")
    sv_code.append("endmodule")

    return "\n".join(sv_code)

if __name__ == "__main__":
    # Load registers from Excel first
    registers = load_registers_from_excel(EXCEL_FILE_PATH)

    if not registers:
        print("No register data loaded. Exiting.")
    else:
        # --- Print loaded structure for verification ---
        print("Register data loaded successfully. Structure:")
        import json
        print(json.dumps(registers, indent=2, ensure_ascii=False)) # Use ensure_ascii=False for Chinese chars

        # --- Generate the code ---
        generated_code = generate_sv_code(registers)

        # Option 1: Print to console
        # print("\n--- Generated SV Code ---")
        # print(generated_code)

        # Option 2: Write to file
        output_filename = "reg_generated.sv"
        try:
            with open(output_filename, "w", encoding='utf-8') as f: # Use utf-8 encoding
                f.write(generated_code)
            print(f"Successfully generated SystemVerilog code to {output_filename} based on {EXCEL_FILE_PATH}")
        except IOError as e:
            print(f"Error writing to file {output_filename}: {e}")