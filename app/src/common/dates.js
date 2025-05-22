export const DEFAULT_DAYS = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"];

// Adding a getDayName and getMonthName to Javascript dates
Date.prototype.monthNames = [
  "Janvier",
  "Février",
  "Mars",
  "Avril",
  "Mai",
  "Juin",
  "Juillet",
  "Août",
  "Septembre",
  "Octobre",
  "Novembre",
  "Décembre",
];
Date.prototype.getMonthName = function () {
  return this.monthNames[this.getMonth()];
};
Date.prototype.getShortMonthName = function () {
  return this.getMonthName().substr(0, 3);
};
Date.prototype.dayNames = ["Dimanche", "Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi"];
Date.prototype.getDayName = function () {
  return this.dayNames[this.getDay()];
};
Date.prototype.getShortDayName = function () {
  return this.getDayName().substr(0, 3);
};
Date.prototype.toDateString = function () {
  let day = this.getDate();
  let month = this.getMonth() + 1;
  if (day <= 9) {
    day = "0" + day;
  }
  if (month <= 9) {
    month = "0" + month;
  }
  return this.getFullYear() + "-" + month + "-" + day;
};

export function addDays(date, nbDays) {
  if (date.getHours() > 0) {
    console.log("WARNING : dont call addDays with a date with hours != 0 or minutes != 0 or seconds != 0");
  }
  // We add to the date  24H * nbDays + 6H (making sure we don't change day because of time shifting
  let res = new Date(date.getTime() + (nbDays * 24 + 6) * 60 * 60 * 1000);
  // We rebuild a day at noon
  res = new Date(res.getFullYear(), res.getMonth(), res.getDate());
  return res;
}

export function addMonths(date, nbMonths) {
  const year = date.getFullYear() + Math.floor((date.getMonth() + nbMonths) / 12);
  const month = (date.getMonth() + nbMonths) % 12;
  const maxDate = new Date(year, month + 1, 0).getDate();
  return new Date(year, month, Math.min(maxDate, date.getDate()));
}

export function areSameDate(date1, date2) {
  return (
    date1.getDate() == date2.getDate() && date1.getMonth() == date2.getMonth() && date1.getYear() == date2.getYear()
  );
}

/*
 * Returns a date which is N years ago
 */
export function nYearsAgo(nbYears) {
  const d = todayAtMidnight();
  return addDays(d, -365 * nbYears);
}

/*
 * Returns day + 24h
 */
export function nextDay(date) {
  return addDays(date, 1);
}

/*
 * Returns day - 24h
 */
export function previousDay(date) {
  return addDays(date, -1);
}

/*
 * Returns day + 6 days
 */
export function weekEndFromWeekStart(date) {
  return addDays(date, 6);
}

/*
 * Returns tomorrow
 */
export function tomorrow() {
  const in24H = nextDay(todayAtMidnight());
  return new Date(in24H.getFullYear(), in24H.getMonth(), in24H.getDate());
}

/*
 * Returns true if it is today
 */
export function isToday(date) {
  date = new Date(date);
  const now = new Date();
  return (
    date.getFullYear() == now.getFullYear() && date.getMonth() == now.getMonth() && date.getDate() == now.getDate()
  );
}

/*
 * Returns true if date is before reference (considering only the day)
 * if they are same days, return includeSame
 */
export function isDateBefore(date, reference, includeSame) {
  if (date.getFullYear() < reference.getFullYear()) {
    return true;
  }
  if (reference.getFullYear() < date.getFullYear()) {
    return false;
  }
  if (date.getMonth() < reference.getMonth()) {
    return true;
  }
  if (reference.getMonth() < date.getMonth()) {
    return false;
  }
  if (date.getDate() < reference.getDate()) {
    return true;
  }
  if (reference.getDate() < date.getDate()) {
    return false;
  }

  return includeSame;
}

/*
 * Returns true if date is after reference (considering only the day)
 * if they are same days, return includeSame
 */
export function isDateAfter(date, reference, includeSame) {
  return !isDateBefore(date, reference, !includeSame);
}

export function isPast(date) {
  return isDateBefore(date, new Date());
}

export function isFuture(date) {
  return isDateAfter(date, new Date());
}

/*
 * Returns next monday
 */
export function nextMonday() {
  let nextMonday = todayAtMidnight();
  do {
    // Adding one day
    nextMonday = addDays(nextMonday, 1);
  } while (nextMonday.getDay() != 1);
  return new Date(nextMonday.getFullYear(), nextMonday.getMonth(), nextMonday.getDate());
}

/*
 * Modify a date so that hours = minutes = seconds = 0
 */
export function setDateToMidnight(date) {
  date.setHours(0);
  date.setMinutes(0);
  date.setSeconds(0);
  date.setMilliseconds(0);
}

export function todayAtMidnight() {
  const res = new Date();
  setDateToMidnight(res);
  return res;
}

/*
 * Returns previous monday (can be today)
 */
export function previousMonday() {
  let monday = todayAtMidnight();
  while (monday.getDay() != 1) {
    // Substracting one day
    monday = addDays(monday, -1);
  }
  return new Date(monday.getFullYear(), monday.getMonth(), monday.getDate());
}

export function dateSecondsDifference(firstDate, secondDate) {
  const secondDuration = 1000;
  firstDate = Date.parse(firstDate);
  secondDate = Date.parse(secondDate);
  return Math.floor(Math.abs(firstDate - secondDate) / secondDuration);
}

export function dateDaysDifference(firstDate, secondDate) {
  const dayDuration = 24 * 60 * 60 * 1000; // hours * minutes * seconds * miliseconds
  firstDate = Date.parse(firstDate);
  secondDate = Date.parse(secondDate);
  return Math.round(Math.abs(firstDate - secondDate) / dayDuration);
}

/*
 * Returns a date from a string in the following format : 'YYYY-mm-dd'
 */
export function stringToDate(dateStr) {
  // WARNING: don't use the Date constructor, it doesn't work the same way on every browser
  if (!dateStr) {
    return null;
  }
  const dateValues = dateStr.split("-");
  return new Date(dateValues[0], dateValues[1] - 1, dateValues[2]); // JS nonsense : months start at 0
}

export function ageFromBirth(input) {
  const totalYearMiliseconds = 1000 * 60 * 60 * 24 * 365.25;

  if (!input) {
    return null;
  }
  const birthDate = new Date(input);
  return ~~((Date.now() - birthDate) / totalYearMiliseconds);
}
