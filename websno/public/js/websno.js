var websno = {
  views: {},
  models: {},
  collections: {},
  events: {},

  initialize: function(){
    websno.templateLoader.load(["Header","HomePage","CmosPage","ScreamersPage","Screamer","SmallScreamer","SmallScreamerList","CmosRateList","TimePlot"],function() {
      websno.router = new websno.Router();
      _.extend(websno.events,Backbone.Events);
      Backbone.history.start();
      setInterval(function() {
        websno.events.trigger("increment");
      },100);
    });
  }
}

$(function() {
  websno.initialize();
});
