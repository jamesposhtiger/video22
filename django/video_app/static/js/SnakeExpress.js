Class('SnakeExpress').includes(CustomEventSupport)({
    capitalise: function (string) {
        return string.charAt(0).toUpperCase() + string.slice(1);
    },
    prototype: {
        _io: null, //Socket Io Connection
        init: function (config) {
            var snakeExpress = this;
            try {
                this._io = io.connect(config.io);
            }
            catch (e) {
                console.log(e.message);
                return;
            }
            this._io.on('connect', function (data) {
                console.log('connect data', data);
                snakeExpress.connected = true;
                snakeExpress.dispatch('connect');
            });
        },
        send: function (model, message, obj) {
            if (this._io) {
                this._io.emit(model + '::' + message, obj)
            }
        }
    }
});

Class(SnakeExpress, 'Plug').includes(CustomEventSupport)({
    prototype: {
        namespace: "",// Model Name
        init: function (config) {
            if (!window.snakeExpress) {
                throw "Create a SnakeExpress before a SnakeExpress Model";
            }

            if (!config.name) {
                throw "All snakeExpress models require a name";
            }

            config.events = config.events || [];

            for (var property in config) {
                if (config.hasOwnProperty(property)) {
                    this[property] = config[property];
                }
            }

            this._bindCrud();
        },
        _bindCrud: function () {
            var snakeExpressPlug = this;

            window.snakeExpress._io.on(this.name + '::create', function (data) {
                snakeExpressPlug.onCreate(data);
            });
            window.snakeExpress._io.on(this.name + '::delete', function (data) {
                snakeExpressPlug.onDelete(data);
            });
            window.snakeExpress._io.on(this.name + '::update', function (data) {
                snakeExpressPlug.onUpdate(data);
            });

            this.events.forEach(function (event) {
                window.snakeExpress._io.on(snakeExpressPlug.name + '::' + event, function (data) {
                    snakeExpressPlug['on' + SnakeExpress.capitalise(event)](data);

                    snakeExpressPlug.dispatch(event, data);
                });
            });
        },
        onCreate: function (data) {
            if (!data.id) {
                throw "SnakeExpress Items need id";
            }

            this.dispatch('create', data);
        },
        onDelete: function (data) {
            if (!data.id) {
                throw "SnakeExpress Items need id";
            }

            this.dispatch('delete', data);
        },
        onUpdate: function (data) {
            if (!data.id) {
                throw "SnakeExpress Items need id";
            }

            this.dispatch('update', data);
        }
    }
});

Class(SnakeExpress, 'BackbonePlug').inherits(SnakeExpress.Plug)({
    prototype: {
        namespace: "",// Model Name
        events: [],
        init: function (config) {
            config.name = config.name || config.collection.name;

            if (config.channel) {
                snakeExpress._io.emit('channel', config.channel);
            }

            SnakeExpress.Plug.prototype.init.call(this, config);
        },
        onCreate: function (data) {
            if (!data.id) {
                throw "SnakeExpress Items need id";
            }

            //this.collection.add(data);
            this.collection.paginationView.updateList();

            this.dispatch('create', data);
        },
        onDelete: function (data) {
            if (!data.id) {
                throw "SnakeExpress Items need id";
            }

            var item = this.collection.find(function (item) {
                return item.get('id') === data.id;
            });

            // Item could have been removed before
            if (!item) {
                return;
            }

            // Destroy model with out notifiing the server
            // http://stackoverflow.com/questions/10218578/backbone-js-how-to-disable-sync-for-delete
            item.trigger('destroy', item, item.collection);

            this.dispatch('update', data);

        },
        onUpdate: function (data) {
            if (!data.id) {
                throw "SnakeExpress Items need id";
            }

            var item = this.collection.find(function (item) {
                return item.get('id') === data.id;
            });

            // Item could have been removed before
            if (!item) {
                return;
            }
            item.fetch();
            //item.set(data);

            this.dispatch('update', data);
        }
    }
});
