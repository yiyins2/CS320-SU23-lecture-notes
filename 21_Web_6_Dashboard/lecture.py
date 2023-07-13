import flask
import matplotlib.pyplot as plt
import io # input / output
import pandas as pd

# Notes for matplotlib.pyplot module
"""
fig, ax = plt.subplots(figsize=(3, 2)) enables us to create multiple subplots within one plot
    the default is one subplot if we didn't specify the number of subplots
    fig refers to the entire plot
    ax refers to all the axes for subplots
fig.savefig(<file object>, format=<fig format>) enables us to save the figure into a file - default format is png
plt.close() closes most recent fig
plt.tight_layout() enables us to avoid cropping of the image
"""

# Notes for io module
"""
io.BytesIO for fake binary file
io.StringIO for fake text file
<fileobject>.getvalue() returns the content of the fake file
"""

# Notes for flask
"""
flask.request: incoming user's request data
attributes of flask.request: 
    flask.request.args: parsed query string
    flask.request.remote_addr: user's IP address
    
@app.route("<URL>", methods=["POST"]) enables us to process HTTP POST requests
flask.request.get_data() enables us to access data (byte format) sent via HTTP POST request
"""

# Overview of flask
"""
user/browser - flask.request -> server
    GET req:
        request.args (query string)
        request.remote_addr (IP addresses)
    POST req:
        curl commands (send data)
        flask.request.get_data()
        
server - flask.Response -> user/browser
    Response(
        content of the page, 
        status: 429,
        headers (metadata): {
            Content-Type: default is text/html, others could be text/plain, image/png, image/svg+xml
            Retry-After (429)
        }
    )
"""

temps = [80, 85, 83, 90]

app = flask.Flask("my dashboard")

# DYNAMIC
@app.route("/")
def home():
    return """
    <html>
    <body bgcolor="Salmon">
    
    <h3>Example 1: PNG</h3>
    <img src="plot1.png">
    
    <h3>Example 2: SVG</h3>
    <img src="plot2.svg">
    
    </body>
    </html>
    """ 

# TODO: add route to plot1.png 
"""
IMPORTANT: file name and extension should match as in html content
Steps:
     1. generate a plot
     2. return the image contents:
         2a. v1: write and read from a temporary file
         2b. v2: use a fake file (io module)
     3. fix the content type: default content type is text/html: Content-Type: text/html
         3a. How can we find various content types? Google for "MIME types".
     4. IMPORTANT: close the figure. If this is not done, after 20 refreshes, you will start getting the below warning:
More than 20 figures have been opened. Figures created through the pyplot interface (`matplotlib.pyplot.figure`) are retained until explicitly closed and may consume too much memory. (To control this warning, see the rcParam `figure.max_open_warning`).
     5. try to set y_label for the plot. This will not show up. 
     6. create a line plot with temps Series

"""
@app.route("/plot1.png")
def plot1():
    fig, ax = plt.subplots(figsize=(3, 2))
    #pd.Series(temps).plot.line(ax=ax)
    
    #CDF code
    s = pd.Series(sorted(temps))
    rev = pd.Series((s.index+1)/len(s)*100, index=s.values)
    rev.plot.line(ax=ax, ylim=0, drawstyle="steps-post")
    
    ax.set_xlabel("Temperatures")
    ax.set_ylabel("Distribution")
    plt.tight_layout()
    
    # v1 - write and read a temporary plot file (cumbersome)
    # with open("temporary.png", "wb") as f:
    #     fig.savefig(f)
    # with open("temporary.png", "rb") as f:
    #     return f.read()
    
    # v2 - write and read from a fake file
    f = io.BytesIO() 
    fig.savefig(f)
    plt.close()
    
    return flask.Response(f.getvalue(), headers={"Content-type": "image/png"})

# TODO: add route to plot2.svg
"""
IMPORTANT: file name and extension should match as in html content
Things to change from plot1 function:
     1. Change content type
     2. Change format for savefig
     3. SVG files have text type (unlike PNG) - so we should use io.StringIO

"""
@app.route("/plot2.svg")
def plot2():    
    fig, ax = plt.subplots(figsize=(3, 2))
    #pd.Series(temps).plot.line(ax=ax)
    pd.Series(temps).plot.hist(ax=ax, bins=100)
    
    ax.set_ylabel("Temperatures")
    plt.tight_layout()
    
    f = io.StringIO() 
    fig.savefig(f, format="svg")
    plt.close()
    
    return flask.Response(f.getvalue(), headers={"Content-type": "image/svg+xml"})

# TODO: add route for "/upload"
"""
Steps:
     1. support query string:
         - with key/parameter as temps and value as "," separated temperature values
         - add the values into temps list
     2. return len(temps)
     
Disadvantages of query string approach:
     1. If we have a lot of data, it is difficult to type. What if we are trying to upload a video?
     2. Caching:
         - memory of what we have already seen before; instead of slow web request, show what was already sent previously for the same request
         - browser cache
         - cache devices that sit in front of the server
         - server caching
         
Use POST request instead:
     1. Update route to add "methods=["POST"]"
     2. Humans don't send POST requests, instead we need to use "curl -X POST <URL> -d <data>" --- curl is a simple command line tool that enables us to send HTTP requests
     3. Use flask.request.get_data() - make sure to convert type to str
"""
@app.route("/upload", methods=["POST"])
def upload():
    # v1 - query string
    # new_temps = flask.request.args["temps"]
    # new_temps = new_temps.split(",")
    # for val in new_temps:
    #     temps.append(float(val))
    
    # v2 - POST request
    new_temps = str(flask.request.get_data(), encoding="utf-8")
    new_temps = new_temps.split(",")
    for val in new_temps:
        temps.append(float(val))
        
    return f"thanks, you now have {len(temps)} records"

# TODO: change SVG to histogram - very sensitive to number of "bins"
# TODO: change PNG to CDF (Cumulative Distribution Function):
"""
Idea: sort the data to observe some distribution, then switch x and y axes
Steps:
     1. sort the data
     2. switch x and y axes
     3. normalize the y axis from 0 to 100 - make sure to set ylim to 0
     4. change line plot "drawstyle" to "steps-post" - avoid extrapolating information between points

    s = pd.Series(sorted(temps))
    rev = pd.Series((s.index+1)/len(s)*100, index=s.values)
    rev.plot.line(ax=ax, ylim=0, drawstyle="steps-post")
"""

if __name__ == "__main__":
    # threaded must be False whenever we use matplotlib
    app.run(host="0.0.0.0", debug=True, threaded=False)

# app.run never returns, so don't define functions
# after this (the def lines will never be reached)
