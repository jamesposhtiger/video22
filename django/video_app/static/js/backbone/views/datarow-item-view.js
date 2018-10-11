Videos.Views.CsvFileItemView = Backbone.View.extend({
    events: {
        //"click .clear-btn": "clearForm"
    },
    tagName: "tr",
    className: "data-row",
    initialize: function () {
        var self = this;
        this.model.on('change', function (model) {
            self.render()
        });
        this.template = swig.compile($('#data-row-template').html())
    },
    render: function () {
        var data = this.model.toJSON();
        var html = this.template(data);
        this.$el.html(html);
    }
});
