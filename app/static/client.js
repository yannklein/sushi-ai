const el = x => document.getElementById(x);

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
            ${data.resultPct >= 60 ? `That's... a ${data.result} sushi!` : `Not sure about that one... maybe a ${data.result} sushi?`}
          </h2>
          <p>Full result:</p>
          <ul>
          ${Object.keys(data.details)
            .filter(key => data.details[key] >= 5)
            .sort((keyA, keyB) => data.details[keyB] - data.details[keyA])
            .map(key =>
              `<li>${key[0].toUpperCase()}${key.substring(1)} sushi - ${data.details[key]}%</li>`)
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



