# Azure deployment and runtime preservation

RIPARIA runs on Azure App Service `riparia-oah`, resource group `signwise-rg`,
using the existing Linux Python 3.12 app. No service plan, pricing or model
credential changes are required for this release.

## Runtime data is separate from releases

On Azure, `WEBSITE_SITE_NAME` makes the backend use:

```text
/home/data/riparia/riparia.db
/home/data/riparia/uploads/
```

Local defaults remain `backend/adapters/riparia.db` and `backend/uploads/`.
`RIPARIA_DATA_DIR` can override the data directory. This matters because Oryx
serves a built Python application from `/tmp/<uid>`, which is not persistent
across restarts. Runtime files should live under `/home`.
[Azure Python configuration](https://learn.microsoft.com/en-us/azure/app-service/configure-language-python).

The release ZIP includes only Python source, requirements and built frontend
assets. It excludes `.env`, credentials, virtual environments, SQLite files and
uploads. Persistent data is never bundled into a code release or public repository.

## Prepare and verify a release

```bash
cd frontend
npm run lint
npm run build
cd ../backend
.venv/bin/python test_assess.py
.venv/bin/python -m unittest -v test_handoff
cd ..
python3 scripts/stage_release.py
```

`stage_release.py` creates a temporary directory outside the repository, prints
the ZIP path and writes a `manifest.json`. It checks the package for forbidden
runtime files and the configured model key without printing the key. Stage only
after the last frontend build; the printed shell hash identifies that release.

## One-time migration from the previous temporary runtime

`scripts/preserve_runtime.py` is a standalone standard-library script. Copy it
into `/home/data/riparia-tools/` in the app container through an authenticated
Azure SSH session. This copy contains code only, no credentials. Enter the
container with:

```bash
az webapp ssh --resource-group signwise-rg --name riparia-oah
```

Then run inside that container:

```bash
python /home/data/riparia-tools/preserve_runtime.py
```

The script uses SQLite's online backup API, checks integrity and every row,
copies existing uploads, and verifies referenced file hashes. It writes a dated
backup under `/home/data/riparia-backups/` and a persistent runtime copy. Any
already-missing photo is recorded as missing; it is never reconstructed from a
similarly named local image.

An initial snapshot does not freeze ongoing writes. When the ZIP is ready,
refresh the snapshot with the following command **immediately before deploying**:

```bash
python /home/data/riparia-tools/preserve_runtime.py --freeze
```

This waits for an existing SQLite writer, then installs three temporary triggers
that abort new inserts, updates and deletes against the old runtime database.
Reads remain available; clients may need to retry a save during this short
maintenance window. The final backup therefore cannot miss a write accepted by
the old worker during Azure's build. The persistent destination has these
triggers removed and accepts writes as soon as the new application starts.

From the local machine, use the ZIP path printed by the staging script:

```bash
az webapp deploy --resource-group signwise-rg --name riparia-oah \
  --src-path /absolute/path/from/stage_release/riparia.zip --type zip \
  --clean false --restart true --track-status false --async true
```

After this first migration, future releases use the persistent directory and do
not repeat the temporary-runtime migration. Take a fresh backup before future
data/schema changes; never replace a populated persistent database with an older
snapshot.

## Roll back the write freeze

If deployment fails and the old worker remains active, restore its write access
in the same SSH session immediately:

```bash
python /home/data/riparia-tools/preserve_runtime.py --unfreeze
```

If the shell no longer has the old `APP_PATH`, pass the original runtime directory
explicitly with `--runtime /tmp/<original-id>`. This drops only the three
`riparia_deploy_block_*` triggers. It does not delete reports or backups. The
migration script also removes the old freeze automatically if its own copy or
verification fails. If an application rollback is needed after the new worker
starts, preserve its `/home/data/riparia` first; do not overwrite new reports with
the earlier backup.

## Verify the running application

The Azure command's exit code is insufficient: previous deploys reported a
failure after a working app started, and served the old bundle during cold start.
Verify all of these against the public URL:

- The response body of `/` hashes to the staged `index_sha256` and references the
  intended fingerprinted JavaScript/CSS files.
- `/api/health` returns JSON and `/api/sites` returns site JSON, not an HTML fallback.
- Every pre-deployment record ID and original stored report remains readable.
- Every previously available photo has the same hash. Pre-existing missing
  references remain documented as missing.
- A post-start inspection confirms `store.DB_PATH` and `UPLOADS` are under
  `/home/data/riparia` and no maintenance triggers remain there.

## September 15, 2026 release evidence

Final frontend assets: `index-a93AXrZU.js` and `index-BJBnMzlj.css`.
Shell SHA256: `bf7cc9d41bcc77e5cc42d0ecf407dc579708d48c3f97cb7dc7ca179086fac0ea`.
Backend verification: **39 assessment checks and 12 isolated HTTP tests passed**.
A separate temporary-database rehearsal verified migration, old-write blocking,
new-write acceptance and freeze rollback.

The live source contained **7 reports** (5 labelled authentic, 2 synthetic) and
**2 references to one already-missing file**, `/uploads/test_stream.png`. The
runtime upload directory was already empty and that URL already returned 404.
No photo bytes existed to preserve or hash, and no replacement image was supplied.
All 7 rows were compared exactly after copying to persistent storage. This
documents a pre-existing limitation, not a claim that those labels are verified.

Final pre-deployment backup:
`/home/data/riparia-backups/20260915T081706769189Z`.
The manifest records counts, hashes of available files, and missing references.

Deployment `17a364da-f2c1-43b7-baec-1b190973b729` completed its Azure build at
08:18:46 UTC. After cold start, the public shell and both frontend assets matched
the staged bytes exactly. `/api/sites` and `/api/health` returned JSON. All seven
pre-deployment observation objects matched the live records field for field.
The pre-existing missing photo still returned 404.

A new SSH session inside the running release confirmed
`store.DB_PATH=/home/data/riparia/riparia.db`,
`UPLOADS=/home/data/riparia/uploads`, seven records, SQLite integrity `ok`, and
**zero maintenance triggers**. The new release accepts writes to persistent
storage. No extra live test observations were created during this deployment.
