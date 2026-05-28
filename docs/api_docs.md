
# MoMo SMS API Documentation

Base URL: `http://127.0.0.1:8000`

Start server
- Run the API server from the project root:

```bash
py -3 -m api.server
# or
python -m api.server
```

Authentication
- This API uses HTTP Basic Authentication. Use the credentials `admin:password123` for all requests.
- Requests without valid Basic Auth credentials will receive a `401 Unauthorized` response.
- Note: examples show `curl` usage. In Windows PowerShell use `curl.exe` to avoid the `Invoke-WebRequest` alias; in Git Bash use `curl` normally.

Examples in this document use `-u admin:password123` with `curl`.

Common fields (from parsed SMS XML)
- `id` (int) — assigned by the API
- `protocol`, `address`, `date`, `type`, `subject`, `body`, `toa`, `sc_toa`, `service_center`, `read`, `status`, `locked`, `date_sent`, `sub_id`, `readable_date`, `contact_name` (strings as parsed from the XML)

---

Base URL: `http://127.0.0.1:8000`

Authentication
-
- This API uses HTTP Basic Authentication. Use the credentials `admin:password123` for all requests.
- Requests without valid Basic Auth credentials will receive a `401 Unauthorized` response.

Examples in this document use `-u admin:password123` with `curl`.

Common fields (from parsed SMS XML)
- `id` (int) — assigned by the API
- `protocol`, `address`, `date`, `type`, `subject`, `body`, `toa`, `sc_toa`, `service_center`, `read`, `status`, `locked`, `date_sent`, `sub_id`, `readable_date`, `contact_name` (strings as parsed from the XML)

---

## GET /transactions

- Method: `GET`
- URL: `/transactions`

Curl example:

```bash
curl -u admin:password123 http://127.0.0.1:8000/transactions
```

Success response (200):

```json
[
  {
    "id": 1,
    "protocol": "0",
    "address": "M-Money",
    "date": "1715351458724",
    "type": "1",
    "subject": "null",
    "body": "You have received 2000 RWF from Jane Smith (*********013) on your mobile money account at 2024-05-10 16:30:51. Message from sender: . Your new balance:2000 RWF. Financial Transaction Id: 76662021700.",
    "toa": "null",
    "sc_toa": "null",
    "service_center": "+250788110381",
    "read": "1",
    "status": "-1",
    "locked": "0",
    "date_sent": "1715351451000",
    "sub_id": "6",
    "readable_date": "10 May 2024 4:30:58 PM",
    "contact_name": "(Unknown)"
  }
]
```

Possible error responses:

- `401 Unauthorized`

```json
{ "error": "Unauthorized" }
```

- `404 Not Found` (wrong endpoint):

```json
{ "error": "Not Found" }
```

---

## GET /transactions/{id}

- Method: `GET`
- URL: `/transactions/{id}` (e.g. `/transactions/1`)

Curl example:

```bash
curl -u admin:password123 http://127.0.0.1:8000/transactions/1
```

Success response (200):

```json
{
  "id": 1,
  "protocol": "0",
  "address": "M-Money",
  "date": "1715351458724",
  "type": "1",
  "subject": "null",
  "body": "You have received 2000 RWF from Jane Smith (*********013) on your mobile money account at 2024-05-10 16:30:51. Message from sender: . Your new balance:2000 RWF. Financial Transaction Id: 76662021700.",
  "toa": "null",
  "sc_toa": "null",
  "service_center": "+250788110381",
  "read": "1",
  "status": "-1",
  "locked": "0",
  "date_sent": "1715351451000",
  "sub_id": "6",
  "readable_date": "10 May 2024 4:30:58 PM",
  "contact_name": "(Unknown)"
}
```

Possible error responses:

- `401 Unauthorized`

```json
{ "error": "Unauthorized" }
```

- `404 Not Found` (transaction id does not exist):

```json
{ "error": "Transaction not found" }
```

---

## POST /transactions

- Method: `POST`
- URL: `/transactions`
- Body: JSON object containing SMS fields (the `id` will be assigned by the server).

Curl example:

