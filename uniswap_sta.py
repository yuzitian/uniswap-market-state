import json
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from pyecharts.charts import Graph
from pyecharts import options as opts
import math

sample_transport=RequestsHTTPTransport(
    url='https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3',
)
client = Client(transport=sample_transport, fetch_schema_from_transport=True)

#token0Price:每个token1能换多少token0
query = gql('''
{
  pools(first:100, orderBy:totalValueLockedUSD, orderDirection:desc){
    token0{
      symbol
      totalValueLockedUSD
    }
    token1{
      symbol
      totalValueLockedUSD
    }
    token0Price
    token1Price
    liquidity
  }
}
''')

pools = client.execute(query)
#print(pools)

pool = pools["pools"]
poollength = len(pool)
#print(pool)
#print(pool[1])
#print(pool[1]["token0"]["symbol"])

symbolc = {}
pricec = {}
liquidc = {}
Value = {}
path = []

for i in range(poollength):
    if len(pool[i]["token0"]["symbol"]) >= 10:
        pool[i]["token0"]["symbol"] = pool[i]["token0"]["symbol"][1:10]
    if len(pool[i]["token1"]["symbol"]) >= 10:
        pool[i]["token1"]["symbol"] = pool[i]["token1"]["symbol"][1:10]
    if pool[i]["token0"]["symbol"] not in symbolc.keys():
        symbolc[pool[i]["token0"]["symbol"]] = []
        symbolc[pool[i]["token0"]["symbol"]].append(pool[i]["token1"]["symbol"])
        pricec[pool[i]["token0"]["symbol"]] = []
        pricec[pool[i]["token0"]["symbol"]].append(pool[i]["token1Price"])
        liquidc[pool[i]["token0"]["symbol"]] = []
        liquidc[pool[i]["token0"]["symbol"]].append(pool[i]["liquidity"])
        Value[pool[i]["token0"]["symbol"]] = pool[i]["token0"]["totalValueLockedUSD"]
    else:
        if pool[i]["token1"]["symbol"] not in symbolc[pool[i]["token0"]["symbol"]]:
            symbolc[pool[i]["token0"]["symbol"]].append(pool[i]["token1"]["symbol"])
            pricec[pool[i]["token0"]["symbol"]].append(pool[i]["token1Price"])
            liquidc[pool[i]["token0"]["symbol"]].append(pool[i]["liquidity"])
    if pool[i]["token1"]["symbol"] not in symbolc.keys():
        symbolc[pool[i]["token1"]["symbol"]] = []
        symbolc[pool[i]["token1"]["symbol"]].append(pool[i]["token0"]["symbol"])
        pricec[pool[i]["token1"]["symbol"]] = []
        pricec[pool[i]["token1"]["symbol"]].append(pool[i]["token0Price"])
        liquidc[pool[i]["token1"]["symbol"]] = []
        liquidc[pool[i]["token1"]["symbol"]].append(pool[i]["liquidity"])
        Value[pool[i]["token1"]["symbol"]] = pool[i]["token1"]["totalValueLockedUSD"]
    else:
        if pool[i]["token0"]["symbol"] not in symbolc[pool[i]["token1"]["symbol"]]:
            symbolc[pool[i]["token1"]["symbol"]].append(pool[i]["token0"]["symbol"])
            pricec[pool[i]["token1"]["symbol"]].append(pool[i]["token0Price"])
            liquidc[pool[i]["token1"]["symbol"]].append(pool[i]["liquidity"])
#print(symbolc)
#print(pricec)
#print(liquidc)
#print(Value)

def create_index(symbolc):
    target = dict()
    x = 0
    for i in symbolc.keys():
        target[i] = x
        x += 1
    return target

def fanzhuan(d):
    return dict(map(lambda t:(t[1],t[0]), d.items()))

dict1 = create_index(symbolc)
dict2 = fanzhuan(dict1)
#print(dict1)
#print(dict2)

def change_symbol(symbolc, dict1, dict2):
    target = dict()
    for i in range(len(symbolc)):
        target[i] = []
        for x in symbolc[dict2[i]]:
            target[i].append(dict1[x])
    return target

num = change_symbol(symbolc, dict1, dict2)
#print(num)

