import tkinter as tk
from tkinter import filedialog, messagebox
from monitor import monitor
from watchdog.observers import Observer

observer: Observer = None

def browse_repository_folder():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        repo_folder_entry.delete(0, tk.END)
        repo_folder_entry.insert(0, folder_selected)


def browse_figures_folder():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        figures_folder_entry.delete(0, tk.END)
        figures_folder_entry.insert(0, folder_selected)


def start_process():
    global observer
    if observer is None:
        observer = monitor(log_textbox=log_textbox, repoFolder=repo_folder_entry.get(), localFolder=figures_folder_entry.get())
        if observer is not None:
            log_textbox.insert(tk.END, "Process started...\n")
    else:
        log_textbox.insert(tk.END, "ERROR: There is already an active process.\n")


def stop_process():
    global observer
    if observer is not None:
        observer.stop()
        log_textbox.insert(tk.END, "Process stopped.\n")
    else:
        log_textbox.insert(tk.END, "ERROR: No active process found.\n")


def save_log():
    log_data = log_textbox.get("1.0", tk.END)
    if log_data.strip():  # Check if the log is not empty
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, 'w') as file:
                file.write(log_data)
            messagebox.showinfo("Success", "Log saved successfully.")
    else:
        messagebox.showwarning("Warning", "The log is empty. Nothing to save.")


# Initialize the main window
root = tk.Tk()
root.title("Figure Synchronization Tool")

# Repository Folder
tk.Label(root, text="Repository Folder:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
repo_folder_entry = tk.Entry(root, width=50)
repo_folder_entry.grid(row=0, column=1, padx=5, pady=5)
tk.Button(root, text="Explore", command=browse_repository_folder).grid(row=0, column=2, padx=5, pady=5)

# Local Figures Folder
tk.Label(root, text="Local Figures Folder:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
figures_folder_entry = tk.Entry(root, width=50)
figures_folder_entry.grid(row=1, column=1, padx=5, pady=5)
tk.Button(root, text="Explore", command=browse_figures_folder).grid(row=1, column=2, padx=5, pady=5)

# Start and Stop Buttons
tk.Button(root, text="Start", command=start_process).grid(row=2, column=0, padx=5, pady=5)
tk.Button(root, text="Stop", command=stop_process).grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

# Log Textbox
tk.Label(root, text="Log:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
log_textbox = tk.Text(root, height=10, width=60)
log_textbox.grid(row=4, column=0, columnspan=3, padx=5, pady=5)

# Save Log Button
tk.Button(root, text="Save Log", command=save_log).grid(row=5, column=0, columnspan=3, pady=10)

# Start the GUI event loop
root.mainloop()
