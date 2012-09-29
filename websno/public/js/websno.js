var websno = {
  views: {},

  initialize: function(){
    websno.templateLoader.load(["Header","Home"],function() {
      websno.router = new websno.Router();
      Backbone.history.start();
    });
  }
}

$(function() {
  websno.initialize();
});
