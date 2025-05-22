import { upperFirst, includes } from "lodash";

function ensureSentenceEnd(str) {
  const validEndChars = ".?!";
  str = str.trim();
  return includes(validEndChars, str.charAt(str.length - 1)) ? str : str + ".";
}

export function sentenceTypoCheck(str) {
  return upperFirst(ensureSentenceEnd(str));
}

export function textToHtml(str) {
  return str.replace(/\n/g, "<br>");
}
