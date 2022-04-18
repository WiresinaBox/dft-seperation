from flask import Flask, request, Blueprint
from flask_restx import Resource, Api
import json
#blueprints are bundles of routes
blueprint = Blueprint("api", __name__, url_prefix='/api')

api = Api(
        blueprint,
        version='0.01',
        title='NWchem Parser API',
        description='',
        base_url='/api/'
        
        ) #Register an api interface to it

ns = api.namespace("items", description='operations')
api.add_namespace(ns)

#websites pass info through side-URLs or routes
#each API should be listening to a specific endpoint (the end of a route)

#Data to pass in.
parserDict = {}
plotFuncDict = {} #'plot name':function handle

#Each of these defines the endpoints to listen to
@api.route('/filename') 
class structAPI(Resource):
    #Each HTML signal gets its own thing here
    #Anything (like Curl) that pings 'url/data' will get this back.
    def get(self):
        """Return a json of names already in database ready to go"""
        print('getting something!')
        return json.dumps(list(parserDict.keys()))

    #the second variable is the name of the route. e.g. "url/hello", then filename='hello'
    def put(self):
        fn = request.get_data().decode() #Bytes to string
        #print(parserDict)
        returnData = parserDict[fn] #Change this later to whatever we need
        return json.dumps(returnData)

@api.route('/plots') 
class plotAPI(Resource):
    #Each HTML signal gets its own thing here
    #Anything (like Curl) that pings 'url/data' will get this back.
    #def get(self):
    #    """Return a json of names already in database ready to go"""
    #    print('getting something!')
    #    return json.dumps(list(parserDict.keys()))

    #the second variable is the name of the route. e.g. "url/hello", then filename='hello'
    def get(self):
        return list(plotFuncDict.keys())


    def post(self):
        req = json.loads(request.get_data().decode()) #Bytes to string
        plotTypeList = req['plotType'] #A list of plot types
        complexList = req['complexList'] #A list of complexes to plot
        speciesStr = req['orbitalSpecies'] #A string of species to filter the orbitals by, sperated by commas
        viewSize = req['viewSize'] #A string of species to filter the orbitals by, sperated by commas
        orbitalSpecies = [val.strip().capitalize() for val in speciesStr.split(',')] 
        if not isinstance(plotTypeList, list):
            plotTypeList = [plotTypeList]

        dataDict = {}
        
        if 'all' in plotTypeList:
            plotTypeList = list(plotFuncDict.keys())     
        for plotType in plotTypeList:
            if plotType in plotFuncDict:
                data = plotFuncDict[plotType](complexList, orbitalSpecies=orbitalSpecies, viewSize = viewSize)
                dataDict[plotType] = data

        
        return dataDict
