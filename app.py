from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    """Renders default text"""
    return "What is Love!"


if __name__ == '__main__':
    app.run(debug=True, port=5555)
