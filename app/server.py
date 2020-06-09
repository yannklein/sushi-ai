import aiohttp
import asyncio
import uvicorn
from fastai import *
from fastai.vision import *
from io import BytesIO
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse, JSONResponse
from starlette.staticfiles import StaticFiles

# Base example model
# export_file_url = 'https://www.dropbox.com/s/6bgq8t6yextloqp/export.pkl?raw=1'
# export_file_name = 'export.pkl'

# https://www.dropbox.com/s/oeha2t6ip0w2thl/super-multi-sushi.pth?dl=0

# Custom model
model_name = "super-multi-sushi"
export_file_url = f'https://www.dropbox.com/s/oeha2t6ip0w2thl/{model_name}.pth?raw=1'
model_file_name = 'model'
export_file_name = f'models/{model_file_name}.pth'

path = Path(__file__).parent

# Base example classes
# classes = ['black', 'grizzly', 'teddys']

# Custom classes
# classes = ['salmon','tuna','saba','aji','anago','unagi','tamago','ikura','ebi','tai']
classes = [
  {'jp': 'サーモン', 'en': 'salmon'},
  {'jp': 'マグロ', 'en': 'tuna'},
  {'jp': 'さば', 'en': 'mackerel'},
  {'jp': 'アジ', 'en': 'spanish mackerel'},
  {'jp': 'アナゴ', 'en': 'sea eel'},
  {'jp': 'ウナギ', 'en': 'eel'},
  {'jp': '卵', 'en': 'egg'},
  {'jp': 'いくら', 'en': 'salmon roe'},
  {'jp': 'えび', 'en': 'shrimp'},
  {'jp': '鯛', 'en': 'sea bream'},
  {'jp': 'つぶ貝', 'en': 'whelk'},
  {'jp': 'ブリ', 'en': 'yellowtail fish'},
  {'jp': 'ホッキ貝', 'en': 'surf clam'},
  {'jp': '縁側', 'en': 'halibut fin'},
  {'jp': 'たこ', 'en': 'octopus'},
  {'jp': 'イカ', 'en': 'squid'},
  {'jp': 'カンパチ', 'en': 'amberjack'},
  {'jp': 'イワシ', 'en': 'sardine'},
  {'jp': 'ウニ', 'en': 'sea urchin'},
  {'jp': 'ホタテ', 'en': 'scallop'},
  {'jp': '赤貝', 'en': 'ark clam'},
  {'jp': 'かに', 'en': 'crab'},
  {'jp': 'カツオ', 'en': 'bonito'},
  {'jp': '小肌', 'en': 'shad'},
  {'jp': '大トロ', 'en': 'fatty tuna'}
]
classes = map(lambda classe: classe['en'], classes)
classes = sorted(classes)
print(classes)

if os.path.isfile(export_file_name):
  os.remove(export_file_name)
  print("Old model removed!")

app = Starlette()
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_headers=['X-Requested-With', 'Content-Type'])
app.mount('/static', StaticFiles(directory='app/static'))


async def download_file(url, dest):
    if dest.exists(): return
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.read()
            with open(dest, 'wb') as f:
                f.write(data)


async def setup_learner():
    await download_file(export_file_url, path / export_file_name)
    try:
        # Base code to use .pkl
        # learn = load_learner(path, export_file_name)

        # Custom code for .pth
        data_bunch = ImageDataBunch.single_from_classes(path, classes,
        ds_tfms=get_transforms(), size=224).normalize(imagenet_stats)
        learn = cnn_learner(data_bunch, models.resnet34, pretrained=False)
        learn.load(model_file_name)

        return learn
    except RuntimeError as e:
        if len(e.args) > 0 and 'CPU-only machine' in e.args[0]:
            print(e)
            message = "\n\nThis model was trained with an old version of fastai and will not work in a CPU environment.\n\nPlease update the fastai library in your training environment and export your model again.\n\nSee instructions for 'Returning to work' at https://course.fast.ai."
            raise RuntimeError(message)
        else:
            raise


loop = asyncio.get_event_loop()
tasks = [asyncio.ensure_future(setup_learner())]
learn = loop.run_until_complete(asyncio.gather(*tasks))[0]
loop.close()


@app.route('/')
async def homepage(request):
    html_file = path / 'view' / 'index.html'
    return HTMLResponse(html_file.open().read())


@app.route('/analyze', methods=['POST'])
async def analyze(request):
    img_data = await request.form()
    img_bytes = await (img_data['file'].read())
    img = open_image(BytesIO(img_bytes))
    prediction = learn.predict(img)
    print('prediction:', round(prediction[2][prediction[1].item()].item() * 100))
    details = {}
    for index, each_class in enumerate(classes):
      details[each_class] = round(prediction[2][index].item() * 100)

    return JSONResponse(
      {
        'result': str(prediction[0]),
        'resultPct': round(prediction[2][prediction[1].item()].item() * 100),
        'details': details
      }
    )


if __name__ == '__main__':
    if 'serve' in sys.argv:
        uvicorn.run(app=app, host='0.0.0.0', port=5000, log_level="info")
