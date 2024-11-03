Object.defineProperty(this, 'PROP_NAME', {
    get: function() {
        return this._invoke('get_PROP_NAME');
    },
    set: function(value) {
        return this._invoke('set_PROP_NAME', {value: value});
    }
});