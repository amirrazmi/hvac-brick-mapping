"""Library and template thinking: one reusable AHU template, many instances.
Same idea as class-based control module templates in a DCS or a standard
application library: define once, instantiate per project."""
from rdflib import Namespace, RDF, RDFS, Literal

BRICK = Namespace("https://brickschema.org/schema/Brick#")

# Standard AHU parts: tag code -> (Brick class, label)
AHU_PARTS = {
    "SF": (BRICK.Supply_Fan, "Supply fan"),
    "RF": (BRICK.Return_Fan, "Return fan"),
    "FLT": (BRICK.Filter, "Filter"),
    "OAD": (BRICK.Outside_Damper, "Outside air damper"),
    "CHW_VLV": (BRICK.Chilled_Water_Valve, "Chilled water valve"),
    "HW_VLV": (BRICK.Hot_Water_Valve, "Hot water valve"),
}

def add_ahu(g, ns, ahu_id):
    """Instantiate the AHU template: the AHU plus its standard parts."""
    ahu = ns[ahu_id]
    g.add((ahu, RDF.type, BRICK.Air_Handling_Unit))
    g.add((ahu, RDFS.label, Literal(ahu_id)))
    for code, (cls, label) in AHU_PARTS.items():
        part = ns[f"{ahu_id}_{code}"]
        g.add((part, RDF.type, cls))
        g.add((part, RDFS.label, Literal(f"{ahu_id} {label}")))
        g.add((ahu, BRICK.hasPart, part))
    return ahu
