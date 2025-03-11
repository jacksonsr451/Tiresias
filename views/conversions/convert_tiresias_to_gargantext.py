import csv
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


def segment_abstract(abstract, source, author, year, month, day, parts_count):
    lines = abstract.split("\n")
    nb_lines = len(lines)

    if nb_lines == 0 or parts_count < 1:
        return []

    if nb_lines > parts_count * 10:
        parts_count = (nb_lines // 10) + (1 if nb_lines % 10 != 0 else 0)

    part_size = nb_lines // parts_count
    remainder = nb_lines % parts_count
    n = 0
    count = 1
    segmented_data = []

    for i in range(parts_count):
        part_lines = part_size + (1 if i < remainder else 0)
        doc = (
            "\n".join(lines[n : n + part_lines])
            .replace("�", "")
            .replace("", "")
            .strip()
        )

        if not doc:
            continue

        title = f"{source} : Part {count}"
        segmented_data.append(
            {
                "publication_day": day,
                "publication_month": month,
                "publication_year": year,
                "source": source,
                "authors": author,
                "title": title,
                "abstract": doc,
            }
        )
        n += part_lines
        count += 1

    return segmented_data


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

        self.parts_entry_label = tk.Label(self.frame4, text="Number of parts:")
        self.parts_entry_label.pack(side=tk.LEFT, padx=5)

        self.parts_entry = tk.Entry(self.frame4, width=10)
        self.parts_entry.insert(0, "6")
        self.parts_entry.pack(side=tk.LEFT, padx=5)

        self.frame5 = tk.Frame(self.parent)
        self.frame5.pack(anchor=tk.W, padx=5, pady=2)

        self.progressbar = ttk.Progressbar(
            self.frame5, orient="horizontal", length=100, mode="determinate"
        )
        self.progressbar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        self.progress_label = tk.Label(self.frame5, text="0%")
        self.progress_label.pack(side=tk.RIGHT, padx=5)

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
            title="Select a directory", initialdir=os.path.expanduser("~")
        )
        if dir_path:
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, dir_path)

    def convert(self):
        file_paths = self.csv_entry.get()
        output_dir = self.dir_entry.get()
        parts_count = self.parts_entry.get()

        if (
            not file_paths
            or not output_dir
            or not parts_count.isdigit()
            or int(parts_count) < 1
        ):
            messagebox.showerror(
                "Error", "Please select a file, directory, and valid number of parts!"
            )
            return

        parts_count = int(parts_count)
        file_paths = file_paths.split("; ")

        for i, file_path in enumerate(file_paths):
            try:
                with open(file_path, "r", encoding="utf8") as infile:
                    reader = csv.reader(infile, delimiter=";")
                    converted_data = []
                    next(reader)  # Skip header

                    for row in reader:
                        if len(row) > 1:
                            title = row[2].strip()
                            source = row[7].strip()
                            publication_info = row[6].strip()
                            abstract = row[14].strip()
                            authors = row[3].strip()

                            publication_parts = publication_info.split("/")
                            if len(publication_parts) == 3:
                                publication_year = publication_parts[2]
                                publication_month = publication_parts[1]
                                publication_day = publication_parts[0]
                            else:
                                publication_year = publication_month = (
                                    publication_day
                                ) = ""

                            segmented = segment_abstract(
                                abstract,
                                source,
                                authors,
                                publication_year,
                                publication_month,
                                publication_day,
                                parts_count,
                            )
                            converted_data.extend(segmented)

                output_file = os.path.join(
                    output_dir,
                    f"gargantext_{os.path.basename(file_path).replace('.csv', '.tsv')}",
                )
                with open(output_file, "w", encoding="utf-8", newline="") as outfile:
                    fieldnames = [
                        "publication_day",
                        "publication_month",
                        "publication_year",
                        "source",
                        "authors",
                        "title",
                        "abstract",
                    ]
                    writer = csv.DictWriter(
                        outfile, fieldnames=fieldnames, delimiter="\t"
                    )
                    writer.writeheader()
                    for row in converted_data:
                        writer.writerow(row)

                # Update progress bar
                progress = ((i + 1) / len(file_paths)) * 100
                self.progressbar["value"] = progress
                self.progress_label["text"] = f"{int(progress)}%"

                messagebox.showinfo(
                    "Success", f"Conversion complete! Saved to {output_file}"
                )

            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {str(e)}")
                self.progressbar["value"] = 0
                self.progress_label["text"] = "0%"
