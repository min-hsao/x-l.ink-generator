# x-l.ink generator
# This is a shorten URL generator for Min's URL shortener'
# 01.20.2025
# by Min-hsao Chen (w/ deepseek v3)
# version 0.0001

import requests
import qrcode
import argparse
import json
import os
import math
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw

# Define the API endpoint and your YOURLS signature
YOURLS_API_URL = "http://x-l.ink/yourls-api.php"  # Replace with your YOURLS API endpoint
YOURLS_SIGNATURE = os.environ.get("YOURLS_SIGNATURE", "YOUR_SIGNATURE_HERE")  # Replace with your YOURLS API token or set as an environment variable

class CustomQRCode(qrcode.QRCode):
    def make_image(self, fill_color="black", back_color="white", style="squares", **kwargs):
        """
        Generate QR code image with custom style
        Styles:
        - squares (default)
        - dots
        - stars
        - diamonds
        - triangles
        """
        matrix = self.get_matrix()
        qr_size = len(matrix)
        img_size = qr_size * self.box_size
        img = Image.new('RGB', (img_size, img_size), back_color)
        draw = ImageDraw.Draw(img)

        border = self.border
        data_size = qr_size - 2 * border

        def is_finder_pattern(r, c):
            # Check all three finder patterns in data area
            return (
                (border <= r < border+7 and border <= c < border+7) or        # Top-left
                (border <= r < border+7 and (qr_size-border-7) <= c < qr_size-border) or  # Top-right
                ((qr_size-border-7) <= r < qr_size-border and border <= c < border+7)     # Bottom-left
            )

        for row in range(qr_size):
            for col in range(qr_size):
                if matrix[row][col]:
                    x = col * self.box_size
                    y = row * self.box_size
                    center_x = x + self.box_size//2
                    center_y = y + self.box_size//2

                    if is_finder_pattern(row, col):
                        # Draw solid square for finder pattern
                        draw.rectangle([x, y, x+self.box_size, y+self.box_size], fill=fill_color)
                    else:
                        if style == "squares":
                            draw.rectangle([x, y, x+self.box_size, y+self.box_size], fill=fill_color)
                        elif style == "dots":
                            # Increased dot size to 70%
                            dot_size = self.box_size * 0.7
                            draw.ellipse([
                                center_x - dot_size/2,
                                center_y - dot_size/2,
                                center_x + dot_size/2,
                                center_y + dot_size/2
                            ], fill=fill_color)
                        elif style == "stars":
                            # Increased star size to 50%
                            radius = self.box_size * 0.5
                            points = []
                            for i in range(10):
                                angle = math.pi * i / 5
                                r = radius * (0.5 if i % 2 else 1)
                                points.append(center_x + r * math.sin(angle))
                                points.append(center_y - r * math.cos(angle))
                            draw.polygon(points, fill=fill_color)
                        elif style == "diamonds":
                            # Increased diamond size to 50%
                            size = self.box_size * 0.5
                            draw.polygon([
                                (center_x, center_y - size),
                                (center_x + size, center_y),
                                (center_x, center_y + size),
                                (center_x - size, center_y)
                            ], fill=fill_color)
                        elif style == "triangles":
                            size = self.box_size * 0.5
                            draw.polygon([
                                (center_x, center_y - size),
                                (center_x + size, center_y + size),
                                (center_x - size, center_y + size)
                            ], fill=fill_color)
        return img

def generate_qr_code(url, output_file, logo_file=None, style="squares"):
    print(f"\nGenerating QR code with style '{style}'...")
    error_correction = qrcode.constants.ERROR_CORRECT_H if logo_file else qrcode.constants.ERROR_CORRECT_L

    qr = CustomQRCode(
        version=1,
        error_correction=error_correction,
        box_size=24,  # Increased for better dot visibility
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", style=style)

    if logo_file and os.path.exists(logo_file):
        print("Adding logo to QR code...")
        logo = Image.open(logo_file)
        logo_size = img.size[0] // 6  # Smaller logo for better scanning
        logo = logo.resize((logo_size, logo_size), Image.LANCZOS)
        pos = ((img.size[0] - logo_size) // 2, (img.size[1] - logo_size) // 2)
        img.paste(logo, pos)

    img.save(output_file)
    print(f"QR code saved as {output_file}")

    # Display ASCII version
    print("\nASCII QR Code:")
    qr.print_ascii()
    print("\nQR structure:")
    print(f"- Size: {len(qr.get_matrix())}x{len(qr.get_matrix())} modules")
    print(f"- Finder patterns: 3 solid squares (7x7 modules each)")
    print(f"- Style: {style} for data modules")

def get_webpage_title(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string.strip() if soup.title else url
        return title
    except Exception as e:
        print(f"Warning: Failed to fetch webpage title. Using URL as title. Error: {e}")
        return url

def shorten_url(url, keyword=None, title=None):
    payload = {
        'signature': YOURLS_SIGNATURE,
        'action': 'shorturl',
        'url': url,
        'format': 'json'
    }
    if keyword:
        payload['keyword'] = keyword
    if title:
        payload['title'] = title

    response = requests.post(YOURLS_API_URL, data=payload)
    if response.status_code == 200:
        result = response.json()
        if result.get('status') == 'fail' and result.get('code') == 'error:keyword':
            print(f"Error: The keyword '{keyword}' is already in use.")
            return None
        return result
    else:
        print(f"Error: Failed to connect to YOURLS API. Status code: {response.status_code}")
        return None

def main():
    parser = argparse.ArgumentParser(
        description="Shorten a URL using your self-hosted YOURLS instance and generate a QR code.",
        epilog="Example usage:\n"
               "  python yourls_shortener.py https://www.example.com -k mykeyword -t 'Example Title' -o myqr.png -l logo.png -s stars\n"
               "  python yourls_shortener.py https://www.example.com -o qrcode.png"
    )
    parser.add_argument('url', type=str, help="The URL to shorten")
    parser.add_argument('-k', '--keyword', type=str, help="Optional custom keyword for the shortened URL", default=None)
    parser.add_argument('-t', '--title', type=str, help="Optional title for the shortened URL", default=None)
    parser.add_argument('-o', '--output_file', type=str, help="Output PNG filename for the QR code (default: qrcode.png)", default="qrcode.png")
    parser.add_argument('-l', '--logo', type=str, help="Optional logo image to center in the QR code", default=None)
    parser.add_argument('-s', '--style', choices=['squares', 'dots', 'stars', 'diamonds', 'triangles'],
                      default='squares', help="Module design style for the QR code (default: squares)")
    args = parser.parse_args()

    # If no title is provided, fetch the webpage title or use the URL
    if not args.title:
        args.title = get_webpage_title(args.url)

    result = shorten_url(args.url, args.keyword, args.title)
    if result and 'shorturl' in result:
        short_url = result['shorturl']
        print(f"Shortened URL: {short_url}")
        print(f"Title: {args.title}")
        generate_qr_code(short_url, args.output_file, args.logo, args.style)
        print("Full response from YOURLS:")
        print(json.dumps(result, indent=4))
    else:
        print("Failed to shorten the URL. Please check your YOURLS API endpoint and signature.")

if __name__ == "__main__":
    main()
