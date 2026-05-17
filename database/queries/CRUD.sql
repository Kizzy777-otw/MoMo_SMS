-- MoMo_SMS CRUD operations
-- Run these queries after loading schema and seed data from database/db.sql

-- ==================================================
-- C - CREATE
-- ==================================================

INSERT INTO Users (username, phone_number)
VALUES ('Diane', '0777000000');

INSERT INTO Transactions (
    amount,
    fee,
    balance,
    status,
    date,
    sender_id,
    receiver_id,
    category_id
) VALUES (
    15.00,
    0.15,
    950.00,
    'Completed',
    '2024-01-07 16:00:00',
    1,
    2,
    2
);

-- ==================================================
-- R - READ
-- ==================================================

SELECT transaction_id, amount, fee, balance, status, sender_id, receiver_id
FROM Transactions
ORDER BY transaction_id
LIMIT 3;

SELECT category_id, category_name
FROM Transaction_Categories;

-- ==================================================
-- U - UPDATE
-- ==================================================

UPDATE Transactions
SET status = 'Reversed'
WHERE transaction_id = 2;

SELECT transaction_id, status
FROM Transactions
WHERE transaction_id = 2;

-- ==================================================
-- D - DELETE
-- ==================================================

DELETE FROM System_Logs
WHERE log_id = 6;

SELECT log_id, transaction_id, message
FROM System_Logs
ORDER BY log_id;
