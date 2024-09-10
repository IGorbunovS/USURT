from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/receive_request', methods=['POST'])
def receive_request():
    data = request.json
    query = data.get("query")
    ip_address = data.get("ip_address")

    # Здесь можно обработать данные, например, сохранить в файл
    with open("requests.log", "a") as log_file:
        log_file.write(f"Запрос: {query}, IP: {ip_address}\n")

    return jsonify({"status": "success"}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
