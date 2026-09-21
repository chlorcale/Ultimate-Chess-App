from __future__ import annotations

import json
import urllib.request

import websocket


class CDP:
    """Very small Chrome DevTools Protocol client."""

    def __init__(self, websocket_url: str):
        self.ws = websocket.create_connection(
            websocket_url,
            timeout=5,
            suppress_origin=True,
        )

        self._message_id = 0

    # --------------------------------------------------------
    # Call CDP method
    # --------------------------------------------------------

    def call(
        self,
        method: str,
        params: dict | None = None,
    ) -> dict:

        self._message_id += 1

        request_id = self._message_id

        payload = {
            "id": request_id,
            "method": method,
            "params": params or {},
        }

        self.ws.send(
            json.dumps(payload)
        )

        while True:

            raw = self.ws.recv()

            message = json.loads(raw)

            # Event -> continue waiting
            if message.get("id") != request_id:
                continue

            return message

    # --------------------------------------------------------
    # Evaluate JavaScript
    # --------------------------------------------------------

    def evaluate(
        self,
        expression: str,
    ):

        result = self.call(
            "Runtime.evaluate",
            {
                "expression": expression,
                "returnByValue": True,
            },
        )

        return (
            result
            .get("result", {})
            .get("result", {})
            .get("value")
        )

    # --------------------------------------------------------
    # Close
    # --------------------------------------------------------

    def close(self):

        try:
            self.ws.close()
        except Exception:
            pass


# ============================================================
# GET CDP TARGETS
# ============================================================

def get_targets(
    host: str,
    port: int,
) -> list[dict]:

    url = (
        f"http://{host}:{port}/json/list"
    )

    try:

        with urllib.request.urlopen(
            url,
            timeout=1,
        ) as response:

            return json.loads(
                response.read().decode("utf-8")
            )

    except Exception:
        return []