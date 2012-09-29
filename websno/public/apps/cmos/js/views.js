websno.views.Screamer = Backbone.View.extend({
  initialize: function() {
    _.bindAll(this,'render');
    this.model.on('change',this.render);
  },

  render: function() {
    $(this.el).html(this.template(this.model.toJSON()));
    return this;
  }
});

websno.views.ScreamersPage = Backbone.View.extend({
  initialize: function() {
    this.model = new websno.collections.CrateList();
    this.views = [];
    _.each(this.model.models, function(crate){
      this.views.push(new websno.views.Screamer({model: crate}));
    },this);
  },

  render: function() {
    $(this.el).html(this.template());
    _.each(this.views, function(crateview){
      var selector = '#screamer-crate' + crateview.model.get('id');
      crateview.setElement(this.$(selector)).render();
    },this);
    return this;
  }
});

websno.views.CmosPage = Backbone.View.extend({
  initialize: function(options) {
    this.model = new websno.collections.CrateList();
    this.focus = options.id;
  },
  render: function() {
    $(this.el).html(this.template());
    return this;
  }
});
