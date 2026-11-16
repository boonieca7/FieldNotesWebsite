<?php
/**
 * Field Notes From Abroad theme.
 *
 * Adds the brand fonts and styles, the homepage carousel script, and five small
 * blocks used in the templates: the header brand, the journey list, a post's
 * travel mark, its journey label and its series badge.
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

require_once __DIR__ . '/inc/marks.php';
require_once __DIR__ . '/inc/map-data.php';

const FIELDNOTES_VERSION = '1.1.0';
const FIELDNOTES_FONTS   = 'https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700&family=IBM+Plex+Mono:wght@400;500&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400&display=swap';

/**
 * Countries are post categories named after the country (Romania, Italy). Any category
 * whose slug matches a country on the map counts, so a new country needs no code:
 * create the category, add posts to it, and it appears on the map.
 * Returns slug => array( term, mark ), most notes first.
 */
function fieldnotes_countries() {
	static $found = null;
	if ( null !== $found ) {
		return $found;
	}
	$map   = fieldnotes_map_countries();
	$terms = get_categories( array( 'hide_empty' => true ) );
	$terms = array_filter(
		$terms,
		function ( $t ) use ( $map ) {
			return isset( $map[ $t->slug ] );
		}
	);
	usort(
		$terms,
		function ( $a, $b ) {
			return $b->count - $a->count;
		}
	);
	$marks = array( 'tag', 'suitcase', 'postmark' );
	$found = array();
	foreach ( array_values( $terms ) as $i => $t ) {
		$found[ $t->slug ] = array( $t, $marks[ $i % 3 ] );
	}
	return $found;
}

/** Place categories from the first semester, shown after the country on a post ("Romania · Hunedoara"). */
function fieldnotes_places() {
	return array( 'timisoara', 'hunedoara', 'bucuresti', 'vienna', 'krakow', 'florence' );
}

/** Series are post tags. */
function fieldnotes_series() {
	return array(
		'series-stories'    => 'is-stories',
		'series-chronicles' => 'is-chronicles',
		'series-leadership' => 'is-leadership',
	);
}

add_action(
	'after_setup_theme',
	function () {
		add_theme_support( 'wp-block-styles' );
		add_theme_support( 'editor-styles' );
		add_editor_style( array( FIELDNOTES_FONTS, 'style.css', 'assets/editor.css' ) );
	}
);

add_action(
	'wp_enqueue_scripts',
	function () {
		wp_enqueue_style( 'fieldnotes-fonts', FIELDNOTES_FONTS, array(), null );
		wp_enqueue_style( 'fieldnotes', get_stylesheet_uri(), array(), FIELDNOTES_VERSION );
		if ( is_front_page() || is_home() ) {
			wp_enqueue_script( 'fieldnotes-carousel', get_theme_file_uri( 'assets/js/carousel.js' ), array(), FIELDNOTES_VERSION, array( 'strategy' => 'defer', 'in_footer' => true ) );
		}
	}
);

/* ------------------------------------------------------------------ marks */

/** One mark as inline SVG. Decorative, so hidden from screen readers. */
function fieldnotes_mark_svg( $name, $size = 48, $fg = 'currentColor', $bg = '#F5EEE6', $class = '' ) {
	$paths = fieldnotes_mark_paths();
	if ( ! isset( $paths[ $name ] ) ) {
		$name = 'tag';
	}
	$body = str_replace( array( '{FG}', '{BG}' ), array( esc_attr( $fg ), esc_attr( $bg ) ), $paths[ $name ] );
	return sprintf(
		'<svg class="fn-mark fn-mark--%1$s %4$s" width="%2$d" height="%2$d" viewBox="0 0 200 200" aria-hidden="true" focusable="false">%3$s</svg>',
		esc_attr( $name ),
		(int) $size,
		$body,
		esc_attr( $class )
	);
}

/** A post always gets the same mark, chosen from its ID, so the marks vary across posts. */
function fieldnotes_mark_for_post( $post_id ) {
	$names = array( 'tag', 'suitcase', 'postmark' );
	return $names[ absint( $post_id ) % 3 ];
}

