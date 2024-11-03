class Wito {
    constructor() {
        this.callId = 0;
        this.pendingCalls = {};
        this.eventListeners = {};
        this.readyCallbacks = [];  
        this.isReady = false;
        this.devMode = false;
        this.appDevMode = false
    }

    _initializeBindings = function() {
        // METHOD_BINDINGS_PLACEHOLDER
        // PROPERTY_BINDINGS_PLACEHOLDER
    };

    _invoke(method, args) {
        return new Promise((resolve, reject) => {
            const id = this.callId++;
            this.pendingCalls[id] = { resolve, reject };
            if (window.webkit && window.webkit.messageHandlers && window.webkit.messageHandlers.Invoke) {
                const message = JSON.stringify({ id, method, args });
                if (this.devMode) console.log(`Sending message to Python: ${message}`);
                window.webkit.messageHandlers.Invoke.postMessage(message);
            } else {
                let msg = "WebKit message handlers not available"
                console.error(msg);
                reject(new Error(msg));
            }
        });
    }
    
    _resolveCall(id, result) {
        console.log(`_resolveCall invoked for id ${id}`);
        if (this.pendingCalls[id]) {
            if (this.devMode) console.log(`Found pending call for id ${id}`);
            try {
                let parsedResult = (typeof result === 'string') ? JSON.parse(result) : result;
                if (this.devMode) console.log(`Parsed result:`, parsedResult);
                this.pendingCalls[id].resolve(parsedResult);
                if (this.devMode) console.log(`Promise resolved for id ${id}`);
            } catch (error) {
                console.error(`Error in _resolveCall for id ${id}:`, error);
                this.pendingCalls[id].reject(error);
            }
            delete this.pendingCalls[id];
        } else {
            console.warn(`No pending call found for id: ${id}`);
        }
    }
    
    _rejectCall(id, error) {
        if (this.devMode) console.log(`_rejectCall invoked for id ${id}`);
        if (this.pendingCalls[id]) {
            this.pendingCalls[id].reject(new Error(error));
            delete this.pendingCalls[id];
        } else {
            console.warn(`No pending call found for id: ${id}`);
        }
    }    

    on(event, callback) {
        if (!this.eventListeners[event]) {
            this.eventListeners[event] = [];
        }
        this.eventListeners[event].push(callback);
    }

    _emitEvent(event, data) {
        if (this.eventListeners[event]) {
            this.eventListeners[event].forEach(callback => callback(data));
        }
    }

    onReady(callback) {
        if (this.isReady) {
            callback();
        } else {
            this.readyCallbacks.push(callback);
        }
    }

    _setReady() {
        this.isReady = true;
        this.readyCallbacks.forEach(callback => callback());
        this.readyCallbacks = [];
    }

    getAllObjects() {
        const objects = Object.getOwnPropertyNames(wito)
        .filter(object => wito[object])
        .map(object => `${object}`);
        return objects
    };
    
    getAllMethods() {
        const methods = Object.getOwnPropertyNames(wito)
        .filter(method => typeof wito[method] === 'function')
        .map(method => `${method}()`);
        return methods
    };

    getAllProperties() {
        const props = Object.getOwnPropertyNames(wito)
        .filter(prop => typeof wito[prop] !== 'function')
        .map(prop => `${prop}`);
        return props
    };
}

const wito = new Wito();
wito._initializeBindings();
wito._setReady();
wito.devMode = // WITO_DEV_MODE_PLACEHOLDER;
wito.appDevMode = // APP_DEV_MODE_PLACEHOLDER;
console.log('Wito Ready');
console.log(`Framework Debug: ${wito.devMode}', 'Application Debug: ${wito.appDevMode}`);

