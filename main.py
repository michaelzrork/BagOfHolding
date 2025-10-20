import importlib.util
import subprocess
import sys
import json
import os

# CHECK TO SEE IF CUSTOMTKINTER IS INSTALLED
if importlib.util.find_spec("customtkinter") is None:
    print("\nThe package for customtkinter is not currently installed on your system.\n")
    option = input("Would you like to attempt to install customtkinter now using 'pip install customtkinter'? (y/n): ").strip().lower()
    if option == "y":
        print("\nBeginning install of customtkinter\n")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "customtkinter"])
            print("\nInstallation of customtkinter succeeded. Continuing with program.\n")
        except subprocess.CalledProcessError:
            print("\ncustomtkinter installation failed. Please try manually with: pip install customtkinter\nProgram aborted.")
            sys.exit(1)
    else:
        print("\ncustomtkinter is required to run this program. Please run 'pip install customtkinter' and then try again.")
        sys.exit(1)

# ------------------ BAG OF HOLDING APP ------------------

import customtkinter as ctk

DATA_FILE = "bag_data.json"

def load_items():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return ["book", "computer", "keys", "travel mug"]

def save_items():
    with open(DATA_FILE, "w") as f:
        json.dump(itemsInBackpack, f)

itemsInBackpack = load_items()

class BagOfHoldingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bag of Holding")
        self.root.minsize(400, 400)

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.main_frame = ctk.CTkFrame(self.root, fg_color="#e5e7eb")  # cool gray background
        self.main_frame.pack(fill="both", expand=True)

        self.success_label = None
        self.prompt_overlay = None
        self.bottom_button_frame = None
        self.check_button = None
        self.yes_btn = None
        self.no_btn = None
        self.confirm_exit_frame = None
        self.blur_frame = None
        self.save_edit_function = None
        self.cancel_edit_function = None

        self.awaiting_add_confirmation = False
        self.check_mode = False
        self.add_mode = False

        self.create_main_menu()
        self.root.bind("<Escape>", self.handle_escape)
        self.root.bind("<Return>", self.handle_enter)

    def create_main_menu(self):
        self.clear_frame()
        self.add_mode = False
        self.check_mode = False

        self.current_screen = "main"

        ctk.CTkLabel(self.main_frame, text="What would you like to do?", text_color="black", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)

        self.styled_button("Add an item", self.add_item_ui)
        self.styled_button("Check for an item", self.check_item_ui)
        self.styled_button("Bag of Holding Contents", self.display_items)

        self.place_bottom_buttons(main_menu=True)

    def add_item_ui(self):
        self.clear_frame()
        self.add_mode = True
        self.check_mode = False
        self.current_screen = "add"

        ctk.CTkLabel(self.main_frame, text="Enter item to add:", text_color="black", font=ctk.CTkFont(size=14)).pack(pady=(10, 0))

        self.item_entry = ctk.CTkEntry(self.main_frame, font=ctk.CTkFont(size=12))
        self.item_entry.pack(pady=10, padx=40, fill="x", ipady=8)
        self.item_entry.focus()

        self.add_button = self.styled_button("Add Item", self.add_item)

        self.success_label = ctk.CTkLabel(self.main_frame, text="", text_color="green", font=ctk.CTkFont(size=12))
        self.success_label.pack(pady=(6, 2))

        self.place_bottom_buttons()

    def add_item(self, event=None):
        item = self.item_entry.get().strip()
        lower_case_item = item.lower()
        if not item:
            self.success_label.configure(text="")
            return
        
        lower_case_backpack = []
        for i in itemsInBackpack:
            lower_case_backpack.append(i.lower())            
            
        if lower_case_item in lower_case_backpack:
            self.success_label.configure(text=f"'{item}' is already in the Bag of Holding.", text_color="darkred")
        else:
            itemsInBackpack.append(item)
            save_items()
            self.success_label.configure(text=f"'{item}' has been added to your Bag of Holding.", text_color="green")

        self.item_entry.delete(0, "end")
        self.item_entry.focus()

    def check_item_ui(self):
        self.clear_frame()
        self.check_mode = True
        self.add_mode = False
        self.current_screen = "check"

        ctk.CTkLabel(self.main_frame, text="Enter item to check:", text_color="black", font=ctk.CTkFont(size=14)).pack(pady=(10, 0))

        self.check_entry = ctk.CTkEntry(self.main_frame, font=ctk.CTkFont(size=12))
        self.check_entry.pack(pady=10, padx=40, fill="x", ipady=8)
        self.check_entry.focus()

        self.check_button = self.styled_button("Check Item", self.check_item)

        self.success_label = ctk.CTkLabel(self.main_frame, text="", text_color="green", font=ctk.CTkFont(size=12))
        self.success_label.pack(pady=(6, 2))

        self.place_bottom_buttons()


    def check_item(self, event=None):
        if self.awaiting_add_confirmation:
            return

        item = self.check_entry.get().strip()
        if not item:
            self.success_label.configure(text="")
            return
        
        lower_case_backpack = []
        for i in itemsInBackpack:
            lower_case_backpack.append(i.lower())   
            
        if item.lower() in lower_case_backpack:
            self.success_label.configure(text=f"Yes, '{item}' is in the Bag of Holding.", text_color="green")
        else:
            self.check_button.pack_forget()
            self.show_add_overlay(item)

        self.check_entry.delete(0, "end")
        self.check_entry.focus()

    def show_add_overlay(self, item):
        self.awaiting_add_confirmation = True

        self.blur_frame = ctk.CTkFrame(self.main_frame, fg_color="#e5e7eb", width=self.main_frame.winfo_width(), height=self.main_frame.winfo_height())
        self.blur_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.blur_frame.lift()

        self.prompt_overlay = ctk.CTkFrame(self.main_frame, fg_color="#e5e7eb", corner_radius=20)
        self.prompt_overlay.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            self.prompt_overlay,
            text=f"No, '{item}' is not in the Bag of Holding.\nWould you like to add it?",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="black",
            justify="center"
        ).pack(pady=20, padx=20)

        btn_container = ctk.CTkFrame(self.prompt_overlay, fg_color="#e5e7eb")
        btn_container.pack(pady=10)

        self.yes_btn = ctk.CTkButton(
            btn_container,
            text="Yes",
            command=lambda: self.add_checked_item(item),
            corner_radius=20,
            fg_color="#28a745",
            hover_color="#218838",
            text_color="white",
            font=ctk.CTkFont(size=12),
            width=100,
            height=45
        )
        self.yes_btn.pack(side="left", padx=10)
        self.yes_btn.focus()

        self.no_btn = ctk.CTkButton(
            btn_container,
            text="No",
            command=self.cancel_checked_item,
            corner_radius=20,
            fg_color="#6c757d",
            hover_color="#5a6268",
            text_color="white",
            font=ctk.CTkFont(size=12),
            width=100,
            height=45
        )
        self.no_btn.pack(side="left", padx=10)

    def add_checked_item(self, item):
        itemsInBackpack.append(item)
        save_items()
        self.success_label.configure(text=f"'{item}' has been added to your Bag of Holding.", text_color="green")
        if self.prompt_overlay:
            self.prompt_overlay.destroy()
            self.prompt_overlay = None
        if self.blur_frame:
            self.blur_frame.destroy()
            self.blur_frame = None
        self.awaiting_add_confirmation = False
        self.check_button.pack(pady=6, padx=40, fill="x")
        self.success_label.pack_forget()
        self.success_label.pack(pady=(6, 2))
        self.check_entry.focus()

    def cancel_checked_item(self, event=None):
        self.success_label.configure(text="Nothing was added.", text_color="darkred")
        if self.prompt_overlay:
            self.prompt_overlay.destroy()
            self.prompt_overlay = None
        if self.blur_frame:
            self.blur_frame.destroy()
            self.blur_frame = None
        self.awaiting_add_confirmation = False
        self.check_button.pack(pady=6, padx=40, fill="x")
        self.success_label.pack_forget()
        self.success_label.pack(pady=(6, 2))
        self.check_entry.focus()

    def handle_enter(self, event=None):
        if self.awaiting_add_confirmation and self.yes_btn:
            self.yes_btn.invoke()
        elif self.confirm_exit_frame:
            self.root.quit()
        elif self.add_mode and hasattr(self, 'item_entry') and self.item_entry.focus_get():
            self.add_item()
        elif self.check_mode and hasattr(self, 'check_entry') and self.check_entry.focus_get():
            self.check_item()
        elif getattr(self, 'current_screen', None) == "edit" and self.save_edit_function:
            self.save_edit_function()


    def display_items(self):
        self.clear_frame()
        self.current_screen = "display"

        ctk.CTkLabel(self.main_frame, text="Your Bag of Holding", text_color="black", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)

        if not itemsInBackpack:
            ctk.CTkLabel(
                self.main_frame,
                text="Bag of Holding is currently empty.",
                text_color="darkred",
                font=ctk.CTkFont(size=12)
            ).pack(pady=10)
        else:
            scroll_frame = ctk.CTkScrollableFrame(self.main_frame, fg_color="#e5e7eb")
            scroll_frame.pack(padx=40, pady=0, fill="both", expand=True)

            for idx, item in enumerate(itemsInBackpack):
                bg_color = "#f9fafb" if idx % 2 == 0 else "#d1d5db"
                row_frame = ctk.CTkFrame(scroll_frame, fg_color=bg_color, height=35)
                row_frame.pack(fill="x", pady=1, padx=1)

                item_label = ctk.CTkLabel(
                    row_frame,
                    text=item,
                    text_color="black",
                    anchor="w",
                    font=ctk.CTkFont(size=12),
                    height=50
                )
                item_label.pack(side="left", padx=10, pady=4, fill="x", expand=True)

                delete_btn = ctk.CTkButton(
                    row_frame,
                    text="🗑",
                    width=30,
                    height=30,
                    font=ctk.CTkFont(size=12),
                    command=lambda i=item: self.delete_item(i),
                    fg_color="#6c757d",
                    hover_color="#c82333",
                    text_color="white"
                )
                delete_btn.pack(side="right", padx=5)

                edit_btn = ctk.CTkButton(
                    row_frame,
                    text="✎",
                    width=30,
                    height=30,
                    font=ctk.CTkFont(size=12),
                    command=lambda i=item: self.edit_item(i),
                    fg_color="#6c757d",
                    hover_color="#0b5ed7",
                    text_color="white"
                )
                edit_btn.pack(side="right", padx=5)

        self.place_bottom_buttons()

        

    def edit_item(self, item):
        self.clear_frame()
        self.current_screen = "edit"

        ctk.CTkLabel(self.main_frame, text=f"Editing: {item}", text_color="black", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=20)

        self.edit_entry = ctk.CTkEntry(self.main_frame, font=ctk.CTkFont(size=12))
        self.edit_entry.insert(0, item)
        self.edit_entry.pack(pady=10, padx=40, fill="x", ipady=8)
        self.edit_entry.focus()

        self.success_label = ctk.CTkLabel(self.main_frame, text="", text_color="darkred", font=ctk.CTkFont(size=12))
        self.success_label.pack()

        button_frame = ctk.CTkFrame(self.main_frame, fg_color="#e5e7eb")
        button_frame.pack(pady=10)

        def save():
            new_item = self.edit_entry.get().strip()
            if new_item and new_item != item:
                if new_item in itemsInBackpack:
                    self.success_label.configure(text=f"'{new_item}' already exists.")
                else:
                    idx = itemsInBackpack.index(item)
                    itemsInBackpack[idx] = new_item
                    save_items()
                    self.display_items()
            else:
                self.display_items()

        def cancel():
            self.display_items()
            
        self.save_edit_function = save
        self.cancel_edit_function = cancel

        ctk.CTkButton(button_frame, text="Save", command=save,
                    corner_radius=20, fg_color="#28a745", hover_color="#218838", text_color="white",
                    font=ctk.CTkFont(size=12), width=100, height=45).pack(side="left", padx=10)

        ctk.CTkButton(button_frame, text="Cancel", command=cancel,
                    corner_radius=20, fg_color="#6c757d", hover_color="#5a6268", text_color="white",
                    font=ctk.CTkFont(size=12), width=100, height=45).pack(side="left", padx=10)


    def delete_item(self, item):
        
        lower_case_backpack = []
        for i in itemsInBackpack:
            lower_case_backpack.append(i.lower())   
            
        if item.lower() in lower_case_backpack:
            itemsInBackpack.remove(item)
            save_items()
            self.display_items()

    def styled_button(self, text, command, fg_color="#0056b3", hover_color="#004080"):
        btn = ctk.CTkButton(self.main_frame, text=text, command=command, corner_radius=20,
                            fg_color=fg_color, hover_color=hover_color,
                            font=ctk.CTkFont(size=12), text_color="white", height=45)
        btn.pack(pady=6, padx=40, fill="x")
        return btn

    def place_bottom_buttons(self, main_menu=False):
        if self.bottom_button_frame:
            self.bottom_button_frame.destroy()

        self.bottom_button_frame = ctk.CTkFrame(self.main_frame, fg_color="#e5e7eb")
        self.bottom_button_frame.pack(side="bottom", pady=10, padx=40, fill="x")

        if not main_menu:
            ctk.CTkButton(self.bottom_button_frame, text="Back to Main Menu", command=self.create_main_menu,
                          corner_radius=20, font=ctk.CTkFont(size=12),
                          fg_color="#6c757d", hover_color="#5a6268", text_color="white", height=45).pack(side="left", expand=True, fill="x", padx=(0, 5))

        ctk.CTkButton(self.bottom_button_frame, text="Exit", command=self.confirm_exit,
                      corner_radius=20, font=ctk.CTkFont(size=12),
                      fg_color="#dc3545", hover_color="#c82333", text_color="white", height=45).pack(side="left", expand=True, fill="x", padx=(5, 0))

    def confirm_exit(self):
        self.clear_frame()
        self.confirm_exit_frame = ctk.CTkFrame(self.main_frame, fg_color="#e5e7eb")
        self.confirm_exit_frame.pack(expand=True)

        ctk.CTkLabel(self.confirm_exit_frame, text="Are you sure you want to exit?", text_color="black", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=20)

        btn_frame = ctk.CTkFrame(self.confirm_exit_frame, fg_color="#e5e7eb")
        btn_frame.pack()

        exit_btn = ctk.CTkButton(btn_frame, text="Exit", command=self.root.quit,
                                 corner_radius=20, font=ctk.CTkFont(size=12),
                                 fg_color="#dc3545", hover_color="#c82333", text_color="white", height=45, width=100)
        exit_btn.pack(side="left", padx=10)
        exit_btn.focus()

        cancel_btn = ctk.CTkButton(btn_frame, text="Cancel", command=self.create_main_menu,
                                   corner_radius=20, font=ctk.CTkFont(size=12),
                                   fg_color="#6c757d", hover_color="#5a6268", text_color="white", height=45, width=100)
        cancel_btn.pack(side="left", padx=10)

    def handle_escape(self, event=None):
        if self.prompt_overlay:
            self.cancel_checked_item()
        elif self.confirm_exit_frame:
            self.create_main_menu()
        elif getattr(self, 'current_screen', None) == "edit" and self.cancel_edit_function:
            self.cancel_edit_function()
        elif getattr(self, 'current_screen', None) == "main":
            self.confirm_exit()
        else:
            self.create_main_menu()


    def clear_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        self.confirm_exit_frame = None
        self.prompt_overlay = None
        self.blur_frame = None
        self.save_edit_function = None
        self.cancel_edit_function = None


if __name__ == "__main__":
    root = ctk.CTk()
    app = BagOfHoldingApp(root)
    root.mainloop()
