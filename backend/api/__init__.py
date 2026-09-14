"""HTTP layer. Thin on purpose.

Routers translate between HTTP and the domain and nothing else -- no ecological
knowledge, no business rules, no persistence details. Each resource is one module,
so adding or removing an endpoint touches one file.
"""
