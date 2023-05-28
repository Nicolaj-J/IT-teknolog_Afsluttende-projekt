import matplotlib.pyplot as plt
import networkx as nx
import json
import PIL


def make_local_diagram(company_name=""):
    """
    Creates a local network topologi map from json file.
    Json file have to be saved in scan-results as local-scan.json
    """

    with open(f"final/scan-results/{company_name}_local_scan.json") as f:
        data = json.load(f)
    icons = {
        "router": r"final\network-topologi-images\cisco-symbols\router.jpg",
        "switch": r"final\network-topologi-images\cisco-symbols\layer 2 remote switch.jpg",
        "PC": r"final\network-topologi-images\cisco-symbols\workstation.jpg",
        "Not identified": r"final\network-topologi-images\cisco-symbols\host.jpg",
        "Server": r"final\network-topologi-images\cisco-symbols\fileserver.jpg"
    }
    images = {k: PIL.Image.open(fname) for k, fname in icons.items()}
    G = nx.Graph()
    G.add_node("router", image=images["router"])
    for i in range(len(data)):
        if data[i]["device_type"] == "Workstation":
            G.add_node(f"PC_{i}", image=images["PC"])
            G.add_edge(f"router", f"PC_{i}")
    for i in range(len(data)):
        if data[i]["device_type"] == "Not identified":
            G.add_node(f"device_{i}", image=images["Not identified"])
            G.add_edge(f"router", f"device_{i}")
    pos = nx.spring_layout(G, seed=1734289230)
    fig, ax = plt.subplots()
    print(G)
    nx.draw_networkx_edges(
        G,
        pos=pos,
        ax=ax,
        arrows=True,
        arrowstyle="-",
        min_source_margin=15,
        min_target_margin=15,
    )
    tr_figure = ax.transData.transform
    tr_axes = fig.transFigure.inverted().transform
    icon_size = (ax.get_xlim()[1] - ax.get_xlim()[0]) * 0.025
    icon_center = icon_size / 2.0
    for n in G.nodes:
        xf, yf = tr_figure(pos[n])
        xa, ya = tr_axes((xf, yf))
        a = plt.axes([
            xa - icon_center,
            ya - icon_center,
            icon_size,
            icon_size])
        a.imshow(G.nodes[n]["image"])
        a.axis("off")
    plt.savefig(f"final/network_diagrams/{company_name}_local_diagram.png",
                format="PNG")


def make_cloud_diagram(company_name=""):
    """
    Creates cloud topologi map from json file.
    Json file have to be saved in scan results as cloud-scan.json
    """
    with open(f"final/scan-results/{company_name}_cloud_scan.json") as f:
        data = json.load(f)
    icons = {
        "router": r"final\network-topologi-images\cisco-symbols\router.jpg",
        "cloud": r"final\network-topologi-images\cisco-symbols\cloud.jpg",
        "switch": r"final\network-topologi-images\cisco-symbols\layer 2 remote switch.jpg",
        "PC": r"final\network-topologi-images\cisco-symbols\workstation.jpg",
        "Not identified": r"final\network-topologi-images\cisco-symbols\host.jpg",
        "Server": r"final\network-topologi-images\cisco-symbols\fileserver.jpg"
    }
    images = {k: PIL.Image.open(fname) for k, fname in icons.items()}
    G = nx.Graph()
    G.add_node("cloud", image=images["cloud"])
    for i in range(len(data)):
        if data[i]["Device_type"] == "Workstation":
            print(1)
            G.add_node(f"PC_{i}", image=images["PC"])
            G.add_edge(f"cloud", f"PC_{i}")
    for i in range(len(data)):
        if data[i]["Device_type"] == "Not identified":
            print("2")
            G.add_node(f"device_{i}", image=images["Not identified"])
            G.add_edge(f"cloud", f"device_{i}")
    for i in range(len(data)):
        if data[i]["Device_type"] == "Server":
            print("3")
            G.add_node(f"server_{i}", image=images["Server"])
            G.add_edge(f"cloud", f"server_{i}")
    pos = nx.spring_layout(G, seed=1734289230)
    fig, ax = plt.subplots()
    nx.draw_networkx_edges(
        G,
        pos=pos,
        ax=ax,
        arrows=True,
        arrowstyle="-",
        min_source_margin=15,
        min_target_margin=15,
    )
    tr_figure = ax.transData.transform
    tr_axes = fig.transFigure.inverted().transform
    icon_size = (ax.get_xlim()[1] - ax.get_xlim()[0]) * 0.025
    icon_center = icon_size / 2.0
    for n in G.nodes:
        xf, yf = tr_figure(pos[n])
        xa, ya = tr_axes((xf, yf))
        a = plt.axes([
                xa - icon_center,
                ya - icon_center,
                icon_size,
                icon_size])
        print(G.nodes)
        a.imshow(G.nodes[n]["image"])
        a.axis("off")
    plt.savefig(f"final/network_diagrams/{company_name}cloud_diagram.png",
                format="PNG")
