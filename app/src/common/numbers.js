// @return [float] a random number between min and max (or 0 and min if max is undefined)
export function randFloat(min, max) {
  if (!max) {
    max = min;
    min = 0.0;
  }
  return Math.random() * (max - min) + min;
}

// @return [integer] a random int between min and max (or 0 and min if max is undefined)
export function randInt(min, max) {
  if (!max) {
    max = min;
    min = 0.0;
  }
  return Math.round(Math.random() * (max - min) + min);
}
