# HVAC to Brick Schema: semantic modelling and tag mapping

Small Python project modelling HVAC systems with [Brick Schema](https://brickschema.org) (RDF) and mapping
DCS/BMS-style tag lists to a semantic building model.

## Contents
- `ahu_brick_model.py`: Brick model of one air handling unit (equipment, parts, zones, BMS points) with SPARQL queries.
- `templates.py`: reusable AHU template (define once, instantiate per unit), the same idea as class-based control module libraries.
- `map_tags_to_brick.py`: maps hierarchical tag names (e.g. `B1.AHU01.SF.STS`) to Brick classes with rule-based mapping, flags unmapped tags for engineer review, and queries the result.
- `tag_list.csv`: example tag list (synthetic data).

## Run
```
pip install rdflib
python ahu_brick_model.py
python map_tags_to_brick.py
```

## Key relationships
- `brick:hasPart`: component structure (AHU has fans, coils, filter, dampers)
- `brick:feeds`: air or water flow path (AHU feeds VAV feeds zone)
- `brick:hasPoint`: BMS data points (sensors, setpoints, commands, status)

## Next steps
- AI-assisted mapping: use an LLM to suggest Brick classes for unmapped or inconsistent tag names, with engineer approval
- Brick validation with SHACL shapes
- Web of Things Thing Models for device templates
