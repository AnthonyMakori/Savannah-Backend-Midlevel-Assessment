
echo " Anthony Store - Quick Neon Setup"
echo "=========================================="

if ! command -v python3 &> /dev/null; then
    echo " Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

if ! command -v pip3 &> /dev/null; then
    echo " pip3 is not installed. Please install pip."
    exit 1
fi

if [ ! -d "venv" ]; then
    echo " Creating virtual environment..."
    python3 -m venv venv
fi

echo " Activating virtual environment..."
source venv/bin/activate

echo "⬆ Upgrading pip..."
pip install --upgrade pip

echo " Installing requirements..."
pip install -r requirements.txt

echo " Installing PostgreSQL dependencies..."
pip install psycopg2-binary

if [ ! -f ".env" ]; then
    echo " Creating .env file..."
    cp .env.example .env
    echo "  Please update .env file with your database credentials"
fi

echo " Setting up Neon database..."
python scripts/setup_neon_database.py

echo " Starting development server..."
echo "Visit: http://127.0.0.1:8000"
echo "Admin: http://127.0.0.1:8000/admin/"
echo "API Docs: http://127.0.0.1:8000/api/docs/"
echo ""
echo "Login credentials:"
echo "Admin: admin / admin123"
echo "Customer: customer1 / customer123"
echo ""

python manage.py runserver