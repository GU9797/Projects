'use strict';

Object.defineProperty(exports, "__esModule", {
  value: true
});

var _slicedToArray2 = require('babel-runtime/helpers/slicedToArray');

var _slicedToArray3 = _interopRequireDefault(_slicedToArray2);

var _getPrototypeOf = require('babel-runtime/core-js/object/get-prototype-of');

var _getPrototypeOf2 = _interopRequireDefault(_getPrototypeOf);

var _classCallCheck2 = require('babel-runtime/helpers/classCallCheck');

var _classCallCheck3 = _interopRequireDefault(_classCallCheck2);

var _createClass2 = require('babel-runtime/helpers/createClass');

var _createClass3 = _interopRequireDefault(_createClass2);

var _possibleConstructorReturn2 = require('babel-runtime/helpers/possibleConstructorReturn');

var _possibleConstructorReturn3 = _interopRequireDefault(_possibleConstructorReturn2);

var _inherits2 = require('babel-runtime/helpers/inherits');

var _inherits3 = _interopRequireDefault(_inherits2);

var _keys = require('babel-runtime/core-js/object/keys');

var _keys2 = _interopRequireDefault(_keys);

var _assign = require('babel-runtime/core-js/object/assign');

var _assign2 = _interopRequireDefault(_assign);

var _react = require('react');

var _propTypes = require('prop-types');

var _propTypes2 = _interopRequireDefault(_propTypes);

var _baseControl = require('./base-control');

var _baseControl2 = _interopRequireDefault(_baseControl);

var _dynamicPosition = require('../utils/dynamic-position');

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

// Copyright (c) 2015 Uber Technologies, Inc.

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
var propTypes = (0, _assign2.default)({}, _baseControl2.default.propTypes, {
  // Custom className
  className: _propTypes2.default.string,
  // Longitude of the anchor point
  longitude: _propTypes2.default.number.isRequired,
  // Latitude of the anchor point
  latitude: _propTypes2.default.number.isRequired,
  // Offset from the left
  offsetLeft: _propTypes2.default.number,
  // Offset from the top
  offsetTop: _propTypes2.default.number,
  // Size of the tip
  tipSize: _propTypes2.default.number,
  // Whether to show close button
  closeButton: _propTypes2.default.bool,
  // Whether to close on click
  closeOnClick: _propTypes2.default.bool,
  // The popup's location relative to the coordinate
  anchor: _propTypes2.default.oneOf((0, _keys2.default)(_dynamicPosition.ANCHOR_POSITION)),
  // Whether the popup anchor should be auto-adjusted to fit within the container
  dynamicPosition: _propTypes2.default.bool,
  // Callback when component is closed
  onClose: _propTypes2.default.func
});

var defaultProps = (0, _assign2.default)({}, _baseControl2.default.defaultProps, {
  className: '',
  offsetLeft: 0,
  offsetTop: 0,
  tipSize: 10,
  anchor: 'bottom',
  dynamicPosition: true,
  closeButton: true,
  closeOnClick: true,
  onClose: function onClose() {}
});

/*
 * PureComponent doesn't update when context changes.
 * The only way is to implement our own shouldComponentUpdate here. Considering
 * the parent component (StaticMap or InteractiveMap) is pure, and map re-render
 * is almost always triggered by a viewport change, we almost definitely need to
 * recalculate the popup's position when the parent re-renders.
 */

