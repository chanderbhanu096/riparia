# RIPARIA — frontend

React PWA. Holds no ecological knowledge of its own: the indicator list and the
field differentials are served from the backend's `field_protocol.py` via
`/api/protocol`, so domain content has exactly one home.

See the root `README.md` for what this is and `AUDIT.md` for why it is built this way.

```bash
npm install
npm run dev     # expects the API on :8000
npm run build   # FastAPI serves dist/ in production
```
