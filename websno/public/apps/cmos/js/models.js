websno.models.Channel = Backbone.Model.extend({
  initialize: function() {
    this.set('rate',0,{silent: true});
  }
});

websno.collections.ChannelList = Backbone.Collection.extend({
  model: websno.models.Channel
});

websno.models.Crate = Backbone.Model.extend({
  initialize: function() {
    this.set('screamers',0,{silent: true});
    this.channels = new websno.collections.ChannelList();
    for (var i=0;i<32;i++){
      var id = this.id*32+i;
      this.channels.add(new websno.models.Channel({id: id}),{silent: true});
    }
    websno.events.on('increment',this.increment,this);
  },

  increment: function() {
    this.set('screamers',this.get('screamers')+1);
  }
});

websno.collections.CrateList = Backbone.Collection.extend({
  model: websno.models.Crate,
  initialize: function(){
    for (var i=0;i<19;i++){
      this.add(new websno.models.Crate({id: i}),{silent: true});
    }
  }
});
