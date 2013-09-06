/**
 * Javascript for pyarchives_enhanced.py. See the README for details.
 *
 * Copyright 2008 Klaus Trainer
 *
 * Permission is hereby granted, free of charge, to any person
 * obtaining a copy of this software and associated documentation
 * files (the "Software"), to deal in the Software without restriction,
 * including without limitation the rights to use, copy, modify,
 * merge, publish, distribute, sublicense, and/or sell copies of the
 * Software, and to permit persons to whom the Software is furnished
 * to do so, subject to the following conditions:
 * 
 * The above copyright notice and this permission notice shall be
 * included in all copies or substantial portions of the Software.
 * 
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
 * EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
 * OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
 * NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
 * BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
 * ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
 * CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
*/

var ccn = "clicker";
var clcn = "closed";
var opcn = "open";

function getElementsByTagAndClassName(tag, cname) {
	var tags = document.getElementsByTagName(tag);
	var cEls = new Array();
	for (i = 0; i < tags.length; i++) {
		var rE = new RegExp("(^|\s)" + cname + "(\s|$)");
		if (rE.test(tags[i].className)) {
			cEls.push(tags[i]);
		}
	}
	return cEls;
}

function toggleNextOpenClose(el) {
	var next = el.nextSibling;
	el.className = el.className.replace(new RegExp(opcn + "\\b"), "");
	el.className = el.className.replace(new RegExp(clcn + "\\b"), "");
	while(next.nodeType != 1)
		next = next.nextSibling;
	next.style.display = (next.style.display == "none" ? "block" : "none");
	el.className +=
		(next.style.display == "block" ? " " + opcn : " " + clcn);
}

function toggleNextByTagAndClassName(tag, cname) {
	clickers = getElementsByTagAndClassName(tag, cname);
	for (i = 0; i < clickers.length; i++) {
		clickers[i].className += " " + ccn;
		clickers[i].className += " " + clcn;
		clickers[i].onclick = function() {
			toggleNextOpenClose(this);
		}
		toggleNextOpenClose(clickers[i]);
	}
}


function addEvent(obj, type, fn) {
	if (obj.addEventListener) {
		obj.addEventListener(type, fn, false);
		EventCache.add(obj, type, fn);
	} else if (obj.attachEvent) {
		obj["e" + type + fn] = fn;
		obj[type + fn] = function() {
			obj["e" + type + fn](window.event);
		}
		obj.attachEvent("on" + type, obj[type + fn]);
		EventCache.add(obj, type, fn);
	} else {
		obj["on" + type] = obj["e" + type + fn];
	}
}
	
var EventCache = function() {
	var listEvents = [];
	return {
		listEvents : listEvents,
		add : function(node, sEventName, fHandler, bCapture) {
			listEvents.push(arguments);
		},
		flush : function() {
			var i, item;
			for (i = listEvents.length - 1; i >= 0; i = i - 1) {
				item = listEvents[i];
				if(item[0].removeEventListener) {
					item[0].removeEventListener(item[1],
						item[2], item[3]);
				};
				if (item[1].substring(0, 2) != "on") {
					item[1] = "on" + item[1];
				};
				if (item[0].detachEvent) {
					item[0].detachEvent(item[1], item[2]);
				};
				item[0][item[1]] = null;
			};
		}
	};
}();
	
	
function pageLoaders(e) {
	toggleNextByTagAndClassName("div", "archiveYear");
	toggleNextByTagAndClassName("div", "archiveMonth");
}

addEvent(window, "unload", EventCache.flush);
addEvent(window, "load", pageLoaders);
