"""
svedala_loader.py
=================
Reconstitute a pandapower network from the five CSV files produced by
KTH-EPE's `Pandapower_CIM_import.ipynb` (the simplified Svedala model).

The CIM-imported CSVs contain pandapower's standard element columns plus a
number of CIM/origin metadata columns. We assign them straight onto the
network's element tables — pandapower ignores unknown columns at power-flow
time, so the metadata travels along harmlessly.

Two fix-ups are applied:

1. **Line ratings.** The simplified model has empty `max_i_ka` for every
   line (typical of CGMES exports — thermal limits live in a separate profile
   that is not always shipped). We fill in conservative defaults based on
   each line's nominal voltage so that loading_percent calculations work.

2. **Geo coordinate column.** Newer pandapower stores GeoJSON-string
   coordinates in `bus.geo`. The CSVs already use that column; we leave it
   alone.
"""
import os
import pandas as pd


# Voltage-level → default thermal rating (kA per single circuit).
# These are conservative typical Nordic values. Override per-line if needed.
DEFAULT_MAX_I_KA = {
    400.0: 2.50,   # ~ 1700 MVA
    220.0: 1.50,   # ~  570 MVA
    135.0: 0.95,   # ~  220 MVA
    20.0:  1.00,
    17.0:  1.00,
}


def _fill_line_ratings(net):
    """In-place: populate net.line.max_i_ka where it is missing,
    using the from_bus voltage level as the lookup."""
    for idx in net.line.index:
        if pd.isna(net.line.at[idx, "max_i_ka"]):
            vn = net.bus.at[net.line.at[idx, "from_bus"], "vn_kv"]
            # Pick the closest known voltage level.
            key = min(DEFAULT_MAX_I_KA.keys(), key=lambda k: abs(k - vn))
            net.line.at[idx, "max_i_ka"] = DEFAULT_MAX_I_KA[key]


def load_svedala(data_dir="data"):
    """Build a pandapower network from the Svedala CSVs in `data_dir`.

    Expects the files: buses.csv, lines.csv, transformers.csv,
    generators.csv, loads.csv.
    """
    import pandapower as pp

    needed = ["buses.csv", "lines.csv", "transformers.csv",
              "generators.csv", "loads.csv"]
    for f in needed:
        path = os.path.join(data_dir, f)
        if not os.path.isfile(path):
            raise FileNotFoundError(
                f"Missing {path!r}. Place the five Svedala CSVs in "
                f"{data_dir!r} (see KTH-EPE/CIM_exportimport)."
            )

    net = pp.create_empty_network(name="Svedala")

    # Element tables: index is the original pandapower index (preserved from CSV).
    net.bus    = pd.read_csv(os.path.join(data_dir, "buses.csv"),        index_col=0)
    net.line   = pd.read_csv(os.path.join(data_dir, "lines.csv"),        index_col=0)
    net.trafo  = pd.read_csv(os.path.join(data_dir, "transformers.csv"), index_col=0)
    net.gen    = pd.read_csv(os.path.join(data_dir, "generators.csv"),   index_col=0)
    net.load   = pd.read_csv(os.path.join(data_dir, "loads.csv"),        index_col=0)

    # Fix #1: line thermal ratings.
    _fill_line_ratings(net)

    # Sanity: there must be exactly one slack source (a slack=True gen, since
    # this model has no ext_grid).
    if "slack" in net.gen.columns:
        n_slack = int(net.gen.slack.fillna(False).astype(bool).sum())
    else:
        n_slack = 0
    if n_slack == 0 and len(net.ext_grid) == 0:
        raise RuntimeError(
            "No slack found. Expected one generator with slack=True "
            "or a populated ext_grid table."
        )

    return net


if __name__ == "__main__":
    # Quick smoke test
    net = load_svedala("data")
    print(net)
    print("Zones:", sorted(net.bus.zone.dropna().unique()))
    print("Voltage levels:", sorted(net.bus.vn_kv.unique()))
    print("Slack gens:", net.gen[net.gen.slack.fillna(False).astype(bool)]["name"].tolist())
