import json
from db import get_connection


# FETCH LOGS FOR ONE TRANSACTION
def get_transaction_logs(connection, transaction_id):

    cursor = connection.cursor(dictionary=True)

    query = """
    SELECT
        log_id,
        message
    FROM system_logs
    WHERE transaction_id = %s
    """

    cursor.execute(query, (transaction_id,))
    return cursor.fetchall()


# SERIALIZE ONE TRANSACTION
def serialize_transaction(row, logs):

    return {
        "transaction_id": row["transaction_id"],
        "amount": float(row["amount"]),
        "fee": float(row["fee"]),
        "balance": float(row["balance"]),
        "status": row["status"],
        "date": str(row["date"]),

        "sender": {
            "user_id": row["sender_id"],
            "username": row["sender_username"],
            "phone_number": row["sender_phone"]
        },

        "receiver": {
            "user_id": row["receiver_id"],
            "username": row["receiver_username"],
            "phone_number": row["receiver_phone"]
        },

        "category": {
            "category_id": row["category_id"],
            "category_name": row["category_name"],
            "description": row["category_description"]
        },

        "logs": logs
    }


# MAIN FUNCTION
def fetch_transactions():

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
    SELECT
        t.transaction_id,
        t.amount,
        t.fee,
        t.balance,
        t.status,
        t.date,

        s.user_id AS sender_id,
        s.username AS sender_username,
        s.phone_number AS sender_phone,

        r.user_id AS receiver_id,
        r.username AS receiver_username,
        r.phone_number AS receiver_phone,

        c.category_id,
        c.category_name,
        c.description AS category_description

    FROM transactions t

    JOIN users s ON t.sender_id = s.user_id
    JOIN users r ON t.receiver_id = r.user_id
    JOIN transaction_categories c ON t.category_id = c.category_id
    """

    cursor.execute(query)
    rows = cursor.fetchall()

    transactions = []

    for row in rows:
        logs = get_transaction_logs(connection, row["transaction_id"])

        transactions.append(
            serialize_transaction(row, logs)
        )

    connection.close()
    return transactions


# RUN SCRIPT
if __name__ == "__main__":
    transactions = fetch_transactions()
    print(json.dumps(transactions, indent=4))
