import math
import re
from flask import Flask, render_template_string, request

# 1. BI-ENTROPY CORE
def shannon_entropy(bitstring):
    if not bitstring: return 0
    p1 = bitstring.count('1') / len(bitstring)
    p0 = 1 - p1
    if p1 == 0 or p0 == 0: return 0
    return -(p1 * math.log2(p1) + p0 * math.log2(p0))

def binary_derivative(s):
    return "".join('1' if s[i] != s[i+1] else '0' for i in range(len(s)-1))

def calculate_bientropy(numerical_stream):
    bit_str = "".join(bin(abs(int(n)))[2:] for n in numerical_stream)
    n = len(bit_str)
    if n < 2: return 0
    total_entropy, weight_sum, current_deriv = 0, 0, bit_str
    for k in range(min(n - 1, 32)): 
        weight = 2**k
        total_entropy += shannon_entropy(current_deriv) * weight
        weight_sum += weight
        current_deriv = binary_derivative(current_deriv)
        if len(current_deriv) < 2: break
    return total_entropy / weight_sum if weight_sum > 0 else 0

# 2. HAILSTONE ENGINE
def collatz_process(n, depth):
    for _ in range(depth):
        if n <= 1: break
        n = n // 2 if n % 2 == 0 else (3 * n + 1)
    return n

def encrypt(msg, key):
    key = re.sub(r'[^A-Z]', '', key.upper()) or "KEY"
    output, k_len, k_pos = [], len(key), 0
    for char in msg.upper():
        code = ord(char)
        if code < 65 or code > 90:
            output.append(-code)
            continue
        l_pos = code - 64
        k_val = ord(key[k_pos % k_len])
        math_res = collatz_process(l_pos + 101, k_val - 64)
        output.append((math_res * 1000) + (l_pos + k_val))
        k_pos += 1
    b_score = calculate_bientropy(output)
    output.append(999999)
    output.extend([ord(k) for k in key])
    return ",".join(map(str, output)), b_score

def decrypt(cipher_str):
    try:
        data = [int(x.strip()) for x in cipher_str.split(',') if x.strip()]
        if 999999 not in data:
            return "ERROR: Key Fence (999999) missing.", "N/A"
        fence_idx = data.index(999999)
        cipher_values = data[:fence_idx]
        key = "".join(chr(k) for k in data[fence_idx + 1:])
        decoded, k_pos = [], 0
        for val in cipher_values:
            if val <= 0:
                decoded.append(chr(abs(val)))
                continue
            k_val = ord(key[k_pos % len(key)])
            l_pos = (val % 1000) - k_val
            decoded.append(chr(l_pos + 64) if 1 <= l_pos <= 26 else "?")
            k_pos += 1
        return "".join(decoded), key
    except:
        return "ERROR: Invalid ciphertext format.", "N/A"

# 3. WEB INTERFACE
app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hailstone v4.1 | UI Update</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        :root { --rattlesden-red: #a52a2a; }
        body { background-color: #f4f1ea; padding-bottom: 50px; }
        .navbar { background-color: var(--rattlesden-red) !important; box-shadow: 0 2px 4px rgba(0,0,0,0.2); }
        .card { border: none; border-radius: 15px; box-shadow: 0 6px 12px rgba(0,0,0,0.08); }
        .btn-rattlesden { background-color: var(--rattlesden-red); color: white; border: none; }
        .btn-rattlesden:hover { background-color: #8b0000; color: white; }
        .result-area { background-color: #ffffff; border: 1px solid #ced4da; border-radius: 8px; font-family: 'Courier New', monospace; font-size: 0.95rem; min-height: 80px; padding: 15px; overflow-y: auto; }
    </style>
</head>
<body>
    <nav class="navbar navbar-dark mb-4">
        <div class="container">
            <span class="navbar-brand fw-bold">🧊 HAILSTONE SYSTEM v4.1</span>
            <span class="text-white-50 small">Recursive Chaos Engine</span>
        </div>
    </nav>

    <div class="container">
        <div class="row justify-content-center">
            <div class="col-lg-8">
                <div class="card p-4 mb-4">
                    <form method="POST">
                        <div class="row g-3 mb-3">
                            <div class="col-md-6">
                                <label class="form-label fw-bold">Secret Key</label>
                                <input type="text" name="key" class="form-control" placeholder="e.g. RATTLESDEN">
                            </div>
                            <div class="col-md-6 d-flex align-items-end">
                                <div class="d-grid w-100">
                                    <button name="action" value="enc" class="btn btn-rattlesden">ENCRYPT</button>
                                </div>
                            </div>
                        </div>
                        <div class="mb-3">
                            <label class="form-label fw-bold">Message / Ciphertext</label>
                            <textarea name="text" class="form-control" rows="4" placeholder="Input text here..." required></textarea>
                        </div>
                        <div class="d-grid">
                            <button name="action" value="dec" class="btn btn-outline-secondary">DECRYPT (Auto-extract Key)</button>
                        </div>
                    </form>

                    {% if b_score is not none %}
                    <div class="mt-4 border-top pt-3">
                        <div class="d-flex justify-content-between small fw-bold mb-1">
                            <span>BiEntropy Security: {{ "%.4f"|format(b_score) }}</span>
                            <span class="{{ 'text-success' if b_score > 0.8 else 'text-danger' }}">
                                {{ 'HIGH CHAOS' if b_score > 0.8 else 'LOW CHAOS' }}
                            </span>
                        </div>
                        <div class="progress" style="height: 8px;">
                            <div class="progress-bar {{ 'bg-success' if b_score > 0.8 else 'bg-warning' if b_score > 0.5 else 'bg-danger' }}" style="width: {{ b_score * 100 }}%"></div>
                        </div>
                    </div>
                    {% endif %}
                </div>

                {% if result %}
                <div class="card p-4">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <label class="form-label fw-bold mb-0">Engine Output</label>
                        <button class="btn btn-sm btn-dark" onclick="copyResult()">Copy Result</button>
                    </div>
                    <div id="resultContent" class="result-area shadow-sm">
                        {{ result }}
                    </div>
                </div>
                {% endif %}
            </div>
        </div>
    </div>

    <script>
        function copyResult() {
            const text = document.getElementById('resultContent').innerText;
            navigator.clipboard.writeText(text).then(() => {
                const btn = event.target;
                const originalText = btn.innerText;
                btn.innerText = 'Copied!';
                btn.classList.replace('btn-dark', 'btn-success');
                setTimeout(() => {
                    btn.innerText = originalText;
                    btn.classList.replace('btn-success', 'btn-dark');
                }, 2000);
            });
        }
    </script>
</body>
</html>
'''

@app.route("/", methods=["GET", "POST"])
def index():
    res, b_score = None, None
    if request.method == "POST":
        k, t, act = request.form.get("key"), request.form.get("text"), request.form.get("action")
        if act == "enc" and t:
            if not k: res = "Error: Key required for encryption."
            else: res, b_score = encrypt(t, k)
        elif act == "dec" and t:
            msg, key_found = decrypt(t)
            res = f"MESSAGE: {msg} | KEY: {key_found}"
    return render_template_string(HTML_TEMPLATE, result=res, b_score=b_score)

if __name__ == "__main__":
    app.run(port=8080)