```bash
curl -u admin:password123 -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "protocol": "0",
    "address": "M-Money",
    "date": "1718000000000",
    "type": "1",
    "subject": "null",
    "body": "TxId: 1234567890. Sample transaction body text.",
    "toa": "null",
    "sc_toa": "null",
    "service_center": "+250788110381",
    "read": "1",
    "status": "-1",
    "locked": "0",
    "date_sent": "1717999990000",
    "sub_id": "6",
    "readable_date": "10 May 2024 12:00:00 PM",
    "contact_name": "(Unknown)"
  }' \
  http://127.0.0.1:8000/transactions
```

Success response (201):

```json
{
  "id": 1694,
  "protocol": "0",
  "address": "M-Money",
  "date": "1718000000000",
  "type": "1",
  "subject": "null",
  "body": "TxId: 1234567890. Sample transaction body text.",
  "toa": "null",
  "sc_toa": "null",
  "service_center": "+250788110381",
  "read": "1",
  "status": "-1",
  "locked": "0",
  "date_sent": "1717999990000",
  "sub_id": "6",
  "readable_date": "10 May 2024 12:00:00 PM",
  "contact_name": "(Unknown)"
}
```

Possible error responses:

- `400 Bad Request` (malformed JSON):

```json
{ "error": "Malformed JSON" }
```

- `401 Unauthorized`

```json
{ "error": "Unauthorized" }
```

---

## PUT /transactions/{id}

- Method: `PUT`
- URL: `/transactions/{id}` (e.g. `/transactions/1`)
- Body: JSON object containing updated SMS fields (the `id` in the payload is ignored and the URL id is preserved).

Curl example:

```bash
curl -u admin:password123 -X PUT \
  -H "Content-Type: application/json" \
  -d '{
    "protocol": "0",
    "address": "M-Money",
    "date": "1715351458724",
    "type": "1",
    "subject": "null",
    "body": "Updated body text for transaction.",
    "toa": "null",
    "sc_toa": "null",
    "service_center": "+250788110381",
    "read": "1",
    "status": "-1",
    "locked": "0",
    "date_sent": "1715351451000",
    "sub_id": "6",
    "readable_date": "10 May 2024 4:30:58 PM",
    "contact_name": "(Unknown)"
  }' \
  http://127.0.0.1:8000/transactions/1
```

Success response (200):

```json
{
  "id": 1,
  "protocol": "0",
  "address": "M-Money",
  "date": "1715351458724",
  "type": "1",
  "subject": "null",
  "body": "Updated body text for transaction.",
  "toa": "null",
  "sc_toa": "null",
  "service_center": "+250788110381",
  "read": "1",
  "status": "-1",
  "locked": "0",
  "date_sent": "1715351451000",
  "sub_id": "6",
  "readable_date": "10 May 2024 4:30:58 PM",
  "contact_name": "(Unknown)"
}
```

Possible error responses:

- `400 Bad Request` (malformed JSON):

```json
{ "error": "Malformed JSON" }
```

- `401 Unauthorized`

```json
{ "error": "Unauthorized" }
```

- `404 Not Found` (transaction id does not exist):

```json
{ "error": "Transaction not found" }
```

---

## DELETE /transactions/{id}

- Method: `DELETE`
- URL: `/transactions/{id}` (e.g. `/transactions/1`)

Curl example:

```bash
curl -u admin:password123 -X DELETE http://127.0.0.1:8000/transactions/1
```

Success response (200):

```json
{ "status": "deleted", "id": 1 }
```

Possible error responses:

- `401 Unauthorized`

```json
{ "error": "Unauthorized" }
```

- `404 Not Found` (transaction id does not exist):

```json
{ "error": "Transaction not found" }
```

---

## Error Code Reference

| Code | Meaning | Example body |
|------|---------|--------------|
| 200  | OK — request succeeded and returned data | `{ "...": "..." }` |
| 201  | Created — resource created successfully | Created resource JSON (see POST example) |
| 400  | Bad Request — malformed JSON or invalid payload | `{ "error": "Malformed JSON" }` |
| 401  | Unauthorized — missing or invalid Basic Auth credentials | `{ "error": "Unauthorized" }` |
| 404  | Not Found — endpoint or resource not found | `{ "error": "Not Found" }` or `{ "error": "Transaction not found" }` |
