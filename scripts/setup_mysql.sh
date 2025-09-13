
echo "Setting up MySQL for Django Store Backend..."

if ! command -v mysql &> /dev/null; then
    echo "MySQL is not installed. Please install MySQL first."
    echo "On Ubuntu/Debian: sudo apt-get install mysql-server"
    echo "On macOS: brew install mysql"
    echo "On Windows: Download from https://dev.mysql.com/downloads/mysql/"
    exit 1
fi

if ! pgrep -x "mysqld" > /dev/null; then
    echo "MySQL is not running. Please start MySQL service."
    echo "On Ubuntu/Debian: sudo systemctl start mysql"
    echo "On macOS: brew services start mysql"
    exit 1
fi

echo "Creating database and user..."
mysql -u root -p << EOF
CREATE DATABASE IF NOT EXISTS store CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'store_user'@'localhost' IDENTIFIED BY 'store_password';
GRANT ALL PRIVILEGES ON store.* TO 'store_user'@'localhost';
FLUSH PRIVILEGES;
EOF

echo "Database setup complete!"
echo "Database: store"
echo "User: store_user"
echo "Password: store_password"
echo ""
echo "Update your .env file with these credentials:"
echo "DB_NAME=store"
echo "DB_USER=store_user"
echo "DB_PASSWORD=store_password"
echo "DB_HOST=localhost"
echo "DB_PORT=3306"