/**
 * Google Maps for the details view.
 *
 * var geojson must be defined in
 */
function initMap() {
    var mapDiv = document.getElementById('map-view');

    var map = new google.maps.Map(mapDiv, {
        mapTypeId: google.maps.MapTypeId.HYBRID,
        disableDefaultUI: true,
        zoomControl: true,
        // Initial dummy center and zoom
        center: {lat: 0, lng: 0},
        zoom: 2
    });

    // Add event listener to zoom to all features after they were added.
    var bounds = new google.maps.LatLngBounds();
    map.data.addListener('addfeature', function(e) {
        processPoints(e.feature.getGeometry(), bounds.extend, bounds);
        map.fitBounds(bounds);

        // Adjust zoom level (max 6)
        google.maps.event.addListenerOnce(map, 'idle', function() {
            if (map.getZoom() > 6) map.setZoom(6);
        });
    });

    function processPoints(geometry, callback, thisArg) {
      if (geometry instanceof google.maps.LatLng) {
        callback.call(thisArg, geometry);
      } else if (geometry instanceof google.maps.Data.Point) {
        callback.call(thisArg, geometry.get());
      } else {
        geometry.getArray().forEach(function(g) {
          processPoints(g, callback, thisArg);
        });
      }
    }

    if ('mapViewGeojson' in window) {
        map.data.addGeoJson(mapViewGeojson);
    }
}
