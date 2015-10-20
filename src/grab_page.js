var page = require('webpage').create();
page.open('http://www.elysee.fr/declarations', function(status) {
  if (status == 'success') {
    var content = page.evaluate(function() {
      return document;
    })
    console.log(document);
    phantom.exit();
  }
});
