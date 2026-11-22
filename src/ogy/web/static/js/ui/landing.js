// The page that shows an address: a part of an entity, workflow or decision opens its owner's page, anything else its own
// address. One place, so a row of the owed list and a path of a lifecycle agree on where a name leads.
const OWNERS = /^([^/]+\/[^/]+\/(?:entity|workflow|decision)\/[^/]+)(?:\/.*)?$/;

export function landing(address) {
  return `#/${OWNERS.exec(address)?.[1] ?? address}`;
}
