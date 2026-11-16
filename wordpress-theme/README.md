# Field Notes From Abroad WordPress theme

`field-notes/` is the WordPress block theme for fieldnotesfromabroad.com, built from the same brand as the static site in this repository. `field-notes.zip` is the same folder packaged for WordPress's theme installer.

- Countries are post categories named after the country (Romania, Italy, Austria, Poland). The homepage map lights up every category whose slug matches a country in `inc/map-data.php`, so a new country only needs a new category. `tools/make-map-data.mjs` regenerates the outlines (Natural Earth 1:110m via the world-atlas npm package).
- Series are post tags: series-stories, series-chronicles, series-leadership.
- The homepage carousel is the five newest posts. `assets/js/carousel.js` adds the rotation and buttons.
- Each post gets the luggage tag, suitcase or postmark, chosen from its ID so it stays the same.

To change the theme, edit `field-notes/`, then rebuild the zip from this folder: `zip -r field-notes.zip field-notes`.
