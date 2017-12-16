"""Variables for gallery.py."""

"""root = '/Volumes/Local_stuff/zdjecia_ubranek/chlopiec_56'  # path to jpgs or folders of jpgs and output root"""
tmp = '/tmp'              # temporary folder to move corrupt files to
index = 'index.html'      # filename for html files
index_mini = 'index_mini.html' # index with only thumbs gallery'
n_thumbs = 6              # number of thumbnails to display on index page
min_size = 1000,1000        # minimum dimensions required to create thumbnail
thumb_size = 1000,1000      # dimensions of thumbnail to create

header = ("""<!doctype html>
<html>
<head>
  <title>%s</title>
  <meta charset="utf-8" />
  <meta http-equiv="Content-type" content="text/html; charset=utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <style type="text/css">
	#photos {
	   /* Prevent vertical gaps */
	   line-height: 0;

	   -webkit-column-count: 5;
	   -webkit-column-gap:   0px;
	   -moz-column-count:    5;
	   -moz-column-gap:      0px;
	   column-count:         5;
	   column-gap:           0px;
	}

	#photos img {
	  /* Just in case there are inline attributes */
	  width: 100%% !important;
	  height: auto !important;
	}

	@media (max-width: 1200px) {
	  #photos {
	  -moz-column-count:    4;
	  -webkit-column-count: 4;
	  column-count:         4;
	  }
	}
	@media (max-width: 1000px) {
	  #photos {
	  -moz-column-count:    3;
	  -webkit-column-count: 3;
	  column-count:         3;
	  }
	}
	@media (max-width: 800px) {
	  #photos {
	  -moz-column-count:    2;
	  -webkit-column-count: 2;
	  column-count:         2;
	  }
	}
	@media (max-width: 400px) {
	  #photos {
	  -moz-column-count:    1;
	  -webkit-column-count: 1;
	  column-count:         1;
	  }
	}
    body {
      background-color: #FFFFFF;
      color: gray;
      font-family: "Open Sans", "Helvetica Neue", Helvetica, Arial, sans-serif;
      margin: 2;
      padding: 2;
    }
    div {
      background-color: #FFFFFF;
      border-radius: 0.25em;
      border-color: #000000;
      margin: 1em auto;
      width: 1000px;
    }
    p {
      font-size: 16px;
      padding-bottom: 1.5em;
    }
    a:link, a:visited {
      color: #93a1a1;
      font-size: 24px;
      text-decoration: underline;
    }
    .image {
     margin-right: 5px;
     padding: 2px;
     background-color: #fff;
    }
    tr {
      padding: 3px;
    }
    td {
      padding: 3px;
    }
    table {
      width: 1000px;
    }
    img {
      background-color: #FFF;
      width: 100%%;
      height: 100%%
      padding: 3px;
      border-color: #000;
      border-radius: 0.4em;
      align: center;
    }
  </style>
</head>
<body>
<div>
""")

br = '\n<br>'
columns = 2
threads = 2
thread_sleep = 2
font_size_full = 100
font_size_thumb = 50
footer = '\n</div></body></html>'
img_src = '\n<img src="%s">'
timestamp = '\n<p>This page was created on %s</p>'
url_dir = '\n<p><a href="%s" target="_blank">%s</a></p>'
url_img = '\n<td class="image"><a href="%s" target="_blank"><img title="%s" src="%s"></a></td>'
images = '\n<img title="%s" src="%s">'

