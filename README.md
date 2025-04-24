# Grants monitoring bot

AusTender emails - CSV attachment. Parse URL from row[4]. Fetch webpage and parse out:
  - <span><label for="Description">Description</label>:</span>
  - div.list-desc-inner sibling of above element
  - parse internal text for tender description

We are looking for a `div.list-desc-inner` element which is the sibling of a  `<span><label for="Description">Description</label>:</span>` element. That will give us the description, which is all we need for now.
