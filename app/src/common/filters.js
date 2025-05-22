export function conversionClean(conversion, foodName) {
  const conversionName = conversion.unit.toLowerCase();

  if (conversion.grams <= 4 && conversionName.indexOf("pincée") == -1) {
    return "un peu";
  }

  if (foodName && conversionName === foodName.toLowerCase()) {
    // If foodName is conversionName, just keep the numbers
    return conversion.htmlValue;
  }

  return conversion.htmlValue + " " + conversionName;
}
