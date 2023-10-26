# -------------------------------------------------------------------------

# Copyright (c) 2023 General Motors GTO LLC

# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at

#    http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

# -------------------------------------------------------------------------

import ipaddress
from typing import Optional


class UAuthority:
    """
    An Authority represents the deployment location of a specific Software Entity.<br>Data representation of an
    <b>Authority</b>.<br> An Authority consists of a device, a domain and a micro version in the form of an IP
    Address.<br>Device and domain names are used as part of the URI for device and service discovery. Optimized micro
    versions of the UUri will use the IP Address.<br>Devices will be grouped together into realms of Zone of
    Authority.<br>
    """
    EMPTY = None

    def __init__(self, device: str, domain: str, address: ipaddress.IPv4Address, marked_remote: bool,
                 marked_resolved: bool):
        """
        Constructor for building a UAuthority.<br><br>
        @param device: The device a software entity is deployed on, such as the VCU, CCU or cloud provider. A device
        is a logical independent representation of a service bus in different execution environments. Devices will
        be grouped together into realms of Zone of Authority.
        @param domain: The domain a software entity is deployed on, such as vehicle or Cloud (PaaS).
        @param address:The device IP address of the device.
        @param marked_remote:Indicates if this UAuthority was implicitly marked as remote.
        @param marked_resolved:Indicates that this uAuthority has all the information needed to be serialised in the
        long format or the micro format of a UUri.
        """
        self.device = device.lower() if device else None
        self.domain = domain.lower() if domain else None
        self.address = address
        self.marked_remote = marked_remote
        self.marked_resolved = marked_resolved

    @staticmethod
    def local():
        """
        Static factory method for creating a local uAuthority.<br>A local uri does not contain an authority and looks
        like this:<pre> :&lt;service&gt;/&lt;version&gt;/&lt;resource&gt;#&lt;Message&gt; </pre> <br>
        @return:Returns a local uAuthority that has no domain, device, or ip address information, indicating to
        uProtocol that the uAuthority part in the UUri is relative to the sender/receiver deployment environment.
        """
        return UAuthority.EMPTY

    @staticmethod
    def long_remote(device: str, domain: str):
        """
        Static factory method for creating a remote authority supporting the long serialization information
        representation of a UUri.<br> Building a UAuthority with this method will create an unresolved uAuthority
        that can only be serialised in long UUri format. An uri with a long representation of uAUthority can be
        serialised as follows:
         <pre> //&lt;device&gt;.&lt;domain&gt;/&lt;service&gt;/&lt;version&gt;/&lt;resource&gt;#&lt;Message&gt;
         </pre>
        @param device:The device a software entity is deployed on, such as the VCU, CCU or cloud provider.
        @param domain:The domain a software entity is deployed on, such as vehicle or Cloud (PaaS). Vehicle Domain
        name <b>MUST</b> be that of the vehicle VIN.
        @return:Returns a uAuthority that contains the device and the domain and can only be serialized in long UUri
        format.
        """
        return UAuthority(device, domain, None, True, False)

    @staticmethod
    def micro_remote(address: ipaddress.IPv4Address):
        """
        Static factory method for creating a remote authority supporting the micro serialization information
        representation of a UUri.<br>Building a UAuthority with this method will create an unresolved uAuthority that
        can only be serialised in micro UUri format.<br><br>
        @param address:The ip address of the device a software entity is deployed on.
        @return:Returns a uAuthority that contains only the internet address of the device, and can only be
        serialized in micro UUri format.
        """
        return UAuthority(None, None, address, True, False)

    @staticmethod
    def resolved_remote(device: str, domain: str, address: ipaddress.IPv4Address):
        """
        Static factory method for creating a remote authority that is completely resolved with name, device and ip
        address of the device.<br>Building a UAuthority with this method will enable serialisation in both UUri
        formats, long UUri format and micro UUri format. Note that in the case of missing data, this will not fail,
        but simply create a UAuthority that is not resolved.<br><br>
        @param device:The device name for long serialization of UUri.
        @param domain:The domain name for long serialization of UUri.
        @param address:The IP address for the device, for micro serialization of UUri.
        @return:Returns a uAuthority that contains all resolved data and so can be serialized into a long UUri or a
        micro UUri.
        """
        resolved = device is not None and device.strip() != "" and address is not None
        return UAuthority(device, domain, address, True, resolved)

    @staticmethod
    def empty():
        """
        Static factory method for creating an empty uAuthority, to avoid working with null<br>Empty uAuthority is
        still serializable in both long and micro UUri formats, and will be as local to the current deployment
        environment.<br><br>
        @return:Returns an empty authority that has no domain, device, or device ip address information.
        """
        return UAuthority.EMPTY

    def is_remote(self) -> bool:
        """
        Support for determining if this uAuthority defines a deployment that is defined as remote.<br><br>
        @return:Returns true if this uAuthority is remote, meaning it contains information for serialising a long
        UUri or a micro UUri.
        """
        return self.is_marked_Remote()

    #
    def is_local(self) -> bool:
        """
        Support for determining if this uAuthority is defined for a local deployment.<br><br>
        @return:Returns true if this uAuthority is local, meaning does not contain a device/domain for long UUri or
        information for micro UUri.
        """
        return self.is_empty() and not self.is_marked_Remote()

    def device(self) -> Optional[str]:
        """
        Accessing an optional device of the uAuthority.<br><br>
        @return:Returns the device a software entity is deployed on, such as the VCU, CCU or cloud provider.
        """
        return self.device if self.device else None

    def domain(self) -> Optional[str]:
        """
        Accessing an optional domain of the uAuthority.<br><br>
        @return:Returns the domain a software entity is deployed on, such as vehicle or backoffice.
        """
        return self.domain if self.domain else None

    def address(self) -> Optional[ipaddress.IPv4Address]:
        """
        Accessing an optional IP address configuration of the uAuthority.<br><br>
        @return:eturns the device IP address.
        """
        try:
            return ipaddress.IPv4Address(self.address)
        except ValueError:
            return None

    def is_marked_remote(self) -> bool:
        """
        Support for determining if this uAuthority was configured to be remote.<br><br>
        @return:Returns true if this uAuthority is explicitly configured remote deployment.
        """
        return self.marked_remote

    def is_resolved(self) -> bool:
        """
        Indicates that this UAuthority has already been resolved.<br>A resolved UAuthority means that it has all the
        information needed to be serialised in the long format or the micro format of a UUri.<br><br>
        @return:Returns true if this UAuthority is resolved with all the information needed to be serialised in the
        long format or the micro format of a UUri.
        """
        return self.marked_resolved

    def is_long_form(self) -> bool:
        """
        Determine if the UAuthority can be used to serialize a UUri in long format.<br><br>
        @return:Returns true if the UAuthority can be used to serialize a UUri in long format.
        """
        return self.is_local() or self.device is not None

    def is_micro_form(self) -> bool:
        """
        Determine if the UAuthority can be used to serialize a UUri in micro format.<br><br>
        @return:Returns true if the uAuthority can be serialized a UUri in micro format.
        """
        return self.is_local() or self.address is not None

    def is_empty(self) -> bool:
        return all([self.domain is None or self.domain.strip() == "", self.device is None or self.device.strip() == "",
                    self.address is None])

    def __eq__(self, other):
        if not isinstance(other, UAuthority):
            return False
        return (
                self.marked_remote == other.marked_remote and self.device == other.device and self.domain ==
                other.domain)

    def __hash__(self):
        return hash((self.device, self.domain, self.marked_remote))

    def __str__(self):
        return f"UAuthority{{device='{self.device}', domain='{self.domain}', markedRemote={self.marked_remote}}}"


# Initialize EMPTY
UAuthority.EMPTY = UAuthority(None, None, None, False, True)
