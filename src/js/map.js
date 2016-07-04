(function ($) {

    var dataProjection = 'EPSG:4326';
    var featureProjection = 'EPSG:3857';
    var geomFormat = new ol.format.GeoJSON({
        defaultDataProjection: dataProjection
    });

    $('.map-form-container').each(function() {
        var mapContainer = this;
        var deleteMode = false;

        // The default style for features on the map.
        var defaultStyle = new ol.style.Style({
            image: new ol.style.Circle({
                radius: 5,
                fill: new ol.style.Fill({
                    color: 'rgba(255, 255, 255, 0.4)'
                }),
                stroke: new ol.style.Stroke({
                    color: '#dc7d35',
                    width: 1.25
                })
            })
        });

        // The style when a feature is selected.
        var selectStyle = new ol.style.Style({
            image: new ol.style.Circle({
                radius: 5,
                fill: new ol.style.Fill({
                    color: 'rgba(255, 255, 255, 0.4)'
                }),
                stroke: new ol.style.Stroke({
                    color: '#dc7d35',
                    width: 1.25
                })
            })
        });

        // The style for mouseover on features to be deleted.
        var deleteStyle = new ol.style.Style({
            image: new ol.style.Circle({
                radius: 7,
                fill: new ol.style.Fill({
                    color: 'rgba(255, 0, 0, 0.2)'
                }),
                stroke: new ol.style.Stroke({
                    color: 'rgba(255, 0, 0, 0.6)',
                    width: 1.25
                })
            })
        });

        // Vector layer containing the features.
        var vector_source = new ol.source.Vector();
        var vector_layer = new ol.layer.Vector({
            source: vector_source,
            style: defaultStyle,
            name: 'vector'
        });

        // Base layers
        // https://leaflet-extras.github.io/leaflet-providers/preview/
        var layers = [
            new ol.layer.Tile({
                name: 'osm',
                source: new ol.source.OSM()
            }),
            new ol.layer.Tile({
                name: 'komoot',
                visible: false,
                source: new ol.source.XYZ({
                    attributions: '&copy; <a href="http://www.komoot.de/">Komoot</a>, &copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
                    url: 'http://a.tile.komoot.de/komoot-2/{z}/{x}/{y}.png'
                })
            }),
            new ol.layer.Tile({
                name: 'aerial',
                visible: false,
                source: new ol.source.XYZ({
                    attributions: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community',
                    url: 'http://a.tile.komoot.de/komoot-2/{z}/{x}/{y}.png'
                })
            }),
            new ol.layer.Tile({
                name: 'opentopo',
                visible: false,
                source: new ol.source.XYZ({
                    attributions: 'Map data: &copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>, <a href="http://viewfinderpanoramas.org">SRTM</a> | Map style: &copy; <a href="https://opentopomap.org">OpenTopoMap</a> (<a href="https://creativecommons.org/licenses/by-sa/3.0/">CC-BY-SA</a>)',
                    url: 'http://{a-c}.tile.opentopomap.org/{z}/{x}/{y}.png'
                })
            }),
            new ol.layer.Tile({
                name: 'landscape',
                visible: false,
                source: new ol.source.XYZ({
                    attributions: '&copy; <a href="http://www.thunderforest.com/">Thunderforest</a>, &copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
                    url: 'http://{a-c}.tile.thunderforest.com/landscape/{z}/{x}/{y}.png'
                })
            }),
            new ol.layer.Tile({
                name: 'worldtopo',
                visible: false,
                source: new ol.source.XYZ({
                    attributions: 'Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ, TomTom, Intermap, iPC, USGS, FAO, NPS, NRCAN, GeoBase, Kadaster NL, Ordnance Survey, Esri Japan, METI, Esri China (Hong Kong), and the GIS User Community',
                    url: 'http://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}'
                })
            }),
            vector_layer
        ];

        // Map container.
        var map = new ol.Map({
            target: mapContainer,
            layers: layers,
            view: new ol.View({
                center: [0, 0],
                zoom: 2,
                minZoom: 2,
                maxZoom: 20
            })
        });
        $(mapContainer).data('map', map);

        // Initial layer: Komoot
        toggleLayer('komoot');

        // The hidden input field where the coordinates are stored.
        var coordinatesField = $(mapContainer).closest('.map-container').next(
            '.single-item').find('input:hidden');

        // The current interaction mode.
        var interaction;

        // The currently highlighted features.
        var highlighted = [];

        // Action called when changing interaction mode.
        var interactionSwitch = $('[name="map-actions"]');
        interactionSwitch.on('change', function(e) {

            // Remove the previous interaction mode.
            map.removeInteraction(interaction);

            // Unbind mouseover function used to delete features.
            $(map.getViewport()).unbind('mousemove');

            if (!$(this).is(':checked')) {
                // No interaction selected (or interaction deselected)
                return;
            }

            switch(this.value) {

                case 'draw':
                    // Draw (add) new features on the map.
                    interaction = new ol.interaction.Draw({
                        source: vector_source,
                        type: 'Point',
                        maxPoints: 10,
                        style: selectStyle
                      });
                    break;

                case 'modify':
                    // Modify (move) features on the map.
                    interaction = new ol.interaction.Modify({
                        features: new ol.Collection(
                            vector_source.getFeatures()),
                        style: selectStyle
                    });
                    break;

                case 'delete':
                    // Delete (remove) features from the map.
                    interaction = new ol.interaction.Select({
                        layers: [vector_layer]
                    });
                    interaction.on('select', function(event) {
                        if (event.selected.length) {
                            var feature = event.selected[0];
                            vector_source.removeFeature(feature);
                            interaction.getFeatures().clear();
                        }
                    });

                    // This seems to be necessary just to get a little mouseover
                    // effect.
                    $(map.getViewport()).on('mousemove', function(e) {
                        unselectPreviousFeatures();
                        map.forEachFeatureAtPixel(
                            map.getEventPixel(e.originalEvent),
                            function(feature) {
                                feature.setStyle(deleteStyle);
                                highlighted.push(feature);
                        });
                    });
                    break;

                default:
                    break;
            }

            map.addInteraction(interaction);
        });

        if (coordinatesField.val()) {
            // Put initial features on map and set interaction type: Modify.
            // Zoom to features.
            var features = geomFormat.readFeatures(coordinatesField.val(), {
                featureProjection: featureProjection
            });

            vector_source.addFeatures(features);
            interactionSwitch.filter(
                '[value="modify"]').attr('checked', true).trigger('change');
            zoomToFeatures();
            toggleDeleteMode(true);
        } else {
            // Set initial interaction type: Draw.
            interactionSwitch.filter(
                '[value="draw"]').attr('checked', true).trigger('change');
            toggleDeleteMode(false);
        }

        // Listen to changes on the vector layer.
        vector_layer.on('change', function() {
            saveFeatures();
        });

        // Parse GPS coordinates.
        $('.button-parse-coordinates').click(function() {
            var listItem = $(mapContainer).closest('.list-item');
            var logField = listItem.find('.map-coordinates-log');
            var coordsField = listItem.find('.map-coordinates-field');
            if (!coordsField.val()) return;

            var msg = document.createElement('p');
            var coords = getCoordinatesFromText(coordsField.val());
            if (!coords.valid) {
                $(msg).html(coords.msg).addClass('error');
            } else {
                var coords_transformed = ol.proj.transform(coords.coords, dataProjection, featureProjection)
                var feature = new ol.Feature(new ol.geom.Point(coords_transformed));
                vector_source.addFeatures([feature]);
                $(msg).html('The point was successfully added.').addClass('success');
                coordsField.val('');
            }
            logField.html(msg);
        });

        $('.map-coordinates-show').click(function() {
            var listItem = $(mapContainer).closest('.list-item');
            listItem.find('.map-menu').not('.map-coordinates').hide();
            listItem.find('.map-coordinates').toggle();
        });
        $('.map-coordinates-close').click(function() {
            var listItem = $(mapContainer).closest('.list-item');
            listItem.find('.map-coordinates').toggle(false);
        });

        $('[name="map-layers"]').on('change', function(e) {
            toggleLayer(this.value);
        });
        $('.map-layers-show').click(function() {
            var listItem = $(mapContainer).closest('.list-item');
            listItem.find('.map-menu').not('.map-layers').hide();
            listItem.find('.map-layers').toggle();
        });
        $('.map-layers-close').click(function() {
            var listItem = $(mapContainer).closest('.list-item');
            listItem.find('.map-layers').toggle(false);
        });

        $('.map-search-show').click(function() {
            var listItem = $(mapContainer).closest('.list-item');
            listItem.find('.map-menu').not('.map-search').hide();
            listItem.find('.map-search').toggle();
        });
        $('.map-search-close').click(function() {
            var listItem = $(mapContainer).closest('.list-item');
            listItem.find('.map-search').toggle(false);
        });

        $('.map-change-size').click(function() {
            var container = $(mapContainer);
            container.height(container.height() == 400 ? 700 : 400);
            map.updateSize();
        });

        /**
         * Unselect previously selected features.
         */
        function unselectPreviousFeatures() {
            var i;
            for(i = 0; i < highlighted.length; i++) {
                highlighted[i].setStyle(null);
            }
            highlighted = [];
        }

        /**
         * Save features on the map (store coordinates in the hidden field).
         */
        function saveFeatures() {
            var features = vector_source.getFeatures();
            if (features.length) {
                coordinatesField.val(geomFormat.writeFeatures(features, {
                    featureProjection: featureProjection
                }));
                toggleDeleteMode(true);
            } else {
                coordinatesField.val('');
                toggleDeleteMode(false);
            }
        }


        /**
         * Enable or disable the buttons to modify/edit existing points.
         * @param enabled
         */
        function toggleDeleteMode(enabled) {
            if (enabled != deleteMode) {
                // Mode changed
                deleteMode = enabled;
                var btnToggle = $(mapContainer).closest('.map-container').find('.map-btn-toggle');
                btnToggle.each(function() {
                    $(this).toggleClass('map-btn-disabled', !deleteMode);
                    $('#' + $(this).attr('for')).prop('disabled', !deleteMode);
                });
                if (!deleteMode) {
                    // No points left, deactivate modify and delete mode if enabled.
                    interactionSwitch.filter(
                        '[value="delete"]').attr('checked', false).trigger('change');
                    interactionSwitch.filter(
                        '[value="modify"]').attr('checked', false).trigger('change');
                }
            }
            // Update feature count button
            $(mapContainer).closest('.map-container').find('.button-feature-count')
                .html(vector_source.getFeatures().length);
        }


        /**
         * Toggle the visibility of a certain layer while hiding all the others.
         * Never hide the layer with name "vector" (the one used for the points)
         * @param layername
         */
        function toggleLayer(layername) {
            for (var i=0; i<layers.length; i++) {
                var layer = layers[i];
                layer.set('visible', (layer.get('name') == layername || layer.get('name') == 'vector'));
            }
        }


        /**
         * Zoom to all features on the map.
         */
        function zoomToFeatures() {
            featureCount = vector_source.getFeatures().length;
            if (featureCount) {
                map.getView().fit(vector_source.getExtent(), map.getSize());
                map.getView().setZoom(Math.min(map.getView().getZoom(), 15));
            }
        }
        // Attach the function to the map so it can be called (again) when
        // opening the modal in the detail view.
        map.zoomToFeatures = zoomToFeatures;

        // Zoom to features.
        $('.button-show-features').click(zoomToFeatures);

        // Delete all features.
        $('.button-delete-features').click(function() {
            vector_source.clear();
            // Activate the draw interaction.
            interactionSwitch.filter(
                '[value="draw"]').attr('checked', true).trigger('change');
        });

        if ($.fn.autocomplete) {
            $('.map-search-field').autocomplete({
                source: function(request, response) {
                    var thisElement = $(this.element);
                    var translationNoResults = thisElement.data('translation-no-results');
                    var translationTooManyResults = thisElement.data('translation-too-many-results');
                    var currentLocale = thisElement.data('current-locale');
                    $.ajax({
                        url: 'http://api.geonames.org/searchJSON',
                        dataType: 'json',
                        data: {
                            username: 'wocat_webdev',
                            lang: currentLocale,
                            maxRows: 10,
                            name_startsWith: request.term
                        },
                        success: function(data) {
                            if (data.totalResultsCount == 0) {
                                // No results
                                var result = [
                                    {
                                        error: translationNoResults
                                    }
                                ];
                                return response(result);
                            }
                            var res = data.geonames;
                            if (data.totalResultsCount > 10) {
                                var moreResults = data.totalResultsCount - 10;
                                // Too many results
                                res.push({
                                    error: '(' + moreResults + ') ' + translationTooManyResults
                                });
                            }
                            return response(res);
                        }
                    });
                },
                create: function() {
                    $(this).data('ui-autocomplete')._renderItem = function(ul, item) {
                        var displayName = item.name + (item.adminName1 ? ", " + item.adminName1 : "") + ", " + item.countryName;
                        if (item.error) {
                            displayName = item.error;
                        }
                        return $('<li>')
                            .append('<a>' + displayName + '</a>')
                            .appendTo(ul);
                    }
                },
                select: function(event, ui) {
                    if (ui.item.error) {
                        return false;
                    }
                    var lat = parseFloat(ui.item.lat);
                    var lng = parseFloat(ui.item.lng);
                    if (isNaN(lat) || isNaN(lng)) {
                        return false;
                    }

                    map.getView().setCenter(ol.proj.transform([lng, lat], 'EPSG:4326', 'EPSG:3857'));
                    map.getView().setZoom(15);
                }
            });
        }

    });

    /**
     * Parse a string of coordinates. Returns an object with the coordinates or
     * error message.
     *
     * Caution: The coordinates are reversed to be used by OpenLayers,
     * input: "Latitude, Longitude"
     * output: [lon, lat]
     *
     * @param coords_text. Coordinates as string. Must be of format "Latitude,
     * Longitude", eg. "46.9526, 7.4352".
     * @returns {{valid: boolean, coords: Array, msg: string}}
     */
    function getCoordinatesFromText(coords_text) {
        var coordinates = {
            valid: false,
            coords: [],
            msg: ''
        };

        var coords_list = coords_text.split(',');
        if (coords_list.length != 2) {
            coordinates.msg = 'Must be of format "Latitude, Longitude", eg. ' +
                '"46.9526, 7.4352"';
            return coordinates;
        }

        coordinates.coords = coords_list.map(function(c) {
            var asFloat = parseFloat(c);
            if (isNaN(asFloat)) {
                coordinates.msg = 'Coordinates do not contain valid number ' +
                    'values.'
            }
            return asFloat;
        }).reverse();
        coordinates.valid = coordinates.msg == '';

        return coordinates;
    }

}(jQuery));
