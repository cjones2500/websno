// template loader
websno.templateLoader = {
  load: function(views, callback) {
    var deferreds = [];
    $.each(views, function(index, view) {
      if (websno.views[view]) {
        deferreds.push($.get('templates/' + view + '.html', function(data) {
          websno.views[view].prototype.template = _.template(data);
        }, 'html'));
      }else{
        alert(view + " not found");
      }
    });
    $.when.apply(null,deferreds).done(callback);
  }
};

Backbone.View.prototype.close = function() {
  if (this.onclose){
    this.onclose();
  }
  this.remove();
  this.unbind();
}
