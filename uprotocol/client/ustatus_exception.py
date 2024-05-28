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


class UStatusException(BaseException):
    """
    The unchecked exception which carries uProtocol error model.
    """

    def __init__(self, status, cause):
        """
        Constructs an instance.
        :param status: An error UStatus.
        :param cause: An exception that caused this one.
        """
        self.m_status = status

    def get_status(self):
        """
        Get the error status.
        :return: The error UStatus.
        """
        return self.m_status

    def get_code(self):
        """
        Get the error code.
        :return: The error UCode.
        """
        return self.m_status.code

    def get_message(self):
        """
        Get the error message.
        :return: The error message.
        """
        return self.m_status.message
