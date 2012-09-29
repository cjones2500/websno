websno.Router = Backbone.Router.extend({
  routes: {
    "cmos/:id": "cmos",
    "cmos": "screamers",
    "*path": "home"
  },

  initialize: function() {
    this.headerView = new websno.views.Header();
    $('.header').html(this.headerView.render().el);
  },

  home: function() {
    this.showView(websno.views.HomePage);
  },

  cmos: function(id) {
    this.showView(websno.views.CmosPage,id);
  },

  screamers: function() {
    this.showView(websno.views.ScreamersPage);
  },

  showView: function(view,args) {
    if (this.currentView){
      this.currentView.close();
    }
    this.currentView = new view(args);
    $('#content').html(this.currentView.render().el);
    if (this.currentView.onshow){
      this.currentView.onshow();
    }
  }
});
