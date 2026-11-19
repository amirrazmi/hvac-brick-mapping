"""Map DCS/BMS-style tag names to a Brick Schema model.
Tag structure (ISA-88 style hierarchy): Building.Equipment.[Part.]Signal
e.g. B1.AHU01.SF.STS = building B1, AHU01, supply fan, status.
Run: python map_tags_to_brick.py"""
import csv
from rdflib import Graph, Namespace, RDF, RDFS, Literal
from templates import BRICK, add_ahu

BLDG = Namespace("urn:example-building#")

# Mapping rules: signal code -> Brick point class
SIGNAL_RULES = {
    "SAT": BRICK.Supply_Air_Temperature_Sensor,
    "SAT_SP": BRICK.Supply_Air_Temperature_Setpoint,
    "RAT": BRICK.Return_Air_Temperature_Sensor,
    "STS": BRICK.Fan_Status,
    "SPD_CMD": BRICK.Speed_Command,
    "DP": BRICK.Filter_Differential_Pressure_Sensor,
    "CMD": BRICK.Damper_Position_Command,
}
VALVE_PARTS = {"CHW_VLV", "HW_VLV"}

def map_tag(g, tag, description, ahus):
    parts = tag.split(".")
    ahu_id = parts[1]
    if ahu_id not in ahus:                      # instantiate template once per AHU
        add_ahu(g, BLDG, ahu_id)
        ahus.add(ahu_id)
    if len(parts) == 3:                         # point directly on the AHU
        owner, signal = BLDG[ahu_id], parts[2]
    else:                                       # point on a part of the AHU
        owner, signal = BLDG[f"{ahu_id}_{parts[2]}"], parts[3]
    cls = SIGNAL_RULES.get(signal)
    if len(parts) == 4 and parts[2] in VALVE_PARTS and signal == "CMD":
        cls = BRICK.Valve_Command
    if cls is None:
        return False                            # unmapped: needs engineer review
    point = BLDG[tag.replace(".", "_")]
    g.add((point, RDF.type, cls))
    g.add((point, RDFS.label, Literal(description)))
    g.add((owner, BRICK.hasPoint, point))
    return True

def main():
    g = Graph(); g.bind("brick", BRICK); g.bind("bldg", BLDG)
    ahus, unmapped, total = set(), [], 0
    with open("tag_list.csv") as f:
        for row in csv.DictReader(f):
            total += 1
            if not map_tag(g, row["tag"], row["description"], ahus):
                unmapped.append(row["tag"])
    g.serialize("building_brick.ttl", format="turtle")
    print(f"Mapped {total - len(unmapped)} of {total} tags into {len(ahus)} AHUs, {len(g)} triples")
    print("Needs review:", unmapped or "none")

    q = """SELECT ?ahu ?label WHERE {
      ?ahu a brick:Air_Handling_Unit ; brick:hasPart ?f .
      ?f a brick:Filter ; brick:hasPoint ?p .
      ?p a brick:Filter_Differential_Pressure_Sensor ; rdfs:label ?label . }"""
    print("\nQuery: AHUs with a filter differential pressure sensor")
    for r in g.query(q, initNs={"brick": BRICK, "rdfs": RDFS}):
        print("  ", r.ahu.split("#")[1], "->", r.label)

if __name__ == "__main__":
    main()
