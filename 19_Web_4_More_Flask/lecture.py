import flask # requires installation if not already installed - pip3 install flask
import time
import json

app = flask.Flask("my application") # name of the web application can be anything

major_counts = {}
last_visit = 0 # TODO: dict of visit times, for each IP

# TODO: create a survey page
# query string format: route?key1=value1&key2=value2
# flask.request.args: enables us to get the arguments from query string
@app.route("/survey")
def survey():
    major = flask.request.args.get("major", "unkown")
    if not major in major_counts:
        major_counts[major] = 0
    major_counts[major] += 1
    
    return "MAJORS: \n" + json.dumps(major_counts)

# TODO: create an add page
@app.route("/add")
def adder():
    args = dict(flask.request.args)
    try:
        x = float(args["x"])
        y = float(args["y"])
    except KeyError:
        return "Please specify x and y."
    return f"{x} + {y} = {x+y}"

# TODO: create a never page
@app.route("/never")
def never():
    return "humans only, no bots allowed!"

# TODO: create a robots.txt page
# flask.Response: enables us to create a response object instance
# 		  Arguments: str representing reponse, headers dict representing metadata
@app.route("/robots.txt")
def bot_rules():
    return flask.Response("""\
    User-Agent: *
    Disallow: /never
    """, headers={"Content-Type": "text/plain"})

# RATE LIMITING 
# TODO: create a slow page
# GOAL: don't let people visit this more often than once per 3s
# flask.request.remote_addr: enables us to take action based on the IP address from
#                            which we receive the request
@app.route("/slow")
def slow():
    global last_visit
    print("VISITOR", flask.request.remote_addr)
    if time.time() - last_visit > 3:
        last_visit = time.time()
        return "welcome!"
    else:
        return flask.Response("<b>go away</b>",
                              status=429,
                              headers={"Retry-After": "3"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, threaded=False)

# app.run never returns, so don't define functions
# after this (the def lines will never be reached)
