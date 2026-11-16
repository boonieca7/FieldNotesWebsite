/* Editor view for the theme's small blocks: each shows its real output from the server. */
( function ( blocks, element, ServerSideRender, blockEditor ) {
	var el = element.createElement;
	var empty = function () {
		return null;
	};
	var perPost = { 'post-mark': true, 'journey-label': true, 'series-badge': true };

	[ 'brand', 'route', 'post-mark', 'journey-label', 'series-badge' ].forEach( function ( name ) {
		var full = 'fieldnotes/' + name;
		if ( blocks.getBlockType( full ) ) {
			return;
		}
		blocks.registerBlockType( full, {
			apiVersion: 3,
			title: full,
			category: 'theme',
			usesContext: perPost[ name ] ? [ 'postId' ] : [],
			attributes: perPost[ name ] ? { previewPostId: { type: 'number' } } : {},
			supports: { html: false },
			edit: function ( props ) {
				var attrs = perPost[ name ] && props.context && props.context.postId
					? { previewPostId: props.context.postId }
					: {};
				return el(
					'div',
					blockEditor.useBlockProps(),
					el( ServerSideRender, { block: full, attributes: attrs, EmptyResponsePlaceholder: empty } )
				);
			},
			save: function () {
				return null;
			},
		} );
	} );
} )( window.wp.blocks, window.wp.element, window.wp.serverSideRender, window.wp.blockEditor );
