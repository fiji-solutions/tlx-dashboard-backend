# Database Initialization Revert Instructions

## Files to Revert After One-Time Initialization:

### 1. Remove Init Container from k8s/deployment.yaml
Remove lines that contain the `initContainers` section:

```yaml
# Remove this entire section:
initContainers:
- name: db-init
  image: ${IMAGE}
  command: ["python", "/app/init_db.py"]
  env:
  - name: DB_HOST
    valueFrom:
      secretKeyRef:
        name: tlx-dashboard-secrets
        key: db-host
  # ... (rest of init container config)
```

### 2. Remove Database Init Endpoint from app.py
Remove the `/admin/init-db` endpoint:

```python
# Remove this entire function:
@app.route('/admin/init-db', methods=['POST'])
def init_database():
    # ... entire function
```

Also remove the subprocess import if not used elsewhere:
```python
import subprocess  # Remove this line
```

### 3. Delete Initialization Files
```bash
rm init_db.py
rm REVERT_DB_INIT.md
```

### 4. Git Commands to Revert
```bash
# After one-time initialization is complete:
git checkout -- k8s/deployment.yaml app.py
git rm init_db.py REVERT_DB_INIT.md
git commit -m "Remove one-time database initialization setup"
```

## Quick Revert Command
```bash
# One-liner to revert everything:
git checkout -- k8s/deployment.yaml app.py && git rm init_db.py REVERT_DB_INIT.md
```

## Notes
- The init container runs only once when the pod starts
- If initialization is already complete, the script detects this and skips
- The CSV data and schema will remain in the database after revert
- Only the initialization code is removed, not the data