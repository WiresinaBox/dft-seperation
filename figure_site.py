import flask
import flask_classful as flaskc
import nwchem_parse as nwparse
import matplotlib.pyplot as plt
import plotutil as pltu
import mpld3
from mpld3 import plugins, utils
import json
app = flask.Flask(__name__)


class siteData:
    """
    General idea is to initially pass all of the necessary parsers, references, and additonal matplotlib figures to this class
    Then this object does the dirty work of rendering it all. Should it get a request from the website for more information,
    it can draw on the stuff inputed here.
    """
    HTML = ''
    parser_dict = dict() #Keyword so we can grab them later from a dropdown or something.
    figure_dict = dict()
    route ='' 
    debug =''
    def __init__(self,  route='/', debug=True):
        self.route = route
        self.debug = debug
    def add_figure(self, key, fig): 
        figHTML = mpld3.fig_to_html(fig, template_type='simple')
        self.figure_dict[str(key)] = {'fig':fig, 'html':figHTML}
    def add_parser(self, key, parser):
        print('adding parser')
        self.parser_dict[str(key)] = parser 
        print(self.parser_dict)
    def setup_HTML(self):
        self.HTML += '<html>\n<body>'
        for key, data in self.figure_dict.items():
            self.HTML+=data['html']

        self.HTML += '</body>\n</html>'

class sitePage(flaskc.FlaskView, siteData): 
    #Every method in this class but NOT in the base classes will be turned into a route.
    route_base='/'
    def index(self):
        return flask.render_template('layout.html')
        #return "hi!" 

    def put(self):
        print(self.parser_dict)
        return json.dumps(list(self.parser_dict.keys()))
    
    def patch(self, dat):
        print(dat, type(dat))
        #return json.dumps(mpld3.fig_to_dict(self.figure_dict[dat]['fig']))
        return self.figure_dict[dat]['html']

#Note, if you're getting an error 405, it's probably because there's a required areguement it's not putting in.

def run(pageClass, **kwargs):
    app.run(**kwargs)

#Do all the registrations here.
sitePage.register(app)

if __name__ == "__main__":
    app.run(debug=True) 

