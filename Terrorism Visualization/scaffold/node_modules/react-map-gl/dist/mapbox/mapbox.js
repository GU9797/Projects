'use strict';

Object.defineProperty(exports, "__esModule", {
  value: true
});

var _assign = require('babel-runtime/core-js/object/assign');

var _assign2 = _interopRequireDefault(_assign);

var _classCallCheck2 = require('babel-runtime/helpers/classCallCheck');

var _classCallCheck3 = _interopRequireDefault(_classCallCheck2);

var _createClass2 = require('babel-runtime/helpers/createClass');

var _createClass3 = _interopRequireDefault(_createClass2);

var _typeof2 = require('babel-runtime/helpers/typeof');

var _typeof3 = _interopRequireDefault(_typeof2);

exports.getAccessToken = getAccessToken;

var _propTypes = require('prop-types');

var _propTypes2 = _interopRequireDefault(_propTypes);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

var isBrowser = !((typeof process === 'undefined' ? 'undefined' : (0, _typeof3.default)(process)) === 'object' && String(process) === '[object process]' && !process.browser); // Copyright (c) 2015 Uber Technologies, Inc.

// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:

// The above copyright notice and this permission notice shall be included in
// all copies or substantial portions of the Software.

// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
// THE SOFTWARE.

/* global window, document, process */


var mapboxgl = isBrowser ? require('mapbox-gl') : null;

function noop() {}

var propTypes = {
  // Creation parameters
  container: _propTypes2.default.object, /** The container to have the map. */
  mapboxApiAccessToken: _propTypes2.default.string, /** Mapbox API access token for Mapbox tiles/styles. */
  attributionControl: _propTypes2.default.bool, /** Show attribution control or not. */
  preserveDrawingBuffer: _propTypes2.default.bool, /** Useful when you want to export the canvas as a PNG. */
  onLoad: _propTypes2.default.func, /** The onLoad callback for the map */
  onError: _propTypes2.default.func, /** The onError callback for the map */
  reuseMaps: _propTypes2.default.bool,
  transformRequest: _propTypes2.default.func, /** The transformRequest callback for the map */

  mapStyle: _propTypes2.default.string, /** The Mapbox style. A string url to a MapboxGL style */
  visible: _propTypes2.default.bool, /** Whether the map is visible */

  // Map view state
  width: _propTypes2.default.number.isRequired, /** The width of the map. */
  height: _propTypes2.default.number.isRequired, /** The height of the map. */
  longitude: _propTypes2.default.number.isRequired, /** The longitude of the center of the map. */
  latitude: _propTypes2.default.number.isRequired, /** The latitude of the center of the map. */
  zoom: _propTypes2.default.number.isRequired, /** The tile zoom level of the map. */
  bearing: _propTypes2.default.number, /** Specify the bearing of the viewport */
  pitch: _propTypes2.default.number, /** Specify the pitch of the viewport */

  // Note: Non-public API, see https://github.com/mapbox/mapbox-gl-js/issues/1137
  altitude: _propTypes2.default.number /** Altitude of the viewport camera. Default 1.5 "screen heights" */
};

var defaultProps = {
  mapboxApiAccessToken: getAccessToken(),
  preserveDrawingBuffer: false,
  attributionControl: true,
  preventStyleDiffing: false,
  onLoad: noop,
  onError: noop,
  reuseMaps: false,
  transformRequest: null,

  mapStyle: 'mapbox://styles/mapbox/light-v8',
  visible: true,

  bearing: 0,
  pitch: 0,
  altitude: 1.5
};

// Try to get access token from URL, env, local storage or config
function getAccessToken() {
  var accessToken = null;

  if (typeof window !== 'undefined' && window.location) {
    var match = window.location.search.match(/access_token=([^&\/]*)/);
    accessToken = match && match[1];
  }

  if (!accessToken && typeof process !== 'undefined') {
    // Note: This depends on bundler plugins (e.g. webpack) inmporting environment correctly
    accessToken = accessToken || process.env.MapboxAccessToken; // eslint-disable-line
  }

  return accessToken || null;
}

// Helper function to merge defaultProps and check prop types
function checkPropTypes(props) {
  var component = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : 'component';

  // TODO - check for production (unless done by prop types package?)
  if (props.debug) {
    _propTypes2.default.checkPropTypes(propTypes, props, 'prop', component);
  }
}

// A small wrapper class for mapbox-gl
// - Provides a prop style interface (that can be trivially used by a React wrapper)
// - Makes sure mapbox doesn't crash under Node
// - Handles map reuse (to work around Mapbox resource leak issues)
// - Provides support for specifying tokens during development

