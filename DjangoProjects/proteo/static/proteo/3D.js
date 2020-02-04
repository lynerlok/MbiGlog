
function getfile(){
  input = document.getElementById("thefile");
  var files = input.files;
  if (files.length!=0){
    var data_path = files[0].name;
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
  upload = document.getElementById("upload");
  upload.addEventListener("click",getfile);
}


function main(){
  add_interaction();
}

window.onload=main;
