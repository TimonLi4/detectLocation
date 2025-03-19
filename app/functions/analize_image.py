import easyocr
import os
import cv2
from ultralytics import YOLO
import shutil
# from g4f.client import Client
import ollama
from math import cos,acos,sin


base_path = os.getcwd()
model_path = os.path.join(base_path,'detectLocation','app','bestv1.pt')
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



def subImageInFile(image_path):
    # Загружаем изображение
    image = cv2.imread(image_path)
    height, width, _ = image.shape

    # Предсказания модели
    result = model.predict(source=image, conf=0.8, save=False, show=False)
    detections = result[0].boxes.xyxy
    labels = result[0].boxes.cls
    probabilities = result[0].boxes.conf
    class_names = model.names

    # Создаем новую папку для результатов
    reset_class_folders(class_names, RESULT_FOLDER)

    # JSON-структура для сохранения результатов
    json_data = {}

    # Счетчики для каждой категории (используем defaultdict для избежания KeyError)
    from collections import defaultdict
    class_counters = defaultdict(int)  # По умолчанию 0 для любого ключа

    for i, box in enumerate(detections):
        x1, y1, x2, y2 = map(int, box)

        # Убедимся, что координаты находятся в пределах изображения
        x1, y1, x2, y2 = max(0, x1), max(0, y1), min(width, x2), min(height, y2)

        if x2 > x1 and y2 > y1:
            # Обрезаем изображение
            cropped = image[y1:y2, x1:x2]

            # Класс объекта
            class_id = int(labels[i])
            try:
                class_name = class_names[class_id]
            except IndexError:
                print(f"Warning: class_id {class_id} out of range for class_names {class_names}")
                continue  # Пропускаем некорректный class_id

            probability = round(float(probabilities[i]) * 100, 2)  # Преобразуем вероятность в %

            # Увеличиваем счетчик для данной категории
            class_counters[class_name] += 1
            object_index = class_counters[class_name]

            # Директория для сохранения
            class_dir = os.path.join(RESULT_FOLDER, class_name)
            os.makedirs(class_dir, exist_ok=True)  # Создаем папку, если её нет

            # Путь к файлу с уникальным именем для каждой категории
            file_name = f"{class_name}_{object_index}.jpg"
            file_path = os.path.join(class_dir, file_name)

            # Сохраняем обрезанное изображение
            cv2.imwrite(file_path, cropped)

            # Добавляем информацию об объекте в JSON-структуру
            if class_name not in json_data:
                json_data[class_name] = {}

            json_data[class_name][object_index] = {
                "probability": str(probability),
                "text": read_image(file_path)
            }

    return json_data


# def request(content):
#     client = Client()
#     response = client.chat.completions.create(
#         model="gpt-3.5-turbo",
#         messages=[{"role": "user", "content": content}]
#     )
#     return response.choices[0].message.content


def request(content):
    response = ollama.chat(model="mistral", messages=[{"role": "user", "content": f"{content}"}])
    return response["message"]["content"]


def answer(data_json):
    quation = ''
    content = ''
    content_pointer=''

    if 'building' in data_json:
        content = ', '.join(
        ', '.join(item['text']) if item['text'] else ''
        for item in data_json['building'].values()
        )

    if 'pointer' in data_json:
        content_pointer = ', '.join(
        ', '.join(item['text']) if item['text'] else ''
        for item in data_json['pointer'].values()
        )

    # quation = f'Определи страну, и желательно город, если на фассадах здания написано: {content}, а на дорожных указателях {content_pointer}',
    # quation = f'напиши только широту и долготу этого места, если на фассадах здания написано: {content}, а на дорожных указателях {content_pointer}'
    quation = f'Напиши долготу и широту этого места в формате "Долгота: [значение]; Широта: [значение]" на первой строке, а на следующей строке добавь комментарии, если на фасадах здания написано: {content}, а на дорожных указателях: {content_pointer}'

    ANSWER = request(quation)

    return ANSWER


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


def PATH(fi1,L1,fi2,L2):
    return 111.2*acos(sin(fi1)*sin(fi2)+cos(fi1)*cos(fi2)*cos(L2-L1))


