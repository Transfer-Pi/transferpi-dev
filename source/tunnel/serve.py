from source import App
from source.utils import HTTP

app = App()
http = HTTP()

@app.route("/")
def index(request):
    return http.text_response('Hello, World !')

@app.route("/app")
def app_serve(request):
    return http.json_response({
        'name':"Test",
        'email':"vptl185@gmail.com"
    })

@app.route("/test/<string:var>")
def test(request,var):
    return http.text_response(var)


app.serve()
