import tkinter as tk
from tkinter import ttk

class Toast(ttk.Frame):
    def __init__(self, parent, message, type, duration, on_destroy):
        super().__init__(parent, style=f"Toast{type}.TFrame")
        self.parent = parent
        self.message = message
        self.duration = duration
        self.on_destroy = on_destroy
        self.label = ttk.Label(self, text=self.message, style=f"Toast{type}.TLabel")
        self.label.pack(padx=20, pady=10)
        self.after_id = self.after(self.duration, self.destroy)
        self.bind("<Button-1>", lambda e: self.destroy())
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, event):
        self.after_cancel(self.after_id)

    def on_leave(self, event):
        self.after_id = self.after(self.duration, self.destroy)

    def destroy(self):
        if self.on_destroy:
            self.on_destroy(self)
        super().destroy()

class ToastService:
    def __init__(self, parent):
        self.parent = parent
        self.toasts = []

    def show_toast(self, message, type="Warning", duration=3000):
        toast = Toast(self.parent, message, type, duration, self._remove_toast)
        self.toasts.append(toast)
        # Place off-screen to force geometry calculation
        toast.place(x=-10000, y=-10000)
        toast.update_idletasks()
        self._reposition_toasts()

    def _remove_toast(self, toast):
        if toast in self.toasts:
            self.toasts.remove(toast)
            self._reposition_toasts()

    def _reposition_toasts(self):
        # Stack toasts from the bottom up, newest at the bottom, using fixed pixel distances
        bottom_margin = 50   # Distance from the bottom of the parent window in pixels
        toast_spacing = 10   # Space between toasts in pixels

        self.parent.update_idletasks()
        parent_height = self.parent.winfo_height()
        parent_width = self.parent.winfo_width()

        for idx, toast in enumerate(reversed(self.toasts)):
            toast.update_idletasks()
            toast_height = toast.winfo_height()
            x = (parent_width - toast.winfo_width()) // 2
            y = parent_height - bottom_margin - (toast_height + toast_spacing) * idx
            toast.place(x=x, y=y)

    # def _reposition_toasts(self):
    #     # Stack toasts from the bottom up, newest at the bottom
    #     for idx, toast in enumerate(reversed(self.toasts)):
    #         toast.place(relx=0.5, rely=0.95 - idx * 0.12, anchor="s")  # Adjust 0.12 for spacing

# Example usage:
# toast_service = ToastService(root)
# toast_service.show_toast("Hello!", "Info", 2000)
# toast_service.show_toast("Another message", "Warning", 4000)