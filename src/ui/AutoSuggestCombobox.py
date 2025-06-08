import tkinter as tk
from tkinter import ttk

class AutoSuggestCombobox(ttk.Combobox):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self._completion_list = []
        self._hits = []
        self._hit_index = 0
        self.position = 0
        self.bind('<KeyRelease>', self._handle_keyrelease)
        self.bind('<FocusOut>', self._handle_focusout)
        self.bind('<FocusIn>', self._handle_focusin)
        self.bind('<Return>', self._handle_return)  # bind Enter key
        self.bind('<Down>', self._down_arrow)  # bind Up arrow key
        self.bind('<Up>', self._up_arrow)
        self.bind('<Button-1>', self._handle_click)  # bind mouse click
        master.bind("<Button-1>", self._handle_root_click)  # bind mouse click on root window
        self._popup_menu = None

    def set_completion_list(self, completion_list):
        """Set the list of possible completions."""
        self._completion_list = completion_list
        self['values'] = self._completion_list

    def _handle_keyrelease(self, event):
        """Handle key release events."""
        value = self.get()
        cursor_index = self.index(tk.INSERT)

        if value == '':
            self._hits = self._completion_list
        else:
            # Determine the word before the cursor
            before_cursor = value[:cursor_index].rsplit(' ', 1)[-1]

            # Filter suggestions based on the word before the cursor
            self._hits = [item for item in self._completion_list if before_cursor.lower() in item.lower()]

        # Ignore Down and Up arrow key presses
        if event.keysym in ['Down', 'Up', 'Return']:
            return

        if self._hits:
            self._show_popup(self._hits)


    def _show_popup(self, values):
        """Display the popup listbox."""
        if self._popup_menu:
            self._popup_menu.destroy()

        self._popup_menu = tk.Toplevel(self)
        self._popup_menu.wm_overrideredirect(True)

        popup_frame = tk.Frame(self._popup_menu, borderwidth=0.1)
        popup_frame.pack(padx=1, pady=(1, 1), fill='both', expand=True)

        listbox = tk.Listbox(popup_frame, borderwidth=0, relief=tk.FLAT, bd=0)
        scrollbar = ttk.Scrollbar(popup_frame, orient=tk.VERTICAL, command=listbox.yview)
        listbox.config(yscrollcommand=scrollbar.set)

        for value in values:
            listbox.insert(tk.END, value)

        listbox.bind("<ButtonRelease-1>", self._on_listbox_select)
        listbox.bind("<FocusOut>", self._on_listbox_focusout)
        listbox.bind("<Motion>", self._on_mouse_motion)

        # Automatically select the first entry if no mouse hover has occurred yet
        if not listbox.curselection():
            listbox.selection_set(0)

        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Adjust popup width to match entry box
        popup_width = self.winfo_width()
        self._popup_menu.geometry(f"{popup_width}x165")

        x = self.winfo_rootx()
        y = self.winfo_rooty() + self.winfo_height()
        self._popup_menu.geometry(f"+{x}+{y}")

    def _on_listbox_select(self, event):
        """Select a value from the listbox."""
        widget = event.widget
        selection = widget.curselection()
        if selection:
            value = widget.get(selection[0])
            self._select_value(value)

    def _on_mouse_motion(self, event):
        """Handle mouse motion over the listbox."""
        widget = event.widget
        index = widget.nearest(event.y)
        widget.selection_clear(0, tk.END)
        widget.selection_set(index)

    def _on_listbox_focusout(self, event):
        """Handle listbox losing focus."""
        if self._popup_menu:
            self._popup_menu.destroy()
            self._popup_menu = None

    def _select_value(self, value):
        """Select a value from the popup listbox."""
        self.set(value)
        self.event_generate('<<ComboboxSelected>>')
        self.icursor(tk.END)  # Move cursor to the end
        self.selection_range(0, tk.END)  # Select entire text
        if self._popup_menu:
            self._popup_menu.destroy()
            self._popup_menu = None

    def _handle_focusout(self, event):
        """Handle focus out events."""
        if self._popup_menu:
            try:
                if not self._popup_menu.winfo_containing(event.x_root, event.y_root):
                    self._popup_menu.destroy()
                    self._popup_menu = None
            except tk.TclError:
                pass

    def _handle_focusin(self, event):
        """Handle focus in events."""
        if self._popup_menu:
            self._popup_menu.destroy()
            self._popup_menu = None

    def _handle_return(self, event):
        """Handle Enter key press."""
        if self._popup_menu:
            listbox = self._popup_menu.winfo_children()[0].winfo_children()[0]
            current_selection = listbox.curselection()
            if current_selection:
                value = listbox.get(current_selection[0])
                self._select_value(value)

    def _down_arrow(self, event):
        """Handle down arrow key press."""
        if self._popup_menu:
            listbox = self._popup_menu.winfo_children()[0].winfo_children()[0]
            current_selection = listbox.curselection()
            if current_selection:
                current_index = current_selection[0]
                next_index = (current_index + 1) % len(self._hits)
                listbox.selection_clear(0, tk.END)
                listbox.selection_set(next_index)
                listbox.activate(next_index)
                return 'break'  # prevent default behavior

    def _up_arrow(self, event):
        """Handle up arrow key press."""
        if self._popup_menu:
            listbox = self._popup_menu.winfo_children()[0].winfo_children()[0]
            current_selection = listbox.curselection()
            if current_selection:
                current_index = current_selection[0]
                next_index = (current_index - 1) % len(self._hits)
                listbox.selection_clear(0, tk.END)
                listbox.selection_set(next_index)
                listbox.activate(next_index)
                return 'break'  # prevent default behavior



    def _handle_click(self, event):
        """Handle mouse click events."""
        value = self.get()
        if value == '':
            self._hits = self._completion_list
        else:
            self._hits = [item for item in self._completion_list if item.lower().startswith(value.lower())]

        if self._hits:
            self._show_popup(self._hits)


    def _handle_root_click(self, event):
        """Handle mouse click events on root window."""
        if self._popup_menu:
            x, y = event.x_root, event.y_root
            x0, y0, x1, y1 = self.winfo_rootx(), self.winfo_rooty(), self.winfo_rootx() + self.winfo_width(), self.winfo_rooty() + self.winfo_height()
            if not (x0 <= x <= x1 and y0 <= y <= y1):
                self._popup_menu.destroy()
                self._popup_menu = None