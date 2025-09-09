#!/usr/bin/env bash
set -euo pipefail
REPO="${REPO:-atillaorgunmat/qchain-starter}"

json="$(gh issue list -R "$REPO" --state open --limit 200 --json number,title,labels)"

cmds="$(
  jq -r --arg repo "$REPO" '
    def normhyp(s): s | gsub("[\u2010-\u2015]"; "-");
    .[] as $i
    | (normhyp($i.title)) as $t
    | ($t | capture("^(?<id>(Q-[A-Z0-9-]+|UNK-[A-Z0-9-]+)):" )? ) as $m
    | if ($m|type) == "object" and ($m.id // null) then
        ($m.id) as $id
        | ($i.labels | map(.name)) as $labs
        | ($id|startswith("Q-")) as $isnode
        # Build the edits string
        | (
            "" +
            (if ($isnode and ($labs|index("type:node")|not)) then " --add-label type:node" else "" end) +
            (if (($isnode|not) and ($labs|index("type:question")|not)) then " --add-label type:question" else "" end) +
            (if ($isnode and ($labs|index("type:question"))) then " --remove-label type:question" else "" end) +
            (if (($isnode|not) and ($labs|index("type:node"))) then " --remove-label type:node" else "" end) +
            (if ($labs|index("q:" + $id)|not) then " --add-label q:" + $id else "" end) +
            (
              ($labs | map(select(test("^q:") and . != ("q:" + $id))) ) as $extraq
              | if ($extraq|length) > 0
                  then " " + ( $extraq | map("--remove-label \"" + . + "\"") | join(" ") )
                  else "" end
            )
          ) as $edits
        | if ($edits | length) > 0
            then "gh issue edit -R " + $repo + " " + ($i.number|tostring) + $edits
            else empty end
      else empty end
  ' <<<"$json"
)"

if [[ -z "$cmds" ]]; then
  echo "All open issues already consistent."
  exit 0
fi

if [[ -n "${DRY_RUN:-}" ]]; then
  echo "$cmds"
  exit 0
fi

while IFS= read -r line; do
  eval "$line"
done <<< "$cmds"

echo "Sanitize complete."
