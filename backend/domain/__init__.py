"""Domain layer: what a stream observation means.

Pure. Imports nothing from adapters/ or api/, touches no database, makes no
network call, and knows nothing about HTTP. That isolation is the point -- the
ecological content can be reviewed, tested and replaced without reading a line of
infrastructure code.

    field_protocol.py  indicators and differentials, each cited to published method
    assess.py          the four dimensions, computed from the above

Deliberately NO re-exports here. `from .assess import assess` would bind the name
`assess` in this package to the FUNCTION, shadowing the MODULE of the same name,
so `from domain import assess; assess.assess(...)` would fail with a confusing
AttributeError. Import the modules directly instead.
"""
