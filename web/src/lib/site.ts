/** Ett sted for alt siden peker utover til. */

export const SITE = {
  url: "https://mnist.eivindgeiran.no",
  name: "Eivind Geiran",
  repo: "https://github.com/egeiran/mnist-neural-network",
  home: "https://eivindgeiran.no",

  /** YouTube-ID-en (delen etter ?v= eller youtu.be/). */
  youtubeId: "3KQHb3Rx8PM" as string,

  /**
   * Kapitlene vises bare når tidene under er målt på den publiserte filmen.
   * Et kapittelmerke som hopper til feil sted er verre enn ingen kapitler, så
   * de holdes skjult så lenge tidene er anslag.
   */
  chaptersVerified: false,

  /**
   * Kapitlene i filmen, med starttid i sekunder. Én per scene i scenes/.
   * Tidene her er scenegrensene fra manus.md — altså anslag, ikke målinger.
   */
  chapters: [
    { at: 0, no: "Problemet", en: "The problem" },
    { at: 45, no: "Fra bilde til tall", en: "From image to numbers" },
    { at: 85, no: "Ett nevron", en: "One neuron" },
    { at: 155, no: "Sigmoid, og hvorfor", en: "Sigmoid, and why" },
    { at: 195, no: "Lag og matriser", en: "Layers and matrices" },
    { at: 235, no: "Forward pass og tap", en: "Forward pass and loss" },
    { at: 275, no: "Gradient descent", en: "Gradient descent" },
    { at: 315, no: "Backpropagation", en: "Backpropagation" },
    { at: 355, no: "Var det riktig?", en: "Was it right?" },
    { at: 380, no: "Trening", en: "Training" },
    { at: 410, no: "Hva den lærte", en: "What it learned" },
  ],
} as const;
