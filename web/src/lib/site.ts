/**
 * Ett sted for alt som peker utover, og for det ene som mangler:
 * YouTube-ID-en. Når filmen er rendret og lastet opp, er dette den eneste
 * linja som må endres for at den skal dukke opp på siden.
 */

export const SITE = {
  url: "https://mnist.eivindgeiran.no",
  name: "Eivind Geiran",
  repo: "https://github.com/egeiran/mnist-neural-network",
  home: "https://eivindgeiran.no",

  /** Sett til YouTube-ID-en (delen etter ?v=) når filmen er publisert. */
  youtubeId: "" as string,

  /**
   * Kapitlene i filmen, med starttid i sekunder. Disse svarer til scenene i
   * scenes/ og til tidspunktene i manus.md. Lim samme liste inn i
   * YouTube-beskrivelsen, så får videoen kapittelmerker der også.
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
