
NGL.cssDirectory = "css/"
NGL.documentationUrl = "../build/docs/"
NGL.examplesListUrl = "../build/scriptsList.json"
NGL.examplesScriptUrl = "../scripts/"

    // Datasources
NGL.DatasourceRegistry.add("data", new NGL.StaticDatasource("../data/"))
var mdsrv = NGL.getQuery("mdsrv")
if (mdsrv) {
  var mdsrvDatasource = new NGL.MdsrvDatasource(mdsrv)
  NGL.DatasourceRegistry.add("file", mdsrvDatasource)
  NGL.setListingDatasource(mdsrvDatasource)
  NGL.setTrajectoryDatasource(mdsrvDatasource)
}

var stage;
document.addEventListener("DOMContentLoaded", function () {
  stage = new NGL.Stage();
  NGL.StageWidget(stage);
  var load = NGL.getQuery("load");
  if (load) stage.loadFile(load, {defaultRepresentation: true});
  var script = NGL.getQuery("script");
  if (script) stage.loadScript("./scripts/" + script + ".js");
  var struc = NGL.getQuery("struc");
  var traj = NGL.getQuery("traj");
  if (struc) {
    stage.loadFile(struc, {
      defaultRepresentation: true;
    }).then(function(o) {
      if (traj) o.addTrajectory(traj);
    })
  }
})
