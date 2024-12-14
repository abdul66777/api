from flask import Flask, jsonify
import requests

app = Flask(__name__)

@app.route('/data', methods=['GET'])
def shares():
    # URL untuk mendapatkan data shares
    shares_url = "https://qubic.nevermine.io/VHTDSWYLKHBYCAFESSZGSHABLOEDXZDQYYQZJXNXXAKHDDUJXQZFXQHCHONE"
    # URL untuk mendapatkan data pool stats
    pool_stats_url = "https://qubic.nevermine.io/poolStats"
    # URL untuk mendapatkan harga QUBIC (dalam USD)
    price_url = "https://api.coingecko.com/api/v3/simple/price?ids=qubic-network&vs_currencies=usd"

    # Mengambil data dari API shares
    response = requests.get(shares_url)
    shares_data = response.json()

    # Mengambil data dari API pool stats
    pool_response = requests.get(pool_stats_url)
    pool_data = pool_response.json()

    # Mengambil harga dari API CoinGecko
    price_response = requests.get(price_url)
    price_data = price_response.json()
    price = price_data["qubic-network"]["usd"]

    # Mengambil total shares dari semua worker
    total_shares = sum(worker['shares'] for worker in shares_data)

    # Mengambil poolShares dan poolSolution
    pool_shares = pool_data["poolShares"]
    pool_solution = pool_data["poolSolution"]

    # Menghitung EstIncome dengan rumus
    if pool_shares > 0:  # Pastikan poolShares tidak nol
        est_income = (total_shares / pool_shares) * pool_solution
    else:
        est_income = 0  # Jika poolShares nol, EstIncome set ke 0

    # Membatasi EstIncome hanya sampai 3 angka di belakang koma
    est_income = round(est_income, 3)
    
    # Menghitung total "Its" dari currentIts
    total_its = sum(worker['avgIts'] for worker in shares_data)

    # Menghitung EstQUS dan EstUSD
    qus_multiplier = 3773416
    est_qus = est_income * qus_multiplier
    est_usd = est_qus * price

    # Membatasi EstQUS dan EstUSD ke 3 angka di belakang koma
    est_qus = round(est_qus, 3)
    est_usd = round(est_usd, 3)

    # Menghitung jumlah device berdasarkan avgIts > 0
    total_devices = sum(1 for worker in shares_data if worker['avgIts'] > 0)

    # Membuat output dalam array (sesuai format yang diminta plugin)
    result = {
        "shares": [
            {
                "Its": total_its,
                "totalShare": total_shares,
                "EstIncome": est_income,
                "EstQUS": est_qus,
                "EstUSD": est_usd,
                "Device": total_devices
            }
        ]
    }

    # Mengembalikan hasil dalam format JSON
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
