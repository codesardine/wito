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

        /**
     * Invokes a Python method through WebKit message handlers.
     * 
     * This method creates a bridge between JavaScript and Python, allowing asynchronous 
     * communication through WebKit message handlers. It generates a unique ID for each call
     * and stores the promise callbacks for later resolution.
     * 
     * Args:
     *     method (string): The name of the Python method to be called.
     *     args (Array): An array of arguments to pass to the Python method.
     *     Items in Array must be dict keys. 
     *     Dict values must be (string).
     * 
     * Returns:
     *     Promise: A promise that resolves with the Python method's result or rejects with an error.
     * 
     * Raises:
     *     Error: When WebKit message handlers are not available.
     * 
     * Example:
     *     ```javascript
     *     // Basic usage
     *     try {
     *         const result = await wito._invoke('get_data', [{'username': 'user123']});
     *         console.log(result);
     *     } catch (error) {
     *         console.error('Failed to get data:', error);
     *     }
     * 
     *     // With multiple arguments
     *     const userData = await wito._invoke('save_user', [{
     *         name: 'John',
     *         age: '30'
     *     }]);
     * 
     *     // Without arguments
     *     const status = await wito._invoke('get_status', []);
     *     ```
     * 
     * Notes:
     *     - The method requires WebKit message handlers to be available
     *     - The method requires the Python side to have a corresponding handler to be available
     *     - Arguments must be JSON-serializable
     *     - The callId is automatically incremented for each call
     *     - Debug messages are logged if devMode is enabled
     * 
     * See Also:
     *     - window.webkit.messageHandlers
     *     - JSON.stringify()
     */
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

