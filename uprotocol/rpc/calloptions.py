# -------------------------------------------------------------------------
#
# Copyright (c) 2023 General Motors GTO LLC
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
# SPDX-FileType: SOURCE
# SPDX-FileCopyrightText: 2023 General Motors GTO LLC
# SPDX-License-Identifier: Apache-2.0
#
# -------------------------------------------------------------------------


class CallOptions:
    """
    This class is used when making uRPC calls to pass additional options.
    """
    TIMEOUT_DEFAULT = 10000
    """
    Default timeout of a call in milliseconds.
    """


    def __init__(self, timeout=TIMEOUT_DEFAULT, token=""):
        self.mTimeout = timeout
        self.mToken = token if token else ""


    def get_timeout(self):
        """
        Get a timeout.<br><br>
        @return:  A timeout in milliseconds.
        """
        return self.mTimeout

    def get_token(self):
        """
        Get an OAuth2 access token.<br><br>
        @return: An Optional OAuth2 access token.
        """
        return self.mToken if self.mToken else None

    def __eq__(self, other):
        if not isinstance(other, CallOptions):
            return False
        return self.mTimeout == other.mTimeout and self.mToken == other.mToken

    def __hash__(self):
        return hash((self.mTimeout, self.mToken))

    def __str__(self):
        return f"CallOptions{{mTimeout={self.mTimeout}, mToken='{self.mToken}'}}"


class CallOptionsBuilder:
    """
    Builder for constructing <code>CallOptions</code>.
    """
    TIMEOUT_DEFAULT = 10000
    DEFAULT= CallOptions(TIMEOUT_DEFAULT,'')
    def __init__(self):
        self.mTimeout = self.TIMEOUT_DEFAULT
        self.mToken = ""

    def with_timeout(self, timeout):
        """
        Add a timeout.<br><br>
        @param timeout:A timeout in milliseconds.
        @return:This builder.
        """
        self.mTimeout = timeout if timeout > 0 else self.TIMEOUT_DEFAULT
        return self

    def with_token(self, token):
        """
        Add an OAuth2 access token.<br><br>
        @param token:An OAuth2 access token.
        @return:This builder.
        """
        self.mToken = token
        return self

    def build(self):
        """
        Construct a <code>CallOptions</code> from this builder.<br><br>
        @return:A constructed <code>CallOptions</code>.
        """
        return CallOptions(self.mTimeout, self.mToken)
