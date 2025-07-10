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
    # Directories to remove
    directories_to_remove = ["build", "dist", "htmlcov", ".pytest_cache"]

    # Add *.egg-info dynamically
    directories_to_remove.extend([d for d in os.listdir() if d.endswith('.egg-info')])

    # Remove listed directories if they exist
    for directory in directories_to_remove:
        if os.path.exists(directory):
            shutil.rmtree(directory)
            print(f"Removed {directory}/")

    # Remove generated proto files
    if os.path.exists(TRACK_FILE):
        with open(TRACK_FILE, "r") as f:
            files = [line.strip() for line in f if line.strip()]
        for file in files:
            if os.path.exists(file):
                os.remove(file)
