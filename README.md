# Image-Renamer-Drag-Drop-UI-
A tiny cross‑platform desktop app to bulk‑rename images for product pages. Drop images, enter a part number, and export copies as 1234_ImageName1.jpg, 1234_ImageName1.png, … while preserving original file types.

# ✨ Features
Drag & Drop (via tkinterdnd2) or manual file picker
Keeps original extensions (.jpg, .png, .webp, .tif, .bmp, .heic)
Ordered numbering in the exact order shown (Sort A→Z / Move Up / Move Down)
Customizable prefix (default ImageName)
Choose start number and zero‑padding
Preview‑only mode
Safe exports with auto -1, -2, … when a filename already exists
No external image libraries required for simple copy/rename
Typical output
1234_ImageName1.jpg, 1234_ImageName2.png, 1234_ImageName3.webp

# 🧰 Requirements
Python 3.8+
Tkinter (bundled with most Python distributions)
Optional: tkinterdnd2 for native drag & drop
pip install tkinterdnd2
If drag & drop isn’t available on your system, you can always use Add Images… to browse.

# 🚀 Quick Start
Clone
git clone https://github.com/<your-username>/image-renamer-ui.git
cd image-renamer-ui
(Optional) Create a venv
python -m venv .venv

# Windows
.venv\\Scripts\\activate

# macOS/Linux
source .venv/bin/activate
Install deps
pip install -r requirements.txt
Run
python image_renamer_ui.py

# 🖱️ Usage
Drop image files in the left pane (or click Add Images…).
Enter your Part Number (digits only).
Optionally change Prefix, Start #, and Zero‑pad width.
Pick an Output folder.
Click Generate Output.
Numbering follows the list order. Use Sort A→Z or Move Up/Down before exporting to control sequence.

# 📦 Supported Formats
.jpg, .jpeg, .png, .webp, .bmp, .tif, .tiff, .heic
Files are copied and renamed as‑is (no transcoding). HEIC is not decoded—just renamed.

# 🧩 Troubleshooting
Drag & Drop doesn’t work → Ensure tkinterdnd2 is installed. Some Linux desktop environments need additional DnD integration; use Add Images… as a fallback.
Tkinter missing on Linux → Install your distro’s Tk package (e.g., sudo apt install python3-tk).
App crashes on macOS Gatekeeper → Run from Terminal the first time: python image_renamer_ui.py.
Filenames collide → App appends -1, -2, … automatically.

# 🧪 Dev Notes
No external heavy imaging libs; we just read bytes and write bytes.
UI is pure tkinter with optional tkinterdnd2.
If you want to always export as .jpg, look for _build_name and normalize ext = ".jpg" (or expose as a dropdown).
🗂️ Project Layout
image-renamer-ui/
├─ image_renamer_ui.py
├─ requirements.txt
├─ README.md
├─ LICENSE
├─ .gitignore
└─ docs/
   └─ screenshot.png 
   
# 🤝 Contributing
Fork the repo and create a feature branch: git checkout -b feat/my-improvement
Run and test locally.
Open a PR describing your changes and screenshots (if UI related).
