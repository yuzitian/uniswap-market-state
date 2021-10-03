import json
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from pyecharts.charts import Graph
from pyecharts import options as opts

sample_transport=RequestsHTTPTransport(
    url='https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3',
)
client = Client(transport=sample_transport, fetch_schema_from_transport=True)

#token0Price:每个token1能换多少token0
query = gql('''
{
  pools(first:500){
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

#liqiuidty里面存的是根号k tokenPrice存的是根号p
def price(path, symbol, price, liquidc):
    sum = len(path)
    y = 1.0
    for i in range(sum - 1):
        index = symbol[path[i]].index(path[i+1])
        p = float(price[path[i]][index])
        k = float(liquidc[path[i]][index])
        if k == 0:
            y = 1
            break
        else:
            m = y * p + k
            y = (k * p / m - p) * k
    return y - 1

#套利空间
Price = []
for x in range(len(path)):
    Price.append(price(path[x], symbolc, pricec, liquidc))
#print(Price)
#print(len(Price))

available = []
for x in range(len(path)):
    if Price[x] > 0:
       #print(path[x], Price[x])
       available.append(path[x])
#print(available)

node = []
nodes = []
for i in range(len(available)):
    for j in available[i]:
        if j not in node:
            nodes.append({"name": j, "symbolSize": 10})
            node.append(j)
#print(node)
#print(nodes)

links = []
for i in range(len(available)):
    for j in range(len(available[i]) - 1):
        if {"source": available[i][j], "target": available[i][j + 1]} not in links:
            links.append({"source": available[i][j], "target": available[i][j + 1]})
#print(links)

g = (
    Graph()
    .add("", nodes, links, repulsion=10000, edge_symbol=['circle', 'arrow'],)
    .set_global_opts(title_opts=opts.TitleOpts(title="uniswap-套利路径"))
    .render("uniswap_path.html")
)
