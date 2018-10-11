window.Videos = {};

Videos.Views = {};
Videos.Collections = {};
Videos.Models = {};
Videos.Routers = {};

window.app = {};
window.routers = {};
window.views = {};
window.collections = {};
window.route = 'web';

(function () {
    var _sync = Backbone.sync;
    Backbone.sync = function (method, model, options) {
        options.beforeSend = function (xhr) {
            var token = $('meta[name="csrf-token"]').attr('content');
            xhr.setRequestHeader('X-CSRFToken', token);
        };
        return _sync(method, model, options);
    };
})();