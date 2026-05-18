-- Database: MOMO_SMS

-- Table structure for table `Users`
CREATE TABLE IF NOT EXISTS Users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    phone_number VARCHAR(20) NOT NULL UNIQUE
);

-- Table structure for table `Transaction_Categories`
CREATE TABLE IF NOT EXISTS Transaction_Categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(255),
    description TEXT
);

-- Table structure for table `User_Categories`
CREATE TABLE IF NOT EXISTS User_Categories (
    user_id INT,
    category_id INT,
    usage_count INT DEFAULT 0,
    PRIMARY KEY (user_id, category_id),
    FOREIGN KEY (user_id) REFERENCES Users (user_id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES Transaction_Categories (category_id) ON DELETE CASCADE
);

-- Table structure for table `Transactions`
CREATE TABLE IF NOT EXISTS Transactions (
    transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    amount DECIMAL(10, 2) NOT NULL,
    fee DECIMAL(10, 2) NOT NULL,
    balance DECIMAL(10, 2) NOT NULL,
    status VARCHAR(50) NOT NULL,
    date DATETIME NOT NULL,
    sender_id INT,
    receiver_id INT,
    category_id INT,
    CHECK (
        sender_id IS NULL
        OR receiver_id IS NULL
        OR sender_id <> receiver_id
    ),
    FOREIGN KEY (sender_id) REFERENCES Users (user_id) ON DELETE CASCADE,
    FOREIGN KEY (receiver_id) REFERENCES Users (user_id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES Transaction_Categories (category_id) ON DELETE CASCADE
);

--  Table structure for table `System_Logs`
CREATE TABLE IF NOT EXISTS System_Logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    transaction_id INT,
    message TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (transaction_id) REFERENCES Transactions (transaction_id) ON DELETE CASCADE
);

-- Indexes for the Transactions table
INDEX idx_sender_id ON Transactions (sender_id);

INDEX idx_receiver_id ON Transactions (receiver_id);

INDEX idx_category_id ON Transactions (category_id);

-- Indexes for Users table
INDEX idx_username ON Users (username);