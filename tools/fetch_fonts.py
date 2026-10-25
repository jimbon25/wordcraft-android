#!/usr/bin/env python3
import os
import sys
import urllib.request

FONTS = [
    ('Arial.ttf', 'https://raw.githubusercontent.com/ImageMagick/msttcorefonts/main/fonts/Arial.ttf'),
    ('Arial_Bold.ttf', 'https://raw.githubusercontent.com/ImageMagick/msttcorefonts/main/fonts/Arial_Bold.ttf'),
    ('Arial_Italic.ttf', 'https://raw.githubusercontent.com/ImageMagick/msttcorefonts/main/fonts/Arial_Italic.ttf'),
    ('Times_New_Roman.ttf', 'https://raw.githubusercontent.com/ImageMagick/msttcorefonts/main/fonts/Times_New_Roman.ttf'),
    ('Times_New_Roman_Bold.ttf', 'https://raw.githubusercontent.com/ImageMagick/msttcorefonts/main/fonts/Times_New_Roman_Bold.ttf'),
    ('Times_New_Roman_Italic.ttf', 'https://raw.githubusercontent.com/ImageMagick/msttcorefonts/main/fonts/Times_New_Roman_Italic.ttf'),
    ('Calibri.ttf', 'https://raw.githubusercontent.com/arjafari93/QBluePrint/master/fonts/calibri.ttf'),
    ('Calibri_Bold.ttf', 'https://raw.githubusercontent.com/arjafari93/QBluePrint/master/fonts/calibrib.ttf'),
    ('Courier_New.ttf', 'https://raw.githubusercontent.com/ImageMagick/msttcorefonts/main/fonts/Courier_New.ttf'),
    ('Courier_New_Bold.ttf', 'https://raw.githubusercontent.com/ImageMagick/msttcorefonts/main/fonts/Courier_New_Bold.ttf'),
    ('Comic_Sans_MS.ttf', 'https://raw.githubusercontent.com/ImageMagick/msttcorefonts/main/fonts/Comic_Sans_MS.ttf'),
    ('Comic_Sans_MS_Bold.ttf', 'https://raw.githubusercontent.com/ImageMagick/msttcorefonts/main/fonts/Comic_Sans_MS_Bold.ttf'),
    ('Georgia.ttf', 'https://raw.githubusercontent.com/ImageMagick/msttcorefonts/main/fonts/Georgia.ttf'),
    ('Georgia_Bold.ttf', 'https://raw.githubusercontent.com/ImageMagick/msttcorefonts/main/fonts/Georgia_Bold.ttf'),
    ('Verdana.ttf', 'https://raw.githubusercontent.com/ImageMagick/msttcorefonts/main/fonts/Verdana.ttf'),
    ('Verdana_Bold.ttf', 'https://raw.githubusercontent.com/ImageMagick/msttcorefonts/main/fonts/Verdana_Bold.ttf'),
    ('Trebuchet_MS.ttf', 'https://raw.githubusercontent.com/ImageMagick/msttcorefonts/main/fonts/Trebuchet_MS.ttf'),
    ('Trebuchet_MS_Bold.ttf', 'https://raw.githubusercontent.com/ImageMagick/msttcorefonts/main/fonts/Trebuchet_MS_Bold.ttf'),
    ('Carlito-Regular.ttf', 'https://raw.githubusercontent.com/google/fonts/main/ofl/carlito/Carlito-Regular.ttf'),
    ('Caladea-Regular.ttf', 'https://raw.githubusercontent.com/google/fonts/main/ofl/caladea/Caladea-Regular.ttf'),
    ('Roboto.ttf', 'https://raw.githubusercontent.com/google/fonts/main/ofl/roboto/Roboto%5Bwdth%2Cwght%5D.ttf'),
    ('Roboto-Italic.ttf', 'https://raw.githubusercontent.com/google/fonts/main/ofl/roboto/Roboto-Italic%5Bwdth%2Cwght%5D.ttf')
]

def main():
    if len(sys.argv) < 2:
        print("Usage: fetch_fonts.py <target_fonts_dir>")
        sys.exit(1)
    target_dir = sys.argv[1]
    os.makedirs(target_dir, exist_ok=True)

    print(f"Downloading {len(FONTS)} Office fonts to {target_dir}...")
    headers = {'User-Agent': 'Mozilla/5.0'}

    for filename, url in FONTS:
        dest = os.path.join(target_dir, filename)
        if os.path.exists(dest) and os.path.getsize(dest) > 1000:
            print(f"  [OK] {filename} (cached)")
            continue
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req) as resp:
                data = resp.read()
                with open(dest, 'wb') as f:
                    f.write(data)
            print(f"  [+] {filename} ({len(data)} bytes)")
        except Exception as e:
            print(f"  [!] Failed to download {filename}: {e}")

    print("Font pack download completed successfully!")

if __name__ == "__main__":
    main()
