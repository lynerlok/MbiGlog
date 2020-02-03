/*
Boudin Marina

Projet Glog - groupe proteomics

*/
// Activation des onglets
function activer_onglet(){
  let three=document.getElementById("three");
  three.classList.add("activated");
}

function lunch_visualisation(){
  var stage;
  visu = new NGL.Stage("visualisation");
  visu.viewer.container.addEventListener("dblclick", function () {
      visu.toggleFullscreen();
  });
  var load = NGL.getQuery("load");
  if (load) visu.loadFile(load, {defaultRepresentation: true});
  document.getElementById("pdbidInput").addEventListener("keydown", function (e) {
    if (e.keyCode === 13) {
      visu.removeAllComponents();
      var url = "rcsb://" + e.target.value + ".mmtf";
      visu.loadFile(url, {defaultRepresentation: true});
      e.target.value = "";
      e.target.blur();
    }
  });
}

function main(){
  activer_onglet();
  lunch_visualisation();
}

window.onload=main;
