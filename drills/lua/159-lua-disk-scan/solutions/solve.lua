-- 159-lua-disk-scan — no stat, no opendir: find plus seek("end").
local IN = assert(os.getenv("IN"), "IN not set")
local OUT = assert(os.getenv("OUT"), "OUT not set")
local ROOT = IN .. "/tree"

local function byte_lt(a, b)
  if a == b then return false end
  for i = 1, math.min(#a, #b) do
    local ca, cb = a:byte(i), b:byte(i)
    if ca ~= cb then return ca < cb end
  end
  return #a < #b
end

local function excluded(segment)
  return segment == "node_modules" or segment:sub(1, 1) == "."
end

local pipe = assert(io.popen("find '" .. ROOT .. "' -type f"))
local paths = {}
for line in pipe:lines() do
  paths[#paths + 1] = line
end
pipe:close()

local stats, order = {}, {}
local skipped = {}
local files, total = 0, 0

for _, path in ipairs(paths) do
  local rel = path:sub(#ROOT + 2)
  local segments = {}
  for segment in rel:gmatch("[^/]+") do
    segments[#segments + 1] = segment
  end
  local base = segments[#segments]

  local excluded_dir
  local prefix = {}
  for index = 1, #segments - 1 do
    prefix[#prefix + 1] = segments[index]
    if excluded(segments[index]) then
      excluded_dir = table.concat(prefix, "/")
      break
    end
  end

  if excluded_dir then
    skipped[excluded_dir] = true
  else
    local size = 0
    local fh = io.open(path, "rb")
    if fh then
      size = fh:seek("end") or 0
      fh:close()
    end
    local ext = ""
    local stem, suffix = base:match("^(.*)%.([^%.]*)$")
    if stem and stem ~= "" then ext = suffix:lower() end
    local entry = stats[ext]
    if not entry then
      entry = { count = 0, bytes = 0 }
      stats[ext] = entry
      order[#order + 1] = ext
    end
    entry.count = entry.count + 1
    entry.bytes = entry.bytes + size
    files = files + 1
    total = total + size
  end
end

table.sort(order, function(a, b)
  if stats[a].bytes ~= stats[b].bytes then return stats[a].bytes > stats[b].bytes end
  return byte_lt(a, b)
end)

local out = assert(io.open(OUT .. "/bytes.csv", "w"))
out:write("ext,count,bytes\n")
for _, ext in ipairs(order) do
  out:write(string.format("%s,%d,%d\n", ext, stats[ext].count, stats[ext].bytes))
end
out:close()

local dirs_skipped = 0
for _ in pairs(skipped) do dirs_skipped = dirs_skipped + 1 end

local sum = assert(io.open(OUT .. "/summary.json", "w"))
sum:write(string.format('{"files":%d,"bytes":%d,"dirs_skipped":%d}\n',
  files, total, dirs_skipped))
sum:close()
