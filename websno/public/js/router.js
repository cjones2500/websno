websno.Router = Backbone.Router.extend({
  routes: {
    "cmos": "cmos",
    "*path": "home"
  },

  initialize: function() {
    this.headerView = new websno.views.Header();
    $('.header').html(this.headerView.render().el);
  },

  home: function() {
    this.showView(websno.views.Home);
  },

  cmos: function() {
    this.showView(websno.views.Cmos);
  },

  showView: function(view,args) {
    if (this.currentView){
      this.currentView.close();
    }
    this.currentView = new view(args);
    $('#content').html(this.currentView.render().el);
  }
});
