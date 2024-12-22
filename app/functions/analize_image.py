import easyocr
import os
import cv2
from ultralytics import YOLO
import shutil

base_path = os.getcwd()
model_path = os.path.join(base_path,'app','bestv1.pt')
reader = easyocr.Reader(['en','de','pl'], gpu=False)


model = YOLO(model_path)  # Загрузите свою модель

UPLOAD_FOLDER = r"app\static\images\uploaded_images"
# RESULT_FOLDER = 'result_images'
RESULT_FOLDER = r'app\static\images\result_class'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)


def reset_class_folders(class_names, result_folder):
    for class_id in class_names:
        class_name = str(class_names[class_id])  # Преобразуем class_name в строку
        class_dir = os.path.join(result_folder, class_name)
        
        # Удаляем старую папку, если она существует
        if os.path.exists(class_dir):
            import shutil
            shutil.rmtree(class_dir)
        
        # Создаем новую папку для текущего класса
        os.makedirs(class_dir, exist_ok=True)


def process_image(image_path):
    # Прогоняем изображение через модель
    result = model(image_path)  # Возвращает список объектов с результатами

    # result[0].plot() рисует изображение с размеченными объектами
    result_image_path = os.path.join(RESULT_FOLDER, os.path.basename(image_path))
    
    # Сохраняем результат
    result[0].save(result_image_path)
    class_name = model.names  # Сохраняем обработанное изображение

    return result_image_path, class_name



import cv2
import os
import json as json_module  # Избегаем конфликта с именем переменной json
from pathlib import Path



def subImageInFile(image_path):
    # Загружаем изображение
    image = cv2.imread(image_path)
    height, width, _ = image.shape

    # Предсказания модели
    result = model.predict(source=image, conf=0.5, save=False, show=False)
    detections = result[0].boxes.xyxy
    labels = result[0].boxes.cls
    probabilities = result[0].boxes.conf
    class_names = model.names

    # Создаем новую папку для результатов
    reset_class_folders(class_names, RESULT_FOLDER)

    # JSON-структура для сохранения результатов
    json_data = {}

    for i, box in enumerate(detections):
        x1, y1, x2, y2 = map(int, box)

        # Убедимся, что координаты находятся в пределах изображения
        x1, y1, x2, y2 = max(0, x1), max(0, y1), min(width, x2), min(height, y2)

        if x2 > x1 and y2 > y1:
            # Обрезаем изображение
            cropped = image[y1:y2, x1:x2]

            # Класс объекта
            class_id = int(labels[i])
            class_name = class_names[class_id]
            probability = round(float(probabilities[i]) * 100, 2)  # Преобразуем вероятность в %

            # Директория для сохранения
            class_dir = os.path.join(RESULT_FOLDER, class_name)
            os.makedirs(class_dir, exist_ok=True)  # Создаем папку, если её нет

            # Путь к файлу
            file_name = f"object_{i+1}.jpg"
            file_path = os.path.join(class_dir, file_name)

            # Сохраняем обрезанное изображение
            cv2.imwrite(file_path, cropped)

            # Добавляем информацию об объекте в JSON-структуру
            if class_name not in json_data:
                json_data[class_name] = {}

            json_data[class_name][i] = {
                
                "probability": str(probability),
                'read': read_image(file_path)
            }

    return json_data


def read_image(file_path):
    img = cv2.imread(file_path)
    text_data = []
    text_ = reader.readtext(img)

    threshold = 0.5
    # draw bbox and text
    count = 0
    for t_, t in enumerate(text_):
        bbox, text, score = t
        if score > threshold:
            text_data.append(text) #для списка []
            #text_data

    return text_data


# def subImageInFile(image_path):
#     image = cv2.imread(image_path)
#     json = {}
#     height, width, _ = image.shape

#     result = model.predict(source=image, conf=0.5, save=False, show=False)

#     detections = result[0].boxes.xyxy
#     labels = result[0].boxes.cls
#     class_names = model.names

#     reset_class_folders(class_names,RESULT_FOLDER)  # Создаем новую папку


#     for i, box in enumerate(detections):
#         x1, y1, x2, y2 = map(int, box)

#         # Ensure the bounding box is within image bounds
#         x1, y1, x2, y2 = max(0, x1), max(0, y1), min(width, x2), min(height, y2)

#         if x2 > x1 and y2 > y1:
#             cropped = image[y1:y2, x1:x2]  # Crop the image

#             class_id = int(labels[i])
#             class_name = class_names[class_id]

#             # Create the directory for the class if it doesn't exist
#             class_dir = os.path.join(RESULT_FOLDER, class_name)
            

#             # Сохраняем изображение в новую папку
#             file_path = os.path.join(class_dir, f"object_{i+1}.jpg")
#             cv2.imwrite(file_path, cropped)


#             # print(f"Saved cropped image to: {file_path}")


