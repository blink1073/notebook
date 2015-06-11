// Copyright (c) Jupyter Development Team.
// Distributed under the terms of the Modified BSD License.

import $ = require('jquery')
import events = require('base/js/events')

export class Page {
    "use strict";

    var Page = function ():void {
        this.bind_events();
    };

    public bind_events():void {
        // resize site on:
        // - window resize
        // - header change
        // - page load
        var _handle_resize = $.proxy(this._resize_site, this);
        
        $(window).resize(_handle_resize);

        // On document ready, resize codemirror.
        $(document).ready(_handle_resize);
        events.on('resize-header.Page', _handle_resize);
    };

    public show():void {
        /**
         * The header and site divs start out hidden to prevent FLOUC.
         * Main scripts should call this method after styling everything.
         */
        this.show_header();
        this.show_site();
    };

    public show_header():void {
        /**
         * The header and site divs start out hidden to prevent FLOUC.
         * Main scripts should call this method after styling everything.
         * TODO: selector are hardcoded, pass as constructor argument
         */
        $('div#header').css('display','block');
    };

    public show_site():void {
        /**
         * The header and site divs start out hidden to prevent FLOUC.
         * Main scripts should call this method after styling everything.
         * TODO: selector are hardcoded, pass as constructor argument
         */
        $('div#site').css('display', 'block');
        this._resize_site();
    };

    private _resize_site():void {
        // Update the site's size.
        $('div#site').height($(window).height() - $('#header').height());
    };

}
