function activer_onglet(){
  let three=document.getElementById("three");
  three.classList.add("activated");
}

function getfile(){
  input = document.getElementById("link");
  if (input!=null){
    var lien = input.href;
    sessionStorage.setItem("Path",lien);
    var url = "/proteomics/view3D/";
    var link = document.createElement('a');
    var node = document.createTextNode("GO to the analysis.");
    link.appendChild(node);
    link.setAttribute('href', url);
    var parent = document.getElementById('FILE');
    parent.appendChild(link);
  }
}

function showit(show,hide){
  show = document.getElementById(show);
  show.style = "display:block";
}

function add_interaction(){
  file = document.getElementById("button_file");
  pdb = document.getElementById("button_PDB");
  file.addEventListener("click",function(){
    showit("FILE","PDB_VIEW");
  });
  getfile();
}


function main(){
  activer_onglet();
  add_interaction();
}

window.onload=main;
