# Reference the Previous Sheet in Google Spreadsheets

I'm maintaining this soccer stats sheet and have different games on different sheets.  To build up sums
I like to reference data from the previous sheet.  It took me some trial and error to get going.  Essentially
it requires a custom function and the use of `INDIRECT`.

For the custom function go to `Tools > Script Editor` and paste the following code

```javascript
/**
 * Retrieves a reference to the previous sheet, or null
 * input is unused.
 */
function prevSheet(input) {
  var sheet = SpreadsheetApp.getActiveSpreadsheet();
  var sheets = sheet.getSheets();
  var prev = null;
  for(var i = 0; i < sheets.length; i++) {
    if (sheets[i].getSheetId() == sheet.getSheetId()) {
      return prev.getName();
    }
    prev = sheets[i];
  }
  return null;
};
```

The code is also available [here](
https://script.google.com/macros/s/AKfycbyY4tY4f1u6WqJY2AXHzb4Mvqk1sahQadgwc5JPj0CdrwAlLKd8/exec) as an add-on.

To use the function you need to use the `INDIRECT` function, for example to reference cell `A2`
on the previous sheet:

```
=INDIRECT("'" & prevSheet(GoogleClock()) & "'!A2")
```

Enjoy.

[This](http://webapps.stackexchange.com/questions/16009/display-sheet-name-in-google-spreadsheet) was very helpful to get me started.
