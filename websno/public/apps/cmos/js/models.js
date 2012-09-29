websno.models.Channel = Backbone.Model.extend({
  initialize: function() {
    this.data = [];
  },

  increment: function() {
    if (this.data.length > 10){
      this.data = this.data.slice(1);
    }
    if (this.data.length == 0){
      this.data.push([1,0]);
    }else{
      this.data.push([this.data[this.data.length-1][0]+1,this.data[this.data.length-1][1]+1]);
    }
    this.trigger("change");
  }
});

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
