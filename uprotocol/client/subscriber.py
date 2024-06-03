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

from uprotocol.client.transport_wrapper import TransportWrapper
from uprotocol.client.rpc_client import RpcClient
from uprotocol.client.rpc_mapper import RpcMapper
from uprotocol.transport.ulistener import UListener
from uprotocol.uri.factory.uri_factory import UriFactory
from uprotocol.client.ustatus_exception import UStatusException

from uprotocol.proto.uprotocol.core.usubscription.v3 import usubscription_pb2
from uprotocol.proto.uprotocol.core.usubscription.v3.usubscription_pb2 import (
    SubscriptionRequest,
    SubscriberInfo,
    UnsubscribeRequest,
)
from uprotocol.proto.uprotocol.v1.uri_pb2 import UUri
from uprotocol.proto.uprotocol.v1.ustatus_pb2 import UStatus, UCode

from concurrent.futures import Future, ThreadPoolExecutor

class Subscriber(RpcClient):
    """
    Subscriber interface.

    This interface provides the API to subscribe and unsubscribe
    to a given topic.
    """

    def subscribe(self, topic: UUri, listener: UListener) -> UStatus:
        """
        Subscribe to a given topic.

        @param topic The topic to subscribe to.
        @param listener The listener to be called when a message
        is received on the topic.
        @return Returns the UStatus with the status of the subscription.
        """
        service_descriptor = usubscription_pb2.DESCRIPTOR.services_by_name[
            "uSubscription"
        ]
        subscribe = UriFactory.from_proto(service_descriptor, 0)
        print("subscribe:", type(subscribe), subscribe)
        request: SubscriptionRequest = SubscriptionRequest(
            topic=topic,
            subscriber=SubscriberInfo(uri=self.get_transport().source),
        )

        with ThreadPoolExecutor(max_workers=1) as executor:
            invoke_future: Future = self.invoke_method(subscribe, request)
            result_f: Future = executor.submit(RpcMapper.map_response, 
                                               invoke_future, 
                                               UStatus)
            
            future_UStatus: Future = result_f.result()
            print("future_UStatus:", future_UStatus)

        
        try:
            status: UStatus = future_UStatus.result()
            print("status:", status)
            if status.code == UCode.OK:
                return self.get_transport().register_listener(topic, listener)
            return status
        except UStatusException as ue:
            print("at subscriber UStatusException")
            return ue.get_status()
        except RuntimeError as re:
            raise re
        
        
        '''
        def handle_response(future):
            status = future.result()
            print("status:", status)
            if status.code == UCode.OK:
                return self.get_transport().register_listener(topic, listener)
            return status

        result.add_done_callback(handle_response)
        
        return result
        
        '''
        
        
        # print("future result:", result.done())
        # new_result = await result
        # time.sleep(5)
        # print("future result:", result.done())


    def unsubscribe(self, topic: UUri, listener: UListener) -> UStatus:
        """
        Unsubscribe to a given topic.

        @param topic The topic to subscribe to.
        @param listener The listener to be called when a message
        is received on the topic.
        @return Returns the UStatus with the status of the unsubscription.
        """
        service_descriptor = usubscription_pb2.DESCRIPTOR.services_by_name[
            "uSubscription"
        ]
        subscribe = UriFactory.from_proto(service_descriptor, 0)
        request: UnsubscribeRequest = UnsubscribeRequest(
            topic=topic,
            subscriber=SubscriberInfo(uri=self.get_transport().source),
        )
        result = RpcMapper.map_response(
            RpcClient.invoke_method(subscribe, request), UStatus
        )

        def handle_response(future):
            status = future.result()
            if status.code == UCode.OK:
                return self.get_transport().register_listener(topic, listener)
            return status

        result.add_done_callback(handle_response)

        return result

    def unregister_listener(self, topic: UUri, listener: UListener) -> UStatus:
        """
        Unregister a listener from a topic.

        This method is similar to unsubscribe but it does not issue
        an unsubscribe request to the usubscription service, it just removes
        the listener from the local cache of listeners.

        @param topic The topic to subscribe to.
        @param listener The listener to be called when a message is
        received on the topic.
        @return Returns the UStatus with the status of the unsubscription.
        """
        return TransportWrapper.get_transport().unregister_listener(
            topic, listener
        )
