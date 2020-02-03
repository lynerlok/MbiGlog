
function showit(show,hide){
  show = document.getElementById(show);
  show.style = "display:block";
}

function add_interaction(){
  file = document.getElementById("button_file");
  pdb = document.getElementById("button_PDB");
  console.log(file);
  file.addEventListener("click",function(){
    console.log("coucou");
    showit("FILE","PDB_VIEW");
  });
}


function main(){
  add_interaction();
}

window.onload=main;
