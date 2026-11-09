"""Works out which IP ranges to block. Pure logic: no Windows calls, no GUI.

Two sources are combined:

1. Google Cloud's published IP ranges (https://www.gstatic.com/ipranges/cloud.json).
   Overwatch 2 game servers run on Google Cloud, and Google lists every range
   with its region ("asia-southeast1" is Singapore, "australia-southeast1" is
   Sydney). Google keeps this list current, so it doesn't go stale the way a
   hand-made list does.
2. The hand-curated ips.json from the original project, which also covers
   Blizzard-owned and Korean ranges that aren't on Google Cloud.

Australian ranges from both sources are then cut out of whatever is blocked,
so a broad range can never take out a Sydney or Melbourne server.
"""

import ipaddress
import json
import os
import urllib.request

GCP_RANGES_URL = "https://www.gstatic.com/ipranges/cloud.json"

# The region groups the app offers, in display order.
GROUPS = {
    "asia": {
        "label": "Asia (Singapore, Japan, Korea, Taiwan, Hong Kong, India...)",
        "gcp_prefixes": ("asia-",),
        "curated": ("Japan", "Singapore", "Korea", "Taiwan"),
    },
    "americas": {
        "label": "Americas (US, Canada, Brazil...)",
        "gcp_prefixes": ("us-", "northamerica-", "southamerica-"),
        "curated": ("Americas",),
    },
    "europe": {
        "label": "Europe, Middle East and Africa",
        "gcp_prefixes": ("europe-", "me-", "africa-"),
        "curated": ("Netherlands", "Others"),
    },
}

# Never blocked, whatever is selected.
PROTECTED_GCP_PREFIXES = ("australia-",)
PROTECTED_CURATED = ("Australia",)
# Google's "global" scope is anycast load balancing shared by every region;
# blocking it would hit Australian traffic too, so it's left alone.
IGNORED_GCP_SCOPES = ("global",)


def resource_path(*parts):
    """Path to a bundled file, both from source and inside a PyInstaller exe."""
    base = getattr(__import__("sys"), "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, *parts)


def parse_gcp(data):
    """Validate Google's cloud.json and return [(network, scope)].

    Raises ValueError if it doesn't look like the real list, so a broken or
    truncated download can't silently produce an empty block list.
    """
    prefixes = data.get("prefixes") if isinstance(data, dict) else None
    if not isinstance(prefixes, list) or len(prefixes) < 200:
        raise ValueError("Google range list is missing or too short")
    out = []
    for p in prefixes:
        cidr = p.get("ipv4Prefix") or p.get("ipv6Prefix")
        scope = p.get("scope")
        if not cidr or not isinstance(scope, str):
            continue
        out.append((ipaddress.ip_network(cidr, strict=False), scope))
    scopes = {s for _, s in out}
    if not any(s.startswith("australia-") for s in scopes) or not any(s.startswith("asia-") for s in scopes):
        raise ValueError("Google range list has no Australian or Asian regions")
    return out


def load_gcp(cache_path=None, fetch=True, timeout=6):
    """Return (ranges, source_label). Tries live, then the local cache, then the bundled snapshot."""
    if fetch:
        try:
            with urllib.request.urlopen(GCP_RANGES_URL, timeout=timeout) as resp:
                raw = resp.read()
            data = json.loads(raw)
            ranges = parse_gcp(data)
            if cache_path:
                try:
                    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
                    with open(cache_path, "wb") as f:
                        f.write(raw)
                except OSError:
                    pass
            return ranges, "Google live list (" + data.get("creationTime", "")[:10] + ")"
        except Exception:
            pass
    for path, label in ((cache_path, "saved copy"), (resource_path("data", "gcp_ranges_snapshot.json"), "bundled snapshot")):
        if not path or not os.path.exists(path):
            continue
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return parse_gcp(data), "Google " + label + " (" + data.get("creationTime", "")[:10] + ")"
        except Exception:
            continue
    raise RuntimeError("No usable Google IP range list (live, saved or bundled)")


def load_curated(path=None):
    """Return {region: [network]} from ips.json."""
    with open(path or resource_path("ips.json"), "r", encoding="utf-8") as f:
        data = json.load(f)
    return {region: [ipaddress.ip_network(c, strict=False) for c in cidrs] for region, cidrs in data.items()}


def protected_networks(gcp, curated):
    nets = [n for n, scope in gcp if scope.startswith(PROTECTED_GCP_PREFIXES)]
    for region in PROTECTED_CURATED:
        nets.extend(curated.get(region, []))
    return nets


def subtract(networks, protected):
    """Remove every protected range from networks, splitting ranges where needed."""
    result = []
    for net in networks:
        pieces = [net]
        for prot in protected:
            if prot.version != net.version:
                continue
            next_pieces = []
            for piece in pieces:
                if not piece.overlaps(prot):
                    next_pieces.append(piece)
                elif piece.subnet_of(prot):
                    continue  # entirely Australian: drop it
                else:
                    next_pieces.extend(piece.address_exclude(prot))
            pieces = next_pieces
        result.extend(pieces)
    return result


def build_block_list(selected_groups, gcp, curated):
    """Return {group: [network]} to block for the selected groups, Australia cut out."""
    protected = protected_networks(gcp, curated)
    out = {}
    for key in GROUPS:
        if key not in selected_groups:
            continue
        group = GROUPS[key]
        nets = [n for n, scope in gcp
                if scope.startswith(group["gcp_prefixes"]) and scope not in IGNORED_GCP_SCOPES]
        for region in group["curated"]:
            nets.extend(curated.get(region, []))
        nets = subtract(nets, protected)
        v4 = list(ipaddress.collapse_addresses(n for n in nets if n.version == 4))
        v6 = list(ipaddress.collapse_addresses(n for n in nets if n.version == 6))
        out[key] = v4 + v6
    return out
