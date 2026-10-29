-- 160-lua-file-hunt — translate the glob, then match the base name.
local IN = assert(os.getenv("IN"), "IN not set")
local OUT = assert(os.getenv("OUT"), "OUT not set")
local ROOT = IN .. "/hunt"
local GLOB = "*.log"
local MIN_BYTES = 100

local function byte_lt(a, b)
  if a == b then return false end
  for i = 1, math.min(#a, #b) do
    local ca, cb = a:byte(i), b:byte(i)
    if ca ~= cb then return ca < cb end
  end
  return #a < #b
end

-- a glob is not a pattern: escape the literals, then translate '*' and '?'
local function glob_to_pattern(glob)
  local parts = { "^" }
  for index = 1, #glob do
    local char = glob:sub(index, index)
    if char == "*" then
      parts[#parts + 1] = ".*"
    elseif char == "?" then
      parts[#parts + 1] = "."
    elseif char:match("[%^%$%(%)%%%.%[%]%+%-]") then
      parts[#parts + 1] = "%" .. char
    else
      parts[#parts + 1] = char
    end
  end
  parts[#parts + 1] = "$"
  return table.concat(parts)
end

local MATCHER = glob_to_pattern(GLOB)

local function excluded(segment)
  return segment == "archive" or segment:sub(1, 1) == "."
end

local pipe = assert(io.popen("find '" .. ROOT .. "' -type f"))
local paths = {}
for line in pipe:lines() do
  paths[#paths + 1] = line
end
pipe:close()

local found, scanned, bytes = {}, 0, 0

for _, path in ipairs(paths) do
  local rel = path:sub(#ROOT + 2)
  local segments = {}
  for segment in rel:gmatch("[^/]+") do
    segments[#segments + 1] = segment
  end
  local base = segments[#segments]

  local skip = false
  for index = 1, #segments - 1 do
    if excluded(segments[index]) then skip = true break end
  end

  if not skip then
    local size = 0
    local fh = io.open(path, "rb")
    if fh then
      size = fh:seek("end") or 0
      fh:close()
    end
    scanned = scanned + 1
    if base:match(MATCHER) and size >= MIN_BYTES then
      found[#found + 1] = { path = rel, size = size }
      bytes = bytes + size
    end
  end
end

table.sort(found, function(a, b)
  if a.size ~= b.size then return a.size > b.size end
  return byte_lt(a.path, b.path)
end)

local out = assert(io.open(OUT .. "/found.csv", "w"))
out:write("path,size\n")
for _, file in ipairs(found) do
  out:write(string.format("%s,%d\n", file.path, file.size))
end
out:close()

local sum = assert(io.open(OUT .. "/summary.json", "w"))
sum:write(string.format('{"matched":%d,"bytes":%d,"scanned":%d}\n',
  #found, bytes, scanned))
sum:close()
