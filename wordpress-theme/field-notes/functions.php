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

const FIELDNOTES_VERSION = '1.0.0';
const FIELDNOTES_FONTS   = 'https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700&family=IBM+Plex+Mono:wght@400;500&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400&display=swap';

/**
 * The journeys, in route order. Each is a post category; the mark is the one its
 * journey page and its chip on the homepage always use.
 */
function fieldnotes_journeys() {
	return array(
		'timisoara'       => array( 'num' => '01', 'mark' => 'tag' ),
		'hunedoara'       => array( 'num' => '02', 'mark' => 'suitcase' ),
		'bucuresti'       => array( 'num' => '03', 'mark' => 'postmark' ),
		'vienna'          => array( 'num' => '04', 'mark' => 'tag' ),
		'krakow'          => array( 'num' => '05', 'mark' => 'suitcase' ),
		'florence'        => array( 'num' => '06', 'mark' => 'postmark' ),
		'back-in-romania' => array( 'num' => '07', 'mark' => 'tag' ),
	);
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
		add_editor_style( array( FIELDNOTES_FONTS, 'style.css' ) );
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
		$all  = fieldnotes_journeys();
		if ( $term && isset( $all[ $term->slug ] ) ) {
			return $all[ $term->slug ]['mark'];
		}
	}
	if ( is_singular() ) {
		return fieldnotes_mark_for_post( get_queried_object_id() );
	}
	return 'tag';
}

/** The post's journey category, if it has one. */
function fieldnotes_post_journey( $post_id ) {
	$all = fieldnotes_journeys();
	foreach ( get_the_category( $post_id ) as $cat ) {
		if ( isset( $all[ $cat->slug ] ) ) {
			return array( $cat, $all[ $cat->slug ] );
		}
	}
	return null;
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
				'title'           => 'Journey list',
				'render_callback' => function () {
					$out = '<ul class="fn-route">';
					foreach ( fieldnotes_journeys() as $slug => $j ) {
						$cat = get_category_by_slug( $slug );
						if ( ! $cat ) {
							continue;
						}
						$out .= sprintf(
							'<li><a class="fn-chip" href="%1$s">%2$s<span class="fn-chip__words"><span class="fn-chip__num">%3$s · %4$d notes</span><span class="fn-chip__name">%5$s</span></span></a></li>',
							esc_url( get_category_link( $cat ) ),
							fieldnotes_mark_svg( $j['mark'], 40, '#1C2F3C', '#FFFFFF' ),
							esc_html( $j['num'] ),
							(int) $cat->count,
							esc_html( $cat->name )
						);
					}
					return $out . '</ul>';
				},
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
					return '<div class="fn-sticker">' . fieldnotes_mark_svg( fieldnotes_mark_for_post( $id ), 96, '#1C2F3C', '#F5EEE6' ) . '</div>';
				},
			)
		);

		register_block_type(
			'fieldnotes/journey-label',
			$common + array(
				'title'           => 'Post journey label',
				'attributes'      => $post_attrs,
				'uses_context'    => array( 'postId' ),
				'render_callback' => function ( $attributes, $content, $block ) {
					$found = fieldnotes_post_journey( fieldnotes_post_id_from( $attributes, $block ) );
					if ( ! $found ) {
						return '';
					}
					list( $cat, $j ) = $found;
					return sprintf(
						'<a class="fn-journey-label" href="%1$s">Journey %2$s · %3$s</a>',
						esc_url( get_category_link( $cat ) ),
						esc_html( $j['num'] ),
						esc_html( $cat->name )
					);
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
