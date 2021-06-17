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

import nest_asyncio
nest_asyncio.apply()
print('nest async up!')

# Base example model
# export_file_url = 'https://www.dropbox.com/s/6bgq8t6yextloqp/export.pkl?raw=1'
# export_file_name = 'export.pkl'

# https://www.dropbox.com/s/oeha2t6ip0w2thl/super-multi-sushi.pth?dl=0
# https://www.dropbox.com/s/k9wqc1p5lkgrav8/clean-super-multi-sushi.pth?dl=0

# Custom model
model_name = "clean-super-multi-sushi"
export_file_url = f'https://www.dropbox.com/s/k9wqc1p5lkgrav8/{model_name}.pth?raw=1'
model_file_name = 'model'
export_file_name = f'models/{model_file_name}.pth'

path = Path(__file__).parent

# Base example classes
# classes = ['black', 'grizzly', 'teddys']

# Custom classes
# classes = ['salmon','tuna','saba','aji','anago','unagi','tamago','ikura','ebi','tai']
classes = [
  {'jp': 'サーモン', 'en': 'salmon', 'url': "http://www.sushiencyclopedia.com/sushi-fish/salmon.html"},
  {'jp': 'マグロ', 'en': 'tuna', 'url': "http://www.sushiencyclopedia.com/sushi-fish/tuna.html"},
  {'jp': 'さば', 'en': 'mackerel', 'url': "http://www.sushiencyclopedia.com/sushi-fish/mackerel.html"},
  {'jp': 'アジ', 'en': 'spanish mackerel', 'url': "http://www.sushiencyclopedia.com/sushi-fish/spanish_mackerel.html"},
  {'jp': 'アナゴ', 'en': 'sea eel', 'url': "http://www.sushiencyclopedia.com/sushi-fish/sea-eel.html"},
  {'jp': 'ウナギ', 'en': 'eel', 'url': "http://www.sushiencyclopedia.com/sushi-fish/eel.html"},
  {'jp': '卵', 'en': 'egg', 'url': "http://www.sushiencyclopedia.com/sushi-menu/egg_sushi.html"},
  {'jp': 'いくら', 'en': 'salmon roe', 'url': "http://www.sushiencyclopedia.com/sushi-menu/salmon_roe_sushi.html"},
  {'jp': 'えび', 'en': 'shrimp', 'url': "http://www.sushiencyclopedia.com/sushi-menu/shrimp_sushi.html"},
  {'jp': '鯛', 'en': 'sea bream', 'url': "http://www.sushiencyclopedia.com/sushi-fish/red_snapper.html"},
  {'jp': 'つぶ貝', 'en': 'whelk', 'url': "https://en.wikipedia.org/wiki/Whelk"},
  {'jp': 'ブリ', 'en': 'yellowtail fish', 'url': "http://www.sushiencyclopedia.com/sushi-fish/yellowtail-amberjack.html"},
  {'jp': 'ホッキ貝', 'en': 'surf clam', 'url': "https://www.sushifaq.com/sushi-sashimi-info/sushi-item-profiles/akagai-surf-clam/"},
  {'jp': '縁側', 'en': 'halibut fin', 'url': "http://www.sushiencyclopedia.com/sushi-fish/halibut.html"},
  {'jp': 'たこ', 'en': 'octopus', 'url': "http://www.sushiencyclopedia.com/sushi-other-seafood/octopus.html"},
  {'jp': 'イカ', 'en': 'squid', 'url': "http://www.sushiencyclopedia.com/sushi-menu/squid-sushi.html"},
  {'jp': 'カンパチ', 'en': 'amberjack', 'url': "http://www.sushiencyclopedia.com/sushi-fish/amberjack.html"},
  {'jp': 'イワシ', 'en': 'sardine', 'url': "http://www.sushiencyclopedia.com/sushi-fish/sardine.html"},
  {'jp': 'ウニ', 'en': 'sea urchin', 'url': "https://www.sushifaq.com/sushi-sashimi-info/sushi-item-profiles/sushi-items-uni-sea-urchin/"},
  {'jp': 'ホタテ', 'en': 'scallop', 'url': "https://www.justonecookbook.com/scallop-sushi/"},
  {'jp': '赤貝', 'en': 'ark clam', 'url': "http://www.sushiencyclopedia.com/sushi-shellfish/ark-shell-clam.html"},
  {'jp': 'かに', 'en': 'crab', 'url': "https://www.sushifaq.com/sushi-sashimi-info/sushi-item-profiles/kanikama-or-surimi/"},
  {'jp': 'カツオ', 'en': 'bonito', 'url': "http://www.sushiencyclopedia.com/sushi-fish/bonito.html"},
  {'jp': '小肌', 'en': 'shad', 'url': "http://www.sushiencyclopedia.com/sushi-menu/gizzard_shad_sushi.html"},
  {'jp': '大トロ', 'en': 'fatty tuna', 'url': "http://www.sushiencyclopedia.com/sushi-menu/toro-tuna-belly-sushi.html"}
]
classes = map(lambda classe: classe['en'], classes)
classes = sorted(classes)
print(classes)

# if os.path.isfile(export_file_name):
#   os.remove(export_file_name)
#   print("Old model removed!")

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
        data_bunch = ImageDataBunch.single_from_classes(
          path, 
          classes, 
          ds_tfms=get_transforms(), 
          size=224
          ).normalize(imagenet_stats)
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
    uvicorn.run(app=app, host='0.0.0.0', port=5000, log_level="info")
