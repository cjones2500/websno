var websno = {
  views: {},
  models: {},
  collections: {},

  initialize: function(){
    websno.templateLoader.load(["Header","Home","Cmos"],function() {
      websno.router = new websno.Router();
      Backbone.history.start();
    });
  }
}

$(function() {
  websno.initialize();
});
