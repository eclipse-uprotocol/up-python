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
import re
import shutil
import subprocess

import git
from git import Repo

REPO_URL = "https://github.com/eclipse-uprotocol/up-spec.git"
PROTO_REPO_DIR = os.path.abspath("../target")
TAG_NAME = "main"
PROTO_OUTPUT_DIR = os.path.abspath("../uprotocol/proto")
MAVEN_COMMAND = "mvn protobuf:compile-python"


def clone_or_pull():
    try:
        repo = Repo.clone_from(REPO_URL, PROTO_REPO_DIR)
        print(
            f"Repository cloned successfully from {REPO_URL} "
            f"to {PROTO_REPO_DIR}"
        )
        # Checkout the specific tag
        repo.git.checkout(TAG_NAME)
    except git.exc.GitCommandError:
        try:
            git_pull_command = ["git", "pull", "origin", TAG_NAME]
            subprocess.run(git_pull_command, cwd=PROTO_REPO_DIR, check=True)
            print("Git pull successful after clone failure.")
        except subprocess.CalledProcessError as pull_error:
            print(f"Error during Git pull: {pull_error}")


def execute_maven_command():
    try:
        current_working_dir = os.path.join(os.getcwd(), PROTO_REPO_DIR)
        print(f"Current working directory: {current_working_dir}")
        with subprocess.Popen(
            MAVEN_COMMAND,
            cwd=current_working_dir,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        ) as process:
            stdout, stderr = process.communicate()
            print(stdout)

            if process.returncode != 0:
                print(f"Error: {stderr}")
            else:
                print("Maven command executed successfully.")
                src_directory = os.path.join(
                    os.getcwd(),
                    PROTO_REPO_DIR,
                    "target",
                    "generated-sources",
                    "protobuf",
                    "python",
                )

                shutil.copytree(
                    src_directory, PROTO_OUTPUT_DIR, dirs_exist_ok=True
                )
                process_python_protofiles(PROTO_OUTPUT_DIR)
    except Exception as e:
        print(f"Error executing Maven command: {e}")


def replace_in_file(file_path, search_pattern, replace_pattern):
    with open(file_path, "r") as file:
        file_content = file.read()

    updated_content = re.sub(search_pattern, replace_pattern, file_content)

    with open(file_path, "w") as file:
        file.write(updated_content)


def process_python_protofiles(directory):
    for root, dirs, files in os.walk(directory):
        create_init_py(root)
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                replace_in_file(
                    file_path,
                    r"from uprotocol.v1 import ",
                    "import uprotocol.proto.uprotocol.v1.",
                )
                replace_in_file(
                    file_path,
                    r"from uprotocol import ",
                    "import uprotocol.proto.uprotocol.",
                )
                replace_in_file(
                    file_path,
                    r"import uoptions_pb2",
                    "import uprotocol.proto.uprotocol.uoptions_pb2",
                )


def create_init_py(directory):
    init_file_path = os.path.join(directory, "__init__.py")

    # Check if the file already exists
    if not os.path.exists(init_file_path):
        # Create an empty __init__.py file
        with open(init_file_path, "w"):
            pass


def execute():
    clone_or_pull()
    execute_maven_command()


if __name__ == "__main__":
    execute()
