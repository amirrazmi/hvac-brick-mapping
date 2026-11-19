"""Brick Schema model of an air handling unit (AHU-1) serving two zones.
Author: Amir Razmi. Run: pip install rdflib ; python ahu_brick_model.py"""
from rdflib import Graph, Namespace, RDF, RDFS, Literal

BRICK = Namespace("https://brickschema.org/schema/Brick#")
BLDG = Namespace("urn:example-building#")   # my own building namespace

g = Graph()
g.bind("brick", BRICK)
g.bind("bldg", BLDG)

def add(entity, brick_class, label):
    g.add((entity, RDF.type, brick_class))     # "entity IS A brick_class"
    g.add((entity, RDFS.label, Literal(label)))

# 1. Equipment: the AHU and its parts
add(BLDG.AHU1, BRICK.Air_Handling_Unit, "AHU-1")
parts = {
    "SupplyFan1": (BRICK.Supply_Fan, "Supply fan"),
    "ReturnFan1": (BRICK.Return_Fan, "Return fan"),
    "HeatingCoil1": (BRICK.Hot_Water_Coil, "Heating coil"),
    "CoolingCoil1": (BRICK.Chilled_Water_Coil, "Cooling coil"),
    "Filter1": (BRICK.Filter, "Supply air filter"),
    "OADamper1": (BRICK.Outside_Damper, "Outside air damper"),
}
for name, (cls, label) in parts.items():
    add(BLDG[name], cls, label)
    g.add((BLDG.AHU1, BRICK.hasPart, BLDG[name]))   # AHU-1 HAS PART fan, coil...

# 2. Locations: zones the AHU serves (via VAV boxes)
for z in ["1", "2"]:
    add(BLDG["VAV" + z], BRICK.VAV, f"VAV box {z}")
    add(BLDG["Zone" + z], BRICK.HVAC_Zone, f"Zone {z}")
    g.add((BLDG.AHU1, BRICK.feeds, BLDG["VAV" + z]))      # air flows AHU -> VAV
    g.add((BLDG["VAV" + z], BRICK.feeds, BLDG["Zone" + z]))  # VAV -> zone
    add(BLDG[f"Zone{z}_Temp"], BRICK.Zone_Air_Temperature_Sensor, f"Zone {z} temperature")
    g.add((BLDG["VAV" + z], BRICK.hasPoint, BLDG[f"Zone{z}_Temp"]))

# 3. Points: sensors, setpoints, commands, status (the BMS data)
points = [
    ("AHU1", "SAT", BRICK.Supply_Air_Temperature_Sensor, "Supply air temperature"),
    ("AHU1", "SAT_SP", BRICK.Supply_Air_Temperature_Setpoint, "Supply air temperature setpoint"),
    ("AHU1", "RAT", BRICK.Return_Air_Temperature_Sensor, "Return air temperature"),
    ("SupplyFan1", "SF_Status", BRICK.Fan_Status, "Supply fan status"),
    ("SupplyFan1", "SF_Speed", BRICK.Speed_Command, "Supply fan speed command"),
    ("Filter1", "Filter_DP", BRICK.Filter_Differential_Pressure_Sensor, "Filter differential pressure"),
    ("OADamper1", "OAD_Cmd", BRICK.Damper_Position_Command, "Outside air damper command"),
    ("CoolingCoil1", "CHW_Valve", BRICK.Valve_Command, "Chilled water valve command"),
]
for equip, pt, cls, label in points:
    add(BLDG[pt], cls, label)
    g.add((BLDG[equip], BRICK.hasPoint, BLDG[pt]))

g.serialize("ahu1_brick.ttl", format="turtle")
print(f"Model saved: {len(g)} triples in ahu1_brick.ttl\n")

# 4. SPARQL queries: asking questions of the model
q1 = """SELECT ?part ?label WHERE {
  bldg:AHU1 brick:hasPart ?part . ?part rdfs:label ?label . }"""
print("Q1. Parts of AHU-1:")
for r in g.query(q1, initNs={"brick": BRICK, "bldg": BLDG, "rdfs": RDFS}):
    print("  ", r.label)

q2 = """SELECT ?label WHERE {
  { bldg:AHU1 brick:hasPoint ?p } UNION { bldg:AHU1 brick:hasPart ?x . ?x brick:hasPoint ?p }
  ?p rdfs:label ?label . }"""
print("\nQ2. All BMS points of AHU-1 and its parts:")
for r in g.query(q2, initNs={"brick": BRICK, "bldg": BLDG, "rdfs": RDFS}):
    print("  ", r.label)

q3 = """SELECT ?zone ?label WHERE {
  bldg:AHU1 brick:feeds+ ?zone . ?zone a brick:HVAC_Zone ; rdfs:label ?label . }"""
print("\nQ3. Zones served by AHU-1 (following the air path):")
for r in g.query(q3, initNs={"brick": BRICK, "bldg": BLDG, "rdfs": RDFS}):
    print("  ", r.label)
