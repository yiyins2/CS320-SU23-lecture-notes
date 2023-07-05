import flask # requires installation if not already installed - pip3 install flask

app = flask.Flask("my application") # name of the web application can be anything

# @ operator is called a "decorator"
# SYNTAX: @app.route(URL)
@app.route("/")
def home():
    with open("index.html") as f:
        html = f.read()
        
    return html

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, threaded=False)

# app.run never returns, so don't define functions
# after this (the def lines will never be reached)