def find_cir_starts_with(G, length, path):
    l, last = len(path), path[-1]
    sumpath = []
    if l == length - 1:
        for i in G[last]:
            if(i > path[1]) and (i not in path) and (path[0] in G[i]):
                #print(path + [i])
                sumpath.append(path + [i] + [path[0]])
    else:
        for i in G[last]:
            if(i > path[0]) and (i not in path):
                sumpath.extend(find_cir_starts_with(G, length, path + [i]))
    return sumpath

def find_cir_of_length(G, n, length):
    sumpath = []
    for i in range(1, n-length+2):
        sumpath.extend(find_cir_starts_with(G, length, [i]))
    return sumpath

def find_all_cirs(G, n):
    sumpath = []
    for i in range(3, n+1):
        sumpath.extend(find_cir_of_length(G, n, i))
    return sumpath

m = find_all_cirs(num, len(num))
#print(len(m))
#print(m)

for i in range(len(m)):
    demo = []
    for j in m[i]:
        demo.append(dict2[j])
    path.append(demo)

#print(path)

node = []
nodes = []
for i in Value.keys():
    if float(Value[i]) > 500000000 :
        nodes.append({"name": i, "symbolSize": 70, "category": 0})
    elif float(Value[i]) >= 100000000 and float(Value[i]) < 500000000 :
        nodes.append({"name": i, "symbolSize": 60, "category": 1})
    elif float(Value[i]) >= 50000000 and float(Value[i]) < 100000000:
        nodes.append({"name": i, "symbolSize": 50, "category": 2})
    elif float(Value[i]) >= 10000000 and float(Value[i]) < 50000000:
        nodes.append({"name": i, "symbolSize": 40, "category": 3})
    elif float(Value[i]) >= 5000000 and float(Value[i]) < 10000000:
        nodes.append({"name": i, "symbolSize": 30, "category": 4})
    elif float(Value[i]) >= 1000000 and float(Value[i]) < 5000000:
        nodes.append({"name": i, "symbolSize": 20, "category": 4})
    elif float(Value[i]) < 1000000:
        nodes.append({"name": i, "symbolSize": 10, "category": 4})
#print(node)
#print(nodes)

links = []
for i in symbolc.keys():
    for j in symbolc[i]:
        if {"source": i, "target": j} not in links:
            links.append({"source": i, "target": j})

categories = [
    {"name": "一级节点", "color": "red"},
    {"name": "二级节点", "color": "blue"},
    {"name": "三级节点", "color": "green"},
    {"name": "四级节点", "color": "yellow"},
    {"name": "五级节点", "color": "black"},
]

def price0(link, symbolc, price, liquidc):
    index = symbolc[link["source"]].index(link["target"])
    p = float(price[link["source"]][index])
    k = float(liquidc[link["source"]][index])
    if p != 0:
        x = math.sqrt(k / p)
        y = math.sqrt(k * p)
        deltay = y / (x + 1)
        return deltay
    else:
        return 0

rate = []
for link in links:
    if price0(link, symbolc, pricec, liquidc) == 0:
        link["value"] = -1
    else:
        link["value"] = price0(link, symbolc, pricec, liquidc)

#print(links)
links = [link for link in links if not link["value"] == -1]
links = [link for link in links if not link["value"] >= 100000]
links = [link for link in links if not link["value"] <= 0.00001]
#print(links)

for link in links:
    link["value"] = "1 -> " + str(price0(link, symbolc, pricec, liquidc))

new_nodes = []
for link in links:
    if link["source"] not in new_nodes:
        new_nodes.append(link["source"])
    if link["target"] not in new_nodes:
        new_nodes.append(link["target"])

nodes = [new_node for new_node in nodes if new_node["name"] in new_nodes]

g = (
    Graph()
    .add("",
         nodes,
         links,
         categories,
         repulsion=1000,
         is_roam=True,
         is_focusnode=True,
         label_opts=opts.LabelOpts(is_show=True),
         edge_symbol=['none', 'arrow'],
         linestyle_opts=opts.LineStyleOpts(width=0.5, curve=0.3, opacity=0.7),
         edge_label=opts.LabelOpts(
            is_show = False, position="middle", formatter="1->{c} "  # 设置关系说明
         ),
         )
    .set_global_opts(title_opts=opts.TitleOpts(title="uniswap-市场状态"))
    #.render("./templates/uniswap.html")
    .render("/root/yq/pythonProject001/templates/uniswap.html")
)
print(1)