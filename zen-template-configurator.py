import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import re

# ── Data file paths ────────────────────────────────────────────────────────────
DATA_DIR = "data"
TEMPLATES_FILE = os.path.join(DATA_DIR, "zen-templates.json")
LOCATIONS_FILE = os.path.join(DATA_DIR, "zen-locations.json")
SERVICES_FILE  = os.path.join(DATA_DIR, "zen-services.json")
OPERATORS_FILE = os.path.join(DATA_DIR, "zen-operators.json")

# ── Parameter metadata ─────────────────────────────────────────────────────────
# Maps template type name → list of placeholder names used by that type
TYPE_PARAMS = {
    "Appointments": ["FirstName", "Date", "Location", "Services", "Operator", "Plural"],
    "Surveys":      ["FirstName", "Location", "Operator"],
    "Customers":    ["FirstName", "Location", "Services", "Operator"],
}

PARAM_COLORS = [
    "#e06c75",  # red-ish
    "#61afef",  # blue
    "#98c379",  # green
    "#e5c07b",  # yellow
    "#c678dd",  # purple
    "#56b6c2",  # cyan
    "#d19a66",  # orange
]


def load_json(path, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent="\t")


# ══════════════════════════════════════════════════════════════════════════════
# Tab 1: Locations · Services · Operators
# ══════════════════════════════════════════════════════════════════════════════

class ResourcesTab(ttk.Frame):
    """Three side-by-side panels for locations, services and operators."""

    def __init__(self, parent):
        super().__init__(parent, padding=10)
        self._build()

    def _build(self):
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)

        self.loc_panel  = LocationsPanel(self)
        self.svc_panel  = ServicesPanel(self)
        self.ops_panel  = OperatorsPanel(self)

        self.loc_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        self.svc_panel.grid(row=0, column=1, sticky="nsew", padx=5)
        self.ops_panel.grid(row=0, column=2, sticky="nsew", padx=(5, 0))
        self.rowconfigure(0, weight=1)


# ── Generic list panel ─────────────────────────────────────────────────────────

