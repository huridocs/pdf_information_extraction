import pymongo
from fastapi import FastAPI, HTTPException, UploadFile, File
import sys

from data.LabeledData import LabeledData
from data.PredictionData import PredictionData
from get_graylog import get_graylog
from segment_predictor.XmlFile import XmlFile

graylog = get_graylog()

app = FastAPI()

graylog.info(f'PDF information extraction service has started')


def sanitize_tenant(tenant: str):
    tenant = tenant.replace(' ', '_')
    tenant = ''.join(x for x in tenant if x.isalnum() or x == '_')
    return tenant


@app.get('/info')
async def info():
    graylog.info('PDF information extraction endpoint')
    return sys.version


@app.get('/error')
async def error():
    graylog.error("This is a test error from the error endpoint")
    raise HTTPException(status_code=500, detail='This is a test error from the error endpoint')


@app.post('/labeled_data')
async def labeled_data_post(labeled_data: LabeledData):
    client = pymongo.MongoClient('mongodb://mongo:27017')
    pdf_information_extraction_db = client['pdf_information_extraction']
    labeled_data.tenant = sanitize_tenant(labeled_data.tenant)
    pdf_information_extraction_db.labeleddata.insert_one(labeled_data.dict())
    return 'labeled data saved'


@app.post('/prediction_data')
async def prediction_data_post(prediction_data: PredictionData):
    client = pymongo.MongoClient('mongodb://mongo:27017')
    pdf_information_extraction_db = client['pdf_information_extraction']
    prediction_data.tenant = sanitize_tenant(prediction_data.tenant)
    pdf_information_extraction_db.predictiondata.insert_one(prediction_data.dict())
    return 'labeled data saved'


@app.post('/xml_file/{tenant}')
async def xml_file(tenant, file: UploadFile = File(...)):
    filename = '"No file name! Probably an error about the file in the request"'
    try:
        filename = file.filename
        XmlFile(file_name=filename, tenant=sanitize_tenant(tenant)).save(file=file.file.read())
        return 'task registered'
    except Exception:
        graylog.error(f'Error adding task {filename}', exc_info=1)
        raise HTTPException(status_code=422, detail=f'Error adding task {filename}')
