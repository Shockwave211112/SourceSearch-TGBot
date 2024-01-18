import bot_logic
from decouple import config
from flask import Flask, jsonify

app = Flask('')
          
@app.route('/')
def home():
  if bot_logic.bot_check():
    return jsonify(message="Всё окей.")
  else:
    return jsonify(message="Ошибка.")

if __name__ == "__main__":
    while True:
        try:
            app.run(host='0.0.0.0', port=80)
        except Exception as e:
            print(f"Error: {e}")
