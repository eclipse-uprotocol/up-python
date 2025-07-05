"""
SPDX-FileCopyrightText: Copyright (c) 2023 Contributors to the
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

TRACK_FILE = "generated_proto_files.txt"

def clean_project():
    # Remove build/ directory
    if os.path.exists('build'):
        shutil.rmtree('build')
        print("Removed build/")

    # Remove dist/ directory
    if os.path.exists('dist'):
        shutil.rmtree('dist')
        print("Removed dist/")

    # Remove *.egg-info/ directories
    egg_info_directories = [d for d in os.listdir() if d.endswith('.egg-info')]
    for egg_info_directory in egg_info_directories:
        shutil.rmtree(egg_info_directory)
        print(f"Removed {egg_info_directory}/")

    # Remove generated proto files
    if os.path.exists(TRACK_FILE):
        with open(TRACK_FILE, "r") as f:
            files = [line.strip() for line in f if line.strip()]
        for file in files:
            if os.path.exists(file):
                os.remove(file)
                print(f"Deleted {file}")
            else:
                print(f"{file} not found, skipping.")
        os.remove(TRACK_FILE)
        print(f"Removed {TRACK_FILE}")
    else:
        print(f"No {TRACK_FILE} found, skipping proto cleanup.")

    # Remove __pycache__ folders recursively
    for root, dirs, _ in os.walk('.'):
        for d in dirs:
            if d == "__pycache__":
                cache_path = os.path.join(root, d)
                shutil.rmtree(cache_path)
                print(f"Removed {cache_path}")

if __name__ == "__main__":
    clean_project()
    print("Cleanup complete.")
