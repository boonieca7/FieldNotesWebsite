# Field Notes From Abroad WordPress theme

`field-notes/` is the WordPress block theme for fieldnotesfromabroad.com, built from the same brand as the static site in this repository. `field-notes.zip` is the same folder packaged for WordPress's theme installer.

- Journeys are post categories (timisoara, hunedoara, bucuresti, vienna, krakow, florence, back-in-romania). The list and each journey's mark are in `fieldnotes_journeys()` in `functions.php`.
- Series are post tags: series-stories, series-chronicles, series-leadership.
- The homepage carousel is the five newest posts. `assets/js/carousel.js` adds the rotation and buttons.
- Each post gets the luggage tag, suitcase or postmark, chosen from its ID so it stays the same.

To change the theme, edit `field-notes/`, then rebuild the zip from this folder: `zip -r field-notes.zip field-notes`.
