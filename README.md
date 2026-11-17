# mockroute

A tiny local mock backend for testing login flows, run from the command line.

## Why

Frontend and mobile developers often get blocked waiting for a live authentication API, or burn through rate limits and API costs during routine UI testing. `mockroute` runs on your own machine and answers login requests from local JSON files, so you can test success, wrong-password and locked-account states in seconds, offline, without touching a real server.

## What it does

- **Answers logins like a real API.** On `POST` requests it reads `email` and `password` from the JSON body and replies `200 OK` (with the user's profile), `401 Unauthorized` (unknown email or wrong password) or `403 Forbidden` (correct password, suspended account). Bad requests get `400`, unknown paths `404`, and a wrong HTTP method `405`.
- **Keeps its data in plain JSON files** in `~/.config/mockroute/` (`%USERPROFILE%\.config\mockroute\` on Windows): the users, and the routes you register.
- **Has four commands:** `init`, `add`, `list` and `start`.

## Requirements

- Python 3 (developed and tested with Python 3.13). Only the standard library is used, so there is nothing to install.

## Quick start

1. Clone the repo and enter it:

   ```bash
   git clone https://github.com/vjyx/mockroute.git
   cd mockroute
   ```

2. Create the workspace:

   ```bash
   python -m mockroute init
   ```

3. Copy the sample users into the workspace (`init` creates an empty users file):

   - **Windows (PowerShell):**

     ```powershell
     Copy-Item examples\users.json $env:USERPROFILE\.config\mockroute\data\users.json
     ```

   - **Linux / macOS:**

     ```bash
     cp examples/users.json ~/.config/mockroute/data/users.json
     ```

4. Register the login route:

   ```bash
   python -m mockroute add /api/v1/auth --method POST
   ```

5. Start the server (leave this terminal open; stop it with `Ctrl+C`):

   ```bash
   python -m mockroute start --port 9000
   ```

6. In a **second terminal**, from the repo folder, send the three example requests.

   - **Windows (PowerShell)** uses `curl.exe`:

     ```powershell
     curl.exe -i -X POST http://127.0.0.1:9000/api/v1/auth -H "Content-Type: application/json" --data-binary "@examples\ok.json"
     curl.exe -i -X POST http://127.0.0.1:9000/api/v1/auth -H "Content-Type: application/json" --data-binary "@examples\bad.json"
     curl.exe -i -X POST http://127.0.0.1:9000/api/v1/auth -H "Content-Type: application/json" --data-binary "@examples\locked.json"
     ```

   - **Linux / macOS:**

     ```bash
     curl -i -X POST http://127.0.0.1:9000/api/v1/auth -H "Content-Type: application/json" --data-binary @examples/ok.json
     curl -i -X POST http://127.0.0.1:9000/api/v1/auth -H "Content-Type: application/json" --data-binary @examples/bad.json
     curl -i -X POST http://127.0.0.1:9000/api/v1/auth -H "Content-Type: application/json" --data-binary @examples/locked.json
     ```

### What you should see

| File | Meaning | Response |
|---|---|---|
| `examples/ok.json` | correct credentials | `200 OK` |
| `examples/bad.json` | wrong password | `401 Unauthorized` |
| `examples/locked.json` | correct password, suspended account | `403 Forbidden` |

**200 OK**

```http
HTTP/1.0 200 OK
Content-Type: application/json

{"profile": {"uid": 101, "name": "Jane Doe", "role": "Engineer"}}
```

**401 Unauthorized**

```http
HTTP/1.0 401 Unauthorized
Content-Type: application/json

{"error": "Invalid client credentials supplied"}
```

**403 Forbidden**

```http
HTTP/1.0 403 Forbidden
Content-Type: application/json

{"status": "Access Denied", "reason": "Account Suspended"}
```

The server terminal prints one log line per request, for example `"POST /api/v1/auth HTTP/1.1" 200 -`.

## Commands

| Command | What it does |
|---|---|
| `python -m mockroute init` | Creates the workspace and starter files. Safe to run again: it never overwrites existing data. |
| `python -m mockroute add PATH --method METHOD` | Registers a route (`METHOD` defaults to `GET`). |
| `python -m mockroute list` | Shows the registered routes. |
| `python -m mockroute start --port PORT` | Starts the server (`PORT` defaults to `9000`). |

Errors go to `stderr` and the exit code is non-zero (`1` for a runtime error, `2` for invalid usage).

## How it works

```text
  Client (curl / your app)
        |   POST /api/v1/auth   {"email": ..., "password": ...}
        v
  +-------------------------- mockroute ---------------------------+
  |  Server  (server.py)   one thread per request                   |
  |    1. Router.resolve(method, path) ---------> 404 / 405         |
  |    2. read and validate the JSON body ------> 400               |
  |    3. Authenticator.authenticate(...) ------> 200 / 401 / 403   |
  |                         |                                       |
  |                         v                                       |
  |  Storage  (storage.py)  atomic JSON reads and writes            |
  +-------------------------+---------------------------------------+
                            v
        ~/.config/mockroute/
            config.json
            data/users.json
            data/routes.json

  CLI (cli.py): init | add | list | start  --->  Storage / Server
```

Each layer does one job and knows nothing about the others' details:

- **Storage** is the only code that touches the disk. Writes go to a temporary file first and are swapped in with `os.replace`, so a crash can never leave a half-written file.
- **Router** decides whether a request matches a registered route. It has no HTTP code and reads the routes on every request, so routes you add while the server runs are picked up.
- **Authenticator** decides `200`, `401` or `403` from an email and password. It checks, in order: the user exists, the password matches, the account is not locked.
- **Server** turns an HTTP request into calls to the Router and Authenticator, and their answers into HTTP responses.
- **CLI** parses terminal commands and calls Storage or starts the Server.

## Running the tests

```bash
python -m unittest discover -v
```

Run this from the repository root. The suite covers storage, the CLI, authentication, routing and the HTTP server (the server tests start a real server on a free port in a background thread and send real requests).

## Limitations and next steps

- **Every registered route runs the login logic.** A next step is letting each route return a configurable response (status, body, delay) so any API can be mocked, including error cases such as `429` and `500`.
- **Passwords are stored in plain text.** That is acceptable for a local mock tool, but a real system must store them hashed with a slow, salted algorithm such as bcrypt or argon2.
- **Minimal error handling for the server start.** If the port is already in use, you will see a raw Python error instead of a friendly message.
- **The workspace lives in `~/.config/mockroute` on every OS**, including Windows, and `XDG_CONFIG_HOME` is not honoured.
- **HTTP only.** The server does not support HTTPS.
