-- Plausible bug: walks the table with ipairs, which stops at the first nil, so every
-- entry after the first hole is lost and the report looks short.
local IN = assert(os.getenv("IN"), "IN not set")
local OUT = assert(os.getenv("OUT"), "OUT not set")

local function trim(s)
  return (s:gsub("^%s+", ""):gsub("%s+$", ""))
end

local values = {}
local positions, invalid = 0, 0

local fh = assert(io.open(IN .. "/values.txt", "r"))
for raw in fh:lines() do
  positions = positions + 1
  local line = trim(raw)
  if line == "" then
    -- a hole
  elseif line:match("^%-?%d+$") then
    values[positions] = tonumber(line)
  else
    invalid = invalid + 1
  end
end
fh:close()

local total, largest, present = 0, 0, 0
local out = assert(io.open(OUT .. "/present.csv", "w"))
out:write("position,value\n")
for position, value in ipairs(values) do
  out:write(string.format("%d,%d\n", position, value))
  total = total + value
  present = present + 1
  if value > largest then largest = value end
end
out:close()

local sum = assert(io.open(OUT .. "/summary.json", "w"))
sum:write(string.format(
  '{"positions":%d,"present":%d,"missing":%d,"invalid":%d,"total":%d,"max":%d}\n',
  positions, present, positions - present, invalid, total, largest))
sum:close()
