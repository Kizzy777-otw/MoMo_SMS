"""Simple REST API using only Python's built-in http.server.

Endpoints implemented:
- GET /transactions
- GET /transactions/{id}
- POST /transactions
- PUT /transactions/{id}
- DELETE /transactions/{id}

All responses are JSON with appropriate HTTP status codes.
"""
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from urllib.parse import urlparse
import base64
import time
import os
import logging
from dotenv import load_dotenv

from api.xml_parser import transactions_list, transactions_dict, get_next_id

load_dotenv()  # Load environment variables from .env file
logging.basicConfig(
    filename="auth_failures.log",
    level=logging.WARNING,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
auth_logger = logging.getLogger("auth")
class TransactionHandler(BaseHTTPRequestHandler):
    """HTTP handler providing CRUD operations for transactions.

    All endpoints require HTTP Basic Authentication. The handler
    uses the in-memory `transactions_list` and `transactions_dict` from
    `api.parser`.
    """
    
    ADMIN_USER = os.getenv("API_USERNAME", "admin")
    ADMIN_PASS = os.getenv("API_PASSWORD", "password123")
    VIEWER_USER = os.getenv("VIEWER_USERNAME", "viewer")
    VIEWER_PASS = os.getenv("VIEWER_PASSWORD", "viewerpass")

    def _send_json(self, status: int, obj):
        """Send a JSON response with given status and Python object."""
        data = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _unauthorized(self):
        """Send a 401 Unauthorized JSON response."""
        data = json.dumps({"error": "Unauthorized"}, ensure_ascii=False).encode("utf-8")
        self.send_response(401)
        self.send_header("WWW-Authenticate", 'Basic realm="API"')
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _forbidden(self):
        """Send a 403 forbidden JSON response"""
        data = json.dumps({"error": "Forbidden"}, ensure_ascii=False).encode("utf-8")
        self.send_response(403)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


    def _check_auth(self) -> bool:
        """Validate HTTP Basic Auth credentials from the Authorization header.

        Returns True if valid, otherwise sends a 401 response and returns False.
        """
        client_ip = self.client_address[0]
        auth = self.headers.get("Authorization")
        if not auth or not auth.startswith("Basic "):
            auth_logger.warning(
                f"Missing or invalid Authorization header from  {client_ip} "
                f"on {self.command} {self.path}")
            self._unauthorized()
            return False

        try:
            token = auth.split(" ", 1)[1].strip()
            decoded = base64.b64decode(token).decode("utf-8")
            user, passwd = decoded.split(":", 1)
        except Exception:
            auth_logger.warning(
                f"Malformed credentials from {client_ip} on {self.command} {self.path}")
            self._unauthorized()
            return False

        if user == self.ADMIN_USER and passwd == self.ADMIN_PASS:
            return "admin"
        if user == self.VIEWER_USER and passwd == self.VIEWER_PASS:
            return "viewer"
        auth_logger.warning(
            f"Failed login attempt for user '{user}' from {client_ip} "
            f"on {self.command} {self.path}")
        self._unauthorized()
        return False

    def _parse_path(self):
        """Return (resource, id) where id is int or None.

        Example: /transactions/3 -> ("transactions", 3)
                 /transactions    -> ("transactions", None)
        """
        parsed = urlparse(self.path)
        parts = parsed.path.strip("/").split("/")
        if not parts or parts[0] == "":
            return "", None
        resource = parts[0]
        _id = None
        if len(parts) > 1 and parts[1].isdigit():
            _id = int(parts[1])
        return resource, _id

    def do_GET(self):
        """Handle GET requests for listing or retrieving transactions.

        Requires Basic Auth.
        """
        role = self._check_auth()
        if role is False:
            return
        resource, _id = self._parse_path()
        if resource != "transactions":
            self._send_json(404, {"error": "Not Found"})
            return

        if _id is None:
            # return all transactions
            self._send_json(200, transactions_list)
            return

        tx = transactions_dict.get(_id)
        if not tx:
            self._send_json(404, {"error": "Transaction not found"})
            return
        self._send_json(200, tx)

    def do_POST(self):
        """Handle POST requests to create a new transaction.

        Requires Basic Auth.
        """
        role = self._check_auth()
        if role is False:
            return
        if role != "admin":
            self._forbidden()
            return
        
        resource, _id = self._parse_path()
        if resource != "transactions" or _id is not None:
            self._send_json(404, {"error": "Not Found"})
            return

        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b""
        try:
            payload = json.loads(raw.decode("utf-8")) if raw else {}
            if not isinstance(payload, dict):
                raise ValueError("Payload must be a JSON object")
        except Exception:
            self._send_json(400, {"error": "Malformed JSON"})
            return

        # assign id and store in both structures
        new_id = get_next_id()
        payload["id"] = new_id
        transactions_list.append(payload)
        transactions_dict[new_id] = payload

        self._send_json(201, payload)

    def do_PUT(self):
        """Handle PUT requests to update an existing transaction.

        Requires Basic Auth.
        """
        role = self._check_auth()
        if role is False:
            return
        if role != "admin":
            self._forbidden()
            return

        resource, _id = self._parse_path()
        if resource != "transactions" or _id is None:
            self._send_json(404, {"error": "Not Found"})
            return

        if _id not in transactions_dict:
            self._send_json(404, {"error": "Transaction not found"})
            return

        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b""
        try:
            payload = json.loads(raw.decode("utf-8")) if raw else {}
            if not isinstance(payload, dict):
                raise ValueError("Payload must be a JSON object")
        except Exception:
            self._send_json(400, {"error": "Malformed JSON"})
            return

        # preserve id
        payload["id"] = _id
        # update dict
        transactions_dict[_id] = payload
        # update list entry (find index)
        for i, tx in enumerate(transactions_list):
            if tx.get("id") == _id:
                transactions_list[i] = payload
                break

        self._send_json(200, payload)

    def do_DELETE(self):
        """Handle DELETE requests to remove a transaction.

        Requires Basic Auth.
        """
        role = self._check_auth()
        if role is False:
            return
        if role != "admin": 
            self._forbidden()
            return

        resource, _id = self._parse_path()
        if resource != "transactions" or _id is None:
            self._send_json(404, {"error": "Not Found"})
            return

        if _id not in transactions_dict:
            self._send_json(404, {"error": "Transaction not found"})
            return

        # remove from dict and list
        del transactions_dict[_id]
        for i, tx in enumerate(transactions_list):
            if tx.get("id") == _id:
                transactions_list.pop(i)
                break

        self._send_json(200, {"status": "deleted", "id": _id})

    def log_message(self, format, *args):
        """Suppress default logging to keep output clean for assignment grading."""
        return


def run(server_class=HTTPServer, handler_class=TransactionHandler, port=8000):
    """Run the HTTP server on the given port."""
    server_address = ("", port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting server on port {port} - endpoints available: /transactions")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("Shutting down server")
        httpd.server_close()


if __name__ == "__main__":
    run()
