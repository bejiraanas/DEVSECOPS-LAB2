from flask import Flask, request, jsonify
# SECURITY ISSUE FOR TESTING - hardcoded password
#database_password = "mysecretpassword123"
app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "message2": "DevSecOps Lab API - CI/CD Pipeline", 
        "status": "success",
        "version": "1.0",
        "features": ["add", "subtract", "multiply", "divide"]
    })
  
@app.route('/add', methods=['POST'])
def add():
    data = request.get_json()
    result = data['a'] + data['b']
    return jsonify({"operation": "add", "result": result})

@app.route('/subtract', methods=['POST'])
def subtract():
    data = request.get_json()
    result = data['a'] - data['b']
    return jsonify({"operation": "subtract", "result": result})

@app.route('/multiply', methods=['POST'])
def multiply():
    data = request.get_json()
    result = data['a'] * data['b']
    return jsonify({"operation": "multiply", "result": result})

@app.route('/divide', methods=['POST'])
def divide():
    data = request.get_json()
    if data['b'] == 0:
        return jsonify({"error": "Division by zero is not allowed"}), 400
    result = data['a'] / data['b']
    return jsonify({"operation": "divide", "result": result})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)