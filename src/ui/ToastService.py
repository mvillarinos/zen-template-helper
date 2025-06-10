import tkinter as tk
from tkinter import ttk

colors = {
    "Success": "#27AE60",
    "Warning": "#E67E22",
    "Error": "#C0392B"
}
class ToastService:
    def __init__(self, parent, style):
        self.parent = parent
        self.toasts = []
        
        style.configure("ToastSuccess.TFrame", background=colors["Success"])
        style.configure("ToastSuccess.TLabel", foreground="white", background=colors["Success"])
        style.configure("ToastWarning.TFrame", background=colors["Warning"])
        style.configure("ToastWarning.TLabel", foreground="white", background=colors["Warning"])
        style.configure("ToastError.TFrame", background=colors["Error"])
        style.configure("ToastError.TLabel", foreground="white", background=colors["Error"])

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
        bottom_margin = 0   # Distance from the bottom of the parent window in pixels
        toast_spacing = 10   # Space between toasts in pixels

        self.parent.update_idletasks()
        parent_height = self.parent.winfo_height()
        parent_width = self.parent.winfo_width()

        for idx, toast in enumerate(self.toasts):
            toast.update_idletasks()
            toast_height = toast.winfo_height()
            x = (parent_width - toast.winfo_width()) // 2
            y = parent_height - bottom_margin - (toast_height + toast_spacing) * (len(self.toasts) - idx)
            toast.place(x=x, y=y)

class Toast(ttk.Frame):
    def __init__(self, parent, message, type, duration, on_destroy):
        super().__init__(parent, style=f"Toast{type}.TFrame")
        self.parent = parent
        self.message = message
        self.duration = duration
        self.on_destroy = on_destroy
        self.label = ttk.Label(self, text=self.message, style=f"Toast{type}.TLabel")
        self.label.pack(padx=20, pady=6)
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

# Example usage:
# toast_service = ToastService(root)
# toast_service.show_toast("Hello!", "Info", 2000)
# toast_service.show_toast("Another message", "Warning", 4000)

# WIP bordes redondeados (no funciona del todo)
# 
# class Toast(tk.Canvas):
#     def __init__(self, parent, message, type, duration, on_destroy):
#         super().__init__(parent, width=200, height=50, highlightthickness=0)
#         self.parent = parent
#         self.message = message
#         self.duration = duration
#         self.on_destroy = on_destroy

#         background_color = colors[type]

#         # Draw the rectangle with rounded corners
#         self.create_polygon(
#             8, 0,
#             100, 0,
#             192, 0,
#             200, 8,
#             200, 25,
#             200, 42,
#             192, 50,
#             100, 50,
#             8, 50,
#             0, 42,
#             0, 25,
#             0, 8,
#             smooth=True,
#             outline=background_color,
#             fill=background_color,
#             width=2
#         )

#         self.label = tk.Label(self, text=self.message, bg=colors[type], fg="black")
#         self.label.place(x=20, y=15)

#         self.after_id = self.after(self.duration, self.destroy)
#         self.bind("<Button-1>", lambda e: self.destroy())
#         self.bind("<Enter>", self.on_enter)
#         self.bind("<Leave>", self.on_leave)

#     def on_enter(self, event):
#         self.after_cancel(self.after_id)

#     def on_leave(self, event):
#         self.after_id = self.after(self.duration, self.destroy)

#     def destroy(self):
#         if self.on_destroy:
#             self.on_destroy(self)
#         super().destroy()