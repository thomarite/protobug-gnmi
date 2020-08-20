#!/usr/bin/env python

# Modules
import grpc
from bin.gnmi_pb2_grpc import *
from bin.gnmi_pb2 import *
import json
import pprint

# Own modules
from bin.PathGenerator import gnmi_path_generator

# Variables
path = {'inventory': 'inventory.json'}
info_to_collect = ['openconfig-interfaces:interfaces']


# User-defined functions
def json_to_dict(path):
    with open(path, 'r') as f:
        return json.loads(f.read())


# Body
if __name__ == '__main__':
    inventory = json_to_dict(path['inventory'])

    for td_entry in inventory['devices']:
        metadata = [('username', td_entry['username']), ('password', td_entry['password'])]

        channel = grpc.insecure_channel(f'{td_entry["ip_address"]}:{td_entry["port"]}', metadata)
        grpc.channel_ready_future(channel).result(timeout=5)

        stub = gNMIStub(channel)

        for itc_entry in info_to_collect:
            print(f'Getting data for {itc_entry} from {td_entry["hostname"]} over gNMI...\n')

            intent_path = gnmi_path_generator(itc_entry)
            print("gnmi_path:\n")
            print(intent_path)
            gnmi_message_request = GetRequest(path=[intent_path], type=0, encoding=4)
            gnmi_message_response = stub.Get(gnmi_message_request, metadata=metadata)
            # we get the outout of gnmi_response that is json as string of bytes
            x = gnmi_message_response.notification[0].update[0].val.json_ietf_val
            # decode the string of bytes as string and then transform to pure json
            y = json.loads(x.decode('utf-8'))
            #import ipdb; ipdb.set_trace()
            # print nicely json
            pprint.pprint(y)
