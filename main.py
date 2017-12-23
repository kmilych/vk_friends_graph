import requests
import random
import networkx as nx
import json
import time
import tqdm
import argparse
import community
from server import run_local_http_server
from private_settings import ACCESS_TOKEN

api_v = '5.21'

def retry_request(req, times,delay=1):
    try:
        r = requests.get(req).json()['response']
        return r
    except Exception:
        time.sleep(delay)
        if times > 0:
            return retry_request(req, times-1)
        
def vk_api_request(method_name, parameters=False, token=False):
    req_url = 'https://api.vk.com/method/{method_name}'.format(method_name=method_name)
    if parameters:
        req_url +='?{parameters}'.format(parameters=parameters)  
    if token:
        req_url +='&access_token={}'.format(token)
    req_url += '&v={api_v}'.format(api_v=api_v)
    r = retry_request(req_url,5)
    return r

def get_friends(vk_id, token=ACCESS_TOKEN):
    r = vk_api_request('friends.get','user_id={}&fields=first_name,last_name,photo_50'.format(vk_id), token)
    r["items"] = list(filter((lambda x: 'deactivated' not in x.keys()), r['items']))
    return {item['id']: item for item in r['items']}, r['count']

def get_profileInfo(vk_id, token=ACCESS_TOKEN):
    r = vk_api_request('users.get','user_id={}&fields=first_name,last_name,photo_50'.format(vk_id),token)
    return r


def get_mutualFriends(vk_id1, vk_id2, token=ACCESS_TOKEN):
    r = vk_api_request('friends.getMutual','source_uid={}&target_uid={}'.format(vk_id1,vk_id2), token)
    return r

def add_friends_to_graph(graph,vk_id):
    print("Retrieving id{}'s profile info...".format(vk_id))
    friends_network.add_node(vk_id, **get_profileInfo(vk_id)[0])
    friends_network.nodes[vk_id]['root'] = 1
    print("Retrieving id{}'s friends and friends of friends...".format(vk_id))
    for f in tqdm.tqdm(get_friends(vk_id)[0].items()):
        graph.add_node(f[0],**f[1])
        graph.add_edge(vk_id, f[0])
        for m in get_mutualFriends(vk_id, f[0]):
            graph.add_edge(f[0], m)

def find_communities(graph):
    bb = nx.betweenness_centrality(friends_network)
    nx.set_node_attributes(friends_network,bb, 'betweenness')
    parts = community.best_partition(graph)
    values = [parts.get(node) for node in graph.nodes()]
    nx.set_node_attributes(graph, dict(zip(graph.nodes(),values)), 'group')
    g = nx.get_node_attributes(graph,"group")
    edgegroups=dict()
    for edge in graph.edges():
        if g[edge[0]] == g[edge[1]]:
            edgegroups[edge] = g[edge[0]]
        else:
            edgegroups[edge] = -1
    nx.set_edge_attributes(graph, edgegroups, "value")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-v","--vkids",nargs='+',help="Vk id or ids to add as root nodes.(may not be used with -j)")
    group.add_argument("-j","--jsonpath",type=str,help="Load and visualize graph from json.(may not be used with -v)")
    parser.add_argument("-k", "--keeproot",action="store_true",help="If provided with -v keeps the root node in resulting graph. (ignored with -j)")
    args = parser.parse_args()
    print(args.keeproot)
    if args.jsonpath is not None :
        with open(args.jsonpath, 'r') as f:
            friends_network = nx.readwrite.node_link_graph(json.load(f))
    else:
        friends_network = nx.Graph()
        for vid in args.vkids: 
            add_friends_to_graph(friends_network, vid)

        find_communities(friends_network)
        if not args.keeproot:
            for r in [node for node,data in friends_network.nodes(data=True) if 'root' in data.keys()]:
                print("Removing id" + r+' ...')
                friends_network.remove_node(r)
        data = nx.readwrite.json_graph.node_link_data(friends_network)
        with open('friends_network.json', 'w') as f:
            json.dump(data, f, indent=4)
    run_local_http_server()    