var Popup = function (_BaseControl) {
  (0, _inherits3.default)(Popup, _BaseControl);

  function Popup(props) {
    (0, _classCallCheck3.default)(this, Popup);

    var _this = (0, _possibleConstructorReturn3.default)(this, (Popup.__proto__ || (0, _getPrototypeOf2.default)(Popup)).call(this, props));

    _this._getPosition = _this._getPosition.bind(_this);
    _this._onClose = _this._onClose.bind(_this);
    _this._contentLoaded = _this._contentLoaded.bind(_this);
    _this._renderTip = _this._renderTip.bind(_this);
    _this._renderContent = _this._renderContent.bind(_this);
    return _this;
  }

  (0, _createClass3.default)(Popup, [{
    key: 'componentDidMount',
    value: function componentDidMount() {
      // Container just got a size, re-calculate position
      this.forceUpdate();
    }
  }, {
    key: '_getPosition',
    value: function _getPosition(x, y) {
      var viewport = this.context.viewport;
      var _props = this.props,
          anchor = _props.anchor,
          dynamicPosition = _props.dynamicPosition,
          tipSize = _props.tipSize;


      if (this._content) {
        return dynamicPosition ? (0, _dynamicPosition.getDynamicPosition)({
          x: x, y: y, anchor: anchor,
          padding: tipSize,
          width: viewport.width,
          height: viewport.height,
          selfWidth: this._content.clientWidth,
          selfHeight: this._content.clientHeight
        }) : anchor;
      }

      return anchor;
    }
  }, {
    key: '_onClose',
    value: function _onClose() {
      this.props.onClose();
    }
  }, {
    key: '_contentLoaded',
    value: function _contentLoaded(ref) {
      this._content = ref;
    }
  }, {
    key: '_renderTip',
    value: function _renderTip() {
      var tipSize = this.props.tipSize;


      return (0, _react.createElement)('div', {
        key: 'tip',
        className: 'mapboxgl-popup-tip',
        style: { borderWidth: tipSize }
      });
    }
  }, {
    key: '_renderContent',
    value: function _renderContent() {
      var _props2 = this.props,
          closeButton = _props2.closeButton,
          children = _props2.children;

      return (0, _react.createElement)('div', {
        key: 'content',
        ref: this._contentLoaded,
        className: 'mapboxgl-popup-content'
      }, [closeButton && (0, _react.createElement)('button', {
        key: 'close-button',
        className: 'mapboxgl-popup-close-button',
        type: 'button',
        onClick: this._onClose
      }, '×'), children]);
    }
  }, {
    key: 'render',
    value: function render() {
      var _props3 = this.props,
          className = _props3.className,
          longitude = _props3.longitude,
          latitude = _props3.latitude,
          offsetLeft = _props3.offsetLeft,
          offsetTop = _props3.offsetTop,
          closeOnClick = _props3.closeOnClick;

      var _context$viewport$pro = this.context.viewport.project([longitude, latitude]),
          _context$viewport$pro2 = (0, _slicedToArray3.default)(_context$viewport$pro, 2),
          x = _context$viewport$pro2[0],
          y = _context$viewport$pro2[1];

      var positionType = this._getPosition(x, y);
      var anchorPosition = _dynamicPosition.ANCHOR_POSITION[positionType];

      var containerStyle = {
        position: 'absolute',
        left: x + offsetLeft,
        top: y + offsetTop,
        transform: 'translate(' + -anchorPosition.x * 100 + '%, ' + -anchorPosition.y * 100 + '%)'
      };

      return (0, _react.createElement)('div', {
        className: 'mapboxgl-popup mapboxgl-popup-anchor-' + positionType + ' ' + className,
        style: containerStyle,
        ref: this._onContainerLoad,
        onClick: closeOnClick ? this._onClose : null
      }, [this._renderTip(), this._renderContent()]);
    }
  }]);
  return Popup;
}(_baseControl2.default);

exports.default = Popup;


