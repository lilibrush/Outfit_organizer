import os
import json
import tkinter as tk
from PIL import Image, ImageTk

CATEGORIES = ['accessories', 'tops', 'bottoms', 'shoes', 'bag']
IMAGE_DIR = 'outfits'
SAVE_FILE = 'saved_outfits.json'
MAX_HEIGHT = 120
MAX_WIDTH = 160

class OutfitApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Outfit Scroller")
        self.frames = {}
        self.image_labels = {}
        self.image_paths = {}
        self.index = {}
        self.saved_data = self.load_saved_outfits()

        self.current_page = None
        self.build_main_page()
        self.build_browse_page()

        self.switch_page("main")

    def switch_page(self, page_name):
        if self.current_page:
            self.frames[self.current_page].pack_forget()
        self.current_page = page_name
        self.frames[page_name].pack(fill=tk.BOTH, expand=True)

    def build_main_page(self):
        frame = tk.Frame(self.root)
        self.frames["main"] = frame

        self.image_labels.clear()
        self.image_paths.clear()
        self.index.clear()

        for i, category in enumerate(CATEGORIES):
            self.image_paths[category] = self.load_images(category)
            self.index[category] = 0

            row = tk.Frame(frame, pady=5)
            row.grid(row=i, column=0, padx=10, sticky="w")

            img_label = tk.Label(row)
            img_label.pack(side=tk.LEFT)
            self.image_labels[category] = img_label

            btn_frame = tk.Frame(row)
            btn_frame.pack(side=tk.LEFT, padx=5)

            tk.Button(btn_frame, text="◀", command=lambda c=category: self.prev_image(c)).pack()
            tk.Button(btn_frame, text="▶", command=lambda c=category: self.next_image(c)).pack()

            tk.Label(row, text=category.capitalize(), font=("Helvetica", 12)).pack(side=tk.LEFT, padx=10)

            self.show_image(category)

        save_frame = tk.Frame(frame, pady=10)
        save_frame.grid(row=len(CATEGORIES), column=0, sticky="w", padx=10)

        tk.Label(save_frame, text="Category:").pack(side=tk.LEFT)
        self.save_entry = tk.Entry(save_frame, width=20)
        self.save_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(save_frame, text="Save Outfit", command=self.save_outfit).pack(side=tk.LEFT)
        tk.Button(save_frame, text="Browse Saved Outfits", command=lambda: self.switch_page("browse")).pack(side=tk.LEFT, padx=20)

    def build_browse_page(self):
        frame = self.frames.get("browse")
        if not frame:
            frame = tk.Frame(self.root)
            self.frames["browse"] = frame

        # Clear all widgets inside the browse frame to remove old UI
        for widget in frame.winfo_children():
            widget.destroy()

        self.browse_frame = frame
        self.category_buttons_frame = tk.Frame(frame)
        self.category_buttons_frame.pack()

        tk.Label(frame, text="Saved Categories:", font=("Helvetica", 14)).pack(pady=10)

        for cat in self.saved_data:
            tk.Button(self.category_buttons_frame, text=cat, command=lambda c=cat: self.view_saved_category(c)).pack(pady=2)

        tk.Button(frame, text="← Back to Main", command=lambda: self.switch_page("main")).pack(pady=10)


    def view_saved_category(self, category_name):
        for widget in self.browse_frame.winfo_children():
            widget.destroy()

        outfits = self.saved_data.get(category_name, [])

        if not outfits:
            tk.Label(self.browse_frame, text="No outfits saved in this category.").pack()
            tk.Button(self.browse_frame, text="← Back", command=self.build_browse_page).pack(pady=5)
            return

        self.current_outfit_index = 0
        self.current_outfits = outfits

        tk.Label(self.browse_frame, text=f"Category: {category_name}", font=("Helvetica", 14)).pack(pady=5)

        self.outfit_display_frame = tk.Frame(self.browse_frame)
        self.outfit_display_frame.pack()

        btn_row = tk.Frame(self.browse_frame)
        btn_row.pack(pady=5)

        tk.Button(btn_row, text="◀", command=self.prev_saved_outfit).pack(side=tk.LEFT)
        tk.Button(btn_row, text="▶", command=self.next_saved_outfit).pack(side=tk.LEFT)
        tk.Button(self.browse_frame, text="← Back to Categories", command=lambda: [self.build_browse_page(), self.switch_page("browse")]).pack(pady=5)


        self.show_saved_outfit()


    def show_saved_outfit(self):
        for widget in self.outfit_display_frame.winfo_children():
            widget.destroy()

        outfit = self.current_outfits[self.current_outfit_index]
        for cat in CATEGORIES:
            row = tk.Frame(self.outfit_display_frame)
            row.pack(pady=2, anchor="w")

            img_path = os.path.join(IMAGE_DIR, cat, outfit.get(cat, ''))
            if os.path.exists(img_path):
                img = Image.open(img_path)
                img = self.resize_image_to_fit(img)
                photo = ImageTk.PhotoImage(img)
                lbl = tk.Label(row, image=photo)
                lbl.image = photo
                lbl.pack(side=tk.LEFT)
            else:
                lbl = tk.Label(row, text="[Missing Image]")
                lbl.pack(side=tk.LEFT)

            tk.Label(row, text=cat.capitalize(), font=("Helvetica", 12)).pack(side=tk.LEFT, padx=10)

    def next_saved_outfit(self):
        self.current_outfit_index = (self.current_outfit_index + 1) % len(self.current_outfits)
        self.show_saved_outfit()

    def prev_saved_outfit(self):
        self.current_outfit_index = (self.current_outfit_index - 1) % len(self.current_outfits)
        self.show_saved_outfit()

    def load_saved_outfits(self):
        if not os.path.exists(SAVE_FILE):
            return {}
        with open(SAVE_FILE, 'r') as f:
            data = json.load(f)
        return data

    def save_outfit(self):
        category_name = self.save_entry.get().strip()
        if not category_name:
            print("No category name entered.")
            return

        outfit = {}
        for cat in CATEGORIES:
            if self.image_paths[cat]:
                path = self.image_paths[cat][self.index[cat]]
                outfit[cat] = os.path.basename(path)
            else:
                outfit[cat] = None

        if os.path.exists(SAVE_FILE):
            with open(SAVE_FILE, 'r') as f:
                data = json.load(f)
        else:
            data = {}

        if category_name not in data:
            data[category_name] = []

        data[category_name].append(outfit)

        with open(SAVE_FILE, 'w') as f:
            json.dump(data, f, indent=2)

        self.save_entry.delete(0, tk.END)
        self.saved_data = self.load_saved_outfits()


    def load_images(self, category):
        folder = os.path.join(IMAGE_DIR, category)
        if not os.path.exists(folder):
            return []
        return [
            os.path.join(folder, f)
            for f in sorted(os.listdir(folder))
            if f.lower().endswith(('.png', '.jpg', '.jpeg'))
        ]

    def resize_image_to_fit(self, image):
        w, h = image.size
        scale = min(MAX_WIDTH / w, MAX_HEIGHT / h, 1.0)
        return image.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)

    def show_image(self, category):
        if not self.image_paths[category]:
            self.image_labels[category].configure(image='', text="No images")
            return
        path = self.image_paths[category][self.index[category]]
        img = Image.open(path)
        img = self.resize_image_to_fit(img)
        photo = ImageTk.PhotoImage(img)
        self.image_labels[category].configure(image=photo)
        self.image_labels[category].image = photo

    def next_image(self, category):
        if not self.image_paths[category]:
            return
        self.index[category] = (self.index[category] + 1) % len(self.image_paths[category])
        self.show_image(category)

    def prev_image(self, category):
        if not self.image_paths[category]:
            return
        self.index[category] = (self.index[category] - 1) % len(self.image_paths[category])
        self.show_image(category)

if __name__ == "__main__":
    root = tk.Tk()
    app = OutfitApp(root)
    root.mainloop()
