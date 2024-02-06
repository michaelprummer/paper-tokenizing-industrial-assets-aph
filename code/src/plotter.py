from matplotlib import pyplot as plt
import pandas as pd
import numpy as np
from glob import glob
from mconfig import config

plt.rc("figure", dpi=300)
mpl_plot_size = [4, 3.4]

# Config values
out_path = "../paper/res/plots"
valid_label = f"Valid ({config['ave_threshold']})"


def plot_single_df(data: list, cols: list):
    df2 = pd.DataFrame(data, columns=cols)
    #df2.sort_values(inplace=True, by=["pHash","Manipulation"])
    df2 = df2[["pHash", valid_label]]

    df_dict = dict({
        "phash-4": [],
        "phash-8": [],
        "phash-16": [],
        "phash-32": [],
    })

    for _, item in df2.iterrows():
        value = float(item[valid_label][:-1])
        pHash = item["pHash"]
        p = df_dict[f"phash-{pHash}"]
        p.append(value)
    df = pd.DataFrame(df_dict,
                      index=[
                          "Original", "Smaller", "Bigger", "Darker",
                          "Brighter", "Tile 90°", "Flipped"
                      ])
    df.plot(kind="bar")

    plt.title("Single gerber layers against average hash.")
    plt.ylabel("Validity")
    plt.savefig(f'{out_path}/ave-single.png')


path = "./assets/original/plotter"


# Plots:
# Compare 6-Fit / no-fit with wire mpls
def plot_mpls_wires_only_df():
    filter = ["name", "hash_size", "ham", "norm"]
    df16fit = pd.read_excel(f"{path}/h-16-fit-6.xlsx")[filter].sort_values(
        "name")
    df16nofit = pd.read_excel(f"{path}/h-16-nofit-6.xlsx")[filter].sort_values(
        "name")
    df32fit = pd.read_excel(f"{path}/h-32-fit-6.xlsx")[filter].sort_values(
        "name")
    df32nofit = pd.read_excel(f"{path}/h-32-nofit-6.xlsx")[filter].sort_values(
        "name")

    #"phash:16, fit=true, hff-6"
    a = df16fit["norm"].tolist()
    b = df16nofit["norm"].tolist()
    c = df32fit["norm"].tolist()
    d = df32nofit["norm"].tolist()

    df = pd.DataFrame(
        dict({
            "APH-16 aspect": a,
            "APH-16 stretch": b,
            "APH-32 aspect": c,
            "APH-32 stretch": d
        }))

    #print(df16fit["name"].to_list())
    plt.rcParams["figure.figsize"] = mpl_plot_size
    df = pd.DataFrame(dict({
        "APH-16 aspect": a[0:3],
        "APH-16 stretch": b[0:3],
        "APH-32 aspect": c[0:3],
        "APH-32 stretch": d[0:3]
    }),
                      index=['1', '2', '3'])
    plot = df.plot(kind="line")
    plot.set_ylim(0.6, 1)
    plot.set_xlim(0, 2)
    plot.set_title("a. Change of wire routing.")
    plot.axline((1.5, 0.9), (2, 0.9), linestyle=':', color=((1, 0.1, 0, 0.7)))
    plt.savefig(f'{out_path}/wires_only_mpls_L.png')

    df = pd.DataFrame(dict({
        "APH-16 aspect": a[3:6],
        "APH-16 stretch": b[3:6],
        "APH-32 aspect": c[3:6],
        "APH-32 stretch": d[3:6]
    }),
                      index=['0.35mil', '3.5mil', '50mil'])
    plot = df.plot(kind="line")
    plot.set_ylim(0.7, 1)
    plot.set_xlim(0, 2)
    plot.axline((0, 0.9), (2, 0.9), linestyle=':', color=((0.9, 0.1, 0, 0.5)))
    plot.set_title("b. Translation of elements.")
    plt.savefig(f'{out_path}/wires_only_mpls_T.png')

    aa = a[6:16]
    aa.reverse()
    bb = b[6:16]
    bb.reverse()
    cc = c[6:16]
    cc.reverse()
    dd = d[6:16]
    dd.reverse()
    labels = [
        '0.1mil', '0.25mil', '0.5mil', '1mil', '2mil', '4mil', '6mil', '8mil',
        '10mil', '12mil'
    ]
    labels.reverse()
    df = pd.DataFrame(dict({
        "APH-16 aspect": aa,
        "APH-16 stretch": bb,
        "APH-32 aspect": cc,
        "APH-32 stretch": dd
    }),
                      index=labels)
    plot = df.plot(kind="line")
    plot.set_ylim(0.5, 1)
    plot.set_xlim(0, 9)
    plot.axline((0, 0.9), (4, 0.9), linestyle=':', color=((0.9, 0.1, 0, 0.5)))
    plot.set_title("c. Reduction of wire thickness.")
    plt.savefig(f'{out_path}/wires_only_mpls_W.png')


# Scatter plot of valid elements
def rm_elements_scatter():
    files = list(glob(f"{path}/elements/*.xlsx"))
    files.sort()

    def to_int(n):
        return int(n * 100)

    plt.rcParams["figure.figsize"] = mpl_plot_size
    plt.axline((0, 90), (3, 90), linestyle=':', color=((0.9, 0.1, 0, 0.5)))
    labels = []

    for idx, file in enumerate(files):
        sheet = pd.read_excel(file)
        df = sheet[["norm", "hash_size"]]
        hash = df.get("hash_size")[0]

        label = file.split('/').pop()[2:-16]

        label = label.replace("nofit", "S")
        label = label.replace("fit", "A")
        #label = f"APH-{label.replace('-', ' ')}"
        label = f"{label.replace('-', '')}"

        labels.append(label)
        y_axe = list(map(to_int, df["norm"].to_list()))
        x_axe = [idx for _ in range(y_axe.__len__())]

        color = (0, 0, 1, 0.2)
        if hash == 32:
            color = (0, 1, 0, 0.2)
        elif hash == 8:
            color = (0.7, 0.3, 0.9, 0.2)

        plt.scatter(x_axe, y_axe, color=color)
    plt.title("d. Removal of small layout elements.")
    plt.xticks(ticks=[0, 1, 2, 3, 4, 5], labels=labels)
    plt.savefig(f'{out_path}/elements_scatter.png')


#rm_elements_scatter()
#plot_mpls_wires_only_df()
