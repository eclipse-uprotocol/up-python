"""
SPDX-FileCopyrightText: 2025 Contributors to the Eclipse Foundation

See the NOTICE file(s) distributed with this work for additional
information regarding copyright ownership.

This program and the accompanying materials are made available under the
terms of the Apache License Version 2.0 which is available at

    http://www.apache.org/licenses/LICENSE-2.0

SPDX-License-Identifier: Apache-2.0
"""

from grpc_tools import protoc
import os
import google.protobuf

PROTO_DIR = "up-spec/up-core-api"
OUTPUT_DIR = "."
TRACK_FILE = "generated_proto_files.txt"

# Add google protobuf include path
import pkg_resources
PROTOBUF_INCLUDE = pkg_resources.resource_filename('grpc_tools', '_proto')


def generate_all_protos():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    generated_files = []

    for root, _, files in os.walk(PROTO_DIR):
        for file in files:
            if file.endswith(".proto"):
                proto_file = os.path.join(root, file)
                print(f"Compiling {proto_file}...")
                result = protoc.main([
                    '',
                    f'-I{PROTO_DIR}',
                    f'-I{PROTOBUF_INCLUDE}',   # <--- Add this
                    f'--python_out={OUTPUT_DIR}',
                    f'--grpc_python_out={OUTPUT_DIR}',
                    proto_file
                ])
                if result != 0:
                    print(f"Failed to compile {proto_file}")
                else:
                    print(f"Compiled {proto_file} successfully.")

                    base_name = os.path.splitext(file)[0]
                    rel_dir = os.path.relpath(root, PROTO_DIR)
                    output_dir = os.path.join(OUTPUT_DIR, rel_dir)

                    generated_files.append(os.path.join(output_dir, f"{base_name}_pb2.py"))
                    generated_files.append(os.path.join(output_dir, f"{base_name}_pb2_grpc.py"))

    # Ensure __init__.py in all generated proto folders
    for root, dirs, files in os.walk(OUTPUT_DIR):
        init_file = os.path.join(root, '__init__.py')
        if not os.path.exists(init_file):
            open(init_file, 'a').close()
            print(f"Created {init_file}")
            generated_files.append(init_file)

    # Write generated files to track file
    with open(TRACK_FILE, "w") as f:
        for path in generated_files:
            f.write(f"{path}\n")
    print(f"Tracked {len(generated_files)} generated files in {TRACK_FILE}")

if __name__ == "__main__":
    generate_all_protos()
