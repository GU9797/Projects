'use strict';

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.TRANSITION_EVENTS = undefined;

var _assign = require('babel-runtime/core-js/object/assign');

var _assign2 = _interopRequireDefault(_assign);

var _classCallCheck2 = require('babel-runtime/helpers/classCallCheck');

var _classCallCheck3 = _interopRequireDefault(_classCallCheck2);

var _createClass2 = require('babel-runtime/helpers/createClass');

var _createClass3 = _interopRequireDefault(_createClass2);

var _assert = require('assert');

var _assert2 = _interopRequireDefault(_assert);

var _transition = require('./transition');

var _mapState = require('./map-state');

var _mapState2 = _interopRequireDefault(_mapState);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

var noop = function noop() {}; /* global requestAnimationFrame, cancelAnimationFrame */
var TRANSITION_EVENTS = exports.TRANSITION_EVENTS = {
  BREAK: 1,
  SNAP_TO_END: 2,
  IGNORE: 3
};

var DEFAULT_PROPS = {
  transitionDuration: 0,
  transitionEasing: function transitionEasing(t) {
    return t;
  },
  transitionInterpolator: new _transition.LinearInterpolator(),
  transitionInterruption: TRANSITION_EVENTS.BREAK,
  onTransitionStart: noop,
  onTransitionInterrupt: noop,
  onTransitionEnd: noop
};

var DEFAULT_STATE = {
  animation: null,
  propsInTransition: null,
  startProps: null,
  endProps: null
};

var TransitionManager = function () {
  function TransitionManager(props) {
    (0, _classCallCheck3.default)(this, TransitionManager);

    this.props = props;
    this.state = DEFAULT_STATE;

    this._onTransitionFrame = this._onTransitionFrame.bind(this);
  }

  // Returns current transitioned viewport.


  (0, _createClass3.default)(TransitionManager, [{
    key: 'getViewportInTransition',
    value: function getViewportInTransition() {
      return this.state.propsInTransition;
    }

    // Process the viewport change, either ignore or trigger a new transiton.
    // Return true if a new transition is triggered, false otherwise.

  }, {
    key: 'processViewportChange',
    value: function processViewportChange(nextProps) {
      var transitionTriggered = false;
      var currentProps = this.props;
      // Set this.props here as '_triggerTransition' calls '_updateViewport' that uses this.props.
      this.props = nextProps;

      // NOTE: Be cautious re-ordering statements in this function.
      if (this._shouldIgnoreViewportChange(currentProps, nextProps)) {
        return transitionTriggered;
      }

      var isTransitionInProgress = this._isTransitionInProgress();

      if (this._isTransitionEnabled(nextProps)) {
        var startProps = (0, _assign2.default)({}, currentProps, this.state.interruption === TRANSITION_EVENTS.SNAP_TO_END ? this.state.endProps : this.state.propsInTransition);

        if (isTransitionInProgress) {
          currentProps.onTransitionInterrupt();
        }
        nextProps.onTransitionStart();

        this._triggerTransition(startProps, nextProps);

        transitionTriggered = true;
      } else if (isTransitionInProgress) {
        currentProps.onTransitionInterrupt();
        this._endTransition();
      }

      return transitionTriggered;
    }

    // Helper methods

  }, {
    key: '_isTransitionInProgress',
    value: function _isTransitionInProgress() {
      return Boolean(this.state.propsInTransition);
    }
  }, {
    key: '_isTransitionEnabled',
    value: function _isTransitionEnabled(props) {
      return props.transitionDuration > 0 && Boolean(props.transitionInterpolator);
    }
  }, {
    key: '_isUpdateDueToCurrentTransition',
    value: function _isUpdateDueToCurrentTransition(props) {
      if (this.state.propsInTransition) {
        return this.state.interpolator.arePropsEqual(props, this.state.propsInTransition);
      }
      return false;
    }
  }, {
    key: '_shouldIgnoreViewportChange',
    value: function _shouldIgnoreViewportChange(currentProps, nextProps) {
      if (this._isTransitionInProgress()) {
        // Ignore update if it is requested to be ignored
        return this.state.interruption === TRANSITION_EVENTS.IGNORE ||
        // Ignore update if it is due to current active transition.
        this._isUpdateDueToCurrentTransition(nextProps);
      } else if (this._isTransitionEnabled(nextProps)) {
        // Ignore if none of the viewport props changed.
        return nextProps.transitionInterpolator.arePropsEqual(currentProps, nextProps);
      }
      return true;
    }
  }, {
    key: '_triggerTransition',
    value: function _triggerTransition(startProps, endProps) {
      (0, _assert2.default)(this._isTransitionEnabled(endProps), 'Transition is not enabled');

      cancelAnimationFrame(this.state.animation);

      var initialProps = endProps.transitionInterpolator.initializeProps(startProps, endProps);

      this.state = {
        // Save current transition props
        duration: endProps.transitionDuration,
        easing: endProps.transitionEasing,
        interpolator: endProps.transitionInterpolator,
        interruption: endProps.transitionInterruption,

        startTime: Date.now(),
        startProps: initialProps.start,
        endProps: initialProps.end,
        animation: null,
        propsInTransition: {}
      };

      this._onTransitionFrame();
    }
  }, {
    key: '_onTransitionFrame',
    value: function _onTransitionFrame() {
      // _updateViewport() may cancel the animation
      this.state.animation = requestAnimationFrame(this._onTransitionFrame);
      this._updateViewport();
    }
  }, {
    key: '_endTransition',
    value: function _endTransition() {
      cancelAnimationFrame(this.state.animation);
      this.state = DEFAULT_STATE;
    }
  }, {
    key: '_updateViewport',
    value: function _updateViewport() {
      // NOTE: Be cautious re-ordering statements in this function.
      var currentTime = Date.now();
      var _state = this.state,
          startTime = _state.startTime,
          duration = _state.duration,
          easing = _state.easing,
          interpolator = _state.interpolator,
          startProps = _state.startProps,
          endProps = _state.endProps;


      var shouldEnd = false;
      var t = (currentTime - startTime) / duration;
      if (t >= 1) {
        t = 1;
        shouldEnd = true;
      }
      t = easing(t);

      var viewport = interpolator.interpolateProps(startProps, endProps, t);
      // Normalize viewport props
      var mapState = new _mapState2.default((0, _assign2.default)({}, this.props, viewport));
      this.state.propsInTransition = mapState.getViewportProps();

      if (this.props.onViewportChange) {
        this.props.onViewportChange(this.state.propsInTransition);
      }

      if (shouldEnd) {
        this._endTransition();
        this.props.onTransitionEnd();
      }
    }
  }]);
  return TransitionManager;
}();

