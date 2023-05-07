"""
This was a total failure ignore this file - Aidan (05/03/2023)
"""
import tkinter as tk
from tkinter import messagebox
import json
import traceback
import logging
from geopy.geocoders import Nominatim
import pip


class Application(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Facebook Marketplace Bot")
        self.geolocator = Nominatim(user_agent="facebook_marketplace_bot")

        self.progress_bar = tk.Label(self, text="Downloading libraries...")
        self.progress_bar.pack()
        self.download_libraries()

        self.config_button = tk.Button(self, text="CONFIG", command=self.config)
        self.config_button.pack(side="left")
        self.telegram_config_button = tk.Button(
            self, text="TELEGRAM CONFIG", command=self.telegram_config
        )
        self.telegram_config_button.pack(side="right")
        self.run_button = tk.Button(self, text="RUN", command=self.run)
        self.run_button.pack(side="bottom")

    def download_libraries(self):
        try:
            self._extracted_from_download_libraries_4()
        except Exception:
            self.progress_bar.config(text="Failed to download libraries")
            messagebox.showerror("Error", "Failed to download libraries")
            logging.error(traceback.format_exc())

    # TODO Rename this here and in `download_libraries`
    def _extracted_from_download_libraries_4(self):
        # download libraries here
        pip.main(["install", "requests"])
        self.progress_bar.config(text="Downloaded requests")
        pip.main(["install", "logging"])
        self.progress_bar.config(text="Downloaded logging")
        pip.main(["install", "flask"])
        self.progress_bar.config(text="Downloaded flask")
        pip.main(["install", "geopy"])
        self.progress_bar.config(text="Downloaded geopy")
        pip.main(["install", "datetime"])
        self.progress_bar.config(text="Downloaded datetime")
        self.progress_bar.config(text="Downloaded libraries")

    def config(self):
        raise NotImplementedError()

    def telegram_config(self):
        raise NotImplementedError()

    def run(self):
        if self.run_button["text"] == "RUN":
            self.run_button.config(text="PAUSE")
            # start foo.py script here
        elif self.run_button["text"] == "PAUSE":
            self.run_button.config(text="RUN")
            # pause foo.py script here


class ConfigWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Config")
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        try:
            with open("data.json", "r") as f:
                data = json.load(f)
                self.array = data["array"]
                self.title_exclude = data["title_exclude"]
        except FileNotFoundError:
            messagebox.showerror("Error", "data.json file not found")
            logging.error("data.json file not found")
            self.destroy()
        except Exception:
            messagebox.showerror("Error", "An error occurred while reading data.json")
            logging.error(traceback.format_exc())
            self.destroy()
        self.array = data["array"]
        self.title_exclude = data["title_exclude"]

        self.array_frame = tk.LabelFrame(self, text="Array")
        self.array_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.array_boxes = []
        for i, item in enumerate(self.array):
            box = tk.Entry(self.array_frame, width=30)
            box.insert(0, item)
            box.grid(row=i, column=0, padx=5, pady=5)
            self.array_boxes.append(box)

        self.add_button = tk.Button(self.array_frame, text="+", command=self.add_box)
        self.add_button.grid(row=len(self.array_boxes), column=0, padx=5, pady=5)
        self.remove_button = tk.Button(
            self.array_frame, text="-", command=self.remove_box
        )
        self.remove_button.grid(row=len(self.array_boxes), column=0, padx=5, pady=5)

        self.title_exclude_frame = tk.LabelFrame(self, text="Title Exclude")
        self.title_exclude_frame.grid(row=0, column=1, sticky="nsew", padx=50, pady=10)
        self.title_exclude_boxes = []
        for i, item in enumerate(self.title_exclude):
            box = tk.Entry(self.title_exclude_frame, width=30)
            box.insert(0, item)
            box.grid(row=i, column=0, padx=5, pady=5)
            self.title_exclude_boxes.append(box)

        self.message_label = tk.Label(
            self,
            text="Remember: 1 minute per each query!\nIf you want results QUICK the less the better.\nOtherwise more queries, won't per se have faster results.",
            justify="center",
        )
        self.message_label.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

        self.save_button = tk.Button(self, text="SAVE", command=self.save)
        self.save_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10)
        if len(self.array) == 0:
            self.add_array()

    def remove_box(self):
        if len(self.array_boxes) > 0:
            box = self.array_boxes.pop()
            box.destroy()
            self.remove_button.grid_forget()

    def add_box(self):
        row = len(self.array_boxes)
        box = tk.Entry(self.array_frame, width=30)
        box.grid(row=row, column=0, padx=5, pady=5)
        self.array_boxes.append(box)
        self.add_button.grid(row=row + 1, column=0, padx=5, pady=5)

    def save(self):
        self.array = []
        self.array.extend(box.get() for box in self.array_boxes)
        self.title_exclude = []
        self.title_exclude.extend(box.get() for box in self.title_exclude_boxes)
        with open("data.json", "w") as f:
            json.dump(
                {"array": self.array, "title_exclude": self.title_exclude}, f, indent=4
            )


if __name__ == "__main__":
    messagebox.showinfo(
        "Welcome",
        "Hello welcome to Facebook Marketplace Bot! Press 'OK' to run the startup!",
    )
    logging.basicConfig(
        filename="log.txt",
        level=logging.DEBUG,
        format="%(asctime)s:%(levelname)s:%(message)s",
    )
    app = Application()
    app.mainloop()
