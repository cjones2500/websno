websno.models.Crate = Backbone.Model.extend({
  initialize: function() {
    this.set('screamers',0,{silent: true});
    this.set('rates',[],{silent: true});
    for (var i=0;i<512;i++){
      this.attributes.rates.push(0);
    }
  },

  increment: function() {
    this.set('screamers',this.get('screamers')+1);
    for (var i=0;i<512;i++){
      this.attributes.rates[i] += 10;
    }
    this.trigger("change");
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
