$(document).ready(function () {
    window.views.app = new Videos.Views.App($('body'));

    window.collections.rows = new Videos.Collections.CsvFiles;

    function updateList() {
        console.log("updating...");
        window.collections.rows.fetch();
    }

    setInterval(function () {
        updateList();
    }, 3000);
    updateList();


    window.collections.rows.on("add", function (model) {
        var view = new Videos.Views.CsvFileItemView({model: model});
        view.render();
        view.$el.appendTo('#data-row-items');
    });
    window.collections.rows.fetch();

    //Backbone.history.start({pushState: true});

});