Popup.displayName = 'Popup';
Popup.propTypes = propTypes;
Popup.defaultProps = defaultProps;
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJzb3VyY2VzIjpbIi4uLy4uL3NyYy9jb21wb25lbnRzL3BvcHVwLmpzIl0sIm5hbWVzIjpbInByb3BUeXBlcyIsImNsYXNzTmFtZSIsInN0cmluZyIsImxvbmdpdHVkZSIsIm51bWJlciIsImlzUmVxdWlyZWQiLCJsYXRpdHVkZSIsIm9mZnNldExlZnQiLCJvZmZzZXRUb3AiLCJ0aXBTaXplIiwiY2xvc2VCdXR0b24iLCJib29sIiwiY2xvc2VPbkNsaWNrIiwiYW5jaG9yIiwib25lT2YiLCJkeW5hbWljUG9zaXRpb24iLCJvbkNsb3NlIiwiZnVuYyIsImRlZmF1bHRQcm9wcyIsIlBvcHVwIiwicHJvcHMiLCJfZ2V0UG9zaXRpb24iLCJiaW5kIiwiX29uQ2xvc2UiLCJfY29udGVudExvYWRlZCIsIl9yZW5kZXJUaXAiLCJfcmVuZGVyQ29udGVudCIsImZvcmNlVXBkYXRlIiwieCIsInkiLCJ2aWV3cG9ydCIsImNvbnRleHQiLCJfY29udGVudCIsInBhZGRpbmciLCJ3aWR0aCIsImhlaWdodCIsInNlbGZXaWR0aCIsImNsaWVudFdpZHRoIiwic2VsZkhlaWdodCIsImNsaWVudEhlaWdodCIsInJlZiIsImtleSIsInN0eWxlIiwiYm9yZGVyV2lkdGgiLCJjaGlsZHJlbiIsInR5cGUiLCJvbkNsaWNrIiwicHJvamVjdCIsInBvc2l0aW9uVHlwZSIsImFuY2hvclBvc2l0aW9uIiwiY29udGFpbmVyU3R5bGUiLCJwb3NpdGlvbiIsImxlZnQiLCJ0b3AiLCJ0cmFuc2Zvcm0iLCJfb25Db250YWluZXJMb2FkIiwiZGlzcGxheU5hbWUiXSwibWFwcGluZ3MiOiI7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7O0FBbUJBOztBQUNBOzs7O0FBQ0E7Ozs7QUFFQTs7OztBQXZCQTs7QUFFQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7O0FBRUE7QUFDQTs7QUFFQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQU9BLElBQU1BLFlBQVksc0JBQWMsRUFBZCxFQUFr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cUQsQ0FBQ3FCLGVBQWVwQixDQUFoQixHQUFvQixHQUF6RTtBQUpxQixPQUF2Qjs7QUFPQSxhQUFPLDBCQUFjLEtBQWQsRUFBcUI7QUFDMUI1Qiw2REFBbUQrQyxZQUFuRCxTQUFtRS9DLFNBRHpDO0FBRTFCeUMsZUFBT1EsY0FGbUI7QUFHMUJWLGFBQUssS0FBS2UsZ0JBSGdCO0FBSTFCVCxpQkFBU2xDLGVBQWUsS0FBS1csUUFBcEIsR0FBK0I7QUFKZCxPQUFyQixFQUtKLENBQ0QsS0FBS0UsVUFBTCxFQURDLEVBRUQsS0FBS0MsY0FBTCxFQUZDLENBTEksQ0FBUDtBQVNEOzs7OztrQkE5RmtCUCxLOzs7QUFrR3JCQSxNQUFNcUMsV0FBTixHQUFvQixPQUFwQjtBQUNBckMsTUFBTW5CLFNBQU4sR0FBa0JBLFNBQWxCO0FBQ0FtQixNQUFNRCxZQUFOLEdBQXFCQSxZQUFyQiIsImZpbGUiOiJwb3B1cC5qcyIsInNvdXJjZXNDb250ZW50IjpbIi8vIENvcHlyaWdodCAoYykgMjAxNSBVYmVyIFRlY2hub2xvZ2llcywgSW5jLlxuXG4vLyBQZXJtaXNzaW9uIGlzIGhlcmVieSBncmFudGVkLCBmcmVlIG9mIGNoYXJnZSwgdG8gYW55IHBlcnNvbiBvYnRhaW5pbmcgYSBjb3B5XG4vLyBvZiB0aGlzIHNvZnR3YXJlIGFuZCBhc3NvY2lhdGVkIGRvY3VtZW50YXRpb24gZmlsZXMgKHRoZSBcIlNvZnR3YXJlXCIpLCB0byBkZWFsXG4vLyBpbiB0aGUgU29mdHdhcmUgd2l0aG91dCByZXN0cmljdGlvbiwgaW5jbHVkaW5nIHdpdGhvdXQgbGltaXRhdGlvbiB0aGUgcmlnaHRzXG4vLyB0byB1c2UsIGNvcHksIG1vZGlmeSwgbWVyZ2UsIHB1Ymxpc2gsIGRpc3RyaWJ1dGUsIHN1YmxpY2Vuc2UsIGFuZC9vciBzZWxsXG4vLyBjb3BpZXMgb2YgdGhlIFNvZnR3YXJlLCBhbmQgdG8gcGVybWl0IHBlcnNvbnMgdG8gd2hvbSB0aGUgU29mdHdhcmUgaXNcbi8vIGZ1cm5pc2hlZCB0byBkbyBzbywgc3ViamVjdCB0byB0aGUgZm9sbG93aW5nIGNvbmRpdGlvbnM6XG5cbi8vIFRoZSBhYm92ZSBjb3B5cmlnaHQgbm90aWNlIGFuZCB0aGlzIHBlcm1pc3Npb24gbm90aWNlIHNoYWxsIGJlIGluY2x1ZGVkIGluXG4vLyBhbGwgY29waWVzIG9yIHN1YnN0YW50aWFsIHBvcnRpb25zIG9mIHRoZSBTb2Z0d2FyZS5cblxuLy8gVEhFIFNPRlRXQVJFIElTIFBST1ZJREVEIFwiQVMgSVNcIiwgV0lUSE9VVCBXQVJSQU5UWSBPRiBBTlkgS0lORCwgRVhQUkVTUyBPUlxuLy8gSU1QTElFRCwgSU5DTFVESU5HIEJVVCBOT1QgTElNSVRFRCBUTyBUSEUgV0FSUkFOVElFUyBPRiBNRVJDSEFOVEFCSUxJVFksXG4vLyBGSVRORVNTIEZPUiBBIFBBUlRJQ1VMQVIgUFVSUE9TRSBBTkQgTk9OSU5GUklOR0VNRU5ULiBJTiBOTyBFVkVOVCBTSEFMTCBUSEVcbi8vIEFVVEhPUlMgT1IgQ09QWVJJR0hUIEhPTERFUlMgQkUgTElBQkxFIEZPUiBBTlkgQ0xBSU0sIERBTUFHRVMgT1IgT1RIRVJcbi8vIExJQUJJTElUWSwgV0hFVEhFUiBJTiBBTiBBQ1RJT04gT0YgQ09OVFJBQ1QsIFRPUlQgT1IgT1RIRVJXSVNFLCBBUklTSU5HIEZST00sXG4vLyBPVVQgT0YgT1IgSU4gQ09OTkVDVElPTiBXSVRIIFRIRSBTT0ZUV0FSRSBPUiBUSEUgVVNFIE9SIE9USEVSIERFQUxJTkdTIElOXG4vLyBUSEUgU09GVFdBUkUuXG5pbXBvcnQge2NyZWF0ZUVsZW1lbnR9IGZyb20gJ3JlYWN0JztcbmltcG9ydCBQcm9wVHlwZXMgZnJvbSAncHJvcC10eXBlcyc7XG5pbXBvcnQgQmFzZUNvbnRyb2wgZnJvbSAnLi9iYXNlLWNvbnRyb2wnO1xuXG5pbXBvcnQge2dldER5bmFtaWNQb3NpdGlvbiwgQU5DSE9SX1BPU0lUSU9OfSBmcm9tICcuLi91dGlscy9keW5hbWljLXBvc2l0aW9uJztcblxuY29uc3QgcHJvcFR5cGVzID0gT2JqZWN0LmFzc2lnbih7fSwgQmFzZUNvbnRyb2wucHJvcFR5cGVzLCB7XG4gIC8vIEN1c3RvbSBjbGFzc05hbWVcbiAgY2xhc3NOYW1lOiBQcm9wVHlwZXMuc3RyaW5nLFxuICAvLyBMb25naXR1ZGUgb2YgdGhlIGFuY2hvciBwb2ludFxuICBsb25naXR1ZGU6IFByb3BUeXBlcy5udW1iZXIuaXNSZXF1aXJlZCxcbiAgLy8gTGF0aXR1ZGUgb2YgdGhlIGFuY2hvciBwb2ludFxuICBsYXRpdHVkZTogUHJvcFR5cGVzLm51bWJlci5pc1JlcXVpcmVkLFxuICAvLyBPZmZzZXQgZnJvbSB0aGUgbGVmdFxuICBvZmZzZXRMZWZ0OiBQcm9wVHlwZXMubnVtYmVyLFxuICAvLyBPZmZzZXQgZnJvbSB0aGUgdG9wXG4gIG9mZnNldFRvcDogUHJvcFR5cGVzLm51bWJlcixcbiAgLy8gU2l6ZSBvZiB0aGUgdGlwXG4gIHRpcFNpemU6IFByb3BUeXBlcy5udW1iZXIsXG4gIC8vIFdoZXRoZXIgdG8gc2hvdyBjbG9zZSBidXR0b25cbiAgY2xvc2VCdXR0b246IFByb3BUeXBlcy5ib29sLFxuICAvLyBXaGV0aGVyIHRvIGNsb3NlIG9uIGNsaWNrXG4gIGNsb3NlT25DbGljazogUHJvcFR5cGVzLmJvb2wsXG4gIC8vIFRoZSBwb3B1cCdzIGxvY2F0aW9uIHJlbGF0aXZlIHRvIHRoZSBjb29yZGluYXRlXG4gIGFuY2hvcjogUHJvcFR5cGVzLm9uZU9mKE9iamVjdC5rZXlzKEFOQ0hPUl9QT1NJVElPTikpLFxuICAvLyBXaGV0aGVyIHRoZSBwb3B1cCBhbmNob3Igc2hvdWxkIGJlIGF1dG8tYWRqdXN0ZWQgdG8gZml0IHdpdGhpbiB0aGUgY29udGFpbmVyXG4gIGR5bmFtaWNQb3NpdGlvbjogUHJvcFR5cGVzLmJvb2wsXG4gIC8vIENhbGxiYWNrIHdoZW4gY29tcG9uZW50IGlzIGNsb3NlZFxuICBvbkNsb3NlOiBQcm9wVHlwZXMuZnVuY1xufSk7XG5cbmNvbnN0IGRlZmF1bHRQcm9wcyA9IE9iamVjdC5hc3NpZ24oe30sIEJhc2VDb250cm9sLmRlZmF1bHRQcm9wcywge1xuICBjbGFzc05hbWU6ICcnLFxuICBvZmZzZXRMZWZ0OiAwLFxuICBvZmZzZXRUb3A6IDAsXG4gIHRpcFNpemU6IDEwLFxuICBhbmNob3I6ICdib3R0b20nLFxuICBkeW5hbWljUG9zaXRpb246IHRydWUsXG4gIGNsb3NlQnV0dG9uOiB0cnVlLFxuICBjbG9zZU9uQ2xpY2s6IHRydWUsXG4gIG9uQ2xvc2U6ICgpID0+IHt9XG59KTtcblxuLypcbiAqIFB1cmVDb21wb25lbnQgZG9lc24ndCB1cGRhdGUgd2hlbiBjb250ZXh0IGNoYW5nZXMuXG4gKiBUaGUgb25seSB3YXkgaXMgdG8gaW1wbGVtZW50IG91ciBvd24gc2hvdWxkQ29tcG9uZW50VXBkYXRlIGhlcmUuIENvbnNpZGVyaW5nXG4gKiB0aGUgcGFyZW50IGNvbXBvbmVudCAoU3RhdGljTWFwIG9yIEludGVyYWN0aXZlTWFwKSBpcyBwdXJlLCBhbmQgbWFwIHJlLXJlbmRlclxuICogaXMgYWxtb3N0IGFsd2F5cyB0cmlnZ2VyZWQgYnkgYSB2aWV3cG9ydCBjaGFuZ2UsIHdlIGFsbW9zdCBkZWZpbml0ZWx5IG5lZWQgdG9cbiAqIHJlY2FsY3VsYXRlIHRoZSBwb3B1cCdzIHBvc2l0aW9uIHdoZW4gdGhlIHBhcmVudCByZS1yZW5kZXJzLlxuICovXG5leHBvcnQgZGVmYXVsdCBjbGFzcyBQb3B1cCBleHRlbmRzIEJhc2VDb250cm9sIHtcblxuICBjb25zdHJ1Y3Rvcihwcm9wcykge1xuICAgIHN1cGVyKHByb3BzKTtcblxuICAgIHRoaXMuX2dldFBvc2l0aW9uID0gdGhpcy5fZ2V0UG9zaXRpb24uYmluZCh0aGlzKTtcbiAgICB0aGlzLl9vbkNsb3NlID0gdGhpcy5fb25DbG9zZS5iaW5kKHRoaXMpO1xuICAgIHRoaXMuX2NvbnRlbnRMb2FkZWQgPSB0aGlzLl9jb250ZW50TG9hZGVkLmJpbmQodGhpcyk7XG4gICAgdGhpcy5fcmVuZGVyVGlwID0gdGhpcy5fcmVuZGVyVGlwLmJpbmQodGhpcyk7XG4gICAgdGhpcy5fcmVuZGVyQ29udGVudCA9IHRoaXMuX3JlbmRlckNvbnRlbnQuYmluZCh0aGlzKTtcbiAgfVxuXG4gIGNvbXBvbmVudERpZE1vdW50KCkge1xuICAgIC8vIENvbnRhaW5lciBqdXN0IGdvdCBhIHNpemUsIHJlLWNhbGN1bGF0ZSBwb3NpdGlvblxuICAgIHRoaXMuZm9yY2VVcGRhdGUoKTtcbiAgfVxuXG4gIF9nZXRQb3NpdGlvbih4LCB5KSB7XG4gICAgY29uc3Qge3ZpZXdwb3J0fSA9IHRoaXMuY29udGV4dDtcbiAgICBjb25zdCB7YW5jaG9yLCBkeW5hbWljUG9zaXRpb24sIHRpcFNpemV9ID0gdGhpcy5wcm9wcztcblxuICAgIGlmICh0aGlzLl9jb250ZW50KSB7XG4gICAgICByZXR1cm4gZHluYW1pY1Bvc2l0aW9uID8gZ2V0RHluYW1pY1Bvc2l0aW9uKHtcbiAgICAgICAgeCwgeSwgYW5jaG9yLFxuICAgICAgICBwYWRkaW5nOiB0aXBTaXplLFxuICAgICAgICB3aWR0aDogdmlld3BvcnQud2lkdGgsXG4gICAgICAgIGhlaWdodDogdmlld3BvcnQuaGVpZ2h0LFxuICAgICAgICBzZWxmV2lkdGg6IHRoaXMuX2NvbnRlbnQuY2xpZW50V2lkdGgsXG4gICAgICAgIHNlbGZIZWlnaHQ6IHRoaXMuX2NvbnRlbnQuY2xpZW50SGVpZ2h0XG4gICAgICB9KSA6IGFuY2hvcjtcbiAgICB9XG5cbiAgICByZXR1cm4gYW5jaG9yO1xuICB9XG5cbiAgX29uQ2xvc2UoKSB7XG4gICAgdGhpcy5wcm9wcy5vbkNsb3NlKCk7XG4gIH1cblxuICBfY29udGVudExvYWRlZChyZWYpIHtcbiAgICB0aGlzLl9jb250ZW50ID0gcmVmO1xuICB9XG5cbiAgX3JlbmRlclRpcCgpIHtcbiAgICBjb25zdCB7dGlwU2l6ZX0gPSB0aGlzLnByb3BzO1xuXG4gICAgcmV0dXJuIGNyZWF0ZUVsZW1lbnQoJ2RpdicsIHtcbiAgICAgIGtleTogJ3RpcCcsXG4gICAgICBjbGFzc05hbWU6ICdtYXBib3hnbC1wb3B1cC10aXAnLFxuICAgICAgc3R5bGU6IHtib3JkZXJXaWR0aDogdGlwU2l6ZX1cbiAgICB9KTtcbiAgfVxuXG4gIF9yZW5kZXJDb250ZW50KCkge1xuICAgIGNvbnN0IHtjbG9zZUJ1dHRvbiwgY2hpbGRyZW59ID0gdGhpcy5wcm9wcztcbiAgICByZXR1cm4gY3JlYXRlRWxlbWVudCgnZGl2Jywge1xuICAgICAga2V5OiAnY29udGVudCcsXG4gICAgICByZWY6IHRoaXMuX2NvbnRlbnRMb2FkZWQsXG4gICAgICBjbGFzc05hbWU6ICdtYXBib3hnbC1wb3B1cC1jb250ZW50J1xuICAgIH0sIFtcbiAgICAgIGNsb3NlQnV0dG9uICYmIGNyZWF0ZUVsZW1lbnQoJ2J1dHRvbicsIHtcbiAgICAgICAga2V5OiAnY2xvc2UtYnV0dG9uJyxcbiAgICAgICAgY2xhc3NOYW1lOiAnbWFwYm94Z2wtcG9wdXAtY2xvc2UtYnV0dG9uJyxcbiAgICAgICAgdHlwZTogJ2J1dHRvbicsXG4gICAgICAgIG9uQ2xpY2s6IHRoaXMuX29uQ2xvc2VcbiAgICAgIH0sICfDlycpLFxuICAgICAgY2hpbGRyZW5cbiAgICBdKTtcbiAgfVxuXG4gIHJlbmRlcigpIHtcbiAgICBjb25zdCB7Y2xhc3NOYW1lLCBsb25naXR1ZGUsIGxhdGl0dWRlLCBvZmZzZXRMZWZ0LCBvZmZzZXRUb3AsIGNsb3NlT25DbGlja30gPSB0aGlzLnByb3BzO1xuXG4gICAgY29uc3QgW3gsIHldID0gdGhpcy5jb250ZXh0LnZpZXdwb3J0LnByb2plY3QoW2xvbmdpdHVkZSwgbGF0aXR1ZGVdKTtcblxuICAgIGNvbnN0IHBvc2l0aW9uVHlwZSA9IHRoaXMuX2dldFBvc2l0aW9uKHgsIHkpO1xuICAgIGNvbnN0IGFuY2hvclBvc2l0aW9uID0gQU5DSE9SX1BPU0lUSU9OW3Bvc2l0aW9uVHlwZV07XG5cbiAgICBjb25zdCBjb250YWluZXJTdHlsZSA9IHtcbiAgICAgIHBvc2l0aW9uOiAnYWJzb2x1dGUnLFxuICAgICAgbGVmdDogeCArIG9mZnNldExlZnQsXG4gICAgICB0b3A6IHkgKyBvZmZzZXRUb3AsXG4gICAgICB0cmFuc2Zvcm06IGB0cmFuc2xhdGUoJHstYW5jaG9yUG9zaXRpb24ueCAqIDEwMH0lLCAkey1hbmNob3JQb3NpdGlvbi55ICogMTAwfSUpYFxuICAgIH07XG5cbiAgICByZXR1cm4gY3JlYXRlRWxlbWVudCgnZGl2Jywge1xuICAgICAgY2xhc3NOYW1lOiBgbWFwYm94Z2wtcG9wdXAgbWFwYm94Z2wtcG9wdXAtYW5jaG9yLSR7cG9zaXRpb25UeXBlfSAke2NsYXNzTmFtZX1gLFxuICAgICAgc3R5bGU6IGNvbnRhaW5lclN0eWxlLFxuICAgICAgcmVmOiB0aGlzLl9vbkNvbnRhaW5lckxvYWQsXG4gICAgICBvbkNsaWNrOiBjbG9zZU9uQ2xpY2sgPyB0aGlzLl9vbkNsb3NlIDogbnVsbFxuICAgIH0sIFtcbiAgICAgIHRoaXMuX3JlbmRlclRpcCgpLFxuICAgICAgdGhpcy5fcmVuZGVyQ29udGVudCgpXG4gICAgXSk7XG4gIH1cblxufVxuXG5Qb3B1cC5kaXNwbGF5TmFtZSA9ICdQb3B1cCc7XG5Qb3B1cC5wcm9wVHlwZXMgPSBwcm9wVHlwZXM7XG5Qb3B1cC5kZWZhdWx0UHJvcHMgPSBkZWZhdWx0UHJvcHM7XG4iXX0=