// The viewer's own words of the Agent tab. The agent's title and sentences are authored text and never pass through here.
export const words = {
  nothing: "The agent has pointed at nothing.",
  back: "Back",
  next: "Next",
  dismiss: "Dismiss",
  show: "Show me",
  away: "Not on this page",
  request: "The agent asks you to look.",
  by: "Pointed out by",
  step: (at, of) => `${at} of ${of}`,
  calls: (count) => `Calls (${count})`,
  actions: { dismiss: "Dismissed", refused: "Refused" },
  connection: {
    connecting: "Connecting…",
    live: "Live",
    reconnecting: "Reconnecting; asking every 2 seconds",
  },
};
