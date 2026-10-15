# Replace the TypeScript project with Python

The conversion is based on repository commit
`8258cff` (Add Week 4 conversational property search with session memory).
No changes have been pushed to your GitHub repository by this conversion.

## Copy the files

1. Extract the ZIP, then copy its contents into your existing
   `C:\Users\Huy\OneDrive\Documents\A__idx` folder, allowing replacement of
   README and SKILL.md files.
2. Keep the existing `.git` folder, `week3/.env`, SQL data, and any other work.
   The ZIP contains no credentials or `.git` directory.
3. Open Windows Command Prompt and follow the root README to create/reuse the
   Windows virtual environment and install `requirements.txt`.
4. Run the original ten parser tests and the offline regression suite.
5. Keep Ubuntu/MySQL open and test `week3/test_db.py`, an active search, a sold
   search, and the Week 4 conversation.
6. Run `install_openclaw.py` from Windows. It checks the Linux Python helpers
   and MySQL before switching existing skill instructions.
7. Start a new OpenClaw chat and test the helpers, then test through WhatsApp.
8. Once these checks pass, remove the obsolete TypeScript files with:

```cmd
.venv\Scripts\python.exe finish_migration.py
.venv\Scripts\python.exe finish_migration.py --remove-old
```

The first command previews the exact old files. The second removes the named
`.ts` files, each week's `dist` directory, and Node package/lock files. It checks
that Python replacement files exist first. It does not delete `.env`, SQL,
`.git`, or session state. Ignored `node_modules` folders can be deleted manually
afterward; they are no longer needed.

Review your Git diff before pushing, including README and SKILL updates:

```cmd
git status --short
git add README.md MIGRATION.md requirements.txt .env.example .gitignore install_openclaw.py finish_migration.py tests week2 week3 week4
git diff --cached --name-only
git commit -m "Rewrite Weeks 2-4 in Python"
git push origin main
```

Do not use `git add -f` for credentials/data. The updated `.gitignore` excludes
credentials, environments, caches, raw SQL/CSV, Node dependencies, and builds.

## Mapping

| Previous | Python |
| --- | --- |
| `parse_query.ts`, `cli.ts`, demo/test files | Same names with `.py` |
| `db.ts`, `search.ts`, `sold.ts`, `format.ts` | Same names with `.py` |
| `session.ts`, `conversation.ts`, helper/demo files | Same names with `.py` |
| `npm` dependencies | Root `requirements.txt` |
| `node dist/.../cli.js` | Virtual-environment Python and `weekN/cli.py` |
| Compiled `dist` folders | No compilation required |

Python functions use snake_case; output filter keys stay camelCase so existing
JSON and session files remain compatible. `None` replaces TypeScript `null`.
The stored boolean preference strings remain `"True"` and `"False"`.

## Practical limits

This is a port, so existing regex wording limitations and sequential JSON state
updates remain. It does not add cross-process locking, arbitrary language
understanding, new data, automatic session expiry, or model quota.
MySQL and WhatsApp have to be rechecked on your PC; offline tests cannot verify
your running services. Old OpenClaw runtime files may remain unused after the
skill switches to Python. The installer keeps old SKILL instructions for rollback.
