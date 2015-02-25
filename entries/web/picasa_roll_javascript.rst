Javascript based Picasa photo roll on your webpage


From the department of 5-minute Javascript hacks comes this
little gem, which handles the 'Random photo' to the right.
It uses the JSON-API Google API to get the data from the
Picasa-Web-Albums.

::

 <script><!-- //http://code.google.com/apis/gdata/docs/json.html
 // Creative Commons Attribution-ShareAlike 3.0 Unported License
 // http://creativecommons.org/licenses/by-sa/3.0/
 // (c) Jan Dittmer <jdi@l4x.org> 2010
 var es = [];
 function r() {
 	var idx = Math.floor(Math.random()*es.length);
 	var m = es[idx]['media\$group'];
 	var i = document.getElementById("i");
 	document.getElementById("t").innerHTML = m['media\$description']['\$t'];
 	i.src = m['media\$thumbnail'][0]['url'];
 	setTimeout("r();",10*1000);
 }
 function j(p) {
 	es = p['feed']['entry'];
 	r();
 }
 function picasa() {
 	var url='http://picasaweb.google.com/data/feed/base/user/jan.dittmer' +
 		'?kind=photo&thumbsize=160c&access=public&alt=json&callback=j';
 	var s = document.createElement('script');
 	s.src = url; document.body.appendChild(s);
 }
 window.onload = picasa;
 //--></script>
 <a href="http://picasaweb.google.com/jan.dittmer"> <img id="i"> </a>
 <div id="t"></div>

[[!meta date="2010-08-20 20:56:49"]]
