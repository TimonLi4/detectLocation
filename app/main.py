from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import os

import uvicorn

from functions.analize_image import UPLOAD_FOLDER,RESULT_FOLDER
from functions.analize_image import subImageInFile,process_image,answer,PATH



app = FastAPI()
templates = Jinja2Templates(directory='app/templates')
app.mount('/static',StaticFiles(directory='app/static'),name='static')


@app.get("/")
async def get_form(request:Request,response_class=HTMLResponse):
    return templates.TemplateResponse(request=request,name='index.html')
    

@app.get('/test/')
async def test(request:Request,response_class = HTMLResponse):
    return templates.TemplateResponse(request=request,name='photos.html')




@app.post('/upload/')
async def upload_image(file: UploadFile = File(...)):
    # Сохраняем файл в папку uploaded_images
    file_location = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(file_location, "wb") as buffer:
        buffer.write(await file.read())

    # Перенаправляем на результат обработки
    return RedirectResponse(f'/images/{file.filename}', status_code=303)



def create_url_path(result_image_path):
    # Преобразуем файловый путь в URL
        relative_path = os.path.relpath(result_image_path, "app/static")  # Убираем "static/"
        url_path = f"/static/{relative_path.replace(os.sep, '/')}"  # Формируем URL-путь
        return url_path


def get_all_images(path,folder):
    image = []
    for filename in os.listdir(f'{path}/{folder}'):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            image.append(filename)
    return image

@app.get("/images/{image_name}")
async def get_image(image_name: str, request: Request):
    image_path = os.path.join(UPLOAD_FOLDER, image_name)
    print('image_path: ', image_path)

    if os.path.exists(image_path):
        # Обрабатываем изображение
        result_image_path, class_name = process_image(image_path)  # Файловый путь
        print('result: ', class_name)

        url_path_for_main_image = create_url_path(result_image_path)
        json_data = subImageInFile(image_path)

        print(json_data)
        print(image_name)
        
        answer_ = answer(json_data)
        # print(answer_)
        lines = answer_.split('\n')  # Разделяем на строки
        coords = lines[0].split(';')  # Разделяем координаты
        longitude = coords[0].replace("Долгота: ", "").strip()  # "21.0122" L1
        latitude = coords[1].replace("Широта: ", "").strip() # fi1

        print(longitude,latitude)


        # print(PATH(L1=longitude,fi1=latitude))

        pointerPath = RESULT_FOLDER
        pointer_url = get_all_images(pointerPath, 'pointer')
        

        buildingPath = RESULT_FOLDER
        building_url = get_all_images(buildingPath, 'building')

        

        return templates.TemplateResponse('photos.html', context={
            'request': request,
            'image_url': url_path_for_main_image,
            'pointer_url':pointer_url,  # Используем URL
            'building_url':building_url,
            'json_data':json_data,
            'answer': answer_,
            
        })



if __name__ == '__main__':
    uvicorn.run('main:app', reload=True)