var Mapbox = function () {
  (0, _createClass3.default)(Mapbox, null, [{
    key: 'supported',
    value: function supported() {
      return mapboxgl && mapboxgl.supported();
    }
  }]);

  function Mapbox(props) {
    (0, _classCallCheck3.default)(this, Mapbox);

    if (!mapboxgl) {
      throw new Error('Mapbox not supported');
    }

    if (!Mapbox.initialized && console.debug) {
      // eslint-disable-line
      Mapbox.initialized = true;
      console.debug('react-map-gl: using mapbox-gl v' + mapboxgl.version); // eslint-disable-line
    }

    this.props = {};
    this._initialize(props);
  }

  (0, _createClass3.default)(Mapbox, [{
    key: 'finalize',
    value: function finalize() {
      if (!mapboxgl || !this._map) {
        return this;
      }

      this._destroy();
      return this;
    }
  }, {
    key: 'setProps',
    value: function setProps(props) {
      if (!mapboxgl || !this._map) {
        return this;
      }

      this._update(this.props, props);
      return this;
    }

    // Mapbox's map.resize() reads size from DOM, so DOM element must already be resized
    // In a system like React we must wait to read size until after render
    // (e.g. until "componentDidUpdate")

  }, {
    key: 'resize',
    value: function resize() {
      if (!mapboxgl || !this._map) {
        return this;
      }

      this._map.resize();
      return this;
    }

    // External apps can access map this way

  }, {
    key: 'getMap',
    value: function getMap() {
      return this._map;
    }

    // PRIVATE API

  }, {
    key: '_create',
    value: function _create(props) {
      // Reuse a saved map, if available
      if (props.reuseMaps && Mapbox.savedMap) {
        this._map = this.map = Mapbox.savedMap;
        // When reusing the saved map, we need to reparent the map(canvas) and other child nodes
        // intoto the new container from the props.
        // Step1: reparenting child nodes from old container to new container
        var oldContainer = this._map.getContainer();
        var newContainer = props.container;
        newContainer.classList.add('mapboxgl-map');
        while (oldContainer.childNodes.length > 0) {
          newContainer.appendChild(oldContainer.childNodes[0]);
        }
        // Step2: replace the internal container with new container from the react component
        this._map._container = newContainer;
        Mapbox.savedMap = null;
        // TODO - need to call onload again, need to track with Promise?
        props.onLoad();
      } else {
        var mapOptions = {
          container: props.container || document.body,
          center: [props.longitude, props.latitude],
          zoom: props.zoom,
          pitch: props.pitch,
          bearing: props.bearing,
          style: props.mapStyle,
          interactive: false,
          attributionControl: props.attributionControl,
          preserveDrawingBuffer: props.preserveDrawingBuffer
        };
        // We don't want to pass a null or no-op transformRequest function.
        if (props.transformRequest) {
          mapOptions.transformRequest = props.transformRequest;
        }
        this._map = this.map = new mapboxgl.Map(mapOptions);
        // Attach optional onLoad function
        this.map.once('load', props.onLoad);
        this.map.on('error', props.onError);
      }

      return this;
    }
  }, {
    key: '_destroy',
    value: function _destroy() {
      if (!Mapbox.savedMap) {
        Mapbox.savedMap = this._map;
      } else {
        this._map.remove();
      }
    }
  }, {
    key: '_initialize',
    value: function _initialize(props) {
      props = (0, _assign2.default)({}, defaultProps, props);
      checkPropTypes(props, 'Mapbox');

      // Make empty string pick up default prop
      this.accessToken = props.mapboxApiAccessToken || defaultProps.mapboxApiAccessToken;

      // Creation only props
      if (mapboxgl) {
        if (!this.accessToken) {
          mapboxgl.accessToken = 'no-token'; // Prevents mapbox from throwing
        } else {
          mapboxgl.accessToken = this.accessToken;
        }
      }

      this._create(props);

      // Disable outline style
      var canvas = this.map.getCanvas();
      if (canvas) {
        canvas.style.outline = 'none';
      }

      this._updateMapViewport({}, props);
      this._updateMapSize({}, props);

      this.props = props;
    }
  }, {
    key: '_update',
    value: function _update(oldProps, newProps) {
      newProps = (0, _assign2.default)({}, this.props, newProps);
      checkPropTypes(newProps, 'Mapbox');

      this._updateMapViewport(oldProps, newProps);
      this._updateMapSize(oldProps, newProps);

      this.props = newProps;
    }
  }, {
    key: '_updateMapViewport',
    value: function _updateMapViewport(oldProps, newProps) {
      var viewportChanged = newProps.latitude !== oldProps.latitude || newProps.longitude !== oldProps.longitude || newProps.zoom !== oldProps.zoom || newProps.pitch !== oldProps.pitch || newProps.bearing !== oldProps.bearing || newProps.altitude !== oldProps.altitude;

      if (viewportChanged) {
        this._map.jumpTo({
          center: [newProps.longitude, newProps.latitude],
          zoom: newProps.zoom,
          bearing: newProps.bearing,
          pitch: newProps.pitch
        });

        // TODO - jumpTo doesn't handle altitude
        if (newProps.altitude !== oldProps.altitude) {
          this._map.transform.altitude = newProps.altitude;
        }
      }
    }

    // Note: needs to be called after render (e.g. in componentDidUpdate)

  }, {
    key: '_updateMapSize',
    value: function _updateMapSize(oldProps, newProps) {
      var sizeChanged = oldProps.width !== newProps.width || oldProps.height !== newProps.height;
      if (sizeChanged) {
        this._map.resize();
      }
    }
  }]);
  return Mapbox;
}();

exports.default = Mapbox;


