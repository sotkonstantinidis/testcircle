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
        var vector_layer = new ol.layer.Vector({
            source: new ol.source.Vector(),
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

            switch(this.value) {

                case 'draw':
                    // Draw (add) new features on the map.
                    interaction = new ol.interaction.Draw({
                        source: vector_layer.getSource(),
                        type: 'Point',
                        maxPoints: 10,
                        style: selectStyle
                      });
                    break;

                case 'modify':
                    // Modify (move) features on the map.
                    interaction = new ol.interaction.Modify({
                        features: new ol.Collection(
                            vector_layer.getSource().getFeatures()),
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
                            vector_layer.getSource().removeFeature(feature);
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
            var features = geomFormat.readFeatures(coordinatesField.val());
            vector_layer.getSource().addFeatures(features);
            interactionSwitch.filter(
                '[value="modify"]').attr('checked', true).trigger('change');
        } else {
            // Set initial interaction type: Draw.
            interactionSwitch.filter(
                '[value="draw"]').attr('checked', true).trigger('change');
        }

        // Listen to changes on the vector layer.
        vector_layer.on('change', function() {
            saveFeatures();
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
            var features = vector_layer.getSource().getFeatures();
            coordinatesField.val(geomFormat.writeFeatures(features));
        }

    });

}(jQuery));
