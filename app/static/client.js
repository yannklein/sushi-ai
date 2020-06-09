const el = x => document.getElementById(x);

const sushis = [
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
];

const sushiUrl = (name) => {
  return sushis.filter(sushi => sushi.en === name)[0].url;
};

const showPicker = () => {
  el("file-input").click();
}

const showPicked = (event) => {
  el("upload-label").innerHTML = event.currentTarget.files[0].name;
  const reader = new FileReader();
  reader.onload = function(e) {
    el("image-picked").src = e.target.result;
    el("image-picked").className = "";
  };
  reader.readAsDataURL(event.currentTarget.files[0]);
}

const analyze = () => {
  const uploadFiles = el("file-input").files;
  if (uploadFiles.length !== 1) alert("Please select a file to analyze!");

  el("analyze-button").innerHTML = "Analyzing...";


  const formdata = new FormData();
  formdata.append("file", uploadFiles[0]);

  const requestOptions = {
    method: 'POST',
    body: formdata
  };
  const loc = window.location;
  fetch(`${loc.protocol}//${loc.hostname}:${loc.port}/analyze`, requestOptions)
    .then(response => response.json())
    .then(data => {
      window.mydata = data;
      el("result").innerHTML =
        `
          <h2>
            ${data.resultPct >= 60 ? `That's... a <a href="${sushiUrl(data.result)}">${data.result[0].toUpperCase()}${data.result.substring(1)}</a> sushi!` : `Not sure about that one... maybe a ${data.result} sushi?`}
          </h2>
          <p>Full result:</p>
          <ul>
          ${Object.keys(data.details)
            .filter(key => data.details[key] >= 5)
            .sort((keyA, keyB) => data.details[keyB] - data.details[keyA])
            .map(key =>
              `<li><a href="${sushiUrl(key)}">${key[0].toUpperCase()}${key.substring(1)}</a> sushi - ${data.details[key]}%</li>`)
            .join('')}
          </ul>
        `;
      el("analyze-button").innerHTML = "Analyze";
    })
    .catch(error => console.log('error',error));
}

document.querySelector('.choose-file-button').addEventListener('click', showPicker);
document.querySelector('.analyze-button').addEventListener('click', analyze);
document.querySelector('#file-input').addEventListener('change', showPicked);



