import pandas as pd
import re
import sqlite3

from flask import Flask, jsonify
from flask import request
from flasgger import Swagger, LazyString, LazyJSONEncoder
from flasgger import swag_from

class CustomFlaskAppWithEncoder(Flask):
    json_provider_class = LazyJSONEncoder

app = CustomFlaskAppWithEncoder(__name__)

swagger_template = dict(
    info = {
        'title' : LazyString(lambda: "API For Cleansing Data, By Alfa"),
        'version' : LazyString(lambda: "1.0.0"),
        'description' : LazyString(lambda: "API untuk Cleansing Data, Oleh Alfa"),
    },
    host = LazyString(lambda: request.host)
)

swagger_config = {
    "headers" : [],
    "specs" : [
        {
            "endpoint": "docs",
            "route" : "/docs.json",
        }
    ],
    "static_url_path": "/flasgger_static",
    # "static_folder": "static",  # must be set by user
    "swagger_ui": True,
    "specs_route": "/alfa/"
}
swagger = Swagger(app, template=swagger_template, config = swagger_config)

#TEXT PROCESSING ------------------------------------------------------------------------------
@swag_from("docs/text_processing.yml", methods = ['POST'])
@app.route('/text-processing', methods=['POST'])
def text_processing():

    text = request.form.get('text')
    text_clean = re.sub(r'[^a-zA-Z0-9]', ' ', text)

#CONNECT TO SQLITE3 DATABASE--------------------------------------------------------------------
    conn = sqlite3.connect('data/binar_academy_data_science.db')
    print("Opened Database Succesfully")

    conn.execute('''CREATE TABLE IF NOT EXISTS users (raw_text varchar(255), result_text varchar(255));''')

    conn.execute(f"INSERT INTO users (raw_text, result_text) VALUES (?, ?)", (text, text_clean))

    conn.commit()
    print("Records Has Been Created")
    conn.close()

    json_response = {
        'status_code': 200,
        'description': "Teks yang sudah diproses",
        'data_raw':text, 
        'data_clean': text_clean
    }
    response_data = jsonify(json_response)
    return response_data

#TEXT PROCESSING FILE------------------------------------------------------------------------------
@swag_from("docs/text_processing_file.yml", methods = ['POST'])
@app.route('/text-processing-file', methods=['POST'])
def text_processing_file():

    
    file = request.files.getlist('file')[0]
    df = pd.read_csv(file, encoding="ISO-8859-1") 
    texts = df.Tweet.to_list()
    cleaned_text = []
    for text in texts:
        cleaned_text.append(re.sub(r'[^a-zA-Z0-9]', '', text))

#CONNECT TO SQLITE3 DATABASE--------------------------------------------------------------------
    conn = sqlite3.connect('data/binar_academy_data_science.db')
    print("Opened Database Successfully")

    conn.execute('''CREATE TABLE IF NOT EXISTS users (raw_text varchar(255), result_text varchar(255));''')

    
    for text, clean_text in zip(texts, cleaned_text):
        conn.execute("INSERT INTO users (raw_text, result_text) VALUES (?, ?)", (text, clean_text))

    conn.commit()
    print("Records Has Been Created")
    conn.close()

    json_response = {
        'status_code' : 200,
        'description' : "Teks yang telah diproses",
        'data' : cleaned_text,
    }

    response_data = jsonify(json_response)
    return response_data

if __name__ == '__main__':
    app.run()  

