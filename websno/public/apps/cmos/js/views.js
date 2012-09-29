websno.views.Screamers = Backbone.View.extend({
  initialize: function() {
    this.model = new websno.collections.CrateList();
  },
  render: function() {
    $(this.el).html(this.template());
    return this;
  }
});

websno.views.Cmos = Backbone.View.extend({
  initialize: function(options) {
    this.model = new websno.collections.CrateList();
    this.focus = options.id;
  },
  render: function() {
    $(this.el).html(this.template());
    return this;
  }
});
