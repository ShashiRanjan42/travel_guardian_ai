import sys

file_path = r"C:\Users\GenAIDELLUCERNAUSR49\Desktop\app2\travel_guardian_ai\frontend\src\components\CustomerMMTView.jsx"

with open(file_path, "r", encoding="utf-8") as f:
    text = f.read()

# Try to reverse the mojibake
try:
    text = text.replace('\ufeff', '')
    original_bytes = text.encode('windows-1252', errors='ignore')
    fixed_text = original_bytes.decode('utf-8', errors='ignore')
except Exception as e:
    print(f"Failed to reverse mojibake: {e}")
    sys.exit(1)

# Also fix the missing quotes on lines 196 and 204
# In fixed_text it should be: setBookingNotice(✅ Protected Confirmed & Saved to Profile! ( → ));
fixed_text = fixed_text.replace(
    "setBookingNotice(✅ Protected Confirmed & Saved to Profile! ( → ));",
    "setBookingNotice('✅ Protected Confirmed & Saved to Profile! ( → )');"
)
fixed_text = fixed_text.replace(
    "setBookingNotice(✅ Protected Confirmed & Saved to Profile!);",
    "setBookingNotice('✅ Protected Confirmed & Saved to Profile!');"
)
# And the rank option
fixed_text = fixed_text.replace(
    "label: ⚡ Confirm & Book",
    "label: '⚡ Confirm & Book'"
)
# Let's just fix any missing quotes around ✅ and ⚡ inside setBookingNotice
import re
fixed_text = re.sub(r"setBookingNotice\((✅.*?)\);", r'setBookingNotice(`\1`);', fixed_text)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(fixed_text)

print("File encoding restored!")
