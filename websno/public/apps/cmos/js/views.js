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

websno.views.SmallScreamer = Backbone.View.extend({
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

websno.views.SmallScreamerList = Backbone.View.extend({
  initialize: function() {
    this.model = new websno.collections.CrateList();
    this.views = [];
    _.each(this.model.models, function(crate){
      this.views.push(new websno.views.SmallScreamer({model: crate}));
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

websno.views.CmosRateList = Backbone.View.extend({
  initialize: function(options) {
    _.bindAll(this,'render');
    this.id = options.id;
    this.model = new websno.models.Crate({id: this.id});
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

websno.views.CmosPage = Backbone.View.extend({
  className: 'row',

  initialize: function(options) {
    this.focus = options.id;
    this.model = new websno.collections.CrateList();
    this.screamers = new websno.views.SmallScreamerList();
    this.rates = new websno.views.CmosRateList({id: this.focus});
  },

  render: function() {
    $(this.el).html(this.template());
    this.screamers.setElement(this.$('#smallscreamerlist')).render();
    this.rates.setElement(this.$('#cmosratelist')).render();
    return this;
  },

  onclose: function() {
    this.screamers.close();
    this.rates.close();
  }
});
