import $ from "jquery";
import store from "@/store/index.js";

const TUTORIALS = {
  menuTutorial: [
    {
      xquery: "#menu-elt-calendar",
      content: "Obtenez des idées repas pour chaque jour de la semaine",
      position: "bottom",
    },
    {
      xquery: "#menu-elt-shopping-list",
      content: "Une fois les jours planifiés, créez votre liste de courses en 1 clic",
      position: "bottom",
    },
    {
      xquery: "#menu-elt-config",
      content: "Pour aller plus loin : personnalisez vos goûts, votre foyer, la structure de vos repas, ...",
      position: "bottom",
    },
    { xquery: "th.clickable_meal_slot", content: "Cliquez tout d'abord sur un jour pour commencer", position: "top" },
  ],
  // firstDayPlanner: [
  //     {"xquery": '.dish-slot:nth-of-type(1)',
  //     "content": "Cliquez sur une proposition de repas pour la changer",
  //      "position": "top"},
  //     {"xquery": 'op-day-mosaic .meal-slot-header .meal-settings:nth-of-type(1)',
  //     "content": "Ici, vous pouvez modifier les personnes présentes, le temps disponible.",
  //      "position": "top"}
  // ],
};

function pursueTutorial(tutorialKey, step) {
  const tutorial = TUTORIALS[tutorialKey];

  if (step === 0) {
    // Showing empty modal for getting the fade and backdrop effect
    store.commit("dialog/showTutorialOverlay");
  }

  if (step > 0) {
    // Removing previous step
    $(".tutorial-step").remove();
  }
  if (step == tutorial.length) {
    // End of tutorial
    // Hiding empty modal
    store.commit("dialog/hideTutorialOverlay");
    return;
  }

  const { xquery, content, position } = tutorial[step];
  const nextJsCode = `pursueTutorial('${tutorialKey.trim()}', ${step + 1})`; // Action : going to next tutorial step
  const thisStepId = `tutorial-step-${step}`;
  const classes = `tutorial-step tutorial-pos-${position}`;
  const whiteTriangle = require("@/assets/img/white_triangle.png");

  // Creating popup
  const popupContent = `
<div class="${classes}" id="${thisStepId}">
  <div class="tutorial-center">
    <img src="${whiteTriangle}" class="tutorial-pointer-top" />
  </div>
  <div class="tutorial-step-text">${content}</div>
  <div class="btn btn-success" onClick="${nextJsCode}">Ok</div>
  <div class="tutorial-center">
    <img src="${whiteTriangle}" class="tutorial-pointer-bottom" />
  </div>
</div>`;

  // Retrieving focused component
  let elt = $(xquery);
  if (elt.length === 0) {
    console.log("element not found");
    // Security : element not found - aborting
    pursueTutorial(tutorialKey, tutorial.length);
    return;
  }

  if (elt.length > 0) {
    // Multiple elements ? Take first in the DOM
    elt = $(elt[0]);
  }

  // Append or prepend the popup to the focused element
  if (position == "bottom") {
    elt.append(popupContent);
  } else {
    elt.prepend(popupContent);
  }

  setTimeout(() => {
    // Center the popup
    const stepElt = $(`#${thisStepId}`);
    stepElt.css("margin-left", "-" + (stepElt.outerWidth() / 2 - elt.outerWidth() / 2).toString() + "px");

    // Putting the popup over the element
    if (position == "top") {
      stepElt.css("margin-top", "-" + (stepElt.outerHeight() + 20).toString() + "px");
    }
    // Display it !
    stepElt.css("visibility", "visible");
  }, 100);
}

// Necessary to be able to do onclick="pursueTutorial"
window.pursueTutorial = pursueTutorial;

export function startTutorial(tutorialKey) {
  if ($(document).width() < 900) {
    console.log("no tutorial on small screen");
    return;
  }
  pursueTutorial(tutorialKey, 0);
}
