import csv
import os
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk


class ViewConvertTiresiasToGargantext:
    def __init__(self, parent):
        self.parent = parent

        self.window_title = tk.Label(
            self.parent, text="Tiresias to Gargantext", font=("Helvetica", 12, "bold")
        )
        self.window_title.pack(fill=tk.X)

        self.frame1 = tk.Frame(self.parent)
        self.frame1.pack(anchor=tk.W, padx=5, pady=2)

        self.csv_entry = tk.Entry(self.frame1, width=52)
        self.csv_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        self.bn_csv = tk.Button(
            self.frame1, text="Select files", command=self.sel_files
        )
        self.bn_csv.pack(side=tk.RIGHT, padx=5)

        self.frame2 = tk.Frame(self.parent)
        self.frame2.pack(anchor=tk.W, padx=5, pady=2)

        self.dir_entry = tk.Entry(self.frame2, width=52)
        self.dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        self.bn_dir = tk.Button(
            self.frame2, text="Select directory", command=self.sel_dir
        )
        self.bn_dir.pack(side=tk.RIGHT, padx=5)

        self.frame3 = tk.Frame(self.parent)
        self.frame3.pack(anchor=tk.W, padx=5, pady=2)

        self.bn_convert = tk.Button(self.frame3, text="Convert", command=self.convert)
        self.bn_convert.pack(side=tk.RIGHT, padx=5)

        self.frame4 = tk.Frame(self.parent)
        self.frame4.pack(anchor=tk.W, padx=5, pady=2)

        self.progressbar = ttk.Progressbar(
            self.frame4,
            orient="horizontal",
            length=100,
            mode="determinate",
        )
        self.progressbar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        self.progress_label = tk.Label(self.frame4, text="0%")
        self.progress_label.pack(side=tk.RIGHT, padx=5)

        self.progressbar["value"] = 0
        self.progressbar["maximum"] = 100
        self.progress_label["text"] = "0%"

    def sel_files(self):
        file_paths = filedialog.askopenfilenames(
            title="Select one or more files",
            initialdir=os.path.expanduser("~"),
            filetypes=[("CSV Files", "*.csv")],
        )
        if file_paths:
            self.csv_entry.delete(0, tk.END)
            self.csv_entry.insert(0, "; ".join(file_paths))

    def sel_dir(self):
        dir_path = filedialog.askdirectory(
            title="Select a directory",
            initialdir=os.path.expanduser("~"),
        )
        if dir_path:
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, dir_path)

    def convert(self):
        file_paths = self.csv_entry.get()
        output_dir = self.dir_entry.get()

        if not file_paths or not output_dir:
            messagebox.showerror("Error", "Please select a file and directory!")
            return

        file_paths = file_paths.split("; ")

        for file_path in file_paths:
            try:
                with open(file_path, "r", encoding="ISO-8859-1") as infile:
                    reader = csv.reader(infile, delimiter=";")
                    converted_data = []

                    next(reader)

                    for row in reader:
                        if len(row) > 1:
                            title = row[2].strip()  # HD - title
                            source = row[7].strip()  # SN - source
                            publication_info = row[6].strip()  # CR - publication info
                            abstract = row[14].strip()  # TD - abstract
                            authors = row[3].strip()  # BY - authors

                            publication_parts = publication_info.split("/")
                            if len(publication_parts) == 3:
                                publication_year = publication_parts[2]
                                publication_month = publication_parts[1]
                                publication_day = publication_parts[0]
                            else:
                                publication_year = publication_month = (
                                    publication_day
                                ) = ""

                            converted_row = {
                                "publication_day": publication_day,
                                "publication_month": publication_month,
                                "publication_year": publication_year,
                                "authors": authors,
                                "title": title,
                                "source": source,
                                "abstract": abstract,
                            }

                            converted_data.append(converted_row)

                output_file = os.path.join(
                    output_dir,
                    f"gargantext_{os.path.basename(file_path).replace('.csv', '.tsv')}",
                )
                with open(output_file, "w", encoding="utf-8", newline="") as outfile:
                    fieldnames = [
                        "publication_day",
                        "publication_month",
                        "publication_year",
                        "authors",
                        "title",
                        "source",
                        "abstract",
                    ]
                    writer = csv.DictWriter(
                        outfile, fieldnames=fieldnames, delimiter="\t"
                    )

                    writer.writeheader()
                    for row in converted_data:
                        writer.writerow(row)

                self.progressbar["value"] = 100
                self.progress_label["text"] = "100%"
                messagebox.showinfo(
                    "Success", f"Conversion complete! Saved to {output_file}"
                )

            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {str(e)}")
                self.progressbar["value"] = 0
                self.progress_label["text"] = "0%"
