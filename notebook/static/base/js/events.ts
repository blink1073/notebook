// Copyright (c) Jupyter Development Team.
// Distributed under the terms of the Modified BSD License.

// Give us an object to bind all events to. This object should be created
// before all other objects so it exists when others register event handlers.
// To register an event handler:
//
// require(['base/js/events'], function (events) {
//     events.on("event.Namespace", function () { do_stuff(); });
// });

define(['base/js/namespace', 'jquery'], function(IPython, $) {
    "use strict";

    var Events = function () {};
    
    var events = new Events();


    // remove in 5.0
    Object.defineProperty(IPython, 'Event', {
      get: function() { 
          console.warn('accessing `IPython.Event` is deprecated. Use `require("base/js/Events")');
          return Events; 
      },
      enumerable: true,
      configurable: false
    });
    
    Object.defineProperty(IPython, 'event', {
      get: function() { 
          console.warn('accessing `IPython.event` is deprecated. Use `require("base/js/Events")');
          return events;
      },
      enumerable: true,
      configurable: false
    });

    // horrible horrible hack to return an instance from a module.
    return $([events]);
});

