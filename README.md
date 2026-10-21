# nuvio-art

Artwork for Ozzy's Nuvio collections (covers, hover GIFs, logos, backdrops), kept here so nothing depends on
third-party hosts.

- `mirror/` – copies of the third-party art the collections use (Kaptain, prism-wallpapers, Tumblr GIFs…).
  `mirror/urls.json` lists the sources; `.github/workflows/mirror.yml` downloads what is missing, optimises large
  stills and writes `mirror/map.json` (source URL → file here). Files are never deleted by the workflow.
- `art/` – our own designs (Universes, new studio / platform cards, actor portraits…), built by
  github.com/ObliviousTR/nuvio-awards and stored here.

Credits: mirrored art belongs to its creators (ImKaptain, bramst0ne/prism-wallpapers, luckynumb3rs and others);
it is kept only as a backup of what the collections already link to.
