-- 156-lua-sparse-array — count the positions; never trust # on a table with holes.
local IN = assert(os.getenv("IN"), "IN not set")
local OUT = assert(os.getenv("OUT"), "OUT not set")

local function trim(s)
  return (s:gsub("^%s+", ""):gsub("%s+$", ""))
end

local values = {}
local positions, present, invalid = 0, 0, 0

local fh = assert(io.open(IN .. "/values.txt", "r"))
for raw in fh:lines() do
  positions = positions + 1
  local line = trim(raw)
  if line == "" then
    -- a hole: the position exists, the value does not
  elseif line:match("^%-?%d+$") then
    values[positions] = tonumber(line)
    present = present + 1
  else
    invalid = invalid + 1
  end
end
fh:close()

local total, largest = 0, 0
local out = assert(io.open(OUT .. "/present.csv", "w"))
out:write("position,value\n")
for position = 1, positions do
  local value = values[position]
  if value ~= nil then
    out:write(string.format("%d,%d\n", position, value))
    total = total + value
    if value > largest then largest = value end
  end
end
out:close()

local sum = assert(io.open(OUT .. "/summary.json", "w"))
sum:write(string.format(
  '{"positions":%d,"present":%d,"missing":%d,"invalid":%d,"total":%d,"max":%d}\n',
  positions, present, positions - present, invalid, total, largest))
sum:close()
