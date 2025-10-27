#!/usr/bin/env python3
"""
Image Renamer – Drag & Drop UI
---------------------------------
• Drop image files into the app (JPG, JPEG, PNG, WEBP, BMP, TIFF, HEIC*)
• Enter a part number (e.g., 1234)
• Exports renamed copies to: <PartNumber>_ImageName<index>.<ext>
  Example: 1234_ImageName1.jpg, 1234_ImageName2.jpg, ...

Notes:
- *HEIC files are copied/renamed as-is (no decoding). Preview/thumbnail is not required.
- Drag & drop uses tkinterdnd2 if available. Otherwise, use “Add Images…” to browse.
- File order determines numbering. Use Move Up/Down or Sort A→Z before exporting.
- If the destination filename exists, a -1, -2, … suffix is added before the extension.
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# -------- Drag & Drop availability --------
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DND_AVAILABLE = True
except Exception:
    DND_AVAILABLE = False

# -------- Config --------
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff", ".heic"}
DEFAULT_PREFIX = "ImageName"

# -------- Utils --------
def is_image(path: str) -> bool:
    return os.path.isfile(path) and os.path.splitext(path)[1].lower() in IMAGE_EXTS

def uniquify_path(path: str) -> str:
    """Append -1, -2, … if path already exists."""
    if not os.path.exists(path):
        return path
    root, ext = os.path.splitext(path)
    i = 1
    while True:
        cand = f"{root}-{i}{ext}"
        if not os.path.exists(cand):
            return cand
        i += 1

def normalize_dnd_paths(data: str) -> list[str]:
    """Parse tk DND payload with braces and spaces."""
    items, token, in_brace = [], "", False
    for ch in data:
        if ch == "{" and not in_brace:
            in_brace, token = True, ""
        elif ch == "}" and in_brace:
            in_brace = False
            items.append(token)
            token = ""
        elif ch == " " and not in_brace:
            if token:
                items.append(token)
                token = ""
        else:
            token += ch
    if token:
        items.append(token)
    return items

# -------- App --------
class ImageRenamerApp(TkinterDnD.Tk if DND_AVAILABLE else tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Image Renamer – Drag & Drop")
        self.geometry("920x560")
        self.minsize(860, 520)
        self.configure(padx=16, pady=16)

        self.files: list[str] = []
        self.output_dir: str | None = None

        self._build_ui()

    # ---------- UI ----------
    def _build_ui(self):
        title = ttk.Label(self, text="Image Renamer", font=("Segoe UI", 18, "bold"))
        subtitle = ttk.Label(self, text="Drop images, enter a part number, export renamed copies", foreground="#666")
        title.grid(row=0, column=0, sticky="w")
        subtitle.grid(row=1, column=0, sticky="w", pady=(0, 10))

        main = ttk.Frame(self)
        main.grid(row=2, column=0, sticky="nsew")
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        main.grid_columnconfigure(0, weight=3)
        main.grid_columnconfigure(1, weight=2)
        main.grid_rowconfigure(1, weight=1)

        # Left: Drop zone + list
        drop_lbl = ttk.Label(main, text="1) Drop image files here", font=("Segoe UI", 11, "bold"))
        drop_lbl.grid(row=0, column=0, sticky="w")

        drop_style = {"relief": tk.SOLID, "borderwidth": 2, "padding": 10}
        self.drop_area = ttk.Frame(main, **drop_style)
        self.drop_area.grid(row=1, column=0, sticky="nsew", padx=(0, 12))
        self.drop_area.grid_rowconfigure(0, weight=1)
        self.drop_area.grid_columnconfigure(0, weight=1)

        hint = ("Drag & drop image files anywhere in this box\n"
                "or click the button below to browse…")
        self.drop_hint = ttk.Label(self.drop_area, text=hint, anchor="center", justify="center", foreground="#666")
        self.drop_hint.grid(row=0, column=0, sticky="nsew")

        if DND_AVAILABLE:
            self.drop_area.drop_target_register(DND_FILES)
            self.drop_area.dnd_bind("<<Drop>>", self._on_drop)

        # File list
        self.file_list = tk.Listbox(main, height=12, activestyle='dotbox')
        self.file_list.grid(row=2, column=0, sticky="nsew", pady=(8, 0))

        btns = ttk.Frame(main)
        btns.grid(row=3, column=0, sticky="w", pady=(8, 0))
        ttk.Button(btns, text="Add Images…", command=self._add_files_dialog).grid(row=0, column=0, padx=(0, 8))
        ttk.Button(btns, text="Remove Selected", command=self._remove_selected).grid(row=0, column=1, padx=(0, 8))
        ttk.Button(btns, text="Clear List", command=self._clear_list).grid(row=0, column=2, padx=(0, 8))
        ttk.Button(btns, text="Sort A→Z", command=self._sort_az).grid(row=0, column=3, padx=(0, 8))
        ttk.Button(btns, text="Move Up", command=lambda: self._move_selected(-1)).grid(row=0, column=4, padx=(0, 8))
        ttk.Button(btns, text="Move Down", command=lambda: self._move_selected(1)).grid(row=0, column=5)

        # Right panel
        right = ttk.Frame(main)
        right.grid(row=1, column=1, rowspan=3, sticky="nsew")
        right.grid_columnconfigure(1, weight=1)

        # Part number
        ttk.Label(right, text="2) Enter Part Number", font=("Segoe UI", 11, "bold")).grid(row=0, column=0, columnspan=2, sticky="w")
        ttk.Label(right, text="Part Number:").grid(row=1, column=0, sticky="w", pady=(6, 0))
        self.part_var = tk.StringVar()
        self.part_entry = ttk.Entry(right, textvariable=self.part_var)
        self.part_entry.grid(row=1, column=1, sticky="ew", pady=(6, 0))

        # Prefix (fixed to DetailedProductView but editable if you want)
        ttk.Label(right, text="File Prefix (optional)").grid(row=2, column=0, sticky="w", pady=(10, 0))
        self.prefix_var = tk.StringVar(value=DEFAULT_PREFIX)
        ttk.Entry(right, textvariable=self.prefix_var).grid(row=2, column=1, sticky="ew", pady=(10, 0))

        # Numbering options
        opts = ttk.Frame(right)
        opts.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(12, 0))
        ttk.Label(opts, text="Start #:").grid(row=0, column=0, sticky="w")
        self.start_idx_var = tk.IntVar(value=1)
        ttk.Spinbox(opts, from_=1, to=9999, textvariable=self.start_idx_var, width=6).grid(row=0, column=1, sticky="w", padx=(6, 12))

        ttk.Label(opts, text="Zero-pad width:").grid(row=0, column=2, sticky="w")
        self.pad_width_var = tk.IntVar(value=0)  # 0 = no padding (1,2,3…)
        ttk.Spinbox(opts, from_=0, to=6, textvariable=self.pad_width_var, width=6).grid(row=0, column=3, sticky="w", padx=(6, 0))

        # Output folder
        ttk.Label(right, text="3) Choose Output Folder", font=("Segoe UI", 11, "bold")).grid(row=4, column=0, columnspan=2, sticky="w", pady=(14, 0))
        self.output_dir_var = tk.StringVar(value="")
        out_row = ttk.Frame(right)
        out_row.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(6, 0))
        out_row.grid_columnconfigure(0, weight=1)
        ttk.Entry(out_row, textvariable=self.output_dir_var, state="readonly").grid(row=0, column=0, sticky="ew")
        ttk.Button(out_row, text="Browse…", command=self._choose_output_dir).grid(row=0, column=1, padx=(8, 0))

        # Options
        ttk.Label(right, text="Options", font=("Segoe UI", 11, "bold")).grid(row=6, column=0, columnspan=2, sticky="w", pady=(14, 0))
        self.preview_only = tk.BooleanVar(value=False)
        ttk.Checkbutton(right, text="Preview only (no file copy)", variable=self.preview_only).grid(row=7, column=0, columnspan=2, sticky="w")

        # Run/Log
        ttk.Label(right, text="4) Generate", font=("Segoe UI", 11, "bold")).grid(row=8, column=0, columnspan=2, sticky="w", pady=(14, 0))
        run_row = ttk.Frame(right)
        run_row.grid(row=9, column=0, columnspan=2, sticky="ew", pady=(6, 0))
        ttk.Button(run_row, text="Generate Output", command=self._generate).grid(row=0, column=0)

        ttk.Label(right, text="Activity Log:").grid(row=10, column=0, columnspan=2, sticky="w", pady=(12, 0))
        self.log = tk.Text(right, height=12, wrap="word", state="disabled")
        self.log.grid(row=11, column=0, columnspan=2, sticky="nsew")
        right.grid_rowconfigure(11, weight=1)

        footer = ttk.Label(self, text="Tip: reorder items before exporting to control numbering.", foreground="#777")
        footer.grid(row=3, column=0, sticky="we", pady=(10, 0))

    # ---------- Actions ----------
    def _log(self, msg: str):
        self.log.configure(state="normal")
        self.log.insert("end", msg + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def _on_drop(self, event):
        paths = normalize_dnd_paths(event.data)
        self._add_files(paths)

    def _add_files_dialog(self):
        exts = [
            ("Images", "*.jpg *.jpeg *.png *.webp *.bmp *.tif *.tiff *.heic"),
            ("All files", "*.*"),
        ]
        paths = filedialog.askopenfilenames(title="Select image files", filetypes=exts)
        if paths:
            self._add_files(paths)

    def _add_files(self, paths: list[str]):
        added = 0
        for p in paths:
            if is_image(p) and p not in self.files:
                self.files.append(p)
                self.file_list.insert("end", p)
                added += 1
        if added:
            self._log(f"Added {added} image(s).")
        else:
            self._log("No new images added.")

    def _remove_selected(self):
        sel = list(self.file_list.curselection())
        if not sel:
            return
        sel.reverse()
        for idx in sel:
            path = self.file_list.get(idx)
            self.file_list.delete(idx)
            if path in self.files:
                self.files.remove(path)
        self._log("Removed selected item(s).")

    def _clear_list(self):
        self.file_list.delete(0, "end")
        self.files.clear()
        self._log("Cleared file list.")

    def _sort_az(self):
        self.files.sort(key=lambda p: os.path.basename(p).lower())
        self.file_list.delete(0, "end")
        for p in self.files:
            self.file_list.insert("end", p)
        self._log("Sorted A→Z.")

    def _move_selected(self, direction: int):
        sel = self.file_list.curselection()
        if not sel:
            return
        idx = sel[0]
        new_idx = idx + direction
        if new_idx < 0 or new_idx >= self.file_list.size():
            return
        # Swap in listbox
        cur_val = self.file_list.get(idx)
        swap_val = self.file_list.get(new_idx)
        self.file_list.delete(new_idx)
        self.file_list.insert(new_idx, cur_val)
        self.file_list.delete(idx)
        self.file_list.insert(idx, swap_val)
        # Swap in backing list
        self.files[idx], self.files[new_idx] = self.files[new_idx], self.files[idx]
        self.file_list.selection_clear(0, "end")
        self.file_list.selection_set(new_idx)
        self.file_list.activate(new_idx)

    def _choose_output_dir(self):
        d = filedialog.askdirectory(title="Choose output folder")
        if d:
            self.output_dir = d
            self.output_dir_var.set(d)

    def _validate_part(self, part: str) -> bool:
        part = part.strip()
        return bool(part) and part.isdigit()

    def _build_name(self, part: str, idx: int, ext: str, prefix: str, pad_width: int) -> str:
        num_str = str(idx).zfill(pad_width) if pad_width > 0 else str(idx)
        return f"{part}_{prefix}{num_str}{ext}"

    def _generate(self):
        part = self.part_var.get().strip()
        if not self._validate_part(part):
            messagebox.showerror("Invalid Part Number", "Please enter a numeric part number (digits only).")
            self.part_entry.focus_set()
            return

        if not self.files:
            messagebox.showwarning("No Images", "Please add one or more image files.")
            return

        if not self.preview_only.get():
            if not self.output_dir:
                messagebox.showwarning("No Output Folder", "Please choose an output folder.")
                return

        prefix = (self.prefix_var.get().strip() or DEFAULT_PREFIX)
        start_idx = max(1, int(self.start_idx_var.get()))
        pad_width = max(0, int(self.pad_width_var.get()))

        exported = 0
        preview_rows = []

        idx = start_idx
        for src in self.files:
            ext = os.path.splitext(src)[1]
            out_name = self._build_name(part, idx, ext, prefix, pad_width)
            idx += 1

            if self.preview_only.get():
                preview_rows.append((os.path.basename(src), out_name))
                self._log(f"Preview: {os.path.basename(src)}  →  {out_name}")
            else:
                dst = os.path.join(self.output_dir, out_name)
                dst = uniquify_path(dst)
                try:
                    with open(src, "rb") as rf, open(dst, "wb") as wf:
                        wf.write(rf.read())
                    self._log(f"Saved: {os.path.basename(src)}  →  {os.path.basename(dst)}")
                    exported += 1
                except Exception as e:
                    self._log(f"ERROR saving {src}: {e}")

        if self.preview_only.get():
            self._log("\nPreview complete. No files were written.")
        else:
            self._log(f"\nDone. Exported {exported} file(s).")

# -------- Main --------
if __name__ == "__main__":
    try:
        app = ImageRenamerApp()
        app.mainloop()
    except Exception as exc:
        try:
            messagebox.showerror("Fatal Error", str(exc))
        except Exception:
            pass
        raise
