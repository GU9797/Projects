import React from 'react';
import mapboxgl from 'mapbox-gl';

class MapComponent extends React.Component {
  componentWillMount() {
    mapboxgl.accessToken =
    'pk.eyJ1IjoianVzdGNhbWRpZyIsImEiOiJjamh6aXRmdGcweHV2M3FuMGtrbjdwYmozIn0.z1KDeg7R0Ua3qWJpLdI-Yw';
    const map = new mapboxgl.Map({
      container: 'map',
      style: 'mapbox://styles/mapbox/light-v9',
      zoom: 3,
      center: [-100, 40]
    });

    map.on('load', function addPoints(m) {
      map.addLayer({
        id: 'terrorism',
        type: 'circle',
        source: {
          type: 'geojson',
          data: './src/components/convertcsv.geojson'
        },
        paint: {
          'circle-radius': [
            '*',
            ['+',
              ['ln',
              ['+', ['to-number', ['get', 'FIELD10']], 2]],
              0.5],
            7
          ],
          'circle-color': [
            'match',
            ['get', 'FIELD8'],
            'Facility/Infrastructure Attack', '#fbb03b',
            'Armed Assault', '#223b53',
            'Bombing/Explosion', '#e55e5e',
            'Hijacking', '#3bb2d0', '#ccc'
          ],
          'circle-opacity': 0.8
        }
      });

      map.on('click', 'terrorism', function clickResult(e) {
        const coordinates = e.features[0].geometry.coordinates.slice();
        const description = e.features[0].properties.FIELD11;
        const nkills = e.features[0].properties.FIELD10;
        const city = e.features[0].properties.FIELD5;
        const target = e.features[0].properties.FIELD9;

        new mapboxgl.Popup()
            .setLngLat(coordinates)
            .setHTML(`City: ${city }<br />Target Type: ${ target }<br />Number of Casualties:
               ${ nkills }<br />${ description}`)
            .addTo(map);
      });
    // Change the cursor to a pointer when the mouse is over the places layer.
      map.on('mouseenter', 'terrorism', function mouseOn() {
        map.getCanvas().style.cursor = 'pointer';
      });

    // Change it back to a pointer when it leaves.
      map.on('mouseleave', 'terrorism', function mouseOff() {
        map.getCanvas().style.cursor = '';
      });
    });
    const layers = ['Facility/Infrastructure Attack', 'Armed Assault', 'Bombing/Explosion',
      'Hijacking', 'Other'];
    const colors = ['#fbb03b', '#223b53', '#e55e5e', '#3bb2d0', '#ccc'];
    function circleSize(casualty) {
      const radius = 7 * (0.5 + Math.log(casualty + 2));
      const diameter = radius * 2;
      return diameter;
    }
    layers.forEach((d, i) => {
      const layer = layers[i];
      const color = colors[i];
      const item = document.createElement('div');
      const key = document.createElement('span');
      key.className = 'legend-key';
      key.style.backgroundColor = color;

      const value = document.createElement('span');
      value.innerHTML = layer;
      item.appendChild(key);
      item.appendChild(value);
      document.getElementById('legend').appendChild(item);
    });
    const casualties = ['0', '1', '2', '3'];
    casualties.forEach((d, j) => {
      const casualty = parseInt(casualties[j], 10);
      document.getElementById('sizeLeg').insertAdjacentHTML('beforeend', `<div><span style="width:${
     circleSize(casualty) }px;height:${ circleSize(casualty) }px;margin: 0 ${
     [(15 - circleSize(casualty)) / 2] }px"></span><p>${ casualty }</p></div>`);
    });

    document.getElementById('slider').addEventListener('input', function sliderMove(e) {
      const year = e.target.value;
    // update the map
      map.setFilter('terrorism', ['==', ['string', ['get', 'FIELD2']], year]);
    // update text in the UI
      document.getElementById('active-year').innerText = year;
    });
  }
  render() {
    return <div id="map" />;
  }
}
export default MapComponent;
