!function (document, window, $) {
    "use strict";

    function chartistChart() {
    /*---- Basic-map ----*/
    var map1 = new GMaps({
        el: '#Basic-map',
        lat: -12.043333,
        lng: -77.028333,
        zoomControl : true,
        zoomControlOpt: {
            style : 'SMALL',
            position: 'TOP_LEFT'
        },
        panControl : false,
        streetViewControl : false,
        mapTypeControl: false,
        overviewMapControl: false
    });

    /*---- Markets-map ----*/
    var map2 = new GMaps({
        el: '#Markets-map',
        lat: -12.043333,
        lng: -77.028333
    });
    map2.addMarker({
        lat: -12.043333,
        lng: -77.03,
        title: 'Lima',
        details: {
            database_id: 42,
            author: 'HPNeo'
        },
        click: function(e){
            if(console.log)
                console.log(e);
            alert('You clicked in this marker');
        },
        mouseover: function(e){
            if(console.log)
                console.log(e);
        }
    });
    map2.addMarker({
        lat: -12.042,
        lng: -77.028333,
        title: 'Marker with InfoWindow',
        infoWindow: {
            content: '<p>HTML Content</p>'
        }
    });

    /*---- Map-types ----*/
    var map3 = new GMaps({
        el: '#Map-types',
        lat: -12.043333,
        lng: -77.028333,
        mapTypeControlOptions: {
            mapTypeIds : ["hybrid", "roadmap", "satellite", "terrain", "osm", "cloudmade"]
        }
    });
    map3.addMapType("osm", {
        getTileUrl: function(coord, zoom) {
            return "http://tile.openstreetmap.org/" + zoom + "/" + coord.x + "/" + coord.y + ".png";
        },
        tileSize: new google.maps.Size(256, 256),
        name: "OpenStreetMap",
        maxZoom: 18
    });
    map3.addMapType("cloudmade", {
        getTileUrl: function(coord, zoom) {
            return "http://b.tile.cloudmade.com/8ee2a50541944fb9bcedded5165f09d9/1/256/" + zoom + "/" + coord.x + "/" + coord.y + ".png";
        },
        tileSize: new google.maps.Size(256, 256),
        name: "CloudMade",
        maxZoom: 18
    });
    map3.setMapTypeId("osm");

    /*---- KML-layers ----*/
    var map, infoWindow;
    infoWindow = new google.maps.InfoWindow({});
    var map4 = new GMaps({
        el: '#KML-layers',
        zoom: 12,
        lat: 40.65,
        lng: -73.95
    });
    map4.loadFromKML({
        url: 'http://api.flickr.com/services/feeds/geo/?g=322338@N20&lang=en-us&format=feed-georss',
        suppressInfoWindows: true,
        events: {
            click: function(point){
                infoWindow.setContent(point.featureData.infoWindowHtml);
                infoWindow.setPosition(point.latLng);
                infoWindow.open(map4.map);
            }
        }
    });

    /*---- Context menu ----*/
    var map5 = new GMaps({
        el: '#Context-menu',
        lat: -12.043333,
        lng: -77.028333
    });
    map5.setContextMenu({
        control: 'map5',
        options: [{
            title: 'Add marker',
            name: 'add_marker',
            action: function(e){
                console.log(e.latLng.lat());
                console.log(e.latLng.lng());
                this.addMarker({
                    lat: e.latLng.lat(),
                    lng: e.latLng.lng(),
                    title: 'New marker'
                });
                this.hideContextMenu();
            }
        }, {
            title: 'Center here',
            name: 'center_here',
            action: function(e){
                this.setCenter(e.latLng.lat(), e.latLng.lng());
            }
        }]
    });
    map5.setContextMenu({
        control: 'marker',
        options: [{
            title: 'Center here',
            name: 'center_here',
            action: function(e){
                this.setCenter(e.latLng.lat(), e.latLng.lng());
            }
        }]
    });

    /*---- Overlays ----*/
    var map6 = new GMaps({
        el: '#Overlays-map',
        lat: -12.043333,
        lng: -77.028333
    });
    map6.drawOverlay({
        lat: map6.getCenter().lat(),
        lng: map6.getCenter().lng(),
        layer: 'overlayLayer',
        content: '<div class="overlay-map">Plaza<div class="overlay_arrow-map above"></div></div>',
        verticalAlign: 'top',
        horizontalAlign: 'center'
    });

    /*---- Routes-Advanced ----*/
    var map8 = new GMaps({
        div: '#Routes-advanced',
        lat: -12.043333,
        lng: -77.028333
    });
    $('#start_travel').click(function(e){
        e.preventDefault();
        map8.travelRoute({
            origin: [-12.044012922866312, -77.02470665341184],
            destination: [-12.090814532191756, -77.02271108990476],
            travelMode: 'driving',
            step: function(e){
                $('#instructions').append('<li>'+e.instructions+'</li>');
                $('#instructions li:eq('+e.step_number+')').delay(450*e.step_number).fadeIn(200, function(){
                    map8.setCenter(e.end_location.lat(), e.end_location.lng());
                    map8.drawPolyline({
                        path: e.path,
                        strokeColor: '#131540',
                        strokeOpacity: 0.6,
                        strokeWeight: 6
                    });
                });
            }
        });
    });

    /*---- Geocoding ----*/
    var map9 = new GMaps({
        el: '#Geocoding',
        lat: -12.043333,
        lng: -77.028333
    });
    $('#geocoding_form').submit(function(e){
        e.preventDefault();
        GMaps.geocode({
            address: $('#address').val().trim(),
            callback: function(results, status){
                if(status=='OK'){
                    var latlng = results[0].geometry.location;
                    map9.setCenter(latlng.lat(), latlng.lng());
                    map9.addMarker({
                        lat: latlng.lat(),
                        lng: latlng.lng()
                    });
                }
            }
        });
    });

    /*---- Styled Maps ----*/
    var map10 = new GMaps({
        el: "#Styled-maps",
        lat: 41.895465,
        lng: 12.482324,
        zoom: 5,
        zoomControl : true,
        zoomControlOpt: {
            style : "SMALL",
            position: "TOP_LEFT"
        },
        panControl : true,
        streetViewControl : false,
        mapTypeControl: false,
        overviewMapControl: false
    });

    var styles = [
        {
            stylers: [
                { hue: "#00ffe6" },
                { saturation: -20 }
            ]
        }, {
            featureType: "road",
            elementType: "geometry",
            stylers: [
                { lightness: 100 },
                { visibility: "simplified" }
            ]
        }, {
            featureType: "road",
            elementType: "labels",
            stylers: [
                { visibility: "off" }
            ]
        }
    ];

    map10.addStyle({
        styledMapName:"Styled Map",
        styles: styles,
        mapTypeId: "map_style"
    });

    map10.setStyle("map_style");

    }

    /*---- Resize ----*/

    $(window).on('resizeEnd', function () {
        chartistChart();
    });

    $(window).on('load', function () {
        chartistChart();
    });

    //create trigger to resizeEnd event
    $(window).resize(function () {
        if (this.resizeTO) clearTimeout(this.resizeTO);
        this.resizeTO = setTimeout(function () {
            $(this).trigger('resizeEnd');
        }, 500);
    });

    /*---- Fusion-tables-layers ----*/
    var fasionlayers = new google.maps.InfoWindow({});
    var map7 = new GMaps({
        el: '#Fusion-tables-layers',
        zoom: 11,
        lat: 41.850033,
        lng: -87.6500523
    });
    map7.loadFromFusionTables({
        query: {
            select: '\'Geocodable address\'',
            from: '1mZ53Z70NsChnBMm-qEYmSDOvLXgrreLTkQUvvg'
        },
        suppressInfoWindows: true,
        events: {
            click: function(point){
                fasionlayers.setContent('You clicked here!');
                fasionlayers.setPosition(point.latLng);
                fasionlayers.open(map7.map);
            }
        }
    });

}(document, window, jQuery);