exports.default = TransitionManager;


TransitionManager.defaultProps = DEFAULT_PROPS;
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJzb3VyY2VzIjpbIi4uLy4uL3NyYy91dGlscy90cmFuc2l0aW9uLW1hbmFnZXIuanMiXSwibmFtZXMiOlsibm9vcCIsIlRSQU5TSVRJT05fRVZFTlRTIiwiQlJFQUsiLCJTTkFQX1RPX0VORCIsIklHTk9SRSIsIkRFRkFVTFRfUFJPUFMiLCJ0cmFuc2l0aW9uRHVyYXRpb24iLCJ0cmFuc2l0aW9uRWFzaW5nIiwidCIsInRyYW5zaXRpb25JbnRlcnBvbGF0b3IiLCJ0cmFuc2l0aW9uSW50ZXJydXB0aW9uIiwib25UcmFuc2l0aW9uU3RhcnQiLCJvblRyYW5zaXRpb25JbnRlcnJ1cHQiLCJvblRyYW5zaXRpb25FbmQiLCJERUZBVUxUX1NUQVRFIiwiYW5pbWF0aW9uIiwicHJvcHNJblRyYW5zaXRpb24iLCJzdGFydFByb3BzIiwiZW5kUHJvcHMiLCJUcmFuc2l0aW9uTWFuYWdlciIsInByb3BzIiwic3RhdGUiLCJfb25UcmFuc2l0aW9uRnJhbWUiLCJiaW5kIiwibmV4dFByb3BzIiwidHJhbnNpdGlvblRyaWdnZXJlZCIsImN1cnJlbnRQcm9wcyIsIl9zaG91bGRJZ25vcmVWaWV3cG9ydENoYW5nZSIsImlzVHJhbnNpdGlvbkluUHJvZ3Jlc3MiLCJfaXNUcmFuc2l0aW9uSW5Qcm9ncmVzcyIsIl9pc1RyYW5zaXRpb25FbmFibGVkIiwiaW50ZXJydXB0aW9uIiwiX3RyaWdnZXJUcmFuc2l0aW9uIiwiX2VuZFRyYW5zaXRpb24iLCJCb29sZWFuIiwiaW50ZXJwb2xhdG9yIiwiYXJlUHJvcHNFcXVhbCIsIl9pc1VwZGF0ZUR1ZVRvQ3VycmVudFRyYW5zaXRpb24iLCJjYW5jZWxBbmltYXRpb25GcmFtZSIsImluaXRpYWxQcm9wcyIsImluaXRpYWxpemVQcm9wcyIsImR1cmF0aW9uIiwiZWFzaW5nIiwic3RhcnRUaW1lIiwiRGF0ZSIsIm5vdyIsInN0YXJ0IiwiZW5kIiwicmVxdWVzdEFuaW1hdGlvbkZyYW1lIiwiX3VwZGF0ZVZpZXdwb3J0IiwiY3VycmVudFRpbWUiLCJzaG91bGRFbmQiLCJ2aWV3cG9ydCIsImludGVycG9sYXRlUHJvcHMiLCJtYXBTdGF0ZSIsImdldFZpZXdwb3J0UHJvcHMiLCJvblZpZXdwb3J0Q2hhbmdlIiwiZGVmYXVsdFByb3BzIl0sIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7Ozs7Ozs7Ozs7O0FBQ0E7Ozs7QUFDQTs7QUFDQTs7Ozs7O0FBRUEsSUFBTUEsT0FBTyxTQUFQQSxJQUFPLEdBQU0sQ0FBRSxDQUFyQixDLENBTEE7QUFPTyxJQUFNQyxnREFBb0I7QUFDL0JDLFNBQU8sQ0FEd0I7QUFFL0JDLGVBQWEsQ0FGa0I7QUFHL0JDLFVBQVE7QUFIdUIsQ0FBMUI7O0FBTVAsSUFBTUMsZ0JBQWdCO0FBQ3BCQyxzQkFBb0IsQ0FEQTtBQUVwQkMsb0JBQWtCO0FBQUEsV0FBS0MsQ0FBTDtBQUFBLEdBRkU7QUFHcEJDLDBCQUF3QixvQ0FISjtBQUlwQkMsMEJBQXdCVCxrQkFBa0JDLEtBSnRCO0FBS3BCUyxxQkFBbUJYLElBTEM7QUFNcEJZLHlCQUF1QlosSUFOSDtBQU9wQmEsbUJBQWlCYjtBQVBHLENBQXRCOztBQVVBLElBQU1jLGdCQUFnQjtBQUNwQkMsYUFBVyxJQURTO0FBRXBCQyxxQkFBbUIsSUFGQztBQUdwQkMsY0FBWSxJQUhRO0FBSXBCQyxZQUFVO0FBSlUsQ0FBdEI7O0lBT3FCQyxpQjtBQUNuQiw2QkFBWUMsS0FBWixFQUFtQjtBQUFBOztBQUNqQixTQUFLQSxLQUFMLEdBQWFBLEtBQWI7QUFDQSxTQUFLQyxLQUFMLEdBQWFQLGFBQWI7O0FBRUEsU0FBS1Esa0JBQUwsR0FBMEIsS0FBS0Esa0JBQUwsQ0FBd0JDLElBQXhCLENBQTZCLElBQTdCLENBQTFCO0FBQ0Q7O0FBRUQ7Ozs7OzhDQUMwQjtBQUN4QixhQUFPLEtBQUtGLEtBQUwsQ0FBV0wsaUJBQWxCO0FBQ0Q7O0FBRUQ7QUFDQTs7OzswQ0FDc0JRLFMsRUFBVztBQUMvQixVQUFJQyxzQkFBc0IsS0FBMUI7QUFDQSxVQUFNQyxlQUFlLEtBQUtOLEtBQTFCO0FBQ0E7QUFDQSxXQUFLQSxLQUFMLEdB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OztrQkFoSmtCTSxpQjs7O0FBbUpyQkEsa0JBQWtCc0MsWUFBbEIsR0FBaUNwRCxhQUFqQyIsImZpbGUiOiJ0cmFuc2l0aW9uLW1hbmFnZXIuanMiLCJzb3VyY2VzQ29udGVudCI6WyIvKiBnbG9iYWwgcmVxdWVzdEFuaW1hdGlvbkZyYW1lLCBjYW5jZWxBbmltYXRpb25GcmFtZSAqL1xuaW1wb3J0IGFzc2VydCBmcm9tICdhc3NlcnQnO1xuaW1wb3J0IHtMaW5lYXJJbnRlcnBvbGF0b3J9IGZyb20gJy4vdHJhbnNpdGlvbic7XG5pbXBvcnQgTWFwU3RhdGUgZnJvbSAnLi9tYXAtc3RhdGUnO1xuXG5jb25zdCBub29wID0gKCkgPT4ge307XG5cbmV4cG9ydCBjb25zdCBUUkFOU0lUSU9OX0VWRU5UUyA9IHtcbiAgQlJFQUs6IDEsXG4gIFNOQVBfVE9fRU5EOiAyLFxuICBJR05PUkU6IDNcbn07XG5cbmNvbnN0IERFRkFVTFRfUFJPUFMgPSB7XG4gIHRyYW5zaXRpb25EdXJhdGlvbjogMCxcbiAgdHJhbnNpdGlvbkVhc2luZzogdCA9PiB0LFxuICB0cmFuc2l0aW9uSW50ZXJwb2xhdG9yOiBuZXcgTGluZWFySW50ZXJwb2xhdG9yKCksXG4gIHRyYW5zaXRpb25JbnRlcnJ1cHRpb246IFRSQU5TSVRJT05fRVZFTlRTLkJSRUFLLFxuICBvblRyYW5zaXRpb25TdGFydDogbm9vcCxcbiAgb25UcmFuc2l0aW9uSW50ZXJydXB0OiBub29wLFxuICBvblRyYW5zaXRpb25FbmQ6IG5vb3Bcbn07XG5cbmNvbnN0IERFRkFVTFRfU1RBVEUgPSB7XG4gIGFuaW1hdGlvbjogbnVsbCxcbiAgcHJvcHNJblRyYW5zaXRpb246IG51bGwsXG4gIHN0YXJ0UHJvcHM6IG51bGwsXG4gIGVuZFByb3BzOiBudWxsXG59O1xuXG5leHBvcnQgZGVmYXVsdCBjbGFzcyBUcmFuc2l0aW9uTWFuYWdlciB7XG4gIGNvbnN0cnVjdG9yKHByb3BzKSB7XG4gICAgdGhpcy5wcm9wcyA9IHByb3BzO1xuICAgIHRoaXMuc3RhdGUgPSBERUZBVUxUX1NUQVRFO1xuXG4gICAgdGhpcy5fb25UcmFuc2l0aW9uRnJhbWUgPSB0aGlzLl9vblRyYW5zaXRpb25GcmFtZS5iaW5kKHRoaXMpO1xuICB9XG5cbiAgLy8gUmV0dXJucyBjdXJyZW50IHRyYW5zaXRpb25lZCB2aWV3cG9ydC5cbiAgZ2V0Vmlld3BvcnRJblRyYW5zaXRpb24oKSB7XG4gICAgcmV0dXJuIHRoaXMuc3RhdGUucHJvcHNJblRyYW5zaXRpb247XG4gIH1cblxuICAvLyBQcm9jZXNzIHRoZSB2aWV3cG9ydCBjaGFuZ2UsIGVpdGhlciBpZ25vcmUgb3IgdHJpZ2dlciBhIG5ldyB0cmFuc2l0b24uXG4gIC8vIFJldHVybiB0cnVlIGlmIGEgbmV3IHRyYW5zaXRpb24gaXMgdHJpZ2dlcmVkLCBmYWxzZSBvdGhlcndpc2UuXG4gIHByb2Nlc3NWaWV3cG9ydENoYW5nZShuZXh0UHJvcHMpIHtcbiAgICBsZXQgdHJhbnNpdGlvblRyaWdnZXJlZCA9IGZhbHNlO1xuICAgIGNvbnN0IGN1cnJlbnRQcm9wcyA9IHRoaXMucHJvcHM7XG4gICAgLy8gU2V0IHRoaXMucHJvcHMgaGVyZSBhcyAnX3RyaWdnZXJUcmFuc2l0aW9uJyBjYWxscyAnX3VwZGF0ZVZpZXdwb3J0JyB0aGF0IHVzZXMgdGhpcy5wcm9wcy5cbiAgICB0aGlzLnByb3BzID0gbmV4dFByb3BzO1xuXG4gICAgLy8gTk9URTogQmUgY2F1dGlvdXMgcmUtb3JkZXJpbmcgc3RhdGVtZW50cyBpbiB0aGlzIGZ1bmN0aW9uLlxuICAgIGlmICh0aGlzLl9zaG91bGRJZ25vcmVWaWV3cG9ydENoYW5nZShjdXJyZW50UHJvcHMsIG5leHRQcm9wcykpIHtcbiAgICAgIHJldHVybiB0cmFuc2l0aW9uVHJpZ2dlcmVkO1xuICAgIH1cblxuICAgIGNvbnN0IGlzVHJhbnNpdGlvbkluUHJvZ3Jlc3MgPSB0aGlzLl9pc1RyYW5zaXRpb25JblByb2dyZXNzKCk7XG5cbiAgICBpZiAodGhpcy5faXNUcmFuc2l0aW9uRW5hYmxlZChuZXh0UHJvcHMpKSB7XG4gICAgICBjb25zdCBzdGFydFByb3BzID0gT2JqZWN0LmFzc2lnbih7fSwgY3VycmVudFByb3BzLFxuICAgICAgICB0aGlzLnN0YXRlLmludGVycnVwdGlvbiA9PT0gVFJBTlNJVElPTl9FVkVOVFMuU05BUF9UT19FTkQgP1xuICAgICAgICB0aGlzLnN0YXRlLmVuZFByb3BzIDogdGhpcy5zdGF0ZS5wcm9wc0luVHJhbnNpdGlvblxuICAgICAgKTtcblxuICAgICAgaWYgKGlzVHJhbnNpdGlvbkluUHJvZ3Jlc3MpIHtcbiAgICAgICAgY3VycmVudFByb3BzLm9uVHJhbnNpdGlvbkludGVycnVwdCgpO1xuICAgICAgfVxuICAgICAgbmV4dFByb3BzLm9uVHJhbnNpdGlvblN0YXJ0KCk7XG5cbiAgICAgIHRoaXMuX3RyaWdnZXJUcmFuc2l0aW9uKHN0YXJ0UHJvcHMsIG5leHRQcm9wcyk7XG5cbiAgICAgIHRyYW5zaXRpb25UcmlnZ2VyZWQgPSB0cnVlO1xuICAgIH0gZWxzZSBpZiAoaXNUcmFuc2l0aW9uSW5Qcm9ncmVzcykge1xuICAgICAgY3VycmVudFByb3BzLm9uVHJhbnNpdGlvbkludGVycnVwdCgpO1xuICAgICAgdGhpcy5fZW5kVHJhbnNpdGlvbigpO1xuICAgIH1cblxuICAgIHJldHVybiB0cmFuc2l0aW9uVHJpZ2dlcmVkO1xuICB9XG5cbiAgLy8gSGVscGVyIG1ldGhvZHNcblxuICBfaXNUcmFuc2l0aW9uSW5Qcm9ncmVzcygpIHtcbiAgICByZXR1cm4gQm9vbGVhbih0aGlzLnN0YXRlLnByb3BzSW5UcmFuc2l0aW9uKTtcbiAgfVxuXG4gIF9pc1RyYW5zaXRpb25FbmFibGVkKHByb3BzKSB7XG4gICAgcmV0dXJuIHByb3BzLnRyYW5zaXRpb25EdXJhdGlvbiA+IDAgJiYgQm9vbGVhbihwcm9wcy50cmFuc2l0aW9uSW50ZXJwb2xhdG9yKTtcbiAgfVxuXG4gIF9pc1VwZGF0ZUR1ZVRvQ3VycmVudFRyYW5zaXRpb24ocHJvcHMpIHtcbiAgICBpZiAodGhpcy5zdGF0ZS5wcm9wc0luVHJhbnNpdGlvbikge1xuICAgICAgcmV0dXJuIHRoaXMuc3RhdGUuaW50ZXJwb2xhdG9yLmFyZVByb3BzRXF1YWwocHJvcHMsIHRoaXMuc3RhdGUucHJvcHNJblRyYW5zaXRpb24pO1xuICAgIH1cbiAgICByZXR1cm4gZmFsc2U7XG4gIH1cblxuICBfc2hvdWxkSWdub3JlVmlld3BvcnRDaGFuZ2UoY3VycmVudFByb3BzLCBuZXh0UHJvcHMpIHtcbiAgICBpZiAodGhpcy5faXNUcmFuc2l0aW9uSW5Qcm9ncmVzcygpKSB7XG4gICAgICAvLyBJZ25vcmUgdXBkYXRlIGlmIGl0IGlzIHJlcXVlc3RlZCB0byBiZSBpZ25vcmVkXG4gICAgICByZXR1cm4gdGhpcy5zdGF0ZS5pbnRlcnJ1cHRpb24gPT09IFRSQU5TSVRJT05fRVZFTlRTLklHTk9SRSB8fFxuICAgICAgICAvLyBJZ25vcmUgdXBkYXRlIGlmIGl0IGlzIGR1ZSB0byBjdXJyZW50IGFjdGl2ZSB0cmFuc2l0aW9uLlxuICAgICAgICB0aGlzLl9pc1VwZGF0ZUR1ZVRvQ3VycmVudFRyYW5zaXRpb24obmV4dFByb3BzKTtcbiAgICB9IGVsc2UgaWYgKHRoaXMuX2lzVHJhbnNpdGlvbkVuYWJsZWQobmV4dFByb3BzKSkge1xuICAgICAgLy8gSWdub3JlIGlmIG5vbmUgb2YgdGhlIHZpZXdwb3J0IHByb3BzIGNoYW5nZWQuXG4gICAgICByZXR1cm4gbmV4dFByb3BzLnRyYW5zaXRpb25JbnRlcnBvbGF0b3IuYXJlUHJvcHNFcXVhbChjdXJyZW50UHJvcHMsIG5leHRQcm9wcyk7XG4gICAgfVxuICAgIHJldHVybiB0cnVlO1xuICB9XG5cbiAgX3RyaWdnZXJUcmFuc2l0aW9uKHN0YXJ0UHJvcHMsIGVuZFByb3BzKSB7XG4gICAgYXNzZXJ0KHRoaXMuX2lzVHJhbnNpdGlvbkVuYWJsZWQoZW5kUHJvcHMpLCAnVHJhbnNpdGlvbiBpcyBub3QgZW5hYmxlZCcpO1xuXG4gICAgY2FuY2VsQW5pbWF0aW9uRnJhbWUodGhpcy5zdGF0ZS5hbmltYXRpb24pO1xuXG4gICAgY29uc3QgaW5pdGlhbFByb3BzID0gZW5kUHJvcHMudHJhbnNpdGlvbkludGVycG9sYXRvci5pbml0aWFsaXplUHJvcHMoXG4gICAgICBzdGFydFByb3BzLFxuICAgICAgZW5kUHJvcHNcbiAgICApO1xuXG4gICAgdGhpcy5zdGF0ZSA9IHtcbiAgICAgIC8vIFNhdmUgY3VycmVudCB0cmFuc2l0aW9uIHByb3BzXG4gICAgICBkdXJhdGlvbjogZW5kUHJvcHMudHJhbnNpdGlvbkR1cmF0aW9uLFxuICAgICAgZWFzaW5nOiBlbmRQcm9wcy50cmFuc2l0aW9uRWFzaW5nLFxuICAgICAgaW50ZXJwb2xhdG9yOiBlbmRQcm9wcy50cmFuc2l0aW9uSW50ZXJwb2xhdG9yLFxuICAgICAgaW50ZXJydXB0aW9uOiBlbmRQcm9wcy50cmFuc2l0aW9uSW50ZXJydXB0aW9uLFxuXG4gICAgICBzdGFydFRpbWU6IERhdGUubm93KCksXG4gICAgICBzdGFydFByb3BzOiBpbml0aWFsUHJvcHMuc3RhcnQsXG4gICAgICBlbmRQcm9wczogaW5pdGlhbFByb3BzLmVuZCxcbiAgICAgIGFuaW1hdGlvbjogbnVsbCxcbiAgICAgIHByb3BzSW5UcmFuc2l0aW9uOiB7fVxuICAgIH07XG5cbiAgICB0aGlzLl9vblRyYW5zaXRpb25GcmFtZSgpO1xuICB9XG5cbiAgX29uVHJhbnNpdGlvbkZyYW1lKCkge1xuICAgIC8vIF91cGRhdGVWaWV3cG9ydCgpIG1heSBjYW5jZWwgdGhlIGFuaW1hdGlvblxuICAgIHRoaXMuc3RhdGUuYW5pbWF0aW9uID0gcmVxdWVzdEFuaW1hdGlvbkZyYW1lKHRoaXMuX29uVHJhbnNpdGlvbkZyYW1lKTtcbiAgICB0aGlzLl91cGRhdGVWaWV3cG9ydCgpO1xuICB9XG5cbiAgX2VuZFRyYW5zaXRpb24oKSB7XG4gICAgY2FuY2VsQW5pbWF0aW9uRnJhbWUodGhpcy5zdGF0ZS5hbmltYXRpb24pO1xuICAgIHRoaXMuc3RhdGUgPSBERUZBVUxUX1NUQVRFO1xuICB9XG5cbiAgX3VwZGF0ZVZpZXdwb3J0KCkge1xuICAgIC8vIE5PVEU6IEJlIGNhdXRpb3VzIHJlLW9yZGVyaW5nIHN0YXRlbWVudHMgaW4gdGhpcyBmdW5jdGlvbi5cbiAgICBjb25zdCBjdXJyZW50VGltZSA9IERhdGUubm93KCk7XG4gICAgY29uc3Qge3N0YXJ0VGltZSwgZHVyYXRpb24sIGVhc2luZywgaW50ZXJwb2xhdG9yLCBzdGFydFByb3BzLCBlbmRQcm9wc30gPSB0aGlzLnN0YXRlO1xuXG4gICAgbGV0IHNob3VsZEVuZCA9IGZhbHNlO1xuICAgIGxldCB0ID0gKGN1cnJlbnRUaW1lIC0gc3RhcnRUaW1lKSAvIGR1cmF0aW9uO1xuICAgIGlmICh0ID49IDEpIHtcbiAgICAgIHQgPSAxO1xuICAgICAgc2hvdWxkRW5kID0gdHJ1ZTtcbiAgICB9XG4gICAgdCA9IGVhc2luZyh0KTtcblxuICAgIGNvbnN0IHZpZXdwb3J0ID0gaW50ZXJwb2xhdG9yLmludGVycG9sYXRlUHJvcHMoc3RhcnRQcm9wcywgZW5kUHJvcHMsIHQpO1xuICAgICAgLy8gTm9ybWFsaXplIHZpZXdwb3J0IHByb3BzXG4gICAgY29uc3QgbWFwU3RhdGUgPSBuZXcgTWFwU3RhdGUoT2JqZWN0LmFzc2lnbih7fSwgdGhpcy5wcm9wcywgdmlld3BvcnQpKTtcbiAgICB0aGlzLnN0YXRlLnByb3BzSW5UcmFuc2l0aW9uID0gbWFwU3RhdGUuZ2V0Vmlld3BvcnRQcm9wcygpO1xuXG4gICAgaWYgKHRoaXMucHJvcHMub25WaWV3cG9ydENoYW5nZSkge1xuICAgICAgdGhpcy5wcm9wcy5vblZpZXdwb3J0Q2hhbmdlKHRoaXMuc3RhdGUucHJvcHNJblRyYW5zaXRpb24pO1xuICAgIH1cblxuICAgIGlmIChzaG91bGRFbmQpIHtcbiAgICAgIHRoaXMuX2VuZFRyYW5zaXRpb24oKTtcbiAgICAgIHRoaXMucHJvcHMub25UcmFuc2l0aW9uRW5kKCk7XG4gICAgfVxuICB9XG59XG5cblRyYW5zaXRpb25NYW5hZ2VyLmRlZmF1bHRQcm9wcyA9IERFRkFVTFRfUFJPUFM7XG4iXX0=