with open('data.json', 'rb') as infile:
    raw_data = infile.read()

# Decode from UTF-16LE (adjust if needed)
decoded_data = raw_data.decode('utf-16le')

# Optionally, strip any potential BOM or extra whitespace
decoded_data = decoded_data.lstrip('\ufeff').strip()

with open('data_utf8.json', 'w', encoding='utf-8') as outfile:
    outfile.write(decoded_data)

print("Conversion complete. Check data_utf8.json for contents.")