/** The mark for whatever page is being shown: a journey's own, a post's, or the tag. */
function fieldnotes_mark_for_request() {
	if ( is_category() ) {
		$term = get_queried_object();
		$all  = fieldnotes_countries();
		if ( $term && isset( $all[ $term->slug ] ) ) {
			return $all[ $term->slug ][1];
		}
	}
	if ( is_singular() ) {
		return fieldnotes_mark_for_post( get_queried_object_id() );
	}
	return 'tag';
}

/** The post's country category and, if it has one, its place category. */
function fieldnotes_post_country( $post_id ) {
	$map     = fieldnotes_map_countries();
	$places  = fieldnotes_places();
	$country = null;
	$place   = null;
	foreach ( get_the_category( $post_id ) as $cat ) {
		if ( ! $country && isset( $map[ $cat->slug ] ) ) {
			$country = $cat;
		} elseif ( ! $place && in_array( $cat->slug, $places, true ) ) {
			$place = $cat;
		}
	}
	return $country ? array( $country, $place ) : null;
}

/* ----------------------------------------------------------------- blocks */

function fieldnotes_post_id_from( $attributes, $block ) {
	if ( ! empty( $attributes['previewPostId'] ) ) {
		return (int) $attributes['previewPostId'];
	}
	if ( isset( $block->context['postId'] ) ) {
		return (int) $block->context['postId'];
	}
	return get_the_ID();
}

add_action(
	'init',
	function () {
		wp_register_script(
			'fieldnotes-blocks-editor',
			get_theme_file_uri( 'assets/js/blocks-editor.js' ),
			array( 'wp-blocks', 'wp-element', 'wp-server-side-render', 'wp-block-editor' ),
			FIELDNOTES_VERSION,
			true
		);

		$post_attrs = array( 'previewPostId' => array( 'type' => 'number' ) );
		$common     = array(
			'api_version'   => 3,
			'editor_script' => 'fieldnotes-blocks-editor',
			'category'      => 'theme',
			'supports'      => array( 'html' => false ),
		);

		register_block_type(
			'fieldnotes/brand',
			$common + array(
				'title'           => 'Field Notes brand',
				'render_callback' => function () {
					return sprintf(
						'<a class="fn-brand" href="%1$s" rel="home">%2$s<span class="fn-brand__words"><span class="fn-brand__name">Field Notes</span><span class="fn-brand__sub">From Abroad</span></span></a>',
						esc_url( home_url( '/' ) ),
						fieldnotes_mark_svg( fieldnotes_mark_for_request(), 52, '#F5EEE6', '#1C2F3C' )
					);
				},
			)
		);

		register_block_type(
			'fieldnotes/route',
			$common + array(
				'title'           => 'Map of countries',
				'render_callback' => 'fieldnotes_render_map',
			)
		);

		register_block_type(
			'fieldnotes/post-mark',
			$common + array(
				'title'           => 'Post travel mark',
				'attributes'      => $post_attrs,
				'uses_context'    => array( 'postId' ),
				'render_callback' => function ( $attributes, $content, $block ) {
					$id = fieldnotes_post_id_from( $attributes, $block );
					return '<div ' . get_block_wrapper_attributes( array( 'class' => 'fn-sticker' ) ) . '>' . fieldnotes_mark_svg( fieldnotes_mark_for_post( $id ), 96, '#1C2F3C', '#F5EEE6' ) . '</div>';
				},
			)
		);

		register_block_type(
			'fieldnotes/journey-label',
			$common + array(
				'title'           => 'Post country label',
				'attributes'      => $post_attrs,
				'uses_context'    => array( 'postId' ),
				'render_callback' => function ( $attributes, $content, $block ) {
					$found = fieldnotes_post_country( fieldnotes_post_id_from( $attributes, $block ) );
					if ( ! $found ) {
						return '';
					}
					list( $country, $place ) = $found;
					$out = sprintf( '<a href="%1$s">%2$s</a>', esc_url( get_category_link( $country ) ), esc_html( $country->name ) );
					if ( $place ) {
						$out .= sprintf( ' · <a href="%1$s">%2$s</a>', esc_url( get_category_link( $place ) ), esc_html( $place->name ) );
					}
					return '<span class="fn-journey-label">' . $out . '</span>';
				},
			)
		);

		register_block_type(
			'fieldnotes/series-badge',
			$common + array(
				'title'           => 'Post series badge',
				'attributes'      => $post_attrs,
				'uses_context'    => array( 'postId' ),
				'render_callback' => function ( $attributes, $content, $block ) {
					$tags = get_the_tags( fieldnotes_post_id_from( $attributes, $block ) );
					if ( ! $tags ) {
						return '';
					}
					$series = fieldnotes_series();
					foreach ( $tags as $tag ) {
						if ( isset( $series[ $tag->slug ] ) ) {
							return sprintf(
								'<a class="fn-badge %1$s" href="%2$s">%3$s</a>',
								esc_attr( $series[ $tag->slug ] ),
								esc_url( get_tag_link( $tag ) ),
								esc_html( $tag->name )
							);
						}
					}
					return '';
				},
			)
		);
	}
);

