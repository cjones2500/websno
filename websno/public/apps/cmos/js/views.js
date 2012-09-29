websno.views.Screamer = Backbone.View.extend({
  initialize: function() {
    _.bindAll(this,'render');
    websno.events.on('increment',this.model.increment,this.model);
    this.model.on('change',this.render);
  },

  render: function() {
    $(this.el).html(this.template(this.model.toJSON()));
    return this;
  },

  onclose: function() {
    this.model.off('change',this.render);
    websno.events.off('increment',this.model.increment,this.model);
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
      delete selector;
    },this);
    return this;
  },

  onclose: function() {
    _.each(this.views, function(crateview){
      crateview.close();
    });
    delete this.views;
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
