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
        console.log(view + " not found");
      }
    });
    $.when.apply(null,deferreds).done(callback);
  }
};

Backbone.View.prototype.close = function(removedom) {
  removedom = (typeof removedom === "undefined") ? true : removedom;
  if (this.onclose){
    this.onclose();
  }
  if (removedom){
    this.remove();
  }
  this.unbind();
}
