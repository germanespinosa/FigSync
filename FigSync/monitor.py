import configparser
import enum
import os
import tkinter as tk
from .git import *
import time
import argparse
import datetime
import threading
import re
import subprocess
import json

def parse_arguments():
    parser = argparse.ArgumentParser(description='File monitoring and processing Tool')
    parser.add_argument('configuration_file', type=str, help='Configuration File')
    parser.add_argument('path', type=str, help='Path to watch')
    parser.add_argument('--recursive', '-r', action='store_true', help='Include subfolders')
    args = parser.parse_args()
    return args


def log(msg, log_textbox=None):
    if log_textbox:
        log_textbox.insert(tk.END, f"{msg}\n")
    else:
        print(msg)


class ChangeHandler:
    class Action(enum.Enum):
        CREATE = 1
        UPDATE = 2
        DELETE = 3

    def __init__(self,
                 actions,
                 script,
                 log_textbox):
        self.actions = actions
        self.log_textbox = log_textbox
        self.last_file = None
        self.last_update = time.time()
        self.script = script

    def process_update(self, src_path, action: Action):
        log(f"File {action.name}: {src_path}", self.log_textbox)
        if src_path == self.last_file:  # prevent repeated events
            if time.time() - self.last_update < 1:
                return
        self.last_file = src_path
        self.last_update = time.time()
        result = subprocess.run([self.script, src_path], capture_output=True, text=True)
        log(f"finished with code {result.returncode}")  # The exit status (0 for success)
        if result.stdout:
            log(f"output: \n{result.stdout}")
        if result.stderr:
            log(f"error: \n{result.stderr}")


class Observer:
    def __init__(self,
                 path,
                 recursive,
                 handlers,
                 log_textbox=None):
        self.path = path
        self.recursive = recursive
        self.last_updates = self.query_last_updates(path=self.path)
        self.running = False
        self.thread = None
        self.handlers = handlers
        self.log_textbox = log_textbox

    def add_handler(self, pattern, handler):
        self.handlers[pattern] = handler

    def query_last_updates(self, path, last_updates=None, prefix=""):
        if last_updates is None:
            last_updates = {}
        os.listdir(path=path)
        for filename in os.listdir(path=path):
            file_path = os.path.join(path, filename)
            if self.recursive and os.path.isdir(file_path):
                self.query_last_updates(file_path, last_updates, prefix + filename + "/")
            mod_timestamp = os.path.getmtime(file_path)
            modification_time = datetime.datetime.fromtimestamp(mod_timestamp)
            last_updates[prefix + filename] = modification_time
        return last_updates

    @staticmethod
    def get_changes(old_states, new_states):
        changes = {}
        for file_path, update_time in old_states.items():
            if file_path not in new_states:
                changes[file_path] = "DELETE"
            if update_time < new_states[file_path]:
                changes[file_path] = "UPDATE"

        for file_path, update_time in new_states.items():
            if file_path not in old_states:
                changes[file_path] = "CREATE"
        return changes

    def process_changes(self, changes):
        for file_path, action in changes.items():
            for pattern, handler in self.handlers.items():
                if re.search(pattern, file_path):
                    if action in handler.actions:
                        handler.process_update(file_path)

    def __process__(self):
        while self.running:
            time.sleep(1)
            new_updates = self.query_last_updates(self.path)
            changes = self.get_changes(self.last_updates, new_updates)
            if changes:
                print("changes detected")
                self.last_updates = new_updates
                self.process_changes(changes)

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self.__process__)
        self.thread.start()


# def monitor(localFolder,
#             repoFolder,
#             log_textbox=None):
#     if not os.path.isdir(localFolder):
#         log(f"{localFolder} folder does not exist", log_textbox)
#         return None
#     if not os.path.isdir(repoFolder):
#         log(f"{repoFolder} folder does not exist", log_textbox)
#         return None
#     fig_folder = os.path.join(repoFolder, "figures")
#     if not os.path.isdir(fig_folder):
#         log(f"{fig_folder} folder does not exist", log_textbox)
#         return None
#     vector_folder = os.path.join(fig_folder, "vector")
#     if not os.path.isdir(vector_folder):
#         log(f"{vector_folder} folder does not exist", log_textbox)
#         return None
#     bitmap_folder = os.path.join(fig_folder, "bitmap")
#     if not os.path.isdir(bitmap_folder):
#         log(f"{bitmap_folder} folder does not exist", log_textbox)
#         return None
#
#     git_accessible, message = is_git_accessible()
#     if not git_accessible:
#         log("{message}", log_textbox)
#         return None
#
#     event_handler = PDFChangeHandler(vector_folder=vector_folder,
#                                      bitmap_folder=bitmap_folder,
#                                      log_textbox=log_textbox)
#     observer = Observer(path=localFolder, recursive=False)
#     observer.start()
#     return observer


def read_handlers(file_path, log_textbox=None):
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File {file_path} does not exist")
    configuration = json.load(open(file_path))
    handlers = {}
    for handler_data in configuration["handlers"]:
        actions = []
        for action_name in handler_data["actions"]:
            actions.append(ChangeHandler.Action[action_name])

        handler = ChangeHandler(actions=actions, script=handler_data["script"], log_textbox=log_textbox)
        handlers[handler_data["pattern"]] = handler
    return handlers


if __name__ == "__main__":
    try:
        args = parse_arguments()
        handlers = read_handlers(args.configuration_file)
    except argparse.ArgumentError as e:
        print("Error:", e)
        exit(1)

    observer = Observer(path=args.path,
                        recursive=args.recursive,
                        handlers=handlers)

    if observer is not None:
        observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.running = False
            observer.thread.join()
