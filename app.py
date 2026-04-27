from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder='.')
CORS(app)

@app.route('/')
def home():
    return send_from_directory('.', 'index1.html')

@app.route('/simulate', methods=['POST'])
def simulate():
    data = request.json
    processes = data['processes']

    processes.sort(key=lambda x: x['arrival'])
    time = 0
    result = []

    for p in processes:
        if time < p['arrival']:
            time = p['arrival']
        start = time
        end = start + p['burst']

        result.append({
            'pid': p['pid'],
            'start': start,
            'end': end,
            'waiting': start - p['arrival'],
            'turnaround': end - p['arrival']
        })

        time = end

    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