/**
 * The homepage map: every country outlined, the ones with notes filled in and linked,
 * then the same countries as a list of cards for anyone who would rather not use the map.
 */
function fieldnotes_render_map() {
	$map     = fieldnotes_map_countries();
	$visited = fieldnotes_countries();

	$shapes = '';
	$labels = '';
	foreach ( $map as $slug => $c ) {
		list( $name, $x, $y, $d ) = $c;
		if ( ! isset( $visited[ $slug ] ) ) {
			$shapes .= '<path class="fn-map__land" d="' . esc_attr( $d ) . '"></path>';
		}
	}
	foreach ( $visited as $slug => $v ) {
		list( $term ) = $v;
		list( $name, $x, $y, $d ) = $map[ $slug ];
		$notes   = sprintf( _n( '%d note', '%d notes', $term->count, 'field-notes' ), $term->count );
		$shapes .= sprintf(
			'<a class="fn-map__visited" href="%1$s" aria-label="%2$s, %3$s"><path d="%4$s"></path></a>',
			esc_url( get_category_link( $term ) ),
			esc_attr( $term->name ),
			esc_attr( $notes ),
			esc_attr( $d )
		);
		if ( $x >= 0 ) {
			$labels .= sprintf(
				'<g class="fn-map__label" transform="translate(%1$d %2$d)" aria-hidden="true"><circle r="5"></circle><text x="10" y="-4" class="fn-map__name">%3$s</text><text x="10" y="13" class="fn-map__count">%4$s</text></g>',
				$x,
				$y,
				esc_html( strtoupper( $term->name ) ),
				esc_html( strtoupper( $notes ) )
			);
		}
	}

	$svg = '<svg class="fn-map__svg" viewBox="100 150 640 470" role="group" aria-label="Map of the countries these notes come from"><rect class="fn-map__sea" x="0" y="0" width="800" height="640"></rect>' . $shapes . $labels . '</svg>';

	$cards = '';
	foreach ( $visited as $slug => $v ) {
		list( $term, $mark ) = $v;
		$cards .= sprintf(
			'<li><a class="fn-chip" href="%1$s">%2$s<span class="fn-chip__words"><span class="fn-chip__num">%3$s</span><span class="fn-chip__name">%4$s</span></span></a></li>',
			esc_url( get_category_link( $term ) ),
			fieldnotes_mark_svg( $mark, 40, '#1C2F3C', '#FFFFFF' ),
			esc_html( sprintf( _n( '%d note', '%d notes', $term->count, 'field-notes' ), $term->count ) ),
			esc_html( $term->name )
		);
	}

	return '<div class="fn-map"><div class="fn-map__frame">' . $svg . '</div><ul class="fn-route">' . $cards . '</ul></div>';
}
