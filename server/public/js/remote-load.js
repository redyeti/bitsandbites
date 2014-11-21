"use strict";

$(function(){
	$(".remote").each(function(){
		var $this = $(this);
		$this.text("Please wait ...");
		var src = $this.data("src");
		var argscopy = $this.data("argscopy");
		if (argscopy) {
			var args = location.search.substr(1);
		} else {
			var args = $this.data("args");
		}
		$this.load("/cgi-bin/"+src+".cgi", args);
	})
})
