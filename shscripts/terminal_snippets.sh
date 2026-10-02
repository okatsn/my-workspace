# Find files named as `chat___*.md` AND the first line is not `exclude-from-graph-view:: true`
rg -U --files-without-match '\Aexclude-from-graph-view:: true$' -g 'chat___*.md'