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

from org_eclipse_uprotocol.proto.uri_pb2 import UAuthority


class UAuthorityFactory:
    """
    A factory is a part of the software that has methods to generate concrete objects, usually of the same type.<br>
    An Authority represents the deployment location of a specific Software Entity.<br>Data representation of an
    <b>Authority</b>.<br> An Authority consists of a device, a domain and a micro version in the form of an IP
    Address.<br>Device and domain names are used as part of the URI for device and service discovery. Optimized micro
    versions of the UUri will use the IP Address.<br>Devices will be grouped together into realms of Zone of
    Authority.<br> The UAuthority Factory knows how to generate UAuthority proto message.<br>
    """

    @staticmethod
    def local() -> UAuthority:
        """
        Static factory method for creating a local uAuthority.<br>A local uri does not contain an authority and looks
        like this:<pre> :&lt;service&gt;/&lt;version&gt;/&lt;resource&gt;#&lt;Message&gt; </pre> <br>
        @return:Returns a local uAuthority that has no domain, device, or ip address information, indicating to
        uProtocol that the uAuthority part in the UUri is relative to the sender/receiver deployment environment.
        """
        return UAuthority()

    @staticmethod
    def long_remote(name: str) -> UAuthority:
        """
        Static factory method for creating a remote authority supporting the long serialization information
        representation of a UUri.<br> Building a UAuthority with this method will create an unresolved uAuthority
        that can only be serialised in long UUri format. An uri with a long representation of uAUthority can be
        serialised as follows:
         <pre> //&lt;device&gt;.&lt;domain&gt;/&lt;service&gt;/&lt;version&gt;/&lt;resource&gt;#&lt;Message&gt;
         </pre>
        @param name:domain & device name as a string.
        @return:Returns a uAuthority that contains the device and the domain and can only be serialized in long UUri
        format.
        """
        return UAuthority(name=name)

    @staticmethod
    def micro_remote(ip: bytes) -> UAuthority:
        """
        Static factory method for creating a remote authority supporting the micro serialization information
        representation of a UUri.<br>Building a UAuthority with this method will create an unresolved uAuthority that
        can only be serialised in micro UUri format.<br><br>
        @param ip:The ip address of the device a software entity is deployed on in bytes
        @return:Returns a uAuthority that contains only the internet address of the device, and can only be
        serialized in micro UUri format.
        """
        return UAuthority(ip=ip)

    @staticmethod
    def empty() -> UAuthority:
        """
        Static factory method for creating an empty uAuthority, to avoid working with null<br>Empty uAuthority is
        still serializable in both long and micro UUri formats, and will be as local to the current deployment
        environment.<br><br>
        @return:Returns an empty authority that has no domain, device, or device ip address information.
        """
        return UAuthority()

    @staticmethod
    def is_remote(uauthority: UAuthority) -> bool:
        """
        Support for determining if this uAuthority defines a deployment that is defined as remote.<br><br>
        @param uauthority: uAuthority protobuf message
        @return:Returns true if this uAuthority is remote, meaning it contains information for serialising a long
        UUri or a micro UUri.
        """
        return not UAuthorityFactory.is_empty(uauthority)

    @staticmethod
    def is_local(uauthority: UAuthority) -> bool:
        """
        Support for determining if this uAuthority is defined for a local deployment.<br><br>
        @param uauthority: uAuthority protobuf message
        @return:Returns true if this uAuthority is local, meaning does not contain a device/domain for long UUri or
        information for micro UUri.
        """
        return UAuthorityFactory.is_empty(uauthority)

    @staticmethod
    def is_long_form(uauthority: UAuthority) -> bool:
        """
        Determine if the UAuthority can be used to serialize a UUri in long format.<br><br>
        @param uauthority: uAuthority protobuf message
        @return:Returns true if the UAuthority can be used to serialize a UUri in long format.
        """
        return not uauthority.name.strip() == ""

    @staticmethod
    def is_micro_form(uauthority: UAuthority) -> bool:
        """
        Determine if the UAuthority can be used to serialize a UUri in micro format.<br><br>
        @param uauthority: uAuthority protobuf message
        @return:Returns true if the uAuthority can be serialized a UUri in micro format.
        """
        return len(uauthority.ip) != 0

    @staticmethod
    def is_empty(uauthority: UAuthority) -> bool:
        return all([uauthority.name.strip() == "", len(uauthority.ip) == 0, len(uauthority.id) == 0])

    @staticmethod
    def resolved_remote(name: str, ip: bytes):
        """
        Static factory method for creating a remote authority that is completely resolved with name, device and ip
        address of the device.<br>Building a UAuthority with this method will enable serialisation in both UUri
        formats, long UUri format and micro UUri format. Note that in the case of missing data, this will not fail,
        but simply create a UAuthority that is not resolved.<br><br>
        @param name:The domain and device name as a string for long serialization of UUri.
        @param ip:The IP address for the device in bytes, for micro serialization of UUri.
        @return:Returns a uAuthority that contains all resolved data and so can be serialized into a long UUri or a
        micro UUri.
        """
        return UAuthority(name=name if name else None, ip=ip if ip else None)
