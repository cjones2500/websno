websno.views.HomePage = Backbone.View.extend({
  initialize: function() {
    console.log("home view");
  },
  
  render: function() {
    $(this.el).html(this.template());
    return this;
  }
});


websno.views.Header = Backbone.View.extend({
  render: function() {
    $(this.el).html(this.template());
    return this;
  }
});



