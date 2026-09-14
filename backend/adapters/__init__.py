"""Adapters: the only code here that talks to the outside world.

Persistence and model providers live behind narrow interfaces so either can be
replaced without the domain or the API noticing. Swapping SQLite for Postgres is
one file; swapping the vision provider is one file plus one config value.
"""
