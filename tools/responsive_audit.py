import re
import glob
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def read(path):
    return Path(path).read_text(encoding='utf-8')

results = []

# Check viewport meta
html_files = glob.glob(str(ROOT / 'templates' / '*.html')) + glob.glob(str(ROOT / 'templates' / 'admin' / '*.html'))
viewport_ok = True
missing = []
for f in html_files:
    txt = read(f)
    if '<meta name="viewport"' not in txt:
        missing.append(f.replace(str(ROOT) + '/', ''))

results.append(("meta viewport present", len(missing) == 0, missing))

# Check responsive @media queries in main CSS
css_files = glob.glob(str(ROOT / 'static' / 'css' / '*.css'))
media_found = {}
for f in css_files:
    txt = read(f)
    media_found[f.replace(str(ROOT) + '/', '')] = {
        'has_max_768': re.search(r"@media\s*\(max-width:\s*768px\)", txt) is not None,
        'has_max_480': re.search(r"@media\s*\(max-width:\s*480px\)", txt) is not None,
        'has_min_1200': re.search(r"@media\s*\(min-width:\s*1200px\)", txt) is not None,
    }

results.append(("media queries present in CSS files", any(v['has_max_768'] for v in media_found.values()), media_found))

# Check for mobile nav and hamburger
index_html = read(ROOT / 'templates' / 'index.html')
mobile_nav_ok = ("nb-hamburger" in index_html) and ("nb-mobile-menu" in index_html)
results.append(("mobile hamburger & menu in templates/index.html", mobile_nav_ok, None))

# Check modals responsive rules exist
style_css = read(ROOT / 'static' / 'css' / 'style.css')
modal_mobile_ok = re.search(r"@media\s*\(max-width:\s*768px\)[\s\S]*?\.modal\s*\{", style_css) is not None
results.append(("modal responsive rules in style.css", modal_mobile_ok, None))

# Check cards list responsive rule
cards_responsive = re.search(r"@media\s*\(max-width:\s*768px\)[\s\S]*?\.nb-cards-list\s*\{[\s\S]*?grid-template-columns:\s*1fr", style_css) is not None
results.append((".nb-cards-list responsive one-column", cards_responsive, None))

# Check hero responsive rules
hero_mobile = re.search(r"@media\s*\(max-width:\s*768px\)[\s\S]*?\.nb-hero-img", style_css) is not None
results.append(("hero mobile rules", hero_mobile, None))

# Check admin css for responsive adjustments
admin_css = read(ROOT / 'static' / 'css' / 'admin.css')
admin_media = re.search(r"@media\s*\(max-width:\s*768px\)", admin_css) is not None
results.append(("admin.css has media queries", admin_media, None))

# Check images use object-fit rules
object_fit_ok = re.search(r"object-fit:\s*(cover|contain)", style_css) is not None
results.append(("object-fit on images present", object_fit_ok, None))

# Check touch target sizes: presence of .btn padding >= 10px in css
btn_rule = re.search(r"\.btn\s*\{[\s\S]*?padding:\s*(\d+)px\s*(?:\d+px)?", style_css)
btn_padding = int(btn_rule.group(1)) if btn_rule else None
results.append(("button has adequate padding (>=10px)", btn_padding is not None and btn_padding >= 10, btn_padding))

# Print summary
print("Responsiveness Audit Report\n===========================")
for desc, ok, details in results:
    status = "OK" if ok else "MISSING/NEEDS WORK"
    print(f"- {desc}: {status}")
    if details:
        print("  Details:")
        if isinstance(details, dict):
            for k, v in details.items():
                print(f"    {k}: {v}")
        else:
            print(f"    {details}")

# Recommendations
print("\nRecommendations:")
if not admin_media:
    print("- Add admin.css mobile media queries to make admin tables/forms more usable on narrow screens.")
if not cards_responsive:
    print("- Ensure program card grid collapses to one column on small screens (we expect .nb-cards-list to be 1fr).")
if not modal_mobile_ok:
    print("- Make modal windows full width and scrollable on mobile (max-height, overflow-y: auto).")
if not object_fit_ok:
    print("- Add object-fit: cover to card images to prevent distortion on variable sizes.")
print("- Manual visual QA recommended across iPhone (375px), small Android (360px), iPad (768px/1024px) and desktop widths.")


if __name__ == '__main__':
    pass
