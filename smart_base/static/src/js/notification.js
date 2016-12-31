odoo.define('smart_base.notification', function (require) {
"use strict";

var core = require('web.core');
var CalendarView = require('web_calendar.CalendarView');
var data = require('web.data');
var Dialog = require('web.Dialog');
var form_common = require('web.form_common');
var Model = require('web.DataModel');
var Notification = require('web.notification').Notification;
var session = require('web.session');
var WebClient = require('web.WebClient');
 
var _t = core._t;
var _lt = core._lt;
var QWeb = core.qweb;




var BaseNotification = Notification.extend({
    template: "BaseNotification",

    init: function(parent, title, text, eid, action_id, res_id) {
        this._super(parent, title, text, true);
        this.eid = eid;
        this.action_id = action_id;
        this.res_id = res_id;

        this.events = _.extend(this.events || {}, {
            'click .link2event': function() {
                var self = this;

                this.rpc("/web/action/load", {
                	action_id: this.action_id,
                }).then(function(r) {
                	console.log(self.res_id);
                    r.res_id = self.res_id;
                    return self.do_action(r);
                });
            },
            'click .link2showed': function() {
                var self = this;
                console.log(self);
                console.log(this.eid);
                this.rpc("/notification/validate", {
                	notif_id: this.eid,
                	
                }).then(function(r) {
                	
                	console.log('ok');
                });
                this.destroy(true);
            },

            'click .link2recall': function() {
                this.destroy(true);
            },

        });
    },
});

WebClient.include({
    get_next_notif: function() {
    	
    	
        var self = this;
        this.rpc("/notification/notify", {}, {shadow: true})
        .done(function(result) {
        	
            _.each(result, function(res) {
                setTimeout(function() {
                    // If notification not already displayed, we create and display it (FIXME is this check usefull?)
                    if(self.$(".eid_" + res.notif_id).length === 0) {
                    	
                        self.notification_manager.display(new BaseNotification(self.notification_manager, res.title, res.message, res.notif_id, res.res_action, res.res_id));
                    }
                }, res.timer * 1000);
            });
        })
        .fail(function(err, ev) {
            if(err.code === -32098) {
                // Prevent the CrashManager to display an error
                // in case of an xhr error not due to a server error
                ev.preventDefault();
            }
        });
    },
    check_notifications: function() {
        var self = this;
        this.get_next_notif();
        this.intervalNotif = setInterval(function() {
            self.get_next_notif();
        }, 1 * 60 * 1000 /4);
    },
    //Override the show_application of addons/web/static/src/js/chrome.js       
    show_application: function() {
        this._super();
        this.check_notifications();
    },
    //Override addons/web/static/src/js/chrome.js       
    on_logout: function() {
        this._super();
        clearInterval(this.intervalNotif);
    },
});






});
