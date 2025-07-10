"""
SPDX-FileCopyrightText: Copyright (c) 2025 Contributors to the
Eclipse Foundation

See the NOTICE file(s) distributed with this work for additional
information regarding copyright ownership.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
SPDX-FileType: SOURCE
SPDX-License-Identifier: Apache-2.0
"""

import os
import shutil
from config import TRACK_FILE


def clean_project():
    # -----------------------------------
    # Remove known build and cache folders
    # -----------------------------------
    directories_to_remove = ["build", "dist", "htmlcov", ".pytest_cache"]
    directories_to_remove.extend([d for d in os.listdir() if d.endswith('.egg-info')])

    for directory in directories_to_remove:
        if os.path.exists(directory):
            shutil.rmtree(directory)
            print(f"Removed directory: {directory}/")

    # -----------------------------------
    # Remove generated proto files
    # -----------------------------------
    if os.path.exists(TRACK_FILE):
        with open(TRACK_FILE, "r") as f:
            files = [line.strip() for line in f if line.strip()]

        for file in files:
            # Normalize path to avoid './' issues
            file_path = file.lstrip("./")
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"Deleted file: {file_path}")
            else:
                print(f"File not found, skipping: {file_path}")

        # Remove the tracking file itself
        os.remove(TRACK_FILE)
        print(f"Removed tracking file: {TRACK_FILE}")
    else:
        print(f"No {TRACK_FILE} found, skipping proto cleanup.")

    # -----------------------------------
    # Remove all __pycache__ directories
    # -----------------------------------
    for root, dirs, _ in os.walk("."):
        for d in dirs:
            if d == "__pycache__":
                cache_path = os.path.join(root, d)
                shutil.rmtree(cache_path)
                print(f"Removed __pycache__: {cache_path}")

if __name__ == "__main__":
    clean_project()