class _ListPanel(ttk.LabelFrame):
    """Base panel: Listbox + Add / Edit / Delete buttons."""

    title = "Items"

    def __init__(self, parent):
        super().__init__(parent, text=self.title, padding=8)
        self.items = []
        self._build()
        self.load()

    def _build(self):
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        lb_frame = ttk.Frame(self)
        lb_frame.grid(row=0, column=0, columnspan=2, sticky="nsew")
        lb_frame.rowconfigure(0, weight=1)
        lb_frame.columnconfigure(0, weight=1)

        self.listbox = tk.Listbox(lb_frame, selectmode=tk.SINGLE,
                                  activestyle="none", borderwidth=1)
        self.listbox.grid(row=0, column=0, sticky="nsew")
        sb = ttk.Scrollbar(lb_frame, orient=tk.VERTICAL,
                           command=self.listbox.yview)
        sb.grid(row=0, column=1, sticky="ns")
        self.listbox["yscrollcommand"] = sb.set

        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=1, column=0, columnspan=2, pady=(6, 0), sticky="ew")
        ttk.Button(btn_frame, text="Add",    command=self.on_add).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="Edit",   command=self.on_edit).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Delete", command=self.on_delete).pack(side=tk.LEFT)

    # ── Abstract helpers ───────────────────────────────────────────────────────

    def load(self):
        raise NotImplementedError

    def save(self):
        raise NotImplementedError

    def item_label(self, item):
        raise NotImplementedError

    def ask_add(self):
        raise NotImplementedError

    def ask_edit(self, item):
        raise NotImplementedError

    # ── Shared CRUD ────────────────────────────────────────────────────────────

    def refresh_list(self):
        self.listbox.delete(0, tk.END)
        for item in self.items:
            self.listbox.insert(tk.END, self.item_label(item))

    def on_add(self):
        new = self.ask_add()
        if new is None:
            return
        self.items.append(new)
        self.save()
        self.refresh_list()

    def on_edit(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showinfo("Edit", "Select an item first.")
            return
        idx = sel[0]
        updated = self.ask_edit(self.items[idx])
        if updated is None:
            return
        self.items[idx] = updated
        self.save()
        self.refresh_list()

    def on_delete(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showinfo("Delete", "Select an item first.")
            return
        idx = sel[0]
        label = self.item_label(self.items[idx])
        if not messagebox.askyesno("Delete", f"Delete '{label}'?"):
            return
        del self.items[idx]
        self.save()
        self.refresh_list()


# ── Locations panel ────────────────────────────────────────────────────────────

class LocationsPanel(_ListPanel):
    title = "Locations"

    def load(self):
        self.items = load_json(LOCATIONS_FILE, [])
        self.refresh_list()

    def save(self):
        save_json(LOCATIONS_FILE, self.items)

    def item_label(self, item):
        return item.get("title", "")

    def ask_add(self):
        return _ask_location(self, "Add Location", {})

    def ask_edit(self, item):
        return _ask_location(self, "Edit Location", item)


def _ask_location(parent, title, item):
    return _BilingualTitleDialog(parent, title, item).result


class _BilingualTitleDialog(tk.Toplevel):
    """Dialog for items with title + bilingual text (es/en)."""

    def __init__(self, parent, title, item):
        super().__init__(parent)
        self.title(title)
        self.resizable(False, False)
        self.result = None
        self._build(item)
        self.grab_set()
        self.wait_window()

    def _build(self, item):
        f = ttk.Frame(self, padding=12)
        f.pack(fill=tk.BOTH, expand=True)

        ttk.Label(f, text="Title:").grid(row=0, column=0, sticky="w", pady=2)
        self.e_title = ttk.Entry(f, width=40)
        self.e_title.grid(row=0, column=1, sticky="ew", pady=2)
        self.e_title.insert(0, item.get("title", ""))

        ttk.Label(f, text="Text (ES):").grid(row=1, column=0, sticky="w", pady=2)
        self.e_es = ttk.Entry(f, width=40)
        self.e_es.grid(row=1, column=1, sticky="ew", pady=2)
        self.e_es.insert(0, item.get("text", {}).get("es", ""))

        ttk.Label(f, text="Text (EN):").grid(row=2, column=0, sticky="w", pady=2)
        self.e_en = ttk.Entry(f, width=40)
        self.e_en.grid(row=2, column=1, sticky="ew", pady=2)
        self.e_en.insert(0, item.get("text", {}).get("en", ""))

        bf = ttk.Frame(f)
        bf.grid(row=3, column=0, columnspan=2, pady=(10, 0))
        ttk.Button(bf, text="Save",   command=self._save).pack(side=tk.LEFT)
        ttk.Button(bf, text="Cancel", command=self.destroy).pack(side=tk.LEFT, padx=6)

    def _save(self):
        t = self.e_title.get().strip()
        if not t:
            messagebox.showwarning("Validation", "Title is required.", parent=self)
            return
        self.result = {
            "title": t,
            "text": {"es": self.e_es.get().strip(), "en": self.e_en.get().strip()}
        }
        self.destroy()


# ── Services panel ─────────────────────────────────────────────────────────────

class ServicesPanel(_ListPanel):
    title = "Services"

    def load(self):
        data = load_json(SERVICES_FILE, {"services": []})
        self.items = data.get("services", []) if isinstance(data, dict) else data
        self.refresh_list()

    def save(self):
        save_json(SERVICES_FILE, {"services": self.items})

    def item_label(self, item):
        dur = item.get("duration", "")
        return f"{item.get('title', '')} ({dur} min)" if dur else item.get("title", "")

    def ask_add(self):
        return _ask_service(self, "Add Service", {})

    def ask_edit(self, item):
        return _ask_service(self, "Edit Service", item)


def _ask_service(parent, title, item):
    return _ServiceDialog(parent, title, item).result


class _ServiceDialog(tk.Toplevel):
    def __init__(self, parent, title, item):
        super().__init__(parent)
        self.title(title)
        self.resizable(False, False)
        self.result = None
        self._build(item)
        self.grab_set()
        self.wait_window()

    def _build(self, item):
        f = ttk.Frame(self, padding=12)
        f.pack(fill=tk.BOTH, expand=True)

        ttk.Label(f, text="Title:").grid(row=0, column=0, sticky="w", pady=2)
        self.e_title = ttk.Entry(f, width=40)
        self.e_title.grid(row=0, column=1, sticky="ew", pady=2)
        self.e_title.insert(0, item.get("title", ""))

        ttk.Label(f, text="Duration (min):").grid(row=1, column=0, sticky="w", pady=2)
        self.e_dur = ttk.Entry(f, width=10)
        self.e_dur.grid(row=1, column=1, sticky="w", pady=2)
        self.e_dur.insert(0, str(item.get("duration", "")))

        bf = ttk.Frame(f)
        bf.grid(row=2, column=0, columnspan=2, pady=(10, 0))
        ttk.Button(bf, text="Save",   command=self._save).pack(side=tk.LEFT)
        ttk.Button(bf, text="Cancel", command=self.destroy).pack(side=tk.LEFT, padx=6)

    def _save(self):
        t = self.e_title.get().strip()
        if not t:
            messagebox.showwarning("Validation", "Title is required.", parent=self)
            return
        dur_str = self.e_dur.get().strip()
        try:
            dur = int(dur_str) if dur_str else 0
        except ValueError:
            messagebox.showwarning("Validation", "Duration must be a number.", parent=self)
            return
        self.result = {"title": t, "duration": dur}
        self.destroy()


# ── Operators panel ────────────────────────────────────────────────────────────

class OperatorsPanel(_ListPanel):
    title = "Operators"

    def load(self):
        self.items = load_json(OPERATORS_FILE, [])
        self.refresh_list()

    def save(self):
        save_json(OPERATORS_FILE, self.items)

    def item_label(self, item):
        return item  # operators are plain strings

    def ask_add(self):
        return _ask_string(self, "Add Operator", "Operator name:", "")

    def ask_edit(self, item):
        return _ask_string(self, "Edit Operator", "Operator name:", item)


def _ask_string(parent, title, prompt, default):
    return _StringDialog(parent, title, prompt, default).result


class _StringDialog(tk.Toplevel):
    def __init__(self, parent, title, prompt, default):
        super().__init__(parent)
        self.title(title)
        self.resizable(False, False)
        self.result = None
        self._build(prompt, default)
        self.grab_set()
        self.wait_window()

    def _build(self, prompt, default):
        f = ttk.Frame(self, padding=12)
        f.pack(fill=tk.BOTH, expand=True)
        ttk.Label(f, text=prompt).pack(anchor="w")
        self.entry = ttk.Entry(f, width=36)
        self.entry.pack(fill=tk.X, pady=(4, 8))
        self.entry.insert(0, default)
        bf = ttk.Frame(f)
        bf.pack()
        ttk.Button(bf, text="Save",   command=self._save).pack(side=tk.LEFT)
        ttk.Button(bf, text="Cancel", command=self.destroy).pack(side=tk.LEFT, padx=6)
        self.entry.focus_set()

    def _save(self):
        val = self.entry.get().strip()
        if not val:
            messagebox.showwarning("Validation", "Value is required.", parent=self)
            return
        self.result = val
        self.destroy()


# ══════════════════════════════════════════════════════════════════════════════
# Tab 2: Templates
# ══════════════════════════════════════════════════════════════════════════════

class TemplatesTab(ttk.Frame):
    """Left list of templates; right editor with parameter highlighting."""

    def __init__(self, parent):
        super().__init__(parent, padding=10)
        self.templates = []
        self.current_index = -1
        self._dirty = False
        self._build()
        self.load()

    # ── Layout ────────────────────────────────────────────────────────────────

    def _build(self):
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)

        # LEFT: template list
        left = ttk.LabelFrame(self, text="Templates", padding=8)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        left.rowconfigure(0, weight=1)
        left.columnconfigure(0, weight=1)

        lf = ttk.Frame(left)
        lf.grid(row=0, column=0, sticky="nsew")
        lf.rowconfigure(0, weight=1)
        lf.columnconfigure(0, weight=1)

        self.listbox = tk.Listbox(lf, selectmode=tk.SINGLE, activestyle="none",
                                  width=28, borderwidth=1)
        self.listbox.grid(row=0, column=0, sticky="nsew")
        sb = ttk.Scrollbar(lf, orient=tk.VERTICAL, command=self.listbox.yview)
        sb.grid(row=0, column=1, sticky="ns")
        self.listbox["yscrollcommand"] = sb.set
        self.listbox.bind("<<ListboxSelect>>", self._on_select)

        bf = ttk.Frame(left)
        bf.grid(row=1, column=0, pady=(6, 0), sticky="ew")
        ttk.Button(bf, text="New",    command=self._new).pack(side=tk.LEFT)
        ttk.Button(bf, text="Delete", command=self._delete).pack(side=tk.LEFT, padx=4)

        # RIGHT: editor
        right = ttk.LabelFrame(self, text="Editor", padding=8)
        right.grid(row=0, column=1, sticky="nsew")
        right.rowconfigure(4, weight=1)
        right.rowconfigure(6, weight=1)
        right.columnconfigure(1, weight=1)

        # Title
        ttk.Label(right, text="Title:").grid(row=0, column=0, sticky="w", pady=2)
        self.e_title = ttk.Entry(right)
        self.e_title.grid(row=0, column=1, columnspan=2, sticky="ew", pady=2)

        # Type
        ttk.Label(right, text="Type:").grid(row=1, column=0, sticky="w", pady=2)
        self.types = sorted(TYPE_PARAMS.keys())
        self.type_var = tk.StringVar()
        self.type_combo = ttk.Combobox(right, textvariable=self.type_var,
                                       values=self.types, state="readonly", width=20)
        self.type_combo.grid(row=1, column=1, sticky="w", pady=2)
        self.type_combo.bind("<<ComboboxSelected>>", self._on_type_change)

        # Parameter legend
        self.param_legend = ttk.Frame(right)
        self.param_legend.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(4, 2))

        # ES template
        ttk.Label(right, text="Template (ES):").grid(row=3, column=0, sticky="nw", pady=2)
        self.txt_es = tk.Text(right, height=8, wrap=tk.WORD, undo=True)
        self.txt_es.grid(row=4, column=0, columnspan=3, sticky="nsew", pady=2)
        sb_es = ttk.Scrollbar(right, orient=tk.VERTICAL, command=self.txt_es.yview)
        sb_es.grid(row=4, column=3, sticky="ns")
        self.txt_es["yscrollcommand"] = sb_es.set
        self.txt_es.bind("<KeyRelease>", lambda e: self._highlight_params(self.txt_es))

        # EN template
        ttk.Label(right, text="Template (EN):").grid(row=5, column=0, sticky="nw", pady=2)
        self.txt_en = tk.Text(right, height=8, wrap=tk.WORD, undo=True)
        self.txt_en.grid(row=6, column=0, columnspan=3, sticky="nsew", pady=2)
        sb_en = ttk.Scrollbar(right, orient=tk.VERTICAL, command=self.txt_en.yview)
        sb_en.grid(row=6, column=3, sticky="ns")
        self.txt_en["yscrollcommand"] = sb_en.set
        self.txt_en.bind("<KeyRelease>", lambda e: self._highlight_params(self.txt_en))

        # Save button
        bf2 = ttk.Frame(right)
        bf2.grid(row=7, column=0, columnspan=3, pady=(8, 0), sticky="e")
        ttk.Button(bf2, text="Save Template", command=self._save_current).pack()

        self._set_editor_state(tk.DISABLED)

    # ── Data ──────────────────────────────────────────────────────────────────

    def load(self):
        self.templates = load_json(TEMPLATES_FILE, [])
        self._refresh_list()

    def _refresh_list(self):
        self.listbox.delete(0, tk.END)
        for t in self.templates:
            self.listbox.insert(tk.END, f"[{t.get('type','')}] {t.get('title','')}")

    # ── Editor helpers ────────────────────────────────────────────────────────

    def _set_editor_state(self, state):
        widgets = [self.e_title, self.type_combo, self.txt_es, self.txt_en]
        for w in widgets:
            w.config(state=state)

    def _on_select(self, _event=None):
        sel = self.listbox.curselection()
        if not sel:
            return
        if self._dirty and not messagebox.askyesno(
                "Unsaved changes", "You have unsaved changes. Discard them?"):
            # Restore previous selection
            if self.current_index >= 0:
                self.listbox.selection_clear(0, tk.END)
                self.listbox.selection_set(self.current_index)
            return
        self.current_index = sel[0]
        self._load_into_editor(self.templates[self.current_index])
        self._dirty = False

    def _load_into_editor(self, template):
        self._set_editor_state(tk.NORMAL)
        self.e_title.delete(0, tk.END)
        self.e_title.insert(0, template.get("title", ""))
        self.type_var.set(template.get("type", ""))
        self.txt_es.delete("1.0", tk.END)
        self.txt_es.insert("1.0", template.get("template", {}).get("es", ""))
        self.txt_en.delete("1.0", tk.END)
        self.txt_en.insert("1.0", template.get("template", {}).get("en", ""))
        self._build_legend()
        self._highlight_params(self.txt_es)
        self._highlight_params(self.txt_en)

    def _on_type_change(self, _event=None):
        self._build_legend()
        self._highlight_params(self.txt_es)
        self._highlight_params(self.txt_en)

    def _build_legend(self):
        for w in self.param_legend.winfo_children():
            w.destroy()
        t = self.type_var.get()
        params = TYPE_PARAMS.get(t, [])
        ttk.Label(self.param_legend, text="Parameters: ").pack(side=tk.LEFT)
        for i, p in enumerate(params):
            color = PARAM_COLORS[i % len(PARAM_COLORS)]
            lbl = tk.Label(self.param_legend, text=f"{{{p}}}",
                           fg=color, font=("TkDefaultFont", 9, "bold"))
            lbl.pack(side=tk.LEFT, padx=(0, 6))

    def _highlight_params(self, text_widget):
        t = self.type_var.get()
        params = TYPE_PARAMS.get(t, [])
        # Remove old tags
        for tag in text_widget.tag_names():
            if tag.startswith("param_"):
                text_widget.tag_remove(tag, "1.0", tk.END)
        for i, param in enumerate(params):
            color = PARAM_COLORS[i % len(PARAM_COLORS)]
            tag = f"param_{param}"
            text_widget.tag_configure(tag, foreground=color,
                                      font=("TkDefaultFont", 10, "bold"))
            pattern = re.escape(f"{{{param}}}")
            content = text_widget.get("1.0", tk.END)
            for m in re.finditer(pattern, content):
                start = f"1.0+{m.start()}c"
                end   = f"1.0+{m.end()}c"
                text_widget.tag_add(tag, start, end)

    # ── CRUD ──────────────────────────────────────────────────────────────────

    def _new(self):
        blank = {"title": "New Template", "type": self.types[0],
                 "template": {"es": "", "en": ""}}
        self.templates.append(blank)
        save_json(TEMPLATES_FILE, self.templates)
        self._refresh_list()
        self.listbox.selection_clear(0, tk.END)
        self.listbox.selection_set(len(self.templates) - 1)
        self._dirty = False
        self._on_select()

    def _delete(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showinfo("Delete", "Select a template first.")
            return
        idx = sel[0]
        label = f"[{self.templates[idx].get('type','')}] {self.templates[idx].get('title','')}"
        if not messagebox.askyesno("Delete", f"Delete '{label}'?"):
            return
        del self.templates[idx]
        save_json(TEMPLATES_FILE, self.templates)
        self._refresh_list()
        self.current_index = -1
        self._dirty = False
        self._set_editor_state(tk.DISABLED)

    def _save_current(self):
        if self.current_index < 0:
            return
        title = self.e_title.get().strip()
        if not title:
            messagebox.showwarning("Validation", "Title is required.")
            return
        t_type = self.type_var.get()
        if not t_type:
            messagebox.showwarning("Validation", "Type is required.")
            return
        self.templates[self.current_index] = {
            "title": title,
            "type": t_type,
            "template": {
                "es": self.txt_es.get("1.0", tk.END).rstrip("\n"),
                "en": self.txt_en.get("1.0", tk.END).rstrip("\n"),
            }
        }
        save_json(TEMPLATES_FILE, self.templates)
        self._dirty = False
        self._refresh_list()
        self.listbox.selection_set(self.current_index)
        messagebox.showinfo("Saved", "Template saved.")


# ══════════════════════════════════════════════════════════════════════════════
# Tab 3: Template Types
# ══════════════════════════════════════════════════════════════════════════════

class TemplateTypesTab(ttk.Frame):
    """
    Visual editor for template types and their available parameters.
    Changes here update the in-memory TYPE_PARAMS dict and persist to a JSON
    sidecar file (data/zen-template-types.json) so that the configurator
    remembers custom types between sessions.
    """

    TYPES_FILE = os.path.join(DATA_DIR, "zen-template-types.json")

    def __init__(self, parent):
        super().__init__(parent, padding=10)
        self._types = {}   # name → list[str] of parameter names
        self._selected = None
        self._build()
        self._load()

    # ── Layout ────────────────────────────────────────────────────────────────

    def _build(self):
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)

        # LEFT: type list
        left = ttk.LabelFrame(self, text="Template Types", padding=8)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        left.rowconfigure(0, weight=1)
        left.columnconfigure(0, weight=1)

        lf = ttk.Frame(left)
        lf.grid(row=0, column=0, sticky="nsew")
        lf.rowconfigure(0, weight=1)
        lf.columnconfigure(0, weight=1)

        self.listbox = tk.Listbox(lf, selectmode=tk.SINGLE, activestyle="none",
                                  width=22, borderwidth=1)
        self.listbox.grid(row=0, column=0, sticky="nsew")
        sb = ttk.Scrollbar(lf, orient=tk.VERTICAL, command=self.listbox.yview)
        sb.grid(row=0, column=1, sticky="ns")
        self.listbox["yscrollcommand"] = sb.set
        self.listbox.bind("<<ListboxSelect>>", self._on_select)

        bf = ttk.Frame(left)
        bf.grid(row=1, column=0, pady=(6, 0), sticky="ew")
        ttk.Button(bf, text="New",    command=self._new).pack(side=tk.LEFT)
        ttk.Button(bf, text="Delete", command=self._delete).pack(side=tk.LEFT, padx=4)

        # RIGHT: parameter editor
        right = ttk.LabelFrame(self, text="Parameters for selected type", padding=8)
        right.grid(row=0, column=1, sticky="nsew")
        right.rowconfigure(1, weight=1)
        right.columnconfigure(0, weight=1)

        self.type_name_var = tk.StringVar()
        nf = ttk.Frame(right)
        nf.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        ttk.Label(nf, text="Type name:").pack(side=tk.LEFT)
        self.e_type_name = ttk.Entry(nf, textvariable=self.type_name_var, width=24)
        self.e_type_name.pack(side=tk.LEFT, padx=(6, 0))

        # Parameter listbox with add/remove
        pf = ttk.Frame(right)
        pf.grid(row=1, column=0, sticky="nsew")
        pf.rowconfigure(0, weight=1)
        pf.columnconfigure(0, weight=1)

        self.param_listbox = tk.Listbox(pf, selectmode=tk.SINGLE,
                                        activestyle="none", width=28, borderwidth=1)
        self.param_listbox.grid(row=0, column=0, sticky="nsew")
        sb2 = ttk.Scrollbar(pf, orient=tk.VERTICAL, command=self.param_listbox.yview)
        sb2.grid(row=0, column=1, sticky="ns")
        self.param_listbox["yscrollcommand"] = sb2.set

        pb = ttk.Frame(right)
        pb.grid(row=2, column=0, sticky="ew", pady=(4, 0))
        self.e_param = ttk.Entry(pb, width=20)
        self.e_param.pack(side=tk.LEFT)
        ttk.Button(pb, text="Add Param",    command=self._add_param).pack(side=tk.LEFT, padx=4)
        ttk.Button(pb, text="Remove Param", command=self._remove_param).pack(side=tk.LEFT)

        bf2 = ttk.Frame(right)
        bf2.grid(row=3, column=0, pady=(10, 0), sticky="e")
        ttk.Button(bf2, text="Save Type", command=self._save_type).pack()

        self._set_right_state(tk.DISABLED)

    # ── Data ──────────────────────────────────────────────────────────────────

    def _load(self):
        # Start from built-in TYPE_PARAMS, then overlay persisted overrides
        self._types = {k: list(v) for k, v in TYPE_PARAMS.items()}
        persisted = load_json(self.TYPES_FILE, {})
        self._types.update(persisted)
        # Sync in-memory TYPE_PARAMS
        TYPE_PARAMS.clear()
        TYPE_PARAMS.update(self._types)
        self._refresh_list()

    def _save_all(self):
        save_json(self.TYPES_FILE, self._types)
        # Keep TYPE_PARAMS in sync so templates tab uses updated data
        TYPE_PARAMS.clear()
        TYPE_PARAMS.update(self._types)

    def _refresh_list(self):
        self.listbox.delete(0, tk.END)
        for name in self._types:
            self.listbox.insert(tk.END, name)

    def _refresh_param_list(self, name):
        self.param_listbox.delete(0, tk.END)
        for p in self._types.get(name, []):
            self.param_listbox.insert(tk.END, p)

    # ── Events ────────────────────────────────────────────────────────────────

    def _set_right_state(self, state):
        for w in [self.e_type_name, self.e_param]:
            w.config(state=state)
        self.param_listbox.config(state=state)

    def _on_select(self, _event=None):
        sel = self.listbox.curselection()
        if not sel:
            return
        self._selected = self.listbox.get(sel[0])
        self.type_name_var.set(self._selected)
        self._refresh_param_list(self._selected)
        self._set_right_state(tk.NORMAL)

    def _new(self):
        name = _ask_string(self, "New Type", "Type name:", "")
        if name is None:
            return
        if name in self._types:
            messagebox.showwarning("Duplicate", f"Type '{name}' already exists.")
            return
        self._types[name] = []
        self._save_all()
        self._refresh_list()
        # Select the new entry
        items = list(self._types.keys())
        idx = items.index(name)
        self.listbox.selection_clear(0, tk.END)
        self.listbox.selection_set(idx)
        self._on_select()

    def _delete(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showinfo("Delete", "Select a type first.")
            return
        name = self.listbox.get(sel[0])
        if not messagebox.askyesno("Delete", f"Delete type '{name}'?"):
            return
        del self._types[name]
        self._save_all()
        self._refresh_list()
        self._selected = None
        self.param_listbox.delete(0, tk.END)
        self._set_right_state(tk.DISABLED)

    def _add_param(self):
        if not self._selected:
            return
        p = self.e_param.get().strip()
        if not p:
            messagebox.showwarning("Validation", "Enter a parameter name.", parent=self)
            return
        if p in self._types[self._selected]:
            messagebox.showwarning("Duplicate", f"Parameter '{p}' already exists.", parent=self)
            return
        self._types[self._selected].append(p)
        self._refresh_param_list(self._selected)
        self.e_param.delete(0, tk.END)

    def _remove_param(self):
        if not self._selected:
            return
        sel = self.param_listbox.curselection()
        if not sel:
            messagebox.showinfo("Remove", "Select a parameter first.")
            return
        p = self.param_listbox.get(sel[0])
        self._types[self._selected].remove(p)
        self._refresh_param_list(self._selected)

    def _save_type(self):
        if not self._selected:
            return
        new_name = self.type_name_var.get().strip()
        if not new_name:
            messagebox.showwarning("Validation", "Type name is required.")
            return
        if new_name != self._selected and new_name in self._types:
            messagebox.showwarning("Duplicate", f"Type '{new_name}' already exists.")
            return
        # Rename if needed
        if new_name != self._selected:
            self._types[new_name] = self._types.pop(self._selected)
            self._selected = new_name
        self._save_all()
        self._refresh_list()
        items = list(self._types.keys())
        idx = items.index(self._selected)
        self.listbox.selection_clear(0, tk.END)
        self.listbox.selection_set(idx)
        messagebox.showinfo("Saved", f"Type '{new_name}' saved.")


# ══════════════════════════════════════════════════════════════════════════════
# Main application
# ══════════════════════════════════════════════════════════════════════════════

class TemplateConfigurator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Zen Template Configurator")
        self.geometry("1000x700")
        try:
            self.iconbitmap("data/zen-icon.ico")
        except Exception:
            pass

        try:
            self.tk.call('source', 'src/themes/Azure/azure.tcl')
            self.tk.call('set_theme', 'dark')
        except Exception:
            pass

        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        tab1 = ResourcesTab(notebook)
        tab2 = TemplatesTab(notebook)
        tab3 = TemplateTypesTab(notebook)

        notebook.add(tab1, text="  Locations · Services · Operators  ")
        notebook.add(tab2, text="  Templates  ")
        notebook.add(tab3, text="  Template Types  ")


def main():
    app = TemplateConfigurator()
    app.mainloop()


if __name__ == "__main__":
    main()
