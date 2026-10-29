-- 002-log-triage — lua patterns, no dependencies.
local IN = assert(os.getenv("IN"), "IN not set")
local OUT = assert(os.getenv("OUT"), "OUT not set")
os.execute("mkdir -p '" .. OUT .. "'")

local status_counts, path_counts = {}, {}
local valid, skipped = 0, 0

local fh = assert(io.open(IN .. "/access.log", "r"))
for line in fh:lines() do
  local _, path, status = line:match('"(%S+) (%S+) HTTP/[%d%.]+%s*"?%s*(%d%d%d)')
  if not status then
    skipped = skipped + 1
  else
    valid = valid + 1
    status_counts[status] = (status_counts[status] or 0) + 1
    path = path:gsub("%?.*$", "")
    path_counts[path] = (path_counts[path] or 0) + 1
  end
end
fh:close()

local function sorted(counts, numeric)
  local keys = {}
  for k in pairs(counts) do keys[#keys + 1] = k end
  table.sort(keys, function(a, b)
    if counts[a] ~= counts[b] then return counts[a] > counts[b] end
    if numeric then return tonumber(a) < tonumber(b) end
    return a < b
  end)
  return keys
end

local f = assert(io.open(OUT .. "/status.csv", "w"))
f:write("status,count\n")
for _, code in ipairs(sorted(status_counts, true)) do
  f:write(string.format("%s,%d\n", code, status_counts[code]))
end
f:close()

local g = assert(io.open(OUT .. "/top_paths.csv", "w"))
g:write("path,hits\n")
local shown = 0
for _, path in ipairs(sorted(path_counts, false)) do
  if shown == 5 then break end
  g:write(string.format("%s,%d\n", path, path_counts[path]))
  shown = shown + 1
end
g:close()

local h = assert(io.open(OUT .. "/summary.json", "w"))
h:write(string.format('{"valid":%d,"skipped":%d}\n', valid, skipped))
h:close()
