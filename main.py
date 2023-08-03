import firebase_admin
from controller.RNC import consulta_rnc
from firebase_admin import credentials, firestore
from flask import Flask, request, jsonify
import os
import json

# Inicializar Firebase
cred = credentials.Certificate('controller/appbioscam-firebase-adminsdk-cqiv8-4b79627210.json')
firebase_admin.initialize_app(cred)

# Obtener una referencia a la base de datos Firestore
db = firestore.client()

# Función para consultar la base de datos y obtener los campos del documento
def obtener_datos_documento(resultado):
    try:
        # Realizar una consulta para obtener el documento con el campo que contiene el ID conocido
        consulta = db.collection('animales').where('id_especie', '==', resultado).limit(1).get()

        # Verificar si se encontró un documento que cumpla con la consulta
        if not consulta:
            return None

        # Obtener el ID del documento
        document_id = consulta[0].id

        # Obtener los datos del documento como un diccionario
        document_data = consulta[0].to_dict()

        return document_data
    except Exception as e:
        print('Error al consultar la base de datos:', str(e))
        return None

app = Flask(__name__)

@app.route('/api/consulta_rnc', methods=['POST'])
def api_consulta_rnc():
    try:
        # Verifica que se reciba una imagen en el body de la petición
        if 'imagen' not in request.files:
            return jsonify({'error': 'No se proporcionó ninguna imagen.'}), 400

        imagen = request.files['imagen']

        # Guarda la imagen temporalmente
        imagen_path = 'temp_image.jpg'
        imagen.save(imagen_path)

        # Realiza la predicción de la red neuronal convolucional
        resultado = consulta_rnc(imagen_path)

        # Elimina la imagen temporal
        os.remove(imagen_path)

        # Consultar la base de datos para obtener los campos del documento
        document_data = obtener_datos_documento(resultado)

        # Preparar el resultado a devolver como JSON
        if document_data:
            # Convertir los datos del documento a formato JSON
            resultado_json = json.dumps(document_data)
            return resultado_json, 200
        else:
            return jsonify({'error': f"El documento con ID '{resultado}' no existe."}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
if __name__ == '__main__':
    # Establecer la variable de entorno FLASK_ENV en "production"
    os.environ['FLASK_ENV'] = 'production'# Iniciar la aplicación con Gunicorn
    host = '0.0.0.0'
    port = int(os.environ.get('PORT', 8000))
    workers = 4  # Puedes ajustar este valor según tus necesidades
    app.run(host=host, port=port, threaded=True)