Videos.Collections.CsvFiles = Backbone.Collection.extend({
    model: Videos.Models.CsvFile,
    url:'/api/files/'
});
