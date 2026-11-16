/*
 * Homepage carousel. Turns the "Latest field notes" Query Loop into one slide at a
 * time with previous, next, pause and per-slide buttons. Without this script the
 * five posts simply show one under another.
 */
( function () {
	'use strict';

	var DELAY = 6000;

	function pad( n ) {
		return ( n < 10 ? '0' : '' ) + n;
	}

	function button( cls, label, html ) {
		var b = document.createElement( 'button' );
		b.type = 'button';
		b.className = cls;
		b.setAttribute( 'aria-label', label );
		b.innerHTML = html;
		return b;
	}

	function setup( root ) {
		var list = root.querySelector( '.wp-block-post-template' );
		if ( ! list ) {
			return;
		}
		var slides = Array.prototype.slice.call( list.children );
		if ( slides.length < 2 ) {
			return;
		}

		var reduce = window.matchMedia && window.matchMedia( '(prefers-reduced-motion: reduce)' ).matches;
		var index = 0;
		var playing = ! reduce;
		var hovering = false;
		var timer = null;

		root.classList.add( 'is-carousel' );
		root.setAttribute( 'role', 'region' );
		root.setAttribute( 'aria-roledescription', 'carousel' );
		if ( ! root.getAttribute( 'aria-label' ) ) {
			root.setAttribute( 'aria-label', 'Latest field notes' );
		}
		list.setAttribute( 'aria-live', 'off' );

		slides.forEach( function ( s, i ) {
			s.setAttribute( 'role', 'group' );
			s.setAttribute( 'aria-roledescription', 'slide' );
			s.setAttribute( 'aria-label', ( i + 1 ) + ' of ' + slides.length );
		} );

		var bar = document.createElement( 'div' );
		bar.className = 'fn-carousel__controls';

		var arrows = '<svg width="20" height="20" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><polyline points="%"></polyline></svg>';
		var prev = button( 'fn-carousel__btn', 'Previous note', arrows.replace( '%', '15,5 8,12 15,19' ) );
		var next = button( 'fn-carousel__btn is-primary', 'Next note', arrows.replace( '%', '9,5 16,12 9,19' ) );
		var pause = button( 'fn-carousel__btn fn-carousel__pause', '', '' );

		var dotsWrap = document.createElement( 'div' );
		dotsWrap.className = 'fn-carousel__dots';
		var dots = slides.map( function ( s, i ) {
			var title = s.querySelector( '.wp-block-post-title' );
			var d = button( 'fn-carousel__dot', 'Show note ' + ( i + 1 ) + ( title ? ': ' + title.textContent.trim() : '' ), '<span></span>' );
			d.addEventListener( 'click', function () {
				go( i, true );
			} );
			dotsWrap.appendChild( d );
			return d;
		} );

		var counter = document.createElement( 'span' );
		counter.className = 'fn-carousel__count';

		var group = document.createElement( 'div' );
		group.className = 'fn-carousel__buttons';
		group.appendChild( prev );
		group.appendChild( next );
		group.appendChild( pause );
		bar.appendChild( group );
		bar.appendChild( dotsWrap );
		bar.appendChild( counter );
		root.appendChild( bar );

		function render() {
			slides.forEach( function ( s, i ) {
				var on = i === index;
				s.classList.toggle( 'is-active', on );
				s.hidden = ! on;
			} );
			dots.forEach( function ( d, i ) {
				d.classList.toggle( 'is-active', i === index );
				d.setAttribute( 'aria-current', i === index ? 'true' : 'false' );
			} );
			counter.textContent = pad( index + 1 ) + ' / ' + pad( slides.length );
			pause.textContent = playing ? 'Pause' : 'Play';
			pause.setAttribute( 'aria-label', playing ? 'Pause rotation' : 'Start rotation' );
			pause.setAttribute( 'aria-pressed', playing ? 'false' : 'true' );
		}

		function go( i, byUser ) {
			index = ( i + slides.length ) % slides.length;
			// Announce changes the reader asked for, not automatic ones.
			list.setAttribute( 'aria-live', byUser ? 'polite' : 'off' );
			render();
			restart();
		}

		function restart() {
			window.clearInterval( timer );
			timer = null;
			if ( playing ) {
				timer = window.setInterval( function () {
					if ( ! hovering ) {
						go( index + 1, false );
					}
				}, DELAY );
			}
		}

		prev.addEventListener( 'click', function () {
			go( index - 1, true );
		} );
		next.addEventListener( 'click', function () {
			go( index + 1, true );
		} );
		pause.addEventListener( 'click', function () {
			playing = ! playing;
			render();
			restart();
		} );

		root.addEventListener( 'mouseenter', function () {
			hovering = true;
		} );
		root.addEventListener( 'mouseleave', function () {
			hovering = false;
		} );
		root.addEventListener( 'focusin', function () {
			hovering = true;
		} );
		root.addEventListener( 'focusout', function ( e ) {
			if ( ! root.contains( e.relatedTarget ) ) {
				hovering = false;
			}
		} );
		root.addEventListener( 'keydown', function ( e ) {
			if ( e.target.closest( 'a, input, textarea' ) ) {
				return;
			}
			if ( e.key === 'ArrowLeft' ) {
				go( index - 1, true );
			} else if ( e.key === 'ArrowRight' ) {
				go( index + 1, true );
			}
		} );

		render();
		restart();
	}

	function init() {
		Array.prototype.forEach.call( document.querySelectorAll( '.fn-carousel' ), setup );
	}

	if ( document.readyState === 'loading' ) {
		document.addEventListener( 'DOMContentLoaded', init );
	} else {
		init();
	}
} )();
