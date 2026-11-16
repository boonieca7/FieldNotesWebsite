(function () {
  var index = window.FN_INDEX || [];
  var form = document.querySelector('.search-form');
  var input = document.getElementById('q');
  var status = document.getElementById('status');
  var list = document.getElementById('results');

  function fold(s) { return s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, ''); }
  index.forEach(function (d) { d._x = fold(d.x); d._t = fold(d.t); });

  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text != null) e.textContent = text;
    return e;
  }

  function snippet(d, terms) {
    var lx = d._x, at = -1;
    for (var i = 0; i < terms.length && at < 0; i++) {
      var m = lx.match(new RegExp('(^|[^a-z0-9])' + terms[i].replace(/[.*+?^${}()|[\]\\]/g, '\\$&')));
      if (m) at = m.index + m[1].length;
    }
    if (at < 0) return d.s;
    var start = Math.max(0, at - 90), end = Math.min(d.x.length, at + 160);
    return (start > 0 ? '…' : '') + d.x.slice(start, end).trim() + (end < d.x.length ? '…' : '');
  }

  function run(q) {
    list.innerHTML = '';
    var terms = fold(q).split(/\s+/).filter(Boolean);
    if (!terms.length) { status.textContent = index.length + ' field notes. Type a word to search titles and text.'; return; }
    var res = terms.map(function (t) {
      return new RegExp('(^|[^a-z0-9])' + t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g');
    });
    var hits = index.map(function (d) {
      var score = 0;
      for (var i = 0; i < res.length; i++) {
        res[i].lastIndex = 0;
        var n = (d._x.match(res[i]) || []).length;
        if (!n) return null;
        res[i].lastIndex = 0;
        if (res[i].test(d._t)) score += 5;
        score += n;
      }
      return { d: d, score: score };
    }).filter(Boolean).sort(function (a, b) { return b.score - a.score; });
    status.textContent = hits.length
      ? hits.length + (hits.length === 1 ? ' note matches ' : ' notes match ') + '"' + q + '".'
      : 'Nothing matches "' + q + '". Try a single word, a place name, or browse the archive.';
    hits.forEach(function (h) {
      var li = el('li'), a = el('a');
      a.href = '../' + h.d.u;
      var meta = el('span', 'mono latest-meta');
      meta.appendChild(el('span', null, h.d.d));
      meta.appendChild(el('span', 'accent', h.d.j));
      var body = el('span', 'latest-body');
      body.appendChild(el('span', 'latest-title', h.d.t));
      body.appendChild(el('span', 'card-text', snippet(h.d, terms)));
      a.appendChild(meta); a.appendChild(body); li.appendChild(a); list.appendChild(li);
    });
  }

  var params = new URLSearchParams(location.search);
  input.value = params.get('q') || '';
  run(input.value);
  var t;
  input.addEventListener('input', function () {
    clearTimeout(t);
    t = setTimeout(function () {
      var url = new URL(location.href);
      if (input.value) url.searchParams.set('q', input.value); else url.searchParams.delete('q');
      try { history.replaceState(null, '', url); } catch (err) { /* file:// pages can refuse this */ }
      run(input.value);
    }, 150);
  });
  form.addEventListener('submit', function (e) { e.preventDefault(); run(input.value); });
})();