Mapbox.propTypes = propTypes;
Mapbox.defaultProps = defaultProps;
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJzb3VyY2VzIjpbIi4uLy4uL3NyYy9tYXBib3gvbWFwYm94LmpzIl0sIm5hbWVzIjpbImdldEFjY2Vzc1Rva2VuIiwiaXNCcm93c2VyIiwicHJvY2VzcyIsIlN0cmluZyIsImJyb3dzZXIiLCJtYXBib3hnbCIsInJlcXVpcmUiLCJub29wIiwicHJvcFR5cGVzIiwiY29udGFpbmVyIiwib2JqZWN0IiwibWFwYm94QXBpQWNjZXNzVG9rZW4iLCJzdHJpbmciLCJhdHRyaWJ1dGlvbkNvbnRyb2wiLCJib29sIiwicHJlc2VydmVEcmF3aW5nQnVmZmVyIiwib25Mb2FkIiwiZnVuYyIsIm9uRXJyb3IiLCJyZXVzZU1hcHMiLCJ0cmFuc2Zvcm1SZXF1ZXN0IiwibWFwU3R5bGUiLCJ2aXNpYmxlIiwid2lkdGgiLCJudW1iZXIiLCJpc1JlcXVpcmVkIiwiaGVpZ2h0IiwibG9uZ2l0dWRlIiwibGF0aXR1ZGUiLCJ6b29tIiwiYmVhcmluZyIsInBpdGNoIiwiYWx0aXR1ZGUiLCJkZWZhdWx0UHJvcHMiLCJwcmV2ZW50U3R5bGVEaWZmaW5nIiwiYWNjZXNzVG9rZW4iLCJ3aW5kb3ciLCJsb2NhdGlvbiIsIm1hdGNoIiwic2VhcmNoIiwiZW52IiwiTWFwYm94QWNjZXNzVG9rZW4iLCJjaGVja1Byb3BUeXBlcyIsInByb3BzIiwiY29tcG9uZW50IiwiZGVidWciLCJNYXBib3giLCJzdXBwb3J0ZWQiLCJFcnJvciIsImluaXRpYWxpemVkIiwiY29uc29sZSIsInZlcnNpb24iLCJfaW5pdGlhbGl6ZSIsIl9tYXAiLCJfZGVzdHJveSIsIl91cGRhdGUiLCJyZXNpemUiLCJzYXZlZE1hcCIsIm1hcCIsIm9sZENvbnRhaW5lciIsImdldENvbnRhaW5lciIsIm5ld0NvbnRhaW5lciIsImNsYXNzTGlzdCIsImFkZCIsImNoaWxkTm9kZXMiLCJsZW5ndGgiLCJhcHBlbmRDaGlsZCIsIl9jb250YWluZXIiLCJtYXBPcHRpb25zIiwiZG9jdW1lbnQiLCJib2R5IiwiY2VudGVyIiwic3R5bGUiLCJpbnRlcmFjdGl2ZSIsIk1hcCIsIm9uY2UiLCJvbiIsInJlbW92ZSIsIl9jcmVhdGUiLCJjYW52YXMiLCJnZXRDYW52YXMiLCJvdXRsaW5lIiwiX3VwZGF0ZU1hcFZpZXdwb3J0IiwiX3VwZGF0ZU1hcFNpemUiLCJvbGRQcm9wcyIsIm5ld1Byb3BzIiwidmlld3BvcnRDaGFuZ2VkIiwianVtcFRvIiwidHJhbnNmb3JtIiwic2l6ZUNoYW5nZWQiXSwibWFwcGluZ3MiOiI7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7UUErRWdCQSxjLEdBQUFBLGM7O0FBMURoQjs7Ozs7O0FBRUEsSUFBTUMsWUFBWSxFQUNoQixRQUFPQyxPQUFQLHVEQUFPQSxPQUFQLE9BQW1CLFFBQW5CLElBQ0FDLE9BQU9ELE9BQVAsTUFBb0Isa0JBRHBCLElBRUEsQ0FBQ0EsUUFBUUUsT0FITyxDQUFsQixDLENBdkJBOztBQUVBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTs7QUFFQTtBQUNBOztBQUVBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBOztBQUVBOzs7QUFTQSxJQUFNQyxXQUFXSixZQUFZSyxRQUFRLFdBQVIsQ0FBWixHQUFtQyxJQUFwRDs7QUFFQSxTQUFTQyxJQUFULEdBQWdCLENBQUU7O0FBRWxCLElBQU1DLFlBQVk7QUFDaEI7QUFDQUMsYUFBVyxvQkFBVUMsTUFGTCxFQUVhO0FBQzdCQyx3QkFBc0Isb0JBQVVDLE1BSGhCLEVBR3dCO0FBQ3hDQyxzQkFBb0Isb0JBQVVDLElBSmQsRUFJb0I7QUFDcENDLHlCQUF1QixvQkFBVUQsSUFMakIsRUFLdUI7QUFDdkNFLFVBQVEsb0JBQVVDLElBTkYsRUFNUTtBQUN4QkMsV0FBUyxvQkFBVUQsSUFQSCxFQU9TO0FBQ3pCRSxhQUFXLG9CQUFVTCxJQVJMO0FBU2hCTSxvQkFBa0Isb0JBQVVILElBVFosRUFTa0I7O0FBRWxDSSxZQUFVLG9CQUFVVCxNQVhKLEVBV1k7QUFDNUJVLFdBQVMsb0JBQVVSLElBWkgsRUFZUzs7QUFFekI7QUFDQVMsU0FBTyxvQkFBVUMsTUFBVixDQUFpQkMs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dkQsT0FISDtBQUlmQyxpQkFBT3NELFNBQVN0RDtBQUpELFNBQWpCOztBQU9BO0FBQ0EsWUFBSXNELFNBQVNyRCxRQUFULEtBQXNCb0QsU0FBU3BELFFBQW5DLEVBQTZDO0FBQzNDLGVBQUtxQixJQUFMLENBQVVtQyxTQUFWLENBQW9CeEQsUUFBcEIsR0FBK0JxRCxTQUFTckQsUUFBeEM7QUFDRDtBQUNGO0FBQ0Y7O0FBRUQ7Ozs7bUNBQ2VvRCxRLEVBQVVDLFEsRUFBVTtBQUNqQyxVQUFNSSxjQUFjTCxTQUFTN0QsS0FBVCxLQUFtQjhELFNBQVM5RCxLQUE1QixJQUFxQzZELFNBQVMxRCxNQUFULEtBQW9CMkQsU0FBUzNELE1BQXRGO0FBQ0EsVUFBSStELFdBQUosRUFBaUI7QUFDZixhQUFLcEMsSUFBTCxDQUFVRyxNQUFWO0FBQ0Q7QUFDRjs7Ozs7a0JBakxrQlYsTTs7O0FBb0xyQkEsT0FBT3RDLFNBQVAsR0FBbUJBLFNBQW5CO0FBQ0FzQyxPQUFPYixZQUFQLEdBQXNCQSxZQUF0QiIsImZpbGUiOiJtYXBib3guanMiLCJzb3VyY2VzQ29udGVudCI6WyIvLyBDb3B5cmlnaHQgKGMpIDIwMTUgVWJlciBUZWNobm9sb2dpZXMsIEluYy5cblxuLy8gUGVybWlzc2lvbiBpcyBoZXJlYnkgZ3JhbnRlZCwgZnJlZSBvZiBjaGFyZ2UsIHRvIGFueSBwZXJzb24gb2J0YWluaW5nIGEgY29weVxuLy8gb2YgdGhpcyBzb2Z0d2FyZSBhbmQgYXNzb2NpYXRlZCBkb2N1bWVudGF0aW9uIGZpbGVzICh0aGUgXCJTb2Z0d2FyZVwiKSwgdG8gZGVhbFxuLy8gaW4gdGhlIFNvZnR3YXJlIHdpdGhvdXQgcmVzdHJpY3Rpb24sIGluY2x1ZGluZyB3aXRob3V0IGxpbWl0YXRpb24gdGhlIHJpZ2h0c1xuLy8gdG8gdXNlLCBjb3B5LCBtb2RpZnksIG1lcmdlLCBwdWJsaXNoLCBkaXN0cmlidXRlLCBzdWJsaWNlbnNlLCBhbmQvb3Igc2VsbFxuLy8gY29waWVzIG9mIHRoZSBTb2Z0d2FyZSwgYW5kIHRvIHBlcm1pdCBwZXJzb25zIHRvIHdob20gdGhlIFNvZnR3YXJlIGlzXG4vLyBmdXJuaXNoZWQgdG8gZG8gc28sIHN1YmplY3QgdG8gdGhlIGZvbGxvd2luZyBjb25kaXRpb25zOlxuXG4vLyBUaGUgYWJvdmUgY29weXJpZ2h0IG5vdGljZSBhbmQgdGhpcyBwZXJtaXNzaW9uIG5vdGljZSBzaGFsbCBiZSBpbmNsdWRlZCBpblxuLy8gYWxsIGNvcGllcyBvciBzdWJzdGFudGlhbCBwb3J0aW9ucyBvZiB0aGUgU29mdHdhcmUuXG5cbi8vIFRIRSBTT0ZUV0FSRSBJUyBQUk9WSURFRCBcIkFTIElTXCIsIFdJVEhPVVQgV0FSUkFOVFkgT0YgQU5ZIEtJTkQsIEVYUFJFU1MgT1Jcbi8vIElNUExJRUQsIElOQ0xVRElORyBCVVQgTk9UIExJTUlURUQgVE8gVEhFIFdBUlJBTlRJRVMgT0YgTUVSQ0hBTlRBQklMSVRZLFxuLy8gRklUTkVTUyBGT1IgQSBQQVJUSUNVTEFSIFBVUlBPU0UgQU5EIE5PTklORlJJTkdFTUVOVC4gSU4gTk8gRVZFTlQgU0hBTEwgVEhFXG4vLyBBVVRIT1JTIE9SIENPUFlSSUdIVCBIT0xERVJTIEJFIExJQUJMRSBGT1IgQU5ZIENMQUlNLCBEQU1BR0VTIE9SIE9USEVSXG4vLyBMSUFCSUxJVFksIFdIRVRIRVIgSU4gQU4gQUNUSU9OIE9GIENPTlRSQUNULCBUT1JUIE9SIE9USEVSV0lTRSwgQVJJU0lORyBGUk9NLFxuLy8gT1VUIE9GIE9SIElOIENPTk5FQ1RJT04gV0lUSCBUSEUgU09GVFdBUkUgT1IgVEhFIFVTRSBPUiBPVEhFUiBERUFMSU5HUyBJTlxuLy8gVEhFIFNPRlRXQVJFLlxuXG4vKiBnbG9iYWwgd2luZG93LCBkb2N1bWVudCwgcHJvY2VzcyAqL1xuaW1wb3J0IFByb3BUeXBlcyBmcm9tICdwcm9wLXR5cGVzJztcblxuY29uc3QgaXNCcm93c2VyID0gIShcbiAgdHlwZW9mIHByb2Nlc3MgPT09ICdvYmplY3QnICYmXG4gIFN0cmluZyhwcm9jZXNzKSA9PT0gJ1tvYmplY3QgcHJvY2Vzc10nICYmXG4gICFwcm9jZXNzLmJyb3dzZXJcbik7XG5cbmNvbnN0IG1hcGJveGdsID0gaXNCcm93c2VyID8gcmVxdWlyZSgnbWFwYm94LWdsJykgOiBudWxsO1xuXG5mdW5jdGlvbiBub29wKCkge31cblxuY29uc3QgcHJvcFR5cGVzID0ge1xuICAvLyBDcmVhdGlvbiBwYXJhbWV0ZXJzXG4gIGNvbnRhaW5lcjogUHJvcFR5cGVzLm9iamVjdCwgLyoqIFRoZSBjb250YWluZXIgdG8gaGF2ZSB0aGUgbWFwLiAqL1xuICBtYXBib3hBcGlBY2Nlc3NUb2tlbjogUHJvcFR5cGVzLnN0cmluZywgLyoqIE1hcGJveCBBUEkgYWNjZXNzIHRva2VuIGZvciBNYXBib3ggdGlsZXMvc3R5bGVzLiAqL1xuICBhdHRyaWJ1dGlvbkNvbnRyb2w6IFByb3BUeXBlcy5ib29sLCAvKiogU2hvdyBhdHRyaWJ1dGlvbiBjb250cm9sIG9yIG5vdC4gKi9cbiAgcHJlc2VydmVEcmF3aW5nQnVmZmVyOiBQcm9wVHlwZXMuYm9vbCwgLyoqIFVzZWZ1bCB3aGVuIHlvdSB3YW50IHRvIGV4cG9ydCB0aGUgY2FudmFzIGFzIGEgUE5HLiAqL1xuICBvbkxvYWQ6IFByb3BUeXBlcy5mdW5jLCAvKiogVGhlIG9uTG9hZCBjYWxsYmFjayBmb3IgdGhlIG1hcCAqL1xuICBvbkVycm9yOiBQcm9wVHlwZXMuZnVuYywgLyoqIFRoZSBvbkVycm9yIGNhbGxiYWNrIGZvciB0aGUgbWFwICovXG4gIHJldXNlTWFwczogUHJvcFR5cGVzLmJvb2wsXG4gIHRyYW5zZm9ybVJlcXVlc3Q6IFByb3BUeXBlcy5mdW5jLCAvKiogVGhlIHRyYW5zZm9ybVJlcXVlc3QgY2FsbGJhY2sgZm9yIHRoZSBtYXAgKi9cblxuICBtYXBTdHlsZTogUHJvcFR5cGVzLnN0cmluZywgLyoqIFRoZSBNYXBib3ggc3R5bGUuIEEgc3RyaW5nIHVybCB0byBhIE1hcGJveEdMIHN0eWxlICovXG4gIHZpc2libGU6IFByb3BUeXBlcy5ib29sLCAvKiogV2hldGhlciB0aGUgbWFwIGlzIHZpc2libGUgKi9cblxuICAvLyBNYXAgdmlldyBzdGF0ZVxuICB3aWR0aDogUHJvcFR5cGVzLm51bWJlci5pc1JlcXVpcmVkLCAvKiogVGhlIHdpZHRoIG9mIHRoZSBtYXAuICovXG4gIGhlaWdodDogUHJvcFR5cGVzLm51bWJlci5pc1JlcXVpcmVkLCAvKiogVGhlIGhlaWdodCBvZiB0aGUgbWFwLiAqL1xuICBsb25naXR1ZGU6IFByb3BUeXBlcy5udW1iZXIuaXNSZXF1aXJlZCwgLyoqIFRoZSBsb25naXR1ZGUgb2YgdGhlIGNlbnRlciBvZiB0aGUgbWFwLiAqL1xuICBsYXRpdHVkZTogUHJvcFR5cGVzLm51bWJlci5pc1JlcXVpcmVkLCAvKiogVGhlIGxhdGl0dWRlIG9mIHRoZSBjZW50ZXIgb2YgdGhlIG1hcC4gKi9cbiAgem9vbTogUHJvcFR5cGVzLm51bWJlci5pc1JlcXVpcmVkLCAvKiogVGhlIHRpbGUgem9vbSBsZXZlbCBvZiB0aGUgbWFwLiAqL1xuICBiZWFyaW5nOiBQcm9wVHlwZXMubnVtYmVyLCAvKiogU3BlY2lmeSB0aGUgYmVhcmluZyBvZiB0aGUgdmlld3BvcnQgKi9cbiAgcGl0Y2g6IFByb3BUeXBlcy5udW1iZXIsIC8qKiBTcGVjaWZ5IHRoZSBwaXRjaCBvZiB0aGUgdmlld3BvcnQgKi9cblxuICAvLyBOb3RlOiBOb24tcHVibGljIEFQSSwgc2VlIGh0dHBzOi8vZ2l0aHViLmNvbS9tYXBib3gvbWFwYm94LWdsLWpzL2lzc3Vlcy8xMTM3XG4gIGFsdGl0dWRlOiBQcm9wVHlwZXMubnVtYmVyIC8qKiBBbHRpdHVkZSBvZiB0aGUgdmlld3BvcnQgY2FtZXJhLiBEZWZhdWx0IDEuNSBcInNjcmVlbiBoZWlnaHRzXCIgKi9cbn07XG5cbmNvbnN0IGRlZmF1bHRQcm9wcyA9IHtcbiAgbWFwYm94QXBpQWNjZXNzVG9rZW46IGdldEFjY2Vzc1Rva2VuKCksXG4gIHByZXNlcnZlRHJhd2luZ0J1ZmZlcjogZmFsc2UsXG4gIGF0dHJpYnV0aW9uQ29udHJvbDogdHJ1ZSxcbiAgcHJldmVudFN0eWxlRGlmZmluZzogZmFsc2UsXG4gIG9uTG9hZDogbm9vcCxcbiAgb25FcnJvcjogbm9vcCxcbiAgcmV1c2VNYXBzOiBmYWxzZSxcbiAgdHJhbnNmb3JtUmVxdWVzdDogbnVsbCxcblxuICBtYXBTdHlsZTogJ21hcGJveDovL3N0eWxlcy9tYXBib3gvbGlnaHQtdjgnLFxuICB2aXNpYmxlOiB0cnVlLFxuXG4gIGJlYXJpbmc6IDAsXG4gIHBpdGNoOiAwLFxuICBhbHRpdHVkZTogMS41XG59O1xuXG4vLyBUcnkgdG8gZ2V0IGFjY2VzcyB0b2tlbiBmcm9tIFVSTCwgZW52LCBsb2NhbCBzdG9yYWdlIG9yIGNvbmZpZ1xuZXhwb3J0IGZ1bmN0aW9uIGdldEFjY2Vzc1Rva2VuKCkge1xuICBsZXQgYWNjZXNzVG9rZW4gPSBudWxsO1xuXG4gIGlmICh0eXBlb2Ygd2luZG93ICE9PSAndW5kZWZpbmVkJyAmJiB3aW5kb3cubG9jYXRpb24pIHtcbiAgICBjb25zdCBtYXRjaCA9IHdpbmRvdy5sb2NhdGlvbi5zZWFyY2gubWF0Y2goL2FjY2Vzc190b2tlbj0oW14mXFwvXSopLyk7XG4gICAgYWNjZXNzVG9rZW4gPSBtYXRjaCAmJiBtYXRjaFsxXTtcbiAgfVxuXG4gIGlmICghYWNjZXNzVG9rZW4gJiYgdHlwZW9mIHByb2Nlc3MgIT09ICd1bmRlZmluZWQnKSB7XG4gICAgLy8gTm90ZTogVGhpcyBkZXBlbmRzIG9uIGJ1bmRsZXIgcGx1Z2lucyAoZS5nLiB3ZWJwYWNrKSBpbm1wb3J0aW5nIGVudmlyb25tZW50IGNvcnJlY3RseVxuICAgIGFjY2Vzc1Rva2VuID0gYWNjZXNzVG9rZW4gfHwgcHJvY2Vzcy5lbnYuTWFwYm94QWNjZXNzVG9rZW47IC8vIGVzbGludC1kaXNhYmxlLWxpbmVcbiAgfVxuXG4gIHJldHVybiBhY2Nlc3NUb2tlbiB8fCBudWxsO1xufVxuXG4vLyBIZWxwZXIgZnVuY3Rpb24gdG8gbWVyZ2UgZGVmYXVsdFByb3BzIGFuZCBjaGVjayBwcm9wIHR5cGVzXG5mdW5jdGlvbiBjaGVja1Byb3BUeXBlcyhwcm9wcywgY29tcG9uZW50ID0gJ2NvbXBvbmVudCcpIHtcbiAgLy8gVE9ETyAtIGNoZWNrIGZvciBwcm9kdWN0aW9uICh1bmxlc3MgZG9uZSBieSBwcm9wIHR5cGVzIHBhY2thZ2U/KVxuICBpZiAocHJvcHMuZGVidWcpIHtcbiAgICBQcm9wVHlwZXMuY2hlY2tQcm9wVHlwZXMocHJvcFR5cGVzLCBwcm9wcywgJ3Byb3AnLCBjb21wb25lbnQpO1xuICB9XG59XG5cbi8vIEEgc21hbGwgd3JhcHBlciBjbGFzcyBmb3IgbWFwYm94LWdsXG4vLyAtIFByb3ZpZGVzIGEgcHJvcCBzdHlsZSBpbnRlcmZhY2UgKHRoYXQgY2FuIGJlIHRyaXZpYWxseSB1c2VkIGJ5IGEgUmVhY3Qgd3JhcHBlcilcbi8vIC0gTWFrZXMgc3VyZSBtYXBib3ggZG9lc24ndCBjcmFzaCB1bmRlciBOb2RlXG4vLyAtIEhhbmRsZXMgbWFwIHJldXNlICh0byB3b3JrIGFyb3VuZCBNYXBib3ggcmVzb3VyY2UgbGVhayBpc3N1ZXMpXG4vLyAtIFByb3ZpZGVzIHN1cHBvcnQgZm9yIHNwZWNpZnlpbmcgdG9rZW5zIGR1cmluZyBkZXZlbG9wbWVudFxuXG5leHBvcnQgZGVmYXVsdCBjbGFzcyBNYXBib3gge1xuICBzdGF0aWMgc3VwcG9ydGVkKCkge1xuICAgIHJldHVybiBtYXBib3hnbCAmJiBtYXBib3hnbC5zdXBwb3J0ZWQoKTtcbiAgfVxuXG4gIGNvbnN0cnVjdG9yKHByb3BzKSB7XG4gICAgaWYgKCFtYXBib3hnbCkge1xuICAgICAgdGhyb3cgbmV3IEVycm9yKCdNYXBib3ggbm90IHN1cHBvcnRlZCcpO1xuICAgIH1cblxuICAgIGlmICghTWFwYm94LmluaXRpYWxpemVkICYmIGNvbnNvbGUuZGVidWcpIHsgLy8gZXNsaW50LWRpc2FibGUtbGluZVxuICAgICAgTWFwYm94LmluaXRpYWxpemVkID0gdHJ1ZTtcbiAgICAgIGNvbnNvbGUuZGVidWcoYHJlYWN0LW1hcC1nbDogdXNpbmcgbWFwYm94LWdsIHYke21hcGJveGdsLnZlcnNpb259YCk7IC8vIGVzbGludC1kaXNhYmxlLWxpbmVcbiAgICB9XG5cbiAgICB0aGlzLnByb3BzID0ge307XG4gICAgdGhpcy5faW5pdGlhbGl6ZShwcm9wcyk7XG4gIH1cblxuICBmaW5hbGl6ZSgpIHtcbiAgICBpZiAoIW1hcGJveGdsIHx8ICF0aGlzLl9tYXApIHtcbiAgICAgIHJldHVybiB0aGlzO1xuICAgIH1cblxuICAgIHRoaXMuX2Rlc3Ryb3koKTtcbiAgICByZXR1cm4gdGhpcztcbiAgfVxuXG4gIHNldFByb3BzKHByb3BzKSB7XG4gICAgaWYgKCFtYXBib3hnbCB8fCAhdGhpcy5fbWFwKSB7XG4gICAgICByZXR1cm4gdGhpcztcbiAgICB9XG5cbiAgICB0aGlzLl91cGRhdGUodGhpcy5wcm9wcywgcHJvcHMpO1xuICAgIHJldHVybiB0aGlzO1xuICB9XG5cbiAgLy8gTWFwYm94J3MgbWFwLnJlc2l6ZSgpIHJlYWRzIHNpemUgZnJvbSBET00sIHNvIERPTSBlbGVtZW50IG11c3QgYWxyZWFkeSBiZSByZXNpemVkXG4gIC8vIEluIGEgc3lzdGVtIGxpa2UgUmVhY3Qgd2UgbXVzdCB3YWl0IHRvIHJlYWQgc2l6ZSB1bnRpbCBhZnRlciByZW5kZXJcbiAgLy8gKGUuZy4gdW50aWwgXCJjb21wb25lbnREaWRVcGRhdGVcIilcbiAgcmVzaXplKCkge1xuICAgIGlmICghbWFwYm94Z2wgfHwgIXRoaXMuX21hcCkge1xuICAgICAgcmV0dXJuIHRoaXM7XG4gICAgfVxuXG4gICAgdGhpcy5fbWFwLnJlc2l6ZSgpO1xuICAgIHJldHVybiB0aGlzO1xuICB9XG5cbiAgLy8gRXh0ZXJuYWwgYXBwcyBjYW4gYWNjZXNzIG1hcCB0aGlzIHdheVxuICBnZXRNYXAoKSB7XG4gICAgcmV0dXJuIHRoaXMuX21hcDtcbiAgfVxuXG4gIC8vIFBSSVZBVEUgQVBJXG5cbiAgX2NyZWF0ZShwcm9wcykge1xuICAgIC8vIFJldXNlIGEgc2F2ZWQgbWFwLCBpZiBhdmFpbGFibGVcbiAgICBpZiAocHJvcHMucmV1c2VNYXBzICYmIE1hcGJveC5zYXZlZE1hcCkge1xuICAgICAgdGhpcy5fbWFwID0gdGhpcy5tYXAgPSBNYXBib3guc2F2ZWRNYXA7XG4gICAgICAvLyBXaGVuIHJldXNpbmcgdGhlIHNhdmVkIG1hcCwgd2UgbmVlZCB0byByZXBhcmVudCB0aGUgbWFwKGNhbnZhcykgYW5kIG90aGVyIGNoaWxkIG5vZGVzXG4gICAgICAvLyBpbnRvdG8gdGhlIG5ldyBjb250YWluZXIgZnJvbSB0aGUgcHJvcHMuXG4gICAgICAvLyBTdGVwMTogcmVwYXJlbnRpbmcgY2hpbGQgbm9kZXMgZnJvbSBvbGQgY29udGFpbmVyIHRvIG5ldyBjb250YWluZXJcbiAgICAgIGNvbnN0IG9sZENvbnRhaW5lciA9IHRoaXMuX21hcC5nZXRDb250YWluZXIoKTtcbiAgICAgIGNvbnN0IG5ld0NvbnRhaW5lciA9IHByb3BzLmNvbnRhaW5lcjtcbiAgICAgIG5ld0NvbnRhaW5lci5jbGFzc0xpc3QuYWRkKCdtYXBib3hnbC1tYXAnKTtcbiAgICAgIHdoaWxlIChvbGRDb250YWluZXIuY2hpbGROb2Rlcy5sZW5ndGggPiAwKSB7XG4gICAgICAgIG5ld0NvbnRhaW5lci5hcHBlbmRDaGlsZChvbGRDb250YWluZXIuY2hpbGROb2Rlc1swXSk7XG4gICAgICB9XG4gICAgICAvLyBTdGVwMjogcmVwbGFjZSB0aGUgaW50ZXJuYWwgY29udGFpbmVyIHdpdGggbmV3IGNvbnRhaW5lciBmcm9tIHRoZSByZWFjdCBjb21wb25lbnRcbiAgICAgIHRoaXMuX21hcC5fY29udGFpbmVyID0gbmV3Q29udGFpbmVyO1xuICAgICAgTWFwYm94LnNhdmVkTWFwID0gbnVsbDtcbiAgICAgIC8vIFRPRE8gLSBuZWVkIHRvIGNhbGwgb25sb2FkIGFnYWluLCBuZWVkIHRvIHRyYWNrIHdpdGggUHJvbWlzZT9cbiAgICAgIHByb3BzLm9uTG9hZCgpO1xuICAgIH0gZWxzZSB7XG4gICAgICBjb25zdCBtYXBPcHRpb25zID0ge1xuICAgICAgICBjb250YWluZXI6IHByb3BzLmNvbnRhaW5lciB8fCBkb2N1bWVudC5ib2R5LFxuICAgICAgICBjZW50ZXI6IFtwcm9wcy5sb25naXR1ZGUsIHByb3BzLmxhdGl0dWRlXSxcbiAgICAgICAgem9vbTogcHJvcHMuem9vbSxcbiAgICAgICAgcGl0Y2g6IHByb3BzLnBpdGNoLFxuICAgICAgICBiZWFyaW5nOiBwcm9wcy5iZWFyaW5nLFxuICAgICAgICBzdHlsZTogcHJvcHMubWFwU3R5bGUsXG4gICAgICAgIGludGVyYWN0aXZlOiBmYWxzZSxcbiAgICAgICAgYXR0cmlidXRpb25Db250cm9sOiBwcm9wcy5hdHRyaWJ1dGlvbkNvbnRyb2wsXG4gICAgICAgIHByZXNlcnZlRHJhd2luZ0J1ZmZlcjogcHJvcHMucHJlc2VydmVEcmF3aW5nQnVmZmVyXG4gICAgICB9O1xuICAgICAgLy8gV2UgZG9uJ3Qgd2FudCB0byBwYXNzIGEgbnVsbCBvciBuby1vcCB0cmFuc2Zvcm1SZXF1ZXN0IGZ1bmN0aW9uLlxuICAgICAgaWYgKHByb3BzLnRyYW5zZm9ybVJlcXVlc3QpIHtcbiAgICAgICAgbWFwT3B0aW9ucy50cmFuc2Zvcm1SZXF1ZXN0ID0gcHJvcHMudHJhbnNmb3JtUmVxdWVzdDtcbiAgICAgIH1cbiAgICAgIHRoaXMuX21hcCA9IHRoaXMubWFwID0gbmV3IG1hcGJveGdsLk1hcChtYXBPcHRpb25zKTtcbiAgICAgIC8vIEF0dGFjaCBvcHRpb25hbCBvbkxvYWQgZnVuY3Rpb25cbiAgICAgIHRoaXMubWFwLm9uY2UoJ2xvYWQnLCBwcm9wcy5vbkxvYWQpO1xuICAgICAgdGhpcy5tYXAub24oJ2Vycm9yJywgcHJvcHMub25FcnJvcik7XG4gICAgfVxuXG4gICAgcmV0dXJuIHRoaXM7XG4gIH1cblxuICBfZGVzdHJveSgpIHtcbiAgICBpZiAoIU1hcGJveC5zYXZlZE1hcCkge1xuICAgICAgTWFwYm94LnNhdmVkTWFwID0gdGhpcy5fbWFwO1xuICAgIH0gZWxzZSB7XG4gICAgICB0aGlzLl9tYXAucmVtb3ZlKCk7XG4gICAgfVxuICB9XG5cbiAgX2luaXRpYWxpemUocHJvcHMpIHtcbiAgICBwcm9wcyA9IE9iamVjdC5hc3NpZ24oe30sIGRlZmF1bHRQcm9wcywgcHJvcHMpO1xuICAgIGNoZWNrUHJvcFR5cGVzKHByb3BzLCAnTWFwYm94Jyk7XG5cbiAgICAvLyBNYWtlIGVtcHR5IHN0cmluZyBwaWNrIHVwIGRlZmF1bHQgcHJvcFxuICAgIHRoaXMuYWNjZXNzVG9rZW4gPSBwcm9wcy5tYXBib3hBcGlBY2Nlc3NUb2tlbiB8fCBkZWZhdWx0UHJvcHMubWFwYm94QXBpQWNjZXNzVG9rZW47XG5cbiAgICAvLyBDcmVhdGlvbiBvbmx5IHByb3BzXG4gICAgaWYgKG1hcGJveGdsKSB7XG4gICAgICBpZiAoIXRoaXMuYWNjZXNzVG9rZW4pIHtcbiAgICAgICAgbWFwYm94Z2wuYWNjZXNzVG9rZW4gPSAnbm8tdG9rZW4nOyAvLyBQcmV2ZW50cyBtYXBib3ggZnJvbSB0aHJvd2luZ1xuICAgICAgfSBlbHNlIHtcbiAgICAgICAgbWFwYm94Z2wuYWNjZXNzVG9rZW4gPSB0aGlzLmFjY2Vzc1Rva2VuO1xuICAgICAgfVxuICAgIH1cblxuICAgIHRoaXMuX2NyZWF0ZShwcm9wcyk7XG5cbiAgICAvLyBEaXNhYmxlIG91dGxpbmUgc3R5bGVcbiAgICBjb25zdCBjYW52YXMgPSB0aGlzLm1hcC5nZXRDYW52YXMoKTtcbiAgICBpZiAoY2FudmFzKSB7XG4gICAgICBjYW52YXMuc3R5bGUub3V0bGluZSA9ICdub25lJztcbiAgICB9XG5cbiAgICB0aGlzLl91cGRhdGVNYXBWaWV3cG9ydCh7fSwgcHJvcHMpO1xuICAgIHRoaXMuX3VwZGF0ZU1hcFNpemUoe30sIHByb3BzKTtcblxuICAgIHRoaXMucHJvcHMgPSBwcm9wcztcbiAgfVxuXG4gIF91cGRhdGUob2xkUHJvcHMsIG5ld1Byb3BzKSB7XG4gICAgbmV3UHJvcHMgPSBPYmplY3QuYXNzaWduKHt9LCB0aGlzLnByb3BzLCBuZXdQcm9wcyk7XG4gICAgY2hlY2tQcm9wVHlwZXMobmV3UHJvcHMsICdNYXBib3gnKTtcblxuICAgIHRoaXMuX3VwZGF0ZU1hcFZpZXdwb3J0KG9sZFByb3BzLCBuZXdQcm9wcyk7XG4gICAgdGhpcy5fdXBkYXRlTWFwU2l6ZShvbGRQcm9wcywgbmV3UHJvcHMpO1xuXG4gICAgdGhpcy5wcm9wcyA9IG5ld1Byb3BzO1xuICB9XG5cbiAgX3VwZGF0ZU1hcFZpZXdwb3J0KG9sZFByb3BzLCBuZXdQcm9wcykge1xuICAgIGNvbnN0IHZpZXdwb3J0Q2hhbmdlZCA9XG4gICAgICBuZXdQcm9wcy5sYXRpdHVkZSAhPT0gb2xkUHJvcHMubGF0aXR1ZGUgfHxcbiAgICAgIG5ld1Byb3BzLmxvbmdpdHVkZSAhPT0gb2xkUHJvcHMubG9uZ2l0dWRlIHx8XG4gICAgICBuZXdQcm9wcy56b29tICE9PSBvbGRQcm9wcy56b29tIHx8XG4gICAgICBuZXdQcm9wcy5waXRjaCAhPT0gb2xkUHJvcHMucGl0Y2ggfHxcbiAgICAgIG5ld1Byb3BzLmJlYXJpbmcgIT09IG9sZFByb3BzLmJlYXJpbmcgfHxcbiAgICAgIG5ld1Byb3BzLmFsdGl0dWRlICE9PSBvbGRQcm9wcy5hbHRpdHVkZTtcblxuICAgIGlmICh2aWV3cG9ydENoYW5nZWQpIHtcbiAgICAgIHRoaXMuX21hcC5qdW1wVG8oe1xuICAgICAgICBjZW50ZXI6IFtuZXdQcm9wcy5sb25naXR1ZGUsIG5ld1Byb3BzLmxhdGl0dWRlXSxcbiAgICAgICAgem9vbTogbmV3UHJvcHMuem9vbSxcbiAgICAgICAgYmVhcmluZzogbmV3UHJvcHMuYmVhcmluZyxcbiAgICAgICAgcGl0Y2g6IG5ld1Byb3BzLnBpdGNoXG4gICAgICB9KTtcblxuICAgICAgLy8gVE9ETyAtIGp1bXBUbyBkb2Vzbid0IGhhbmRsZSBhbHRpdHVkZVxuICAgICAgaWYgKG5ld1Byb3BzLmFsdGl0dWRlICE9PSBvbGRQcm9wcy5hbHRpdHVkZSkge1xuICAgICAgICB0aGlzLl9tYXAudHJhbnNmb3JtLmFsdGl0dWRlID0gbmV3UHJvcHMuYWx0aXR1ZGU7XG4gICAgICB9XG4gICAgfVxuICB9XG5cbiAgLy8gTm90ZTogbmVlZHMgdG8gYmUgY2FsbGVkIGFmdGVyIHJlbmRlciAoZS5nLiBpbiBjb21wb25lbnREaWRVcGRhdGUpXG4gIF91cGRhdGVNYXBTaXplKG9sZFByb3BzLCBuZXdQcm9wcykge1xuICAgIGNvbnN0IHNpemVDaGFuZ2VkID0gb2xkUHJvcHMud2lkdGggIT09IG5ld1Byb3BzLndpZHRoIHx8IG9sZFByb3BzLmhlaWdodCAhPT0gbmV3UHJvcHMuaGVpZ2h0O1xuICAgIGlmIChzaXplQ2hhbmdlZCkge1xuICAgICAgdGhpcy5fbWFwLnJlc2l6ZSgpO1xuICAgIH1cbiAgfVxufVxuXG5NYXBib3gucHJvcFR5cGVzID0gcHJvcFR5cGVzO1xuTWFwYm94LmRlZmF1bHRQcm9wcyA9IGRlZmF1bHRQcm9wcztcbiJdfQ==