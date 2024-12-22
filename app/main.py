from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import os

import uvicorn

from functions.analize_image import UPLOAD_FOLDER,RESULT_FOLDER
from functions.analize_image import subImageInFile,process_image



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

        pointerPath = RESULT_FOLDER
        pointer_url = get_all_images(pointerPath,class_name[1])
        

        buildingPath = RESULT_FOLDER
        building_url = get_all_images(buildingPath,class_name[0])


        return templates.TemplateResponse('photos.html', context={
            'request': request,
            'image_url': url_path_for_main_image,
            'pointer_url':pointer_url,  # Используем URL
            'building_url':building_url,
            'json_data':json_data,
            
        })



# @app.get("/images/{image_name}")
# async def get_image(image_name: str,request:Request,response_class = HTMLResponse):
#     image_path = os.path.join(UPLOAD_FOLDER, image_name)
#     print('image_path:  ',image_path)
    

#     if os.path.exists(image_path):
#         # result_image_path = subImageInFile(image_path)
#         result_image_path = process_image(image_path)
#         print('result: ', result_image_path)

#     return templates.TemplateResponse('photos.html',context={
#                                               'request':request,
#                                               'image_url':f'{result_image_path}',
                                            
#                                             })


# @app.get(/)
# async def display_images(request:Request):




if __name__ == '__main__':
    uvicorn.run('main:app', reload=True)


# @app.get("/images/{image_name}")
# async def get_image(image_name: str,request:Request,response_class = HTMLResponse):
#     # Получаем путь к исходному изображению
#     image_path = os.path.join(UPLOAD_FOLDER, image_name)
    
#     # Если изображение существует, обработаем его и отдадим результат
#     if os.path.exists(image_path):
#         result_image_path = subImageInFile(image_path)
#         result_image_path = process_image(image_path)

#         pointer_list = os.listdir(r'C:\Users\Timon\Desktop\MyCourse\api\app\result_class\pointer')
#         building_list = os.listdir(r'C:\Users\Timon\Desktop\MyCourse\api\app\result_class\building')

        

#         return templates.TemplateResponse('photos.html',context={
#                                               'request':request,
#                                               'images':{                                 
#                                             'pointer':pointer_list, 
#                                             'building':building_list,
#                                                         },
#                                                 'path': r'C:\Users\Timon\Desktop\MyCourse\api\app\result_class'
                                            
#                                             })
    
    
#     return {"message": "Image not found"}