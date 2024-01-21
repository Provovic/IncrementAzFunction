import azure.functions as func
import logging

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.function_name(name="Get-ID")
@app.route(route="getID")
@app.cosmos_db_input(arg_name="retrieveData",
                     database_name="Visitor Counter DB ID",
                     collection_name="Visitor Counter Container",
                     container_name="Visitor Counter Container",
                     connection_string_setting="CosmosDbConnectionString",
                     connection="CosmosDbConnectionString")


def getID(req: func.HttpRequest, retrieveData: func.DocumentList) -> func.HttpResponse:
    logging.info('Starting the process of searching for an ID')


    # Define CORS headers
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, OPTIONS",
        "Access-Control-Allow-Headers": "Origin, Content-Type, Accept, Authorization, X-Request-With"
    }

    findingID = req.params.get('id')
    if not findingID:
        return func.HttpResponse("Please provide a 'ID' parameter in the request.", headers=headers, status_code=400)
    
    logging.info(f'Begin searching the database for {findingID}')
    checkingForName = [doc for doc in retrieveData if doc.get('id') == findingID]

    if checkingForName:
        # The user exists in the database
        return func.HttpResponse(f"{findingID['totalCount']}", headers=headers, status_code=200)
    else:
        # The user does not exist in the database
        return func.HttpResponse(f"{findingID} does not exist in the database", headers=headers, status_code=404)





"""
===============================================================================================================================
FUNCTION: Increment-Total-Count
DESCRIPTION: When the 'INCREMENT' id/user gets called it'll increment the totalAccount value that's associated to the account. 
                The totalAccount is going to be used as a visitor counter.
===============================================================================================================================
"""
@app.function_name(name="Increment-Total-Count")
@app.route(route="incrementTotalCount", methods=['GET', 'OPTIONS', 'POST'], auth_level=func.AuthLevel.ANONYMOUS)
@app.cosmos_db_input(arg_name="retrieveData",
                     database_name="Visitor Counter DB ID",
                     collection_name="Visitor Counter Container",
                     container_name="Visitor Counter Container",
                     connection_string_setting="CosmosDbConnectionString",
                     connection="CosmosDbConnectionString")
@app.cosmos_db_output(arg_name="outputDocument", 
                      database_name="Visitor Counter DB ID", 
                      collection_name="Visitor Counter Container", 
                      container_name="Visitor Counter Container", 
                      connection_string_setting="CosmosDbConnectionString",
                      connection="CosmosDbConnectionString")
def incrementTotal(req: func.HttpRequest, retrieveData: func.DocumentList, outputDocument: func.Out[func.Document]):
    
    
    # Define CORS headers7
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Origin, Content-Type, Accept, Authorization, X-Request-With"
    }
    
    id_to_search = req.params.get('id')

    if not id_to_search:
        return func.HttpResponse("Please provide an 'id' parameter in the request.", headers=headers, status_code=400)

    updated_doc = None
    for doc in retrieveData:
        if doc.get('id') == id_to_search:
            if id_to_search == "INCREMENT":
                increment_total_count(doc)
                updated_doc = doc

    if updated_doc:
        outputDocument.set(updated_doc)
        return func.HttpResponse(f" {updated_doc['totalCount']}", headers=headers)

    return func.HttpResponse(f"{id_to_search} does not exist in the database", headers=headers)

def increment_total_count(doc):
    if doc.get('totalCount') is not None:
        doc['totalCount'] += 1
