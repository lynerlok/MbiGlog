// visu  1D proteine
// Francois Calaji
// Moco Vincent

function defAaColor(aa) {
  var value = [[204, 0, 0],[204, 102, 0],
  [204, 204, 0],[102, 204, 0],[0, 204, 0],
  [0, 204, 102],[ 0, 204, 204],[0, 102, 204],
  [0, 0, 204],[102, 0, 204],[204, 0, 204],
  [204, 0, 102],[96, 96, 96],[205, 0, 0],
  [205, 128, 0],[255, 255, 0],[128, 255, 0],
  [0, 255, 0],[0, 255, 128],[0, 255, 255]];
  var aa_color = {};
  for (i = 0; i < aa.length; i++) {
	aa_color[aa[i]] = value[i];
  }
  return aa_color;
}

function charToAa(char_, colors){
  let name = char_.toUpperCase();
  return {"name": name, "color":colors[name]}
}

function aaPercent(prot) {
	var aa = "GPAVLIMCFYWHKRQNEDST";
	var aa_percent = {};
	for (var i = 0; i < aa.length; i++) {
		aa_percent[aa[i]] = 0;
	}
	for (var i = 0; i < prot.length; i++) {
		aa_percent[prot[i]]++;
	}
	var highValue = ["key", 0];
	for (var name in aa_percent) {
		if (aa_percent[name] > highValue[1]) {
			highValue = [name, aa_percent[name]];
		}
	}
	return highValue;
}

function drawAa(x,y,diameter,aa){
  black = 0;white = 255;
  strokeWeight(diameter/30);stroke(black);// contour
  fill(aa.color);ellipse(x,y,diameter);
  fill(white);text(aa.name,x,y);
}
function translate_(x,y,distance,theta){
  x += Math.abs(distance*cos(theta));
  y += distance*sin(theta);
  return [x,y]
}

function drawBound(x,y,boundLength,theta){

  let point_ = translate_(x,y,boundLength,theta);
  let x2 = point_[0]; let y2 = point_[1];
  point_ = translate_(x,y,boundLength*2,theta-Math.PI/2)
  let ctrlX1 = point_[0]; let ctrlY1 = point_[1];
  point_ = translate_(ctrlX1,ctrlY1,boundLength,theta);
  let ctrlX2 = point_[0]; let ctrlY2 = point_[1];
  curve(ctrlX1,ctrlY1,x,y,x2,y2,ctrlX2,ctrlY2);
  return [x2,y2]
}


function parseFasta(text) {
	var fastaDict = {}
	text = text.split('\n');
	var key = "";
	for (var i = 0; i < text.length; i++) {
		if (text[i].search('>') !== -1) {
			key = text[i].replace('>', '');
		} else if (text[i].search('>') === -1 && text[i-1].search('>') !== -1) {
			var seq = "";
			var itr = i;
			while (text[itr].search('>') === -1 && text[itr] != "") {
				seq += text[itr];
				itr++;
			}
			fastaDict[key] = seq;
		}
	}
	return fastaDict;
}

function get_path(){
  let path = sessionStorage.getItem("Path");
  if (path!="null"){
    fetch(path).then(x=>x.text()).then(response=>{
      fasta = parseFasta(response);
			addProteinDisplay(fasta);
    });
    sessionStorage.setItem("Path",null);
    let a = document.getElementById("link");
    a.href=path;
    prepare_2D();
  }
}

function getfile(){
  input = document.getElementById("link");
  if (input!=null){
    var lien = input.href;
    sessionStorage.setItem("Path",lien);
    get_path();
  }
}

function prepare_2D(){
  let want = document.getElementById("want");
  want.addEventListener("click",function(){
    console.log("coucou");
    this.style["display"]="none";
    getfile();
    let div = document.getElementById("principal");
    div.style["display"]="none";
    let wish = document.getElementById("wish");
    wish.style["display"]="block";
  });
}

// function getContents(ev) {
//   console.log(sessionStorage.getItem("Path"));
// 	if (window.File && window.FileReader && window.FileList && window.Blob) {
//     let f = ev.target.files[0];
// 		let reader = new FileReader();
// 		reader.onload = (e) => {
// 			let text = reader.result;
// 			fasta = parseFasta(text);
// 			addProteinDisplay(fasta);
// 		};
// 		reader.readAsText(f);
// 	} else {
// 		alert('The File APIs are not fully supported by your browser.');
// 	};
//   console.log(sessionStorage.getItem("Path"));
//   sessionStorage.setItem("Path",null);
//   prepare_2D();
// }

function createElementHtml(href, name, seq, x0, y0, diameter, boundLength, colors) {
	var body = document.getElementsByClassName("vertical-menu");
  var div = document.createElement("div");
  var newA = document.createElement("a");
	newA.href = href;
	newA.textContent = name;
  div.id=name;
  div.classList.add("element");
	newA.classList.add("vert-menu");
	newA.onclick = function () {
    var res = document.getElementById(this.textContent);
    res.classList.add("active");
    this.classList.add("active");
    setup(seq, x0, y0, diameter, boundLength, colors)};
	div.appendChild(newA);
	var newP =  document.createElement("p");
	var highValue = aaPercent(seq);
	newP.classList.add("pourcentage");
	newP.textContent = "Acide aminé le plus présent dans la chaîne: "+highValue[0] + " " + highValue[1]  + "%";
	div.appendChild(newP);
  body[0].appendChild(div);
}

function drawSeq(seq,x0,y0,diameter,boundLength,colors,period){
  let theta = Math.PI/2;
  let radius = diameter/2;
  let point_, x1, y1, x2, y2;
  for (let atom_index = 0; atom_index<seq.length; atom_index++){
    drawAa(x0,y0,diameter,charToAa(seq[atom_index],colors));
    if (atom_index+1 < seq.length){
      point_ = translate_(x0,y0,radius,theta);
      x1 = point_[0]; y1 = point_[1];
      point_ = drawBound(x1,y1,boundLength,theta);
      x2 = point_[0]; y2 = point_[1];
      point_ = translate_(x2,y2,radius,theta);
      x0 = point_[0]; y0 = point_[1];
      theta -= 1/period*Math.PI*2;
    }
  }
}

function setup(seq, x0, y0, diameter, boundLength, colors) {
  let div_cvn = document.getElementById("canvas");
	if (seq != undefined) {
		var cnv  = createCanvas(div_cvn.offsetWidth, div_cvn.offsetHeight);
		cnv.position(0, 0);
		drawSeq(seq, x0, height/2, diameter, boundLength, colors, 7);
	}
  let canvas=document.getElementById("defaultCanvas0");
  let div = document.getElementById("canvas");
  canvas.style["position"]="inherit";
  canvas.style["text-align"]="center";
  canvas.style["margin"]="auto";
  canvas.classList.add("canvas");
  div.appendChild(canvas);
}

function addProteinDisplay(fasta) {
	let aa = "GPAVLIMCFYWHKRQNEDST";
	let colors = defAaColor(aa);
	let aaDiameter = 30;
	let boundLength = 10;
	let x0 = 100;
	let y0 = 100; // centre du premier aa
	for (var key in fasta) {
		createElementHtml("#", key, fasta[key], x0, y0, aaDiameter, boundLength, colors) ;
	}
}



////////////////////////////////////////////////////////////////////
//Add Event Listener
