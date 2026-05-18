# MoMo SMS Data Analyzer

## Team Name

G4 Team

## Project Description

Process MoMo SMS XML data, clean and categorize transactions, store results in SQLite, and visualize analytics on a frontend dashboard.

## Team Members

- Member 1: Aldrick KALISA MPANO
- Member 2: Kizito IMENA UWIZEYE
- Member 3: Dalynah GASARASI

## Project Structure

```text
├── README.md
├── .env.example
├── requirements.txt
├── index.html
├── web/
├── data/
├── etl/
├── api/
├── scripts/
└── tests/
```

## Architecture Diagram

https://miro.com/app/board/uXjVHV3F_yA=/

## SCRUM BOARD

https://trello.com/invite/b/6a00e7a0f22a5baed5d9b258/ATTIe3878dc96b53f39d86fe36d1dd6945e1548919D2/momo-sms

## ERD Diagram

The ERD models how users send/receive transactions, how transactions are categorized, and how audit logs are attached.

### Entities

1. `Users`
- Stores account identity used in transactions.
- Primary key: `user_id`
- Important fields: `username` (unique), `phone_number` (unique)

2. `Transactions`
- Stores each money movement record.
- Primary key: `transaction_id`
- Important fields: `amount`, `fee`, `balance`, `status`, `date`
- Foreign keys:
  - `sender_id` -> `Users.user_id`
  - `receiver_id` -> `Users.user_id`
  - `category_id` -> `Transaction_Categories.category_id`
- Constraint:
  - `CHECK (sender_id IS NULL OR receiver_id IS NULL OR sender_id <> receiver_id)` prevents same-user sender/receiver pairs when both are present.

3. `Transaction_Categories`
- Stores available transaction grouping labels.
- Primary key: `category_id`
- Important fields: `category_name`, `description`

4. `User_Categories`
- Junction table showing category usage per user.
- Composite primary key: (`user_id`, `category_id`)
- Foreign keys:
  - `user_id` -> `Users.user_id`
  - `category_id` -> `Transaction_Categories.category_id`
- Important field: `usage_count`

5. `System_Logs`
- Stores system or audit messages related to transactions.
- Primary key: `log_id`
- Foreign key:
  - `transaction_id` -> `Transactions.transaction_id`
- Important fields: `message`, `timestamp`

### Relationships (Cardinality)

1. `Users` (1) -> (M) `Transactions` as sender
- One user can send many transactions.

2. `Users` (1) -> (M) `Transactions` as receiver
- One user can receive many transactions.

3. `Transaction_Categories` (1) -> (M) `Transactions`
- One category can classify many transactions.

4. `Users` (M) <-> (M) `Transaction_Categories` via `User_Categories`
- A user can be associated with many categories, and a category can be associated with many users.

5. `Transactions` (1) -> (M) `System_Logs`
- One transaction can have multiple log entries.

### Referential Integrity

- `ON DELETE CASCADE` is applied on foreign keys so related child rows are removed automatically when a parent row is deleted.
- This keeps the database consistent and avoids orphan records.

## SQL Database Implementation

- Database Name: momo_sms
  The database contains the following tables:

1. Transactions
2. Users
3. User_Categories
4. Transaction_Categories
5. System_Logs

Schema file: `database/db.sql`
CRUD query file: `database/queries/CRUD.sql`

## CRUD Operations Used and Sample Results

### C - Create

```sql
INSERT INTO Users (username, phone_number)
VALUES ('Diane', '0777000000');
```

Sample result:

```text
Query OK, 1 row affected
```

```sql
INSERT INTO Transactions (
    amount, fee, balance, status, date, sender_id, receiver_id, category_id
) VALUES (
    15.00, 0.15, 950.00, 'Completed', '2024-01-07 16:00:00', 1, 2, 2
);
```

Sample result:

```text
Query OK, 1 row affected
```

### R - Read

```sql
SELECT transaction_id, amount, fee, balance, status, sender_id, receiver_id
FROM Transactions
ORDER BY transaction_id
LIMIT 3;
```

Sample result:

```text
+----------------+--------+------+---------+-----------+-----------+-------------+
| transaction_id | amount | fee  | balance | status    | sender_id | receiver_id |
+----------------+--------+------+---------+-----------+-----------+-------------+
| 1              | 50.00  | 0.50 | 1000.00 | Completed | 1         | 2           |
| 2              | 20.00  | 0.20 | 980.00  | Completed | 1         | 3           |
| 3              | 30.00  | 0.30 | 970.00  | Completed | 2         | 1           |
+----------------+--------+------+---------+-----------+-----------+-------------+
```

```sql
SELECT category_id, category_name
FROM Transaction_Categories;
```

Sample result:

```text
+-------------+------------------+
| category_id | category_name    |
+-------------+------------------+
| 1           | Food             |
| 2           | Transport        |
| 3           | Entertainment    |
+-------------+------------------+
```

### U - Update

```sql
UPDATE Transactions
SET status = 'Reversed'
WHERE transaction_id = 2;
```

Sample result:

```text
Query OK, 1 row affected
Rows matched: 1  Changed: 1  Warnings: 0
```

```sql
SELECT transaction_id, status
FROM Transactions
WHERE transaction_id = 2;
```

Sample result:

```text
+----------------+----------+
| transaction_id | status   |
+----------------+----------+
| 2              | Reversed |
+----------------+----------+
```

### D - Delete

```sql
DELETE FROM System_Logs
WHERE log_id = 6;
```

Sample result:

```text
Query OK, 1 row affected
```

```sql
SELECT log_id, transaction_id, message
FROM System_Logs
ORDER BY log_id;
```

Sample result:

```text
+--------+----------------+------------------------------------+
| log_id | transaction_id | message                            |
+--------+----------------+------------------------------------+
| 1      | 1              | Transaction completed successfully |
| 2      | 2              | Transaction completed successfully |
| 3      | 3              | Transaction completed successfully |
| 4      | 4              | Transaction completed successfully |
| 5      | 5              | Transaction completed successfully |
+--------+----------------+------------------------------------+
```
