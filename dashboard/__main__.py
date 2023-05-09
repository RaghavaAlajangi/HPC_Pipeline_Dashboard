from .app import app

if __name__ == "__main__":
    app.run_server(host="0.0.0.0", debug=False, port=8050)
    # app.run_server(debug=True, port=2000)
