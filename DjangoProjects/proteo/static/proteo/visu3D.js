/*
Boudin Marina

Projet Glog - groupe proteomics

*/
// Activation des onglets
function activer_onglet(){
  let three=document.getElementById("three");
  three.classList.add("activated");
}

function defaultStructureRepresentation( component ){
    // bail out if the component does not contain a structure
    if( component.type !== "structure" ) return;
    // add three representations
    component.addRepresentation( "cartoon", {
        aspectRatio: 3.0,
        scale: 1.5
    } );
    component.addRepresentation( "licorice", {
        sele: "hetero and not ( water or ion )",
        multipleBond: true
    } );
    component.addRepresentation( "spacefill", {
        sele: "water or ion",
        scale: 0.5
    } );
}

function lunch_visualisation(path){
  var stage;
  visu = new NGL.Stage("visualisation");
  visu.viewer.container.addEventListener("dblclick", function () {
      visu.toggleFullscreen();
  });
  visu.removeAllComponents();
  if (path=="null"){
    document.getElementById("pdbidInput").addEventListener("keydown", function(e){
      if (e.keyCode === 13){
        var path = "rcsb://"+e.target.value+".mmtf";
        e.target.value="";
        e.target.blur();
        visu.loadFile(path, {defaultRepresentation: true});
      }
    })
  }
  else{
    visu.loadFile(path, {defaultRepresentation: true});
  }
}

function main(){
  activer_onglet();
  let path = sessionStorage.getItem("Path");
  lunch_visualisation(path);
  sessionStorage.setItem("Path",null);
}

window.onload=main;
