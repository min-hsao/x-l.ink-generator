# x-l.ink generator

A Python script to shorten a URL using a self-hosted YOURLS instance and generate a QR code.

## Dependencies

- `requests`
- `qrcode`
- `Pillow`
- `beautifulsoup4`

Install them using:
```bash
pip install requests qrcode Pillow beautifulsoup4
```

## Setup

1.  **YOURLS API Token:**
    This script requires a YOURLS API token. You can either:
    -   Replace `"YOUR_SIGNATURE_HERE"` in the script with your actual token.
    -   Set an environment variable named `YOURLS_SIGNATURE` with your token.

2.  **YOURLS API Endpoint:**
    Update the `YOURLS_API_URL` variable in the script to your YOURLS API endpoint.
