"""Security notes for the local demonstration implementation.

The approval token is a development gate, not production identity management.
Use a real authenticated identity provider, scoped roles, audit logging and
secret rotation before any production deployment. Bind the development server
to loopback by default and never expose it directly to an untrusted network.
"""
