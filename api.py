from flask import Flask, jsonify
import requests
from cachetools import cached, TTLCache

# Inisialisasi Flask app
app = Flask(__name__)

# Cache untuk menyimpan data API selama 60 detik
cache = TTLCache(maxsize=100, ttl=60)

# Menggunakan session untuk mengoptimalkan HTTP requests
session = requests.Session()

# Header dan API key untuk CoinGecko API
cg_headers = {
    "accept": "application/json",
    "x-cg-demo-api-key": "CG-kG6RCQG7WUbgsLurhibPYh5m"
}

# Fungsi untuk mengambil data dari API dengan cache
@cached(cache)
def fetch_data(url, use_cg_headers=False):
    headers = cg_headers if use_cg_headers else None
    response = session.get(url, headers=headers)
    response.raise_for_status()  # Tangani error HTTP
    return response.json()

# Endpoint utama
@app.route('/data', methods=['GET'])
def shares():
    # URL API
    shares_url = "https://qubic.nevermine.io/VHTDSWYLKHBYCAFESSZGSHABLOEDXZDQYYQZJXNXXAKHDDUJXQZFXQHCHONE"
    pool_stats_url = "https://qubic.nevermine.io/poolStats"
    price_url = "https://api.coingecko.com/api/v3/simple/price?ids=qubic-network&vs_currencies=usd"

    try:
        # Ambil data dari API eksternal
        shares_data = fetch_data(shares_url)
        pool_data = fetch_data(pool_stats_url)
        price_data = fetch_data(price_url, use_cg_headers=True)
    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 500

    # Mengambil harga dari API CoinGecko
    price = price_data.get("qubic-network", {}).get("usd", 0)

    # Menghitung total shares dan total Its
    total_shares = sum(worker['shares'] for worker in shares_data)
    total_its = sum(worker['avgIts'] for worker in shares_data)

    # Mengambil data pool
    pool_shares = pool_data.get("poolShares", 0)
    pool_solution = pool_data.get("poolSolution", 0)

    # Menghitung EstIncome
    est_income = (total_shares / pool_shares) * pool_solution if pool_shares > 0 else 0
    est_income = round(est_income, 3)  # Batasi 3 angka di belakang koma

    # Menghitung EstQUS dan EstUSD
    qus_multiplier = 3773416
    est_qus = round(est_income * qus_multiplier, 3)
    est_usd = round(est_qus * price, 3)

    # Menghitung ShareRate
    share_rate = round(pool_shares / pool_solution, 3) if pool_solution > 0 else 0

    # Format hasil
    result = {
        "shares": [
            {
                "Its": total_its,
                "totalShare": total_shares,
                "EstIncome": est_income,
                "EstQUS": est_qus,
                "EstUSD": est_usd,
                "ShareRate": share_rate
            }
        ]
    }

    # Kembalikan hasil sebagai JSON
    return jsonify(result)

# Tidak menggunakan app.run(), karena Gunicorn akan menjalankan aplikasi
