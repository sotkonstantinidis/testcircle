(function ($) {

    var geomFormat = new ol.format.GeoJSON();

    $('.map-form-container').each(function() {
        var mapContainer = this;

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
            style: defaultStyle
        });

        // Map container.
        var map = new ol.Map({
            target: mapContainer,
            layers: [
                new ol.layer.Tile({
                    source: new ol.source.MapQuest({layer: 'sat'})
                }),
                vector_layer
            ],
            view: new ol.View({
                projection: 'EPSG:4326',
                center: [0, 0],
                zoom: 2
            })
        });

        // The hidden input field where the coordinates are stored.
        var coordinatesField = $(mapContainer).next(
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
            var features = geomFormat.readFeatures(coordinatesField.val());
            vector_source.addFeatures(features);
            interactionSwitch.filter(
                '[value="modify"]').attr('checked', true).trigger('change');
            zoomToFeatures();
        } else {
            // Set initial interaction type: Draw.
            //interactionSwitch.filter('[value="draw"]').click();
            interactionSwitch.filter(
                '[value="draw"]').attr('checked', true).trigger('change');
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
                var feature = new ol.Feature(new ol.geom.Point(coords.coords));
                vector_source.addFeatures([feature]);
                $(msg).html('A point was added.').addClass('success');
                coordsField.val('');
            }
            logField.html(msg);
        });

        $('.map-coordinates-show').click(function() {
            toggleCoordinates(true);
        });
        $('.map-coordinates-close').click(function() {
            toggleCoordinates(false);
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
                coordinatesField.val(geomFormat.writeFeatures(features));
            } else {
                coordinatesField.val('');
            }
        }

        /**
         * Zoom to all features on the map.
         */
        function zoomToFeatures() {
            if (vector_source.getFeatures().length) {
                map.getView().fit(vector_source.getExtent(), map.getSize());
            }
        }

        // Zoom to features.
        $('.button-show-features').click(zoomToFeatures);

        // Delete all features.
        $('.button-delete-features').click(function() {
            vector_source.clear();
            // Activate the draw interaction.
            interactionSwitch.filter(
                '[value="draw"]').attr('checked', true).trigger('change');
        });

        /**
         * Toggle the field for parsing coordinates. Hides the control panel.
         * @param show
         */
        function toggleCoordinates(show) {
            var listItem = $(mapContainer).closest('.list-item');
            listItem.find('.map-controls').toggle(!show);
            listItem.find('.map-coordinates').toggle(show);;
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
