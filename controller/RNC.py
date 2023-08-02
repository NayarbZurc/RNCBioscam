import tensorflow as tf
from tensorflow.keras.preprocessing import image
from PIL import Image
import os

# Función para cargar y preprocesar imágenes
def carga_preprocesa(image_path):
    img = Image.open(image_path).convert("L")  # Convierte a escala de grises
    img = img.resize((100, 100))  # Reduce la calidad de la imagen a 100x100
    img_array = tf.keras.preprocessing.image.img_to_array(img)
    img_array = img_array / 255.0  # Normaliza los valores de píxeles en el rango [0, 1]
    return img_array

# Ruta del archivo con las rutas de las imágenes y etiquetas
ruta = 'controller/imagenesrnc/Rutas.txt'
imagenes = []
etiquetas = []
with open(ruta, 'r') as archivo_txt:
    for linea in archivo_txt:
        ruta_imagen, etiqueta = linea.strip().split()
        imagenes.append(ruta_imagen)
        etiquetas.append(etiqueta)

# Obtener el número de clases (especies animales)
etiquetas_unicas = list(set(etiquetas))
num_classes = len(etiquetas_unicas)
# Verificar que las rutas de las imágenes sean correctas y existan los archivos
# (esto es importante para asegurarse de que no haya errores durante la predicción)
for ruta_imagen in imagenes:
    if not os.path.isfile(ruta_imagen):
        raise FileNotFoundError(f"No se pudo encontrar la imagen: {ruta_imagen}")
print(f"Se encontraron {len(imagenes)} imágenes y {num_classes} clases en el archivo de texto.")

# Cargar el modelo entrenado
if os.path.exists("controller/modelo.h5"):
    model = tf.keras.models.load_model("controller/modelo.h5")
    print("Modelo cargado exitosamente.")
else:
    raise FileNotFoundError("No se pudo encontrar el archivo del modelo entrenado 'modelo.h5'.")

def consulta_rnc(imagen_path):
    img = image.load_img(imagen_path, target_size=(100, 100))
    try:
        # Cargar la imagen seleccionada
        img = Image.open(imagen_path).convert("L")  # Convertir a escala de grises
        img = img.resize((100, 100))  # Reducir la calidad de la imagen a 100x100
        img_array = tf.keras.preprocessing.image.img_to_array(img)
        img_array = img_array / 255.0  # Normalizar los valores de píxeles en el rango [0, 1]

        # Expandir las dimensiones de la imagen para que coincida con el formato de entrada del modelo
        img_array = tf.expand_dims(img_array, axis=0)

        # Realizar la predicción con el modelo entrenado
        prediction = model.predict(img_array)

        # Obtener la clase predicha con mayor probabilidad
        predicted_class_index = tf.argmax(prediction, axis=1)[0].numpy()

        # Obtener el nombre de la clase predicha basándose en las etiquetas únicas
        predicted_class = etiquetas_unicas[predicted_class_index]

        # Retornar el resultado de la predicción
        return predicted_class

    except Exception as e:
        print('Error al procesar la imagen:', str(